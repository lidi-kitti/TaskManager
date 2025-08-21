# TaskManager API

Веб-приложение для управления задачами с использованием FastAPI и тестированием через pytest.

## Функциональные требования

- **CRUD операции для управления задачами:**
  - `create` - создание новой задачи
  - `get` - получение задачи по ID
  - `get_list` - получение списка задач с фильтрацией по статусу
  - `update` - обновление задачи
  - `delete` - удаление задачи

- **Модель задачи включает:**
  - UUID (уникальный идентификатор)
  - Название (обязательное поле)
  - Описание (опциональное поле)
  - Статус (создано, в работе, завершено)
  - Даты создания и обновления

## Технические требования

- **Backend:** FastAPI
- **База данных:** SQLite с SQLAlchemy ORM
- **Тестирование:** pytest
- **Дополнительно:** Swagger документация, Docker, README.md

## Структура проекта

```
TaskManager/
├── app/ # Основной код приложения
│ ├── init.py
│ ├── main.py # Точка входа FastAPI
│ ├── models.py # Pydantic модели
│ ├── database.py # SQLAlchemy модели и конфигурация БД
│ ├── routers.py # API роуты
│ └── services.py # Бизнес-логика
├── data/ # Директория для SQLite базы данных
├── specs/ # Спецификации (остатки от Gauge)
├── step_impl/ # Реализация шагов (остатки от Gauge)
├── requirements.txt # Python зависимости
├── Dockerfile # Docker образ
├── docker-compose.yml # Docker Compose
├── manifest.json # Манифест приложения
├── run_app.py # Скрипт запуска приложения
├── run_tests.py # Скрипт запуска тестов
├── test_api.py # Тесты API
├── create_test_data.py # Скрипт создания тестовых данных
├── check_requirements.py # Скрипт проверки зависимостей
├── taskmanager.db # SQLite база данных
└── README.md # Документация
```

## Быстрый старт

```bash
# 1. Клонирование и переход в директорию
git clone <repository-url>
cd TaskManager

# 2. Установка зависимостей
pip install -r requirements.txt

# 3. Запуск приложения
python run_app.py

# 4. В новом терминале - запуск тестов
python run_tests.py
```

## Установка и запуск

### Предварительные требования

- Python 3.8+
- Docker (опционально)

### Локальная установка

1. **Клонирование репозитория:**
   ```bash
   git clone <repository-url>
   cd TaskManager
   ```

2. **Создание виртуального окружения:**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Установка зависимостей:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Запуск приложения:**
   ```bash
   # Вариант 1: Через uvicorn
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   
   # Вариант 2: Через скрипт
   python run_app.py
   ```

### Запуск через Docker

1. **Сборка и запуск:**
   ```bash
   docker-compose up --build
   ```

2. **Или только сборка:**
   ```bash
   docker build -t taskmanager .
   docker run -p 8000:8000 taskmanager
   ```

## API Endpoints

### Основные эндпоинты

- `GET /` - Информация о приложении
- `GET /health` - Проверка состояния
- `GET /docs` - Swagger документация
- `GET /redoc` - ReDoc документация

### API задач (`/api/v1/tasks`)

- `POST /` - Создание задачи
- `GET /` - Получение списка задач
- `GET /{task_id}` - Получение задачи по ID
- `PUT /{task_id}` - Обновление задачи
- `DELETE /{task_id}` - Удаление задачи

### Примеры запросов

#### Создание задачи
```bash
curl -X POST "http://localhost:8000/api/v1/tasks/" \
     -H "Content-Type: application/json" \
     -d '{
       "title": "Новая задача",
       "description": "Описание задачи"
     }'
```

#### Получение списка задач
```bash
curl "http://localhost:8000/api/v1/tasks/"
```

#### Фильтрация по статусу
```bash
curl "http://localhost:8000/api/v1/tasks/?status=в%20работе"
```

#### Обновление задачи
```bash
curl -X PUT "http://localhost:8000/api/v1/tasks/{task_id}" \
     -H "Content-Type: application/json" \
     -d '{
       "status": "завершено"
     }'
```

## Тестирование

### Установка зависимостей для тестирования

```bash
# Установка всех зависимостей
pip install -r requirements.txt

# Или установка только тестовых пакетов
pip install pytest httpx
```

### Запуск тестов

**Автоматический запуск всех тестов:**
   ```bash
   python run_tests.py
   ```

**Запуск только обычных тестов:**
   ```bash
   python -m pytest test_api.py -v
   ```

### Структура тестов

- **API тесты** (`test_api.py`) - pytest тесты для API эндпоинтов
- **Скрипт запуска** (`run_tests.py`) - автоматический запуск API и тестов

## Разработка

### Добавление новых эндпоинтов

1. Создайте модель в `app/models.py`
2. Добавьте бизнес-логику в `app/services.py`
3. Создайте роут в `app/routers.py`
4. Добавьте тесты в `test_api.py`

### Структура кода

- **Модели** используют Pydantic для валидации данных
- **Сервисы** содержат бизнес-логику
- **Роутеры** обрабатывают HTTP запросы
- **Тесты** написаны с использованием pytest и httpx

## Мониторинг и логирование

- Приложение доступно по адресу: http://localhost:8000
- Swagger документация: http://localhost:8000/docs
- ReDoc документация: http://localhost:8000/redoc
- Проверка состояния: http://localhost:8000/health

## Решение проблем

### Проблемы с зависимостями

Если у вас возникают проблемы с установкой пакетов:

1. **Обновите pip:**
   ```bash
   python -m pip install --upgrade pip
   ```

2. **Установите зависимости по одной:**
   ```bash
   pip install fastapi uvicorn pydantic sqlalchemy aiosqlite httpx requests pytest
   ```