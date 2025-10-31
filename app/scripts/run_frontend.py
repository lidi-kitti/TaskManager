#!/usr/bin/env python3
"""
Скрипт для запуска TaskManager Frontend
"""

import subprocess
import sys
import os
import shutil
from pathlib import Path

def find_npm() -> str:
    """Находит npm в системе"""
    # Пытаемся найти npm через shutil.which
    npm_path = shutil.which("npm")
    if npm_path:
        return npm_path
    
    # В Windows пробуем найти через стандартные пути
    if sys.platform == "win32":
        # Проверяем стандартные пути установки Node.js
        possible_paths = [
            r"C:\Program Files\nodejs\npm.cmd",
            r"C:\Program Files (x86)\nodejs\npm.cmd",
            os.path.expanduser(r"~\AppData\Roaming\npm\npm.cmd"),
        ]
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        # Пытаемся найти через where
        try:
            result = subprocess.run(
                ["where", "npm"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip().split('\n')[0]
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
    
    return "npm"  # Возвращаем просто 'npm' и надеемся, что оно в PATH

def main() -> None:
    # Устанавливаем UTF-8 для Windows
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    
    # Находим npm
    npm_cmd = find_npm()
    
    # Проверяем, что npm доступен
    try:
        result = subprocess.run(
            [npm_cmd, "--version"],
            capture_output=True,
            text=True,
            timeout=5,
            shell=(sys.platform == "win32")
        )
        if result.returncode != 0:
            raise FileNotFoundError
        print(f"✅ Найден npm: {result.stdout.strip()}")
    except (FileNotFoundError, subprocess.TimeoutExpired):
        print("❌ npm не найден. Убедитесь, что Node.js установлен.")
        print("   Скачать: https://nodejs.org/")
        print("\n💡 Подсказка: После установки Node.js:")
        print("   1. Перезапустите терминал/IDE")
        print("   2. Проверьте: node --version")
        print("   3. Проверьте: npm --version")
        sys.exit(1)
    
    # Определяем путь к фронтенду
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent.parent
    frontend_dir = project_root / "app" / "frontend"
    
    if not frontend_dir.exists():
        print(f"❌ Директория фронтенда не найдена: {frontend_dir}")
        sys.exit(1)
    
    print("🚀 Запуск TaskManager Frontend...")
    print(f"📁 Директория: {frontend_dir}")
    print("🌐 Фронтенд будет доступен на: http://localhost:5173")
    print("=" * 50)
    
    # Проверяем, установлены ли зависимости
    node_modules = frontend_dir / "node_modules"
    vite_bin = node_modules / ".bin" / "vite"
    vite_bin_cmd = node_modules / ".bin" / "vite.cmd"  # Для Windows
    
    # Проверяем наличие vite (либо директории node_modules, либо самого vite)
    needs_install = (
        not node_modules.exists() or 
        (not vite_bin.exists() and not vite_bin_cmd.exists())
    )
    
    if needs_install:
        print("📦 Установка зависимостей npm...")
        print("   Это может занять некоторое время...")
        result = subprocess.run(
            [npm_cmd, "install"],
            cwd=frontend_dir,
            check=False,
            shell=(sys.platform == "win32")
        )
        if result.returncode != 0:
            print("❌ Ошибка при установке зависимостей npm")
            print("   Попробуйте запустить вручную: npm install")
            sys.exit(1)
        print("✅ Зависимости установлены\n")
    
    # Запускаем dev сервер
    try:
        subprocess.run(
            [npm_cmd, "run", "dev"],
            cwd=frontend_dir,
            check=True,
            shell=(sys.platform == "win32")  # Используем shell в Windows
        )
    except KeyboardInterrupt:
        print("\n👋 Остановка фронтенда...")
    except FileNotFoundError:
        print("❌ npm не найден во время запуска.")
        print("   Убедитесь, что Node.js установлен и доступен в PATH.")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка при запуске: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

