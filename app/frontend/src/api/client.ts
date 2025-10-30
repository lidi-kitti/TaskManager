import axios from 'axios';
import type { Task, TaskCreate, TaskUpdate, TaskStatus, TaskStatistics, SortBy, SortOrder } from '../types/task';

const API_BASE_URL = 'http://localhost:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Добавляем токен, если он сохранён
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('tm_access_token');
  if (token) {
    config.headers = config.headers || {};
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const taskApi = {
  // Получить все задачи
  getTasks: async (
    status?: TaskStatus,
    search?: string,
    sortBy?: SortBy,
    sortOrder?: SortOrder
  ): Promise<Task[]> => {
    const response = await apiClient.get<Task[]>('/tasks/', {
      params: {
        ...(status && { status }),
        ...(search && { search }),
        ...(sortBy && { sort_by: sortBy }),
        ...(sortOrder && { sort_order: sortOrder }),
      },
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

  // Получить статистику
  getStatistics: async (): Promise<TaskStatistics> => {
    const response = await apiClient.get<TaskStatistics>('/tasks/statistics/summary');
    return response.data;
  },
};

export const authApi = {
  login: async (username: string, password: string): Promise<string> => {
    const params = new URLSearchParams();
    params.append('username', username);
    params.append('password', password);
    const response = await axios.post<{ access_token: string }>(`${API_BASE_URL}/auth/login`, params, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    const token = response.data.access_token;
    localStorage.setItem('tm_access_token', token);
    return token;
  },
  yandexConfig: async (): Promise<{ client_id: string; redirect_uri: string; authorize_url: string }> => {
    const resp = await axios.get(`${API_BASE_URL}/auth/yandex/config`);
    return resp.data;
  },
  yandexExchangeCode: async (code: string): Promise<string> => {
    const resp = await axios.post<{ access_token: string }>(`${API_BASE_URL}/auth/yandex/callback`, null, { params: { code } });
    const token = resp.data.access_token;
    localStorage.setItem('tm_access_token', token);
    return token;
  },
  register: async (username: string, password: string): Promise<void> => {
    await axios.post(`${API_BASE_URL}/auth/register`, { username, password });
  },
  logout: (): void => {
    localStorage.removeItem('tm_access_token');
  },
};

