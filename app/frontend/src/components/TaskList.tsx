import React, { useState, useEffect, useCallback } from 'react';
import type { Task, TaskStatus, SortBy, SortOrder } from '../types/task';
import { taskApi } from '../api/client';
import { TaskCard } from './TaskCard';
import { TaskForm } from './TaskForm';
import { FilterBar } from './FilterBar';
import { Statistics } from './Statistics';
import { TaskStatus as TaskStatusEnum } from '../types/task';

export const TaskList: React.FC = () => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [allTasks, setAllTasks] = useState<Task[]>([]);
  const [filter, setFilter] = useState<TaskStatus | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState<SortBy>(null);
  const [sortOrder, setSortOrder] = useState<SortOrder>('asc');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadTasks = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await taskApi.getTasks(
        filter || undefined,
        searchQuery || undefined,
        sortBy || undefined,
        sortBy ? sortOrder : undefined
      );
      setTasks(data);
      
      // Загружаем все задачи для счетчиков
      const allData = await taskApi.getTasks();
      setAllTasks(allData);
    } catch (err) {
      console.error('Ошибка загрузки задач:', err);
      setError('Не удалось загрузить задачи. Убедитесь, что backend сервер запущен на http://localhost:8000');
    } finally {
      setIsLoading(false);
    }
  }, [filter, searchQuery, sortBy, sortOrder]);

  useEffect(() => {
    const timeoutId = setTimeout(() => {
      loadTasks();
    }, searchQuery ? 300 : 0); // Debounce для поиска

    return () => clearTimeout(timeoutId);
  }, [loadTasks, searchQuery]);

  useEffect(() => {
    loadTasks();
  }, [filter, sortBy, sortOrder]);

  const handleSortChange = (newSortBy: SortBy, newSortOrder: SortOrder) => {
    setSortBy(newSortBy);
    setSortOrder(newSortOrder);
  };

  const taskCounts = {
    all: allTasks.length,
    [TaskStatusEnum.CREATED]: allTasks.filter(t => t.status === TaskStatusEnum.CREATED).length,
    [TaskStatusEnum.IN_PROGRESS]: allTasks.filter(t => t.status === TaskStatusEnum.IN_PROGRESS).length,
    [TaskStatusEnum.COMPLETED]: allTasks.filter(t => t.status === TaskStatusEnum.COMPLETED).length,
  };

  return (
    <div>
      <Statistics />

      <TaskForm onSuccess={loadTasks} />

      <FilterBar
        currentFilter={filter}
        onFilterChange={setFilter}
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        sortBy={sortBy}
        sortOrder={sortOrder}
        onSortChange={handleSortChange}
        taskCounts={taskCounts}
      />

      {isLoading && (
        <div className="text-center py-8">
          <div className="text-gray-500">Загрузка задач...</div>
        </div>
      )}

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-lg mb-6">
          {error}
        </div>
      )}

      {!isLoading && !error && tasks.length === 0 && (
        <div className="bg-white rounded-lg shadow-md p-8 text-center">
          <p className="text-gray-500 text-lg">
            {searchQuery || filter
              ? 'Нет задач, соответствующих критериям поиска'
              : 'Нет задач. Создайте первую задачу!'}
          </p>
        </div>
      )}

      {!isLoading && !error && tasks.length > 0 && (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {tasks.map((task) => (
            <TaskCard key={task.id} task={task} onUpdate={loadTasks} />
          ))}
        </div>
      )}
    </div>
  );
};

