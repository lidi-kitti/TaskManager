#!/usr/bin/env python3
"""
Скрипт для создания тестовых данных в SQLite базе данных
"""

import asyncio
import sys
from app.database import init_db, AsyncSessionLocal
from app.services import task_service
from app.models import TaskCreate, TaskStatus


async def create_test_data():
    """Создание тестовых данных"""
    print("Инициализация базы данных...")
    await init_db()
    
    print("Создание тестовых задач...")
    
    # Тестовые задачи
    test_tasks = [
        TaskCreate(
            title="Изучить FastAPI",
            description="Изучить основы веб-фреймворка FastAPI",
            status=TaskStatus.COMPLETED
        ),
        TaskCreate(
            title="Настроить SQLite",
            description="Настроить базу данных SQLite для приложения",
            status=TaskStatus.IN_PROGRESS
        ),
        TaskCreate(
            title="Написать тесты",
            description="Написать тесты с использованием Gauge",
            status=TaskStatus.CREATED
        ),
        TaskCreate(
            title="Деплой на сервер",
            description="Развернуть приложение на продакшн сервере",
            status=TaskStatus.CREATED
        ),
        TaskCreate(
            title="Оптимизация производительности",
            description="Провести анализ и оптимизацию производительности API",
            status=TaskStatus.CREATED
        )
    ]
    
    async with AsyncSessionLocal() as db:
        created_tasks = []
        
        for task_data in test_tasks:
            try:
                task = await task_service.create_task(db, task_data)
                created_tasks.append(task)
                print(f"Создана задача: {task.title} (статус: {task.status})")
            except Exception as e:
                print(f"Ошибка создания задачи {task_data.title}: {e}")
    
    print(f"\nСоздано {len(created_tasks)} тестовых задач!")
    return created_tasks


async def show_statistics():
    """Показать статистику задач"""
    print("\nСтатистика задач:")
    
    async with AsyncSessionLocal() as db:
        # Общее количество
        all_tasks = await task_service.get_tasks(db)
        print(f"Всего задач: {len(all_tasks)}")
        
        # По статусам
        for status in TaskStatus:
            tasks = await task_service.get_tasks(db, status)
            print(f"Статус '{status.value}': {len(tasks)} задач")


async def main():
    """Основная функция"""
    print("Создание тестовых данных TaskManager")
    print("=" * 45)
    
    try:
        await create_test_data()
        await show_statistics()
        
        print("\nТестовые данные успешно созданы!")
        print("Теперь можно запустить приложение: python run_app.py")
        
    except Exception as e:
        print(f"\nОшибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
