import React, { useState, useEffect } from 'react';
import { taskApi } from '../api/client';
import type { TaskStatistics } from '../types/task';

export const Statistics: React.FC = () => {
  const [stats, setStats] = useState<TaskStatistics | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadStatistics();
  }, []);

  const loadStatistics = async () => {
    try {
      const data = await taskApi.getStatistics();
      setStats(data);
    } catch (error) {
      console.error('Ошибка загрузки статистики:', error);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <div className="text-gray-500">Загрузка статистики...</div>
      </div>
    );
  }

  if (!stats) {
    return null;
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-6">
      <h2 className="text-2xl font-bold mb-4 text-gray-800">Статистика</h2>
      
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-4">
        <div className="bg-blue-50 p-4 rounded-lg">
          <div className="text-sm text-gray-600 mb-1">Всего задач</div>
          <div className="text-2xl font-bold text-blue-600">{stats.total}</div>
        </div>
        
        <div className="bg-gray-50 p-4 rounded-lg">
          <div className="text-sm text-gray-600 mb-1">Новые</div>
          <div className="text-2xl font-bold text-gray-700">{stats.created}</div>
        </div>
        
        <div className="bg-yellow-50 p-4 rounded-lg">
          <div className="text-sm text-gray-600 mb-1">В работе</div>
          <div className="text-2xl font-bold text-yellow-600">{stats.in_progress}</div>
        </div>
        
        <div className="bg-green-50 p-4 rounded-lg">
          <div className="text-sm text-gray-600 mb-1">Завершено</div>
          <div className="text-2xl font-bold text-green-600">{stats.completed}</div>
        </div>
        
        <div className="bg-red-50 p-4 rounded-lg">
          <div className="text-sm text-gray-600 mb-1">Просрочено</div>
          <div className="text-2xl font-bold text-red-600">{stats.overdue}</div>
        </div>
      </div>

      <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-red-50 p-4 rounded-lg">
          <div className="text-sm text-gray-600 mb-1">🔴 Высокий приоритет</div>
          <div className="text-xl font-bold text-red-600">{stats.high_priority}</div>
        </div>
        
        <div className="bg-yellow-50 p-4 rounded-lg">
          <div className="text-sm text-gray-600 mb-1">🟡 Средний приоритет</div>
          <div className="text-xl font-bold text-yellow-600">{stats.medium_priority}</div>
        </div>
        
        <div className="bg-green-50 p-4 rounded-lg">
          <div className="text-sm text-gray-600 mb-1">🟢 Низкий приоритет</div>
          <div className="text-xl font-bold text-green-600">{stats.low_priority}</div>
        </div>
      </div>

      <div className="mt-6 bg-indigo-50 p-4 rounded-lg">
        <div className="text-sm text-gray-600 mb-1">✅ Завершено сегодня</div>
        <div className="text-2xl font-bold text-indigo-600">{stats.completed_today}</div>
      </div>
    </div>
  );
};
