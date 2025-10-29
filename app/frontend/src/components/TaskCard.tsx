import React from 'react';
import type { Task, TaskStatus, Priority } from '../types/task';
import { taskApi } from '../api/client';
import { Priority as PriorityEnum } from '../types/task';

interface TaskCardProps {
  task: Task;
  onUpdate: () => void;
}

const statusColors: Record<TaskStatus, string> = {
  'новая': 'bg-blue-100 text-blue-800',
  'в работе': 'bg-yellow-100 text-yellow-800',
  'завершено': 'bg-green-100 text-green-800',
};

const priorityColors: Record<Priority, string> = {
  'низкий': 'bg-green-100 text-green-800 border-green-300',
  'средний': 'bg-yellow-100 text-yellow-800 border-yellow-300',
  'высокий': 'bg-red-100 text-red-800 border-red-300',
};

const priorityIcons: Record<Priority, string> = {
  'низкий': '🟢',
  'средний': '🟡',
  'высокий': '🔴',
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

  const handlePriorityChange = async (newPriority: Priority) => {
    try {
      await taskApi.updateTask(task.id, { priority: newPriority });
      onUpdate();
    } catch (error) {
      console.error('Ошибка обновления приоритета:', error);
      alert('Не удалось обновить приоритет задачи');
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

  const formatDeadline = (deadlineString: string | null) => {
    if (!deadlineString) return null;
    const deadline = new Date(deadlineString);
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    deadline.setHours(0, 0, 0, 0);
    
    const diffTime = deadline.getTime() - today.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    const formattedDate = deadline.toLocaleDateString('ru-RU', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
    });
    
    if (diffDays < 0) {
      return { text: `Просрочено: ${formattedDate}`, className: 'text-red-600 font-semibold' };
    } else if (diffDays === 0) {
      return { text: `Сегодня: ${formattedDate}`, className: 'text-orange-600 font-semibold' };
    } else if (diffDays === 1) {
      return { text: `Завтра: ${formattedDate}`, className: 'text-yellow-600 font-semibold' };
    } else if (diffDays <= 7) {
      return { text: `Через ${diffDays} дн.: ${formattedDate}`, className: 'text-yellow-500' };
    } else {
      return { text: formattedDate, className: 'text-gray-600' };
    }
  };

  const deadlineInfo = formatDeadline(task.deadline);
  const isOverdue = task.deadline && new Date(task.deadline) < new Date() && task.status !== 'завершено';

  return (
    <div className={`bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow ${isOverdue ? 'border-l-4 border-red-500' : ''}`}>
      <div className="flex justify-between items-start mb-4">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <h3 className="text-xl font-semibold text-gray-800">{task.title}</h3>
            <span className="text-lg">{priorityIcons[task.priority]}</span>
          </div>
          {isOverdue && (
            <div className="text-xs text-red-600 font-semibold mb-2">⚠️ ПРОСРОЧЕНО</div>
          )}
        </div>
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

      <div className="mb-4">
        <label className="block text-xs font-medium text-gray-700 mb-2">Приоритет</label>
        <div className="flex gap-2">
          {([PriorityEnum.LOW, PriorityEnum.MEDIUM, PriorityEnum.HIGH] as Priority[]).map((priority) => (
            <button
              key={priority}
              onClick={() => handlePriorityChange(priority)}
              className={`px-3 py-1 rounded-full text-sm font-medium transition-colors border-2 ${
                task.priority === priority
                  ? priorityColors[priority]
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200 border-gray-300'
              }`}
            >
              {priorityIcons[priority]} {priority}
            </button>
          ))}
        </div>
      </div>

      <div className="mb-4">
        <label className="block text-xs font-medium text-gray-700 mb-2">Статус</label>
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
      </div>

      {deadlineInfo && (
        <div className="mb-4">
          <div className="text-xs font-medium text-gray-700 mb-1">Дедлайн</div>
          <div className={deadlineInfo.className}>{deadlineInfo.text}</div>
        </div>
      )}

      <div className="text-xs text-gray-500">
        <div>Создано: {formatDate(task.created_at)}</div>
        {task.updated_at !== task.created_at && (
          <div>Обновлено: {formatDate(task.updated_at)}</div>
        )}
      </div>
    </div>
  );
};

