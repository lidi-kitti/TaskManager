#!/usr/bin/env python3
"""
Скрипт для запуска тестов TaskManager
"""

import subprocess
import sys
import os
import time
import requests
from pathlib import Path


def check_api_health():
    """Проверка доступности API"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False


def wait_for_api():
    """Ожидание готовности API"""
    print("Ожидание готовности API...")
    max_attempts = 30
    for attempt in range(max_attempts):
        if check_api_health():
            print("API готов!")
            return True
        
        time.sleep(1)
        print(f"Попытка {attempt + 1}/{max_attempts}...")
    
    print("API не готов после 30 попыток")
    return False


def start_api_if_needed():
    """Запуск API если он не работает"""
    if not check_api_health():
        print("API не запущен. Запускаем...")
        try:
            # Запускаем API в фоновом режиме
            script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "run_app.py")
            process = subprocess.Popen([
                sys.executable, script_path
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=os.path.dirname(script_path))
            
            # Ждем запуска API
            for i in range(30):  # Максимум 30 секунд
                time.sleep(1)
                if check_api_health():
                    print("API успешно запущен")
                    return process
                print(f"Ожидание запуска API... ({i+1}/30)")
            
            print("Не удалось запустить API за 30 секунд")
            process.terminate()
            return None
            
        except Exception as e:
            print(f"Ошибка запуска API: {e}")
            return None
    else:
        print("API уже запущен")
        return None


def run_regular_tests():
    """Запуск обычных тестов"""
    print("Запуск обычных тестов...")
    
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        test_file = os.path.join(script_dir, "test_api.py")
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            test_file, 
            "-v",
            "--tb=short"
        ], capture_output=True, text=True, cwd=script_dir)
        
        print("Результаты обычных тестов:")
        print(result.stdout)
        
        if result.stderr:
            print("Предупреждения:")
            print(result.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"Ошибка при запуске тестов: {e}")
        return False


def check_dependencies():
    """Проверка зависимостей"""
    print("Проверка зависимостей...")
    
    required_packages = [
        "fastapi", "uvicorn", "pydantic", "sqlalchemy", 
        "aiosqlite", "httpx", "requests", "pytest"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"{package}")
        except ImportError:
            print(f"{package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\nОтсутствуют пакеты: {', '.join(missing_packages)}")
        print("Установите их командой: py -m pip install -r requirements.txt")
        return False
    
    print("Все зависимости установлены")
    return True


def main():
    """Основная функция"""
    print("TaskManager - Запуск тестов")
    print("=" * 40)
    
    # Проверяем зависимости
    if not check_dependencies():
        print("Не удалось запустить тесты: отсутствуют зависимости")
        sys.exit(1)
    
    # Проверяем и запускаем API
    api_process = start_api_if_needed()
    if api_process is None and not check_api_health():
        print("Не удалось запустить API")
        sys.exit(1)
    
    try:
        # Запускаем обычные тесты
        regular_success = run_regular_tests()
        
        # Общий результат
        overall_success = regular_success
        
        if overall_success:
            print("\nВсе тесты прошли успешно!")
            sys.exit(0)
        else:
            print("\nНекоторые тесты завершились с ошибками")
            sys.exit(1)
            
    finally:
        # Останавливаем API если мы его запускали
        if api_process:
            print("\nОстановка API...")
            api_process.terminate()
            api_process.wait()


if __name__ == "__main__":
    main()
