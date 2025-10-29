#!/usr/bin/env python3
"""
Простой скрипт для тестирования TaskManager API
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_api():
    """Тестирование основных функций API"""
    print("Тестирование TaskManager API")
    print("=" * 40)
    
    # Проверка доступности API
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("API доступен")
        else:
            print(f"API недоступен: {response.status_code}")
            return
    except requests.exceptions.RequestException:
        print("Не удается подключиться к API")
        return
    
    # Создание задачи
    print("\nСоздание задачи...")
    task_data = {
        "title": "Тестовая задача",
        "description": "Описание тестовой задачи"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/tasks/", json=task_data)
    if response.status_code == 201:
        task = response.json()
        task_id = task["id"]
        print(f"Задача создана с ID: {task_id}")
        print(f"Название: {task['title']}")
        print(f"Статус: {task['status']}")
    else:
        print(f"Ошибка создания задачи: {response.status_code}")
        return
    
    # Получение задачи
    print("\nПолучение задачи...")
    response = requests.get(f"{BASE_URL}/api/v1/tasks/{task_id}")
    if response.status_code == 200:
        retrieved_task = response.json()
        print(f"Задача получена: {retrieved_task['title']}")
    else:
        print(f"Ошибка получения задачи: {response.status_code}")
    
    # Получение списка задач
    print("\nПолучение списка задач...")
    response = requests.get(f"{BASE_URL}/api/v1/tasks/")
    if response.status_code == 200:
        tasks = response.json()
        print(f"Получено задач: {len(tasks)}")
    else:
        print(f"Ошибка получения списка задач: {response.status_code}")
    
    # Обновление задачи
    print("\nОбновление задачи...")
    update_data = {
        "status": "в работе",
        "title": "Обновленная тестовая задача"
    }
    
    response = requests.put(f"{BASE_URL}/api/v1/tasks/{task_id}", json=update_data)
    if response.status_code == 200:
        updated_task = response.json()
        print(f"Задача обновлена")
        print(f"Новое название: {updated_task['title']}")
        print(f"Новый статус: {updated_task['status']}")
    else:
        print(f"Ошибка обновления задачи: {response.status_code}")
    
    # Фильтрация по статусу
    print("\nФильтрация задач по статусу...")
    response = requests.get(f"{BASE_URL}/api/v1/tasks/?status=в%20работе")
    if response.status_code == 200:
        filtered_tasks = response.json()
        print(f"Задач в работе: {len(filtered_tasks)}")
    else:
        print(f"Ошибка фильтрации: {response.status_code}")
    
    # Удаление задачи
    print("\nУдаление задачи...")
    response = requests.delete(f"{BASE_URL}/api/v1/tasks/{task_id}")
    if response.status_code == 204:
        print("Задача удалена")
    else:
        print(f"Ошибка удаления задачи: {response.status_code}")
    
    # Проверка удаления
    print("\nПроверка удаления...")
    response = requests.get(f"{BASE_URL}/api/v1/tasks/{task_id}")
    if response.status_code == 404:
        print("Задача успешно удалена (404)")
    else:
        print(f"Задача все еще доступна: {response.status_code}")
    
    print("\nТестирование завершено!")

if __name__ == "__main__":
    test_api()
