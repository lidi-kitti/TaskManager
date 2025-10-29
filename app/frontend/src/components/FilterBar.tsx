import React from 'react';
import type { TaskStatus, SortBy, SortOrder } from '../types/task';
import { TaskStatus as TaskStatusEnum } from '../types/task';

interface FilterBarProps {
  currentFilter: TaskStatus | null;
  onFilterChange: (filter: TaskStatus | null) => void;
  searchQuery: string;
  onSearchChange: (query: string) => void;
  sortBy: SortBy;
  sortOrder: SortOrder;
  onSortChange: (sortBy: SortBy, sortOrder: SortOrder) => void;
  taskCounts: {
    all: number;
    [TaskStatusEnum.CREATED]: number;
    [TaskStatusEnum.IN_PROGRESS]: number;
    [TaskStatusEnum.COMPLETED]: number;
  };
}

export const FilterBar: React.FC<FilterBarProps> = ({
  currentFilter,
  onFilterChange,
  searchQuery,
  onSearchChange,
  sortBy,
  sortOrder,
  onSortChange,
  taskCounts,
}) => {
  return (
    <div className="bg-white rounded-lg shadow-md p-4 mb-6 space-y-4">
      {/* Поиск */}
      <div>
        <input
          type="text"
          placeholder="🔍 Поиск по названию или описанию..."
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>

      {/* Фильтры по статусу */}
      <div className="flex flex-wrap gap-2">
        <button
          onClick={() => onFilterChange(null)}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            currentFilter === null
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          Все ({taskCounts.all})
        </button>
        
        {Object.entries({
          [TaskStatusEnum.CREATED]: 'Новая',
          [TaskStatusEnum.IN_PROGRESS]: 'В работе',
          [TaskStatusEnum.COMPLETED]: 'Завершено',
        }).map(([status, label]) => (
          <button
            key={status}
            onClick={() => onFilterChange(status as TaskStatus)}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              currentFilter === status
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            {label} ({taskCounts[status as TaskStatus] || 0})
          </button>
        ))}
      </div>

      {/* Сортировка */}
      <div className="flex flex-wrap gap-2 items-center">
        <span className="text-sm font-medium text-gray-700">Сортировка:</span>
        <select
          value={sortBy || ''}
          onChange={(e) => onSortChange(e.target.value as SortBy || null, sortOrder)}
          className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
        >
          <option value="">По умолчанию</option>
          <option value="created_at">По дате создания</option>
          <option value="updated_at">По дате обновления</option>
          <option value="status">По статусу</option>
          <option value="priority">По приоритету</option>
          <option value="deadline">По дедлайну</option>
        </select>
        {sortBy && (
          <button
            onClick={() => onSortChange(sortBy, sortOrder === 'asc' ? 'desc' : 'asc')}
            className="px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-100 text-sm"
            title={sortOrder === 'asc' ? 'По возрастанию' : 'По убыванию'}
          >
            {sortOrder === 'asc' ? '↑' : '↓'}
          </button>
        )}
      </div>
    </div>
  );
};

