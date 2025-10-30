from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import httpx

from app.backend.database import UserDB, RoleEnum
from app.backend.database import get_db


# Настройки JWT берём из окружения (с дефолтами для dev)
import os
SECRET_KEY = os.getenv("TM_SECRET_KEY", "CHANGE_ME_DEV_SECRET")
ALGORITHM = os.getenv("TM_JWT_ALG", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("TM_ACCESS_EXPIRE_MIN", "1440"))

# Яндекс OAuth
YA_CLIENT_ID = os.getenv("TM_YA_CLIENT_ID", "")
YA_CLIENT_SECRET = os.getenv("TM_YA_CLIENT_SECRET", "")
YA_REDIRECT_URI = os.getenv("TM_YA_REDIRECT_URI", "http://localhost:5173/")
YA_AUTHORIZE_URL = "https://oauth.yandex.ru/authorize"
YA_TOKEN_URL = "https://oauth.yandex.ru/token"
YA_USERINFO_URL = "https://login.yandex.ru/info"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

auth_router = APIRouter(prefix="/api/v1/auth", tags=["auth"]) 


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=150)
    password: str = Field(min_length=6, max_length=128)


class UserOut(BaseModel):
    id: str
    username: str
    role: str


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_user_by_username(db: AsyncSession, username: str) -> Optional[UserDB]:
    res = await db.execute(select(UserDB).where(UserDB.username == username))
    return res.scalar_one_or_none()


@auth_router.post("/register", response_model=UserOut, status_code=201)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    existing = await get_user_by_username(db, user.username)
    if existing:
        raise HTTPException(status_code=400, detail="Пользователь уже существует")
    db_user = UserDB(username=user.username, hashed_password=hash_password(user.password))
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return UserOut(id=db_user.id, username=db_user.username, role=db_user.role.value)


@auth_router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await get_user_by_username(db, form_data.username)
    if user is None or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверные учетные данные")
    token = create_access_token({"sub": user.id, "username": user.username, "role": user.role.value})
    return Token(access_token=token)


@auth_router.get("/yandex/config")
async def yandex_config():
    if not YA_CLIENT_ID or not YA_REDIRECT_URI:
        raise HTTPException(status_code=500, detail="Яндекс OAuth не настроен")
    return {"client_id": YA_CLIENT_ID, "redirect_uri": YA_REDIRECT_URI, "authorize_url": YA_AUTHORIZE_URL}


@auth_router.get("/yandex/login")
async def yandex_login():
    if not YA_CLIENT_ID or not YA_REDIRECT_URI:
        raise HTTPException(status_code=500, detail="Яндекс OAuth не настроен")
    params = {
        "response_type": "code",
        "client_id": YA_CLIENT_ID,
        "redirect_uri": YA_REDIRECT_URI,
    }
    # Возвращаем полный URL для редиректа на Яндекс
    from urllib.parse import urlencode
    return {"redirect_to": f"{YA_AUTHORIZE_URL}?{urlencode(params)}"}


@auth_router.post("/yandex/callback", response_model=Token)
async def yandex_callback(code: str, db: AsyncSession = Depends(get_db)):
    if not YA_CLIENT_ID or not YA_REDIRECT_URI:
        raise HTTPException(status_code=500, detail="Яндекс OAuth не настроен")
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "client_id": YA_CLIENT_ID,
        "redirect_uri": YA_REDIRECT_URI,
    }
    # Если есть секрет, добавим для серверного обмена
    if YA_CLIENT_SECRET:
        data["client_secret"] = YA_CLIENT_SECRET

    async with httpx.AsyncClient() as client:
        token_resp = await client.post(YA_TOKEN_URL, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
        if token_resp.status_code != 200:
            raise HTTPException(status_code=400, detail="Не удалось обменять код на токен Яндекс")
        ya_token = token_resp.json().get("access_token")
        if not ya_token:
            raise HTTPException(status_code=400, detail="Токен Яндекс отсутствует")

        userinfo_resp = await client.get(YA_USERINFO_URL, params={"format": "json"}, headers={"Authorization": f"OAuth {ya_token}"})
        if userinfo_resp.status_code != 200:
            raise HTTPException(status_code=400, detail="Не удалось получить профиль Яндекс")
        profile = userinfo_resp.json()

    # Связываем/создаём локального пользователя
    ya_user_id = profile.get("id") or profile.get("uid") or profile.get("client_id")
    if not ya_user_id:
        raise HTTPException(status_code=400, detail="В ответе Яндекс нет id пользователя")
    username = f"ya_{ya_user_id}"

    user = await get_user_by_username(db, username)
    if not user:
        # Создаём пользователя со случайным паролем (не используется)
        import secrets
        user = UserDB(
            username=username,
            hashed_password=hash_password(secrets.token_urlsafe(16)),
            role=RoleEnum.USER,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    token = create_access_token({"sub": user.id, "username": user.username, "role": user.role.value})
    return Token(access_token=token)


class CurrentUser(BaseModel):
    id: str
    username: str
    role: RoleEnum


async def get_current_user(token: str = Depends(oauth2_scheme)) -> CurrentUser:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось проверить учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        username: str = payload.get("username")
        role: str = payload.get("role")
        if user_id is None or username is None or role is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return CurrentUser(id=user_id, username=username, role=RoleEnum(role))


def require_admin(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    if user.role != RoleEnum.ADMIN:
        raise HTTPException(status_code=403, detail="Требуются права администратора")
    return user


async def ensure_admin(db: AsyncSession, username: str = "admin", password: str = "admin123") -> None:
    """Создаёт администратора, если его нет (для dev)."""
    res = await db.execute(select(UserDB).where(UserDB.username == username))
    existing = res.scalar_one_or_none()
    if existing is None:
        admin = UserDB(
            username=username,
            hashed_password=hash_password(password),
            role=RoleEnum.ADMIN,
        )
        db.add(admin)
        await db.commit()


