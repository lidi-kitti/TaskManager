from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from app.models import Task, TaskCreate, TaskUpdate, TaskStatus
from app.database import TaskDB, TaskStatusEnum


class TaskService:
    """Сервис для управления задачами с использованием SQLite"""
    
    def __init__(self):
        pass
    
    def _status_to_enum(self, status: TaskStatus) -> TaskStatusEnum:
        """Конвертация статуса из Pydantic в SQLAlchemy enum"""
        mapping = {
            TaskStatus.CREATED: TaskStatusEnum.CREATED,
            TaskStatus.IN_PROGRESS: TaskStatusEnum.IN_PROGRESS,
            TaskStatus.COMPLETED: TaskStatusEnum.COMPLETED
        }
        return mapping[status]
    
    def _enum_to_status(self, enum_status: TaskStatusEnum) -> TaskStatus:
        """Конвертация статуса из SQLAlchemy enum в Pydantic"""
        mapping = {
            TaskStatusEnum.CREATED: TaskStatus.CREATED,
            TaskStatusEnum.IN_PROGRESS: TaskStatus.IN_PROGRESS,
            TaskStatusEnum.COMPLETED: TaskStatus.COMPLETED
        }
        return mapping[enum_status]
    
    def _db_to_pydantic(self, db_task: TaskDB) -> Task:
        """Конвертация SQLAlchemy модели в Pydantic"""
        return Task(
            id=db_task.id,
            title=db_task.title,
            description=db_task.description,
            status=self._enum_to_status(db_task.status),
            created_at=db_task.created_at,
            updated_at=db_task.updated_at
        )
    
    async def create_task(self, db: AsyncSession, task_data: TaskCreate) -> Task:
        """Создание новой задачи"""
        db_task = TaskDB(
            title=task_data.title,
            description=task_data.description,
            status=self._status_to_enum(task_data.status)
        )
        
        db.add(db_task)
        await db.commit()
        await db.refresh(db_task)
        
        return self._db_to_pydantic(db_task)
    
    async def get_task(self, db: AsyncSession, task_id: str) -> Optional[Task]:
        """Получение задачи по ID"""
        result = await db.execute(select(TaskDB).where(TaskDB.id == task_id))
        db_task = result.scalar_one_or_none()
        
        if db_task is None:
            return None
            
        return self._db_to_pydantic(db_task)
    
    async def get_tasks(self, db: AsyncSession, status: Optional[TaskStatus] = None) -> List[Task]:
        """Получение списка задач с возможной фильтрацией по статусу"""
        query = select(TaskDB)
        
        if status is not None:
            enum_status = self._status_to_enum(status)
            query = query.where(TaskDB.status == enum_status)
        
        result = await db.execute(query)
        db_tasks = result.scalars().all()
        
        return [self._db_to_pydantic(db_task) for db_task in db_tasks]
    
    async def update_task(self, db: AsyncSession, task_id: str, task_data: TaskUpdate) -> Optional[Task]:
        """Обновление задачи"""
        # Проверяем существование задачи
        result = await db.execute(select(TaskDB).where(TaskDB.id == task_id))
        db_task = result.scalar_one_or_none()
        
        if db_task is None:
            return None
        
        # Подготавливаем данные для обновления
        update_data = task_data.dict(exclude_unset=True)
        
        # Конвертируем статус если он присутствует
        if "status" in update_data:
            update_data["status"] = self._status_to_enum(update_data["status"])
        
        # Обновляем время последнего изменения
        update_data["updated_at"] = datetime.now(timezone.utc)
        
        # Выполняем обновление
        await db.execute(
            update(TaskDB)
            .where(TaskDB.id == task_id)
            .values(**update_data)
        )
        await db.commit()
        
        # Получаем обновленную задачу
        result = await db.execute(select(TaskDB).where(TaskDB.id == task_id))
        updated_task = result.scalar_one()
        
        return self._db_to_pydantic(updated_task)
    
    async def delete_task(self, db: AsyncSession, task_id: str) -> bool:
        """Удаление задачи"""
        # Проверяем существование задачи
        result = await db.execute(select(TaskDB).where(TaskDB.id == task_id))
        db_task = result.scalar_one_or_none()
        
        if db_task is None:
            return False
        
        # Удаляем задачу
        await db.execute(delete(TaskDB).where(TaskDB.id == task_id))
        await db.commit()
        
        return True


# Глобальный экземпляр сервиса
task_service = TaskService()
