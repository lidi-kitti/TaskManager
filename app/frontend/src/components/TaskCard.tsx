import React from 'react';
import type { Task, TaskStatus } from '../types/task';
import { taskApi } from '../api/client';

interface TaskCardProps {
  task: Task;
  onUpdate: () => void;
}

const statusColors: Record<TaskStatus, string> = {
  'новая': 'bg-blue-100 text-blue-800',
  'в работе': 'bg-yellow-100 text-yellow-800',
  'завершено': 'bg-green-100 text-green-800',
};

export const TaskCard: React.FC<TaskCardProps> = ({ task, onUpdate }) => {
  const handleStatusChange = async (newStatus: TaskStatus) => {
    try {
      await taskApi.updateTask(task.id, { status: newStatus });
      onUpdate();
    } catch (error) {
      console.error('Ошибка обновления статуса:', error);
      alert('Не удалось обновить статус задачи');
    }
  };

  const handleDelete = async () => {
    if (window.confirm('Вы уверены, что хотите удалить эту задачу?')) {
      try {
        await taskApi.deleteTask(task.id);
        onUpdate();
      } catch (error) {
        console.error('Ошибка удаления задачи:', error);
        alert('Не удалось удалить задачу');
      }
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString('ru-RU', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
      <div className="flex justify-between items-start mb-4">
        <h3 className="text-xl font-semibold text-gray-800 flex-1">{task.title}</h3>
        <button
          onClick={handleDelete}
          className="text-red-500 hover:text-red-700 ml-4 text-xl"
          title="Удалить задачу"
        >
          ×
        </button>
      </div>

      {task.description && (
        <p className="text-gray-600 mb-4">{task.description}</p>
      )}

      <div className="flex items-center justify-between">
        <div className="flex gap-2">
          {(['новая', 'в работе', 'завершено'] as TaskStatus[]).map((status) => (
            <button
              key={status}
              onClick={() => handleStatusChange(status)}
              className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                task.status === status
                  ? statusColors[status]
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {status}
            </button>
          ))}
        </div>

        <div className="text-xs text-gray-500">
          <div>Создано: {formatDate(task.created_at)}</div>
          {task.updated_at !== task.created_at && (
            <div>Обновлено: {formatDate(task.updated_at)}</div>
          )}
        </div>
      </div>
    </div>
  );
};

