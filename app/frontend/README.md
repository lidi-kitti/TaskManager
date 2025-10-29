# TaskManager Frontend

Frontend приложение для управления задачами, построенное на React + TypeScript + Vite.

## Установка

```bash
cd app/frontend
npm install
```

## Запуск в режиме разработки

```bash
npm run dev
```

Приложение будет доступно по адресу: http://localhost:3000

**Важно:** Убедитесь, что backend сервер запущен на http://localhost:8000

## Сборка для production

```bash
npm run build
```

Собранные файлы будут в папке `dist/`.

## Просмотр production сборки

```bash
npm run preview
```

## Структура проекта

```
src/
├── api/          # API клиент для взаимодействия с backend
├── components/   # React компоненты
├── types/        # TypeScript типы
├── App.tsx       # Главный компонент
└── main.tsx      # Точка входа
```

## Функциональность

- ✅ Создание задач
- ✅ Просмотр списка задач
- ✅ Фильтрация по статусу
- ✅ Изменение статуса задачи
- ✅ Удаление задач
- ✅ Современный и отзывчивый UI

