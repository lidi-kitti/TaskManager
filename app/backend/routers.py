from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.backend.models import Task, TaskCreate, TaskUpdate, TaskStatus, TaskStatistics
from app.backend.services import task_service
from app.backend.database import get_db
from app.backend.auth import get_current_user, require_admin, CurrentUser

router = APIRouter(prefix="/api/v1/tasks", tags=["tasks"])


@router.post("/", response_model=Task, status_code=201)
async def create_task(task: TaskCreate, db: AsyncSession = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)):
    """Создание новой задачи"""
    return await task_service.create_task(db, task, current_user)


@router.get("/{task_id}", response_model=Task)
async def get_task(task_id: str, db: AsyncSession = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)):
    """Получение задачи по ID"""
    task = await task_service.get_task(db, task_id, current_user)
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return task


@router.get("/", response_model=List[Task])
async def get_tasks(
    status: Optional[TaskStatus] = Query(None, description="Фильтр по статусу"),
    search: Optional[str] = Query(None, description="Поиск по названию и описанию"),
    sort_by: Optional[str] = Query(None, description="Сортировка: created_at, updated_at, status, priority, deadline"),
    sort_order: Optional[str] = Query("asc", description="Порядок сортировки: asc или desc"),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """Получение списка задач"""
    return await task_service.get_tasks(db, status, search, sort_by, sort_order, current_user)


@router.put("/{task_id}", response_model=Task)
async def update_task(task_id: str, task_update: TaskUpdate, db: AsyncSession = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)):
    """Обновление задачи"""
    task = await task_service.update_task(db, task_id, task_update, current_user)
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return task


@router.delete("/{task_id}", status_code=204)
async def delete_task(task_id: str, db: AsyncSession = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)):
    """Удаление задачи"""
    if not await task_service.delete_task(db, task_id, current_user):
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return None

@router.get("/statistics/summary", response_model=TaskStatistics)
async def get_statistics(db: AsyncSession = Depends(get_db)):
    """Получение статистики задач"""
    return await task_service.get_statistics(db)