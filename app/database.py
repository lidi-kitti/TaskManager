from sqlalchemy import Column, String, DateTime, Enum as SQLEnum, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
import enum
from datetime import datetime, timezone
import uuid

# Асинхронная база данных
DATABASE_URL = "sqlite+aiosqlite:///./taskmanager.db"

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


class TaskDB(Base):
    """SQLAlchemy модель для задач"""
    __tablename__ = "tasks"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(200), nullable=False)
    description = Column(String(1000), nullable=True)
    status = Column(SQLEnum(TaskStatusEnum), nullable=False, default=TaskStatusEnum.CREATED)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


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
