#!/usr/bin/env python3
"""
Скрипт для создания тестовых данных в SQLite базе данных
"""

import asyncio
import sys
import os

# Добавляем корневую директорию проекта в путь для импорта
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from app.backend.database import init_db, AsyncSessionLocal, UserDB, RoleEnum
from app.backend.services import task_service
from app.backend.models import TaskCreate, TaskStatus, Priority
from app.backend.auth import hash_password, CurrentUser
from sqlalchemy import select


async def create_test_users(db):
    """Создание тестовых пользователей"""
    print("Создание тестовых пользователей...")
    
    test_users = [
        {
            "username": "admin",
            "password": "admin123",
            "role": RoleEnum.ADMIN,
            "should_exist": True  # Админ уже должен быть создан через ensure_admin
        },
        {
            "username": "user1",
            "password": "user123",
            "role": RoleEnum.USER
        },
        {
            "username": "user2",
            "password": "user456",
            "role": RoleEnum.USER
        }
    ]
    
    created_users = []
    for user_data in test_users:
        # Проверяем, существует ли пользователь
        result = await db.execute(
            select(UserDB).where(UserDB.username == user_data["username"])
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            print(f"  Пользователь '{user_data['username']}' уже существует (пропущен)")
            created_users.append(existing)
        else:
            new_user = UserDB(
                username=user_data["username"],
                hashed_password=hash_password(user_data["password"]),
                role=user_data["role"]
            )
            db.add(new_user)
            await db.commit()
            await db.refresh(new_user)
            created_users.append(new_user)
            print(f"  ✅ Создан пользователь: {user_data['username']} (роль: {user_data['role'].value})")
    
    print(f"Всего пользователей: {len(created_users)}\n")
    return created_users


async def create_test_tasks(db, users):
    """Создание тестовых задач для пользователей"""
    print("Создание тестовых задач...")
    
    # Получаем админа и обычных пользователей
    admin = next((u for u in users if u.role == RoleEnum.ADMIN), None)
    regular_users = [u for u in users if u.role == RoleEnum.USER]
    
    if not admin:
        print("  ⚠️ Администратор не найден!")
        return []
    
    # Тестовые задачи для админа
    admin_tasks = [
        TaskCreate(
            title="Изучить FastAPI",
            description="Изучить основы веб-фреймворка FastAPI",
            status=TaskStatus.COMPLETED,
            priority=Priority.HIGH
        ),
        TaskCreate(
            title="Настроить SQLite",
            description="Настроить базу данных SQLite для приложения",
            status=TaskStatus.IN_PROGRESS,
            priority=Priority.MEDIUM
        ),
        TaskCreate(
            title="Деплой на сервер",
            description="Развернуть приложение на продакшн сервере",
            status=TaskStatus.CREATED,
            priority=Priority.HIGH
        ),
    ]
    
    # Тестовые задачи для обычных пользователей
    user_tasks_template = [
        TaskCreate(
            title="Написать тесты",
            description="Написать тесты для модулей приложения",
            status=TaskStatus.IN_PROGRESS,
            priority=Priority.MEDIUM
        ),
        TaskCreate(
            title="Оптимизация производительности",
            description="Провести анализ и оптимизацию производительности API",
            status=TaskStatus.CREATED,
            priority=Priority.LOW
        ),
        TaskCreate(
            title="Документация API",
            description="Написать документацию для API endpoints",
            status=TaskStatus.CREATED,
            priority=Priority.MEDIUM
        )
    ]
    
    created_tasks = []
    
    # Создаём задачи для админа
    admin_user = CurrentUser(id=admin.id, username=admin.username, role=admin.role)
    for task_data in admin_tasks:
        try:
            task = await task_service.create_task(db, task_data, admin_user)
            created_tasks.append(task)
            print(f"  ✅ Создана задача для {admin.username}: {task.title}")
        except Exception as e:
            print(f"  ❌ Ошибка создания задачи '{task_data.title}' для {admin.username}: {e}")
    
    # Создаём задачи для каждого обычного пользователя
    for user in regular_users:
        user_obj = CurrentUser(id=user.id, username=user.username, role=user.role)
        for task_data in user_tasks_template:
            try:
                task = await task_service.create_task(db, task_data, user_obj)
                created_tasks.append(task)
                print(f"  ✅ Создана задача для {user.username}: {task.title}")
            except Exception as e:
                print(f"  ❌ Ошибка создания задачи '{task_data.title}' для {user.username}: {e}")
    
    print(f"\nСоздано {len(created_tasks)} тестовых задач!")
    return created_tasks


async def show_statistics():
    """Показать статистику задач"""
    print("\n📊 Статистика задач:")
    
    async with AsyncSessionLocal() as db:
        # Получаем всех пользователей для статистики
        result = await db.execute(select(UserDB))
        users = result.scalars().all()
        
        total_tasks = 0
        for user in users:
            user_obj = CurrentUser(id=user.id, username=user.username, role=user.role)
            tasks = await task_service.get_tasks(db, current_user=user_obj)
            total_tasks += len(tasks)
            print(f"  {user.username} ({user.role.value}): {len(tasks)} задач")
        
        print(f"\n  Всего задач в системе: {total_tasks}")
        
        # Статистика по статусам (для админа, который видит все)
        admin = next((u for u in users if u.role == RoleEnum.ADMIN), None)
        if admin:
            admin_obj = CurrentUser(id=admin.id, username=admin.username, role=admin.role)
            all_tasks = await task_service.get_tasks(db, current_user=admin_obj)
            print(f"\n  Статистика по статусам (от имени админа):")
            for status in TaskStatus:
                count = sum(1 for t in all_tasks if t.status == status)
                print(f"    {status.value}: {count} задач")


async def main():
    """Основная функция"""
    # Устанавливаем UTF-8 для Windows
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    
    print("🚀 Создание тестовых данных TaskManager")
    print("=" * 50)
    
    try:
        print("Инициализация базы данных...")
        await init_db()
        print("✅ База данных инициализирована\n")
        
        async with AsyncSessionLocal() as db:
            # Создаём тестовых пользователей
            users = await create_test_users(db)
            
            # Создаём тестовые задачи
            tasks = await create_test_tasks(db, users)
        
        # Показываем статистику
        await show_statistics()
        
        print("\n" + "=" * 50)
        print("✅ Тестовые данные успешно созданы!")
        print("\n📝 Тестовые пользователи:")
        print("   - admin / admin123 (администратор)")
        print("   - user1 / user123 (обычный пользователь)")
        print("   - user2 / user456 (обычный пользователь)")
        print("\n🚀 Теперь можно запустить приложение:")
        print("   uv run taskmanager")
        print("   или")
        print("   uv run python app/scripts/run_app.py")
        
    except Exception as e:
        import traceback
        print(f"\n❌ Ошибка: {e}")
        print("\nДетали ошибки:")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
