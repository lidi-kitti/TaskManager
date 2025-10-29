import axios from 'axios';
import type { Task, TaskCreate, TaskUpdate, TaskStatus } from '../types/task';

const API_BASE_URL = 'http://localhost:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const taskApi = {
  // Получить все задачи
  getTasks: async (status?: TaskStatus): Promise<Task[]> => {
    const response = await apiClient.get<Task[]>('/tasks/', {
      params: status ? { status } : undefined,
    });
    return response.data;
  },

  // Получить задачу по ID
  getTask: async (id: string): Promise<Task> => {
    const response = await apiClient.get<Task>(`/tasks/${id}`);
    return response.data;
  },

  // Создать задачу
  createTask: async (task: TaskCreate): Promise<Task> => {
    const response = await apiClient.post<Task>('/tasks/', task);
    return response.data;
  },

  // Обновить задачу
  updateTask: async (id: string, task: TaskUpdate): Promise<Task> => {
    const response = await apiClient.put<Task>(`/tasks/${id}`, task);
    return response.data;
  },

  // Удалить задачу
  deleteTask: async (id: string): Promise<void> => {
    await apiClient.delete(`/tasks/${id}`);
  },
};

