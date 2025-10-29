from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.backend.models import Task, TaskCreate, TaskUpdate, TaskStatus
from app.backend.services import task_service
from app.backend.database import get_db

router = APIRouter(prefix="/api/v1/tasks", tags=["tasks"])


@router.post("/", response_model=Task, status_code=201)
async def create_task(task: TaskCreate, db: AsyncSession = Depends(get_db)):
    """Создание новой задачи"""
    return await task_service.create_task(db, task)


@router.get("/{task_id}", response_model=Task)
async def get_task(task_id: str, db: AsyncSession = Depends(get_db)):
    """Получение задачи по ID"""
    task = await task_service.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return task


@router.get("/", response_model=List[Task])
async def get_tasks(
    status: Optional[TaskStatus] = Query(None, description="Фильтр по статусу"),
    db: AsyncSession = Depends(get_db)
):
    """Получение списка задач"""
    return await task_service.get_tasks(db, status)


@router.put("/{task_id}", response_model=Task)
async def update_task(task_id: str, task_update: TaskUpdate, db: AsyncSession = Depends(get_db)):
    """Обновление задачи"""
    task = await task_service.update_task(db, task_id, task_update)
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return task


@router.delete("/{task_id}", status_code=204)
async def delete_task(task_id: str, db: AsyncSession = Depends(get_db)):
    """Удаление задачи"""
    if not await task_service.delete_task(db, task_id):
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return None
