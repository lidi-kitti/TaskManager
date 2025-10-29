export enum TaskStatus {
  CREATED = "новая",
  IN_PROGRESS = "в работе",
  COMPLETED = "завершено",
}

export interface Task {
  id: string;
  title: string;
  description: string | null;
  status: TaskStatus;
  created_at: string;
  updated_at: string;
}

export interface TaskCreate {
  title: string;
  description?: string;
  status?: TaskStatus;
}

export interface TaskUpdate {
  title?: string;
  description?: string;
  status?: TaskStatus;
}

