import React from 'react';
import type { TaskStatus } from '../types/task';
import { TaskStatus as TaskStatusEnum } from '../types/task';

interface FilterBarProps {
  currentFilter: TaskStatus | null;
  onFilterChange: (filter: TaskStatus | null) => void;
  taskCounts: {
    all: number;
    [TaskStatusEnum.CREATED]: number;
    [TaskStatusEnum.IN_PROGRESS]: number;
    [TaskStatusEnum.COMPLETED]: number;
  };
}

export const FilterBar: React.FC<FilterBarProps> = ({ currentFilter, onFilterChange, taskCounts }) => {
  return (
    <div className="bg-white rounded-lg shadow-md p-4 mb-6">
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
    </div>
  );
};

