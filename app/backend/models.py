from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
import uuid
from datetime import datetime, timezone


class TaskStatus(str, Enum):
    """Статусы задач"""
    CREATED = "новая"
    IN_PROGRESS = "в работе"
    COMPLETED = "завершено"

class Priority(str, Enum):
    """Приоритеты задач"""
    LOW = "низкий"
    MEDIUM = "средний"
    HIGH = "высокий"

class TaskBase(BaseModel):
    """Базовая модель задачи"""
    title: str = Field(..., min_length=1, max_length=200, description="Название задачи")
    description: Optional[str] = Field(None, max_length=1000, description="Описание задачи")
    status: TaskStatus = Field(default=TaskStatus.CREATED, description="Статус задачи")
    priority: Priority = Field(default=Priority.MEDIUM, description="Приоритет задачи")
    deadline: Optional[datetime] = Field(None, description="Срок выполнения задачи")

class TaskCreate(TaskBase):
    """Модель для создания задачи"""
    pass


class TaskUpdate(BaseModel):
    """Модель для обновления задачи"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    status: Optional[TaskStatus] = None
    priority: Optional[Priority] = None
    deadline: Optional[datetime] = None


class Task(TaskBase):
    """Полная модель задачи"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Уникальный идентификатор")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Дата создания")
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Дата последнего обновления")

    class Config:
        from_attributes = True

class TaskStatistics(BaseModel):
    """Модель статистики задач"""
    total: int
    created: int
    in_progress: int
    completed: int
    overdue: int
    high_priority: int
    medium_priority: int
    low_priority: int
    completed_today: int