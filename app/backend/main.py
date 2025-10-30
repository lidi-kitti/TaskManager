from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from dotenv import load_dotenv

# Загружаем переменные окружения из .env до импорта модулей, которые их читают
load_dotenv()

from app.backend.routers import router
from app.backend.database import init_db, AsyncSessionLocal
from app.backend.auth import auth_router, ensure_admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events для инициализации и завершения приложения"""
    # Startup
    await init_db()
    # Создание дефолтного администратора (dev)
    async with AsyncSessionLocal() as session:
        await ensure_admin(session)
    print("База данных инициализирована")
    yield
    # Shutdown
    print("Завершение работы приложения")


app = FastAPI(
    title="TaskManager API",
    description="API для управления задачами с SQLite базой данных",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутов
app.include_router(router)
app.include_router(auth_router)

@app.get("/")
async def root():
    """Корневой эндпоинт"""
    return {
        "message": "Добро пожаловать в TaskManager API",
        "version": "1.0.0",
        "database": "SQLite",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
async def health_check():
    """Проверка состояния приложения"""
    return {"status": "healthy", "database": "SQLite"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
