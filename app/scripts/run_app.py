#!/usr/bin/env python3
"""
Скрипт для запуска TaskManager API
"""

import uvicorn
import sys
import os

# Добавляем корневую директорию проекта в путь для импорта
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

if __name__ == "__main__":
    print("Запуск TaskManager API...")
    print("Документация: http://localhost:8000/docs")
    print("ReDoc: http://localhost:8000/redoc")
    print("Проверка состояния: http://localhost:8000/health")
    print("=" * 50)
    
    uvicorn.run(
        "app.backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
