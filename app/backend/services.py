from typing import List, Optional
from datetime import datetime, timezone, date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from app.backend.models import Task, TaskCreate, TaskUpdate, TaskStatus, Priority, TaskStatistics
from app.backend.database import TaskDB, TaskStatusEnum, PriorityEnum


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
    
    def _priority_to_enum(self, priority: Priority) -> PriorityEnum:
        """Конвертация приоритета из Pydantic в SQLAlchemy enum"""
        mapping = {
            Priority.LOW: PriorityEnum.LOW,
            Priority.MEDIUM: PriorityEnum.MEDIUM,
            Priority.HIGH: PriorityEnum.HIGH
        }
        return mapping[priority]

    def _enum_to_priority(self, enum_priority: PriorityEnum) -> Priority:
        """Конвертация приоритета из SQLAlchemy enum в Pydantic"""
        mapping = {
            PriorityEnum.LOW: Priority.LOW,
            PriorityEnum.MEDIUM: Priority.MEDIUM,
            PriorityEnum.HIGH: Priority.HIGH
        }
        return mapping[enum_priority]
    
    def _db_to_pydantic(self, db_task: TaskDB) -> Task:
        """Конвертация SQLAlchemy модели в Pydantic"""
        return Task(
            id=db_task.id,
            title=db_task.title,
            description=db_task.description,
            status=self._enum_to_status(db_task.status),
            priority=self._enum_to_priority(db_task.priority),
            deadline=db_task.deadline,
            created_at=db_task.created_at,
            updated_at=db_task.updated_at
        )
    
    async def create_task(self, db: AsyncSession, task_data: TaskCreate) -> Task:
        """Создание новой задачи"""
        db_task = TaskDB(
            title=task_data.title,
            description=task_data.description,
            status=self._status_to_enum(task_data.status),
            priority=self._priority_to_enum(task_data.priority),
            deadline=task_data.deadline
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
    
    async def get_tasks(
        self, 
        db: AsyncSession,
        status: Optional[TaskStatus] = None,
        search: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = "asc") -> List[Task]:
        """Получение списка задач с возможной фильтрацией по статусу"""
        query = select(TaskDB)
        
        if status is not None:
            enum_status = self._status_to_enum(status)
            query = query.where(TaskDB.status == enum_status)
        # Поиск по названию и описанию
        if search:
            search_pattern = f"%{search}%"
            query = query.where(
                or_(
                    TaskDB.title.ilike(search_pattern),
                    TaskDB.description.ilike(search_pattern)
                )
            )
        
        # Сортировка
        if sort_by:
            if sort_by == "created_at":
                query = query.order_by(TaskDB.created_at.desc() if sort_order == "desc" else TaskDB.created_at.asc())
            elif sort_by == "updated_at":
                query = query.order_by(TaskDB.updated_at.desc() if sort_order == "desc" else TaskDB.updated_at.asc())
            elif sort_by == "status":
                query = query.order_by(TaskDB.status.desc() if sort_order == "desc" else TaskDB.status.asc())
            elif sort_by == "priority":
                priority_order = {PriorityEnum.HIGH: 3, PriorityEnum.MEDIUM: 2, PriorityEnum.LOW: 1}
                # Для сортировки по приоритету нужно использовать case
                from sqlalchemy import case
                query = query.order_by(
                    case(
                        (TaskDB.priority == PriorityEnum.HIGH, 3),
                        (TaskDB.priority == PriorityEnum.MEDIUM, 2),
                        (TaskDB.priority == PriorityEnum.LOW, 1),
                        else_=0
                    ).desc() if sort_order == "desc" else 
                    case(
                        (TaskDB.priority == PriorityEnum.HIGH, 3),
                        (TaskDB.priority == PriorityEnum.MEDIUM, 2),
                        (TaskDB.priority == PriorityEnum.LOW, 1),
                        else_=0
                    ).asc()
                )
            elif sort_by == "deadline":
                query = query.order_by(TaskDB.deadline.desc() if sort_order == "desc" else TaskDB.deadline.asc())
        else:
            # Сортировка по умолчанию - по дате создания (новые сначала)
            query = query.order_by(TaskDB.created_at.desc())
        
        result = await db.execute(query)
        db_tasks = result.scalars().all()
        
        return [self._db_to_pydantic(db_task) for db_task in db_tasks]
    
    async def update_task(self, db: AsyncSession, task_id: str, task_data: TaskUpdate) -> Optional[Task]:
        """Обновление задачи"""
        result = await db.execute(select(TaskDB).where(TaskDB.id == task_id))
        db_task = result.scalar_one_or_none()
        
        if db_task is None:
            return None
        
        update_data = task_data.dict(exclude_unset=True)
        
        if "status" in update_data:
            update_data["status"] = self._status_to_enum(update_data["status"])
        if "priority" in update_data:
            update_data["priority"] = self._priority_to_enum(update_data["priority"])
        
        update_data["updated_at"] = datetime.now(timezone.utc)
        
        await db.execute(
            update(TaskDB)
            .where(TaskDB.id == task_id)
            .values(**update_data)
        )
        await db.commit()
        
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

    async def get_statistics(self, db: AsyncSession) -> TaskStatistics:
        """Получение статистики задач"""
        all_tasks = await db.execute(select(TaskDB))
        tasks = all_tasks.scalars().all()
        
        today = date.today()
        
        stats = TaskStatistics(
            total=len(tasks),
            created=sum(1 for t in tasks if t.status == TaskStatusEnum.CREATED),
            in_progress=sum(1 for t in tasks if t.status == TaskStatusEnum.IN_PROGRESS),
            completed=sum(1 for t in tasks if t.status == TaskStatusEnum.COMPLETED),
            overdue=sum(1 for t in tasks if t.deadline and t.status != TaskStatusEnum.COMPLETED and t.deadline < today),
            high_priority=sum(1 for t in tasks if t.priority == PriorityEnum.HIGH),
            medium_priority=sum(1 for t in tasks if t.priority == PriorityEnum.MEDIUM),
            low_priority=sum(1 for t in tasks if t.priority == PriorityEnum.LOW),
            completed_today=sum(1 for t in tasks if t.status == TaskStatusEnum.COMPLETED and t.updated_at.date() == today)
        )
        
        return stats
    

# Глобальный экземпляр сервиса
task_service = TaskService()
