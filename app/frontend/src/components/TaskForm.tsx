import React, { useState } from 'react';
import type { TaskCreate, TaskStatus, Priority } from '../types/task';
import { taskApi } from '../api/client';
import { TaskStatus as TaskStatusEnum, Priority as PriorityEnum } from '../types/task';


interface TaskFormProps {
  onSuccess: () => void;
}

export const TaskForm: React.FC<TaskFormProps> = ({ onSuccess }) => {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [status, setStatus] = useState<TaskStatus>(TaskStatusEnum.CREATED);
  const [priority, setPriority] = useState<Priority>(PriorityEnum.MEDIUM);
  const [deadline, setDeadline] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);


  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!title.trim()) {
      alert('Пожалуйста, введите название задачи');
      return;
    }

    setIsSubmitting(true);
    try {
      const taskData: TaskCreate = {
        title: title.trim(),
        description: description.trim() || undefined,
        status,
        priority,
        deadline: deadline || undefined,
      };
      
      await taskApi.createTask(taskData);
      setTitle('');
      setDescription('');
      setStatus(TaskStatusEnum.CREATED);
      setPriority(PriorityEnum.MEDIUM);
      setDeadline('');
      onSuccess();
    } catch (error) {
      console.error('Ошибка создания задачи:', error);
      alert('Не удалось создать задачу');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow-md p-6 mb-6">
      <h2 className="text-2xl font-bold mb-4 text-gray-800">Новая задача</h2>
      
      <div className="mb-4">
        <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-2">
          Название <span className="text-red-500">*</span>
        </label>
        <input
          type="text"
          id="title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="Введите название задачи"
          maxLength={200}
          required
        />
      </div>

      <div className="mb-4">
        <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-2">
          Описание
        </label>
        <textarea
          id="description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="Введите описание задачи (необязательно)"
          rows={4}
          maxLength={1000}
        />
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
        <div>
          <label htmlFor="status" className="block text-sm font-medium text-gray-700 mb-2">
            Статус
          </label>
          <select
            id="status"
            value={status}
            onChange={(e) => setStatus(e.target.value as TaskStatus)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value={TaskStatusEnum.CREATED}>Новая</option>
            <option value={TaskStatusEnum.IN_PROGRESS}>В работе</option>
            <option value={TaskStatusEnum.COMPLETED}>Завершено</option>
          </select>
        </div>
        <div>
          <label htmlFor="priority" className="block text-sm font-medium text-gray-700 mb-2">
            Приоритет
          </label>
          <select
            id="priority"
            value={priority}
            onChange={(e) => setPriority(e.target.value as Priority)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value={PriorityEnum.LOW}>🟢 Низкий</option>
            <option value={PriorityEnum.MEDIUM}>🟡 Средний</option>
            <option value={PriorityEnum.HIGH}>🔴 Высокий</option>
          </select>
        </div>

        <div>
          <label htmlFor="deadline" className="block text-sm font-medium text-gray-700 mb-2">
            Дедлайн
          </label>
          <input
            type="date"
            id="deadline"
            value={deadline}
            onChange={(e) => setDeadline(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
      </div>

      <button
        type="submit"
        disabled={isSubmitting}
        className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg font-medium hover:bg-blue-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
      >
        {isSubmitting ? 'Создание...' : 'Создать задачу'}
      </button>
    </form>
  );
};

