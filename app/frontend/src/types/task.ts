export enum TaskStatus {
  CREATED = "новая",
  IN_PROGRESS = "в работе",
  COMPLETED = "завершено",
}

export enum Priority {
  LOW = "низкий",
  MEDIUM = "средний",
  HIGH = "высокий",
}

export interface Task {
  id: string;
  title: string;
  description: string | null;
  status: TaskStatus;
  priority: Priority;
  deadline: string | null;
  created_at: string;
  updated_at: string;
}

export interface TaskCreate {
  title: string;
  description?: string;
  status?: TaskStatus;
  priority?: Priority;
  deadline?: string;
}

export interface TaskUpdate {
  title?: string;
  description?: string;
  status?: TaskStatus;
  priority?: Priority;
  deadline?: string;
}

export interface TaskStatistics {
  total: number;
  created: number;
  in_progress: number;
  completed: number;
  overdue: number;
  high_priority: number;
  medium_priority: number;
  low_priority: number;
  completed_today: number;
}

export type SortBy = "created_at" | "updated_at" | "status" | "priority" | "deadline" | null;
export type SortOrder = "asc" | "desc";
