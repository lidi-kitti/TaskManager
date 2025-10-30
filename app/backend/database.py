from sqlalchemy import Column, String, DateTime, Enum as SQLEnum, create_engine, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
import enum
from datetime import datetime, timezone
import uuid

# Асинхронная база данных
import os
from pathlib import Path

# Определяем корневую директорию проекта (на 3 уровня выше от app/backend/database.py)
_project_root = Path(__file__).resolve().parent.parent.parent
_db_path = _project_root / "taskmanager.db"
# URL БД можно переопределить через окружение
import os
_env_db = os.getenv("TM_DATABASE_URL")
DATABASE_URL = _env_db if (_env_db and _env_db.strip()) else f"sqlite+aiosqlite:///{_db_path}"

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()


class TaskStatusEnum(enum.Enum):
    """Enum для статусов задач в БД"""
    CREATED = "новая"
    IN_PROGRESS = "в работе"
    COMPLETED = "завершено"

class PriorityEnum(enum.Enum):
    """Enum для приоритетов задач в БД"""
    LOW = "низкий"
    MEDIUM = "средний"
    HIGH = "высокий"

class RoleEnum(enum.Enum):
    """Роли пользователей"""
    ADMIN = "admin"
    USER = "user"

class UserDB(Base):
    """SQLAlchemy модель для пользователей"""
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(150), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(SQLEnum(RoleEnum), nullable=False, default=RoleEnum.USER)

    # Связь с задачами
    # tasks = relationship("TaskDB", back_populates="user", cascade="all, delete-orphan")


class TaskDB(Base):
    """SQLAlchemy модель для задач"""
    __tablename__ = "tasks"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(String(1000), nullable=True)
    status = Column(SQLEnum(TaskStatusEnum), nullable=False, default=TaskStatusEnum.CREATED)
    priority = Column(SQLEnum(PriorityEnum), nullable=False, default=PriorityEnum.MEDIUM)
    deadline = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # user = relationship("UserDB", backref="tasks")


async def get_db():
    """Получение сессии базы данных"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Инициализация базы данных"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        from sqlalchemy import inspect, text
        inspector = inspect(conn.sync_connection)

        tables = inspector.get_table_names()
        if "users" not in tables:
            await conn.execute(text(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id VARCHAR PRIMARY KEY,
                    username VARCHAR(150) UNIQUE NOT NULL,
                    hashed_password VARCHAR(255) NOT NULL,
                    role VARCHAR NOT NULL
                )
                """
            ))

        # Добавить user_id в tasks, если отсутствует
        columns = [c["name"] for c in inspector.get_columns("tasks")] if "tasks" in tables else []
        if "tasks" in tables and "user_id" not in columns:
            # Добавляем nullable колонку, затем выставим значения и оставим nullable для совместимости
            try:
                await conn.execute(text("ALTER TABLE tasks ADD COLUMN user_id VARCHAR"))
            except Exception:
                pass
