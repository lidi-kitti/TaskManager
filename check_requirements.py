#!/usr/bin/env python3
"""
Скрипт для проверки установки зависимостей TaskManager
"""

import importlib
import sys
import subprocess

def check_python_version():
    """Проверка версии Python"""
    version = sys.version_info
    print(f"Python версия: {version.major}.{version.minor}.{version.micro}")
    
    if version.major >= 3 and version.minor >= 8:
        print("Версия Python подходит")
        return True
    else:
        print("Требуется Python 3.8+")
        return False

def check_package(package_name, import_name=None):
    """Проверка установки пакета"""
    if import_name is None:
        import_name = package_name
    
    try:
        importlib.import_module(import_name)
        print(f"{package_name} установлен")
        return True
    except ImportError:
        print(f"{package_name} не установлен")
        return False

def check_gauge():
    """Проверка установки Gauge"""
    try:
        result = subprocess.run(["gauge", "--version"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("Gauge установлен")
            return True
        else:
            print("Gauge не установлен")
            return False
    except FileNotFoundError:
        print("Gauge не установлен")
        return False

def check_docker():
    """Проверка установки Docker"""
    try:
        result = subprocess.run(["docker", "--version"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("Docker установлен")
            return True
        else:
            print("Docker не установлен")
            return False
    except FileNotFoundError:
        print("Docker не установлен")
        return False

def main():
    """Основная функция проверки"""
    print("Проверка зависимостей TaskManager")
    print("=" * 40)
    
    all_good = True
    
    # Проверка Python
    if not check_python_version():
        all_good = False
    
    print("\nПроверка Python пакетов:")
    
    # Проверка основных пакетов
    packages = [
        ("fastapi", "fastapi"),
        ("uvicorn", "uvicorn"),
        ("pydantic", "pydantic"),
        ("httpx", "httpx"),
        ("requests", "requests"),
        ("sqlalchemy", "sqlalchemy"),
        ("aiosqlite", "aiosqlite")
    ]
    
    for package, import_name in packages:
        if not check_package(package, import_name):
            all_good = False
    
    print("\nПроверка инструментов:")
    
    # Проверка Gauge
    gauge_installed = check_gauge()
    if not gauge_installed:
        all_good = False
    
    # Проверка Docker
    docker_installed = check_docker()
    if not docker_installed:
        print("Docker не установлен (опционально)")
    
    print("\n" + "=" * 40)
    
    if all_good:
        print("Все основные зависимости установлены!")
        print("\nДля запуска приложения выполните:")
        print("   python run_app.py")
        print("\nДля тестирования выполните:")
        print("   python test_api.py")
        if gauge_installed:
            print("   gauge run specs/")
    else:
        print("Некоторые зависимости не установлены")
        print("\nУстановите недостающие зависимости:")
        print("   pip install -r requirements.txt")
        if not gauge_installed:
            print("\nУстановите Gauge:")
            print("   Windows: choco install gauge")
            print("   macOS: brew install gauge")
            print("   Linux: curl -SsL https://downloads.gauge.org/stable | sh")

if __name__ == "__main__":
    main()
