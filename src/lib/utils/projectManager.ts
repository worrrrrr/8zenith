export type TaskStatus = 'todo' | 'in_progress' | 'done';
export type Priority = 'low' | 'medium' | 'high';

export interface Task {
  id: string;
  title: string;
  description: string;
  status: TaskStatus;
  priority: Priority;
  createdAt: number;
}

export interface Project {
  id: string;
  name: string;
  description: string;
  color: string;
  createdAt: number;
  tasks: Task[];
}

const STORAGE_KEY = 'zenith_projects';

const PROJECT_COLORS = [
  '#a855f7', // purple
  '#06b6d4', // cyan
  '#f59e0b', // gold
  '#ec4899', // pink
  '#10b981', // green
  '#3b82f6', // blue
];

export function getProjectColors(): string[] {
  return PROJECT_COLORS;
}

export function loadProjects(): Project[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

export function saveProjects(projects: Project[]): void {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(projects));
}

export function createProject(name: string, description: string, color: string): Project {
  return {
    id: crypto.randomUUID(),
    name,
    description,
    color,
    createdAt: Date.now(),
    tasks: [],
  };
}

export function createTask(title: string, description: string, priority: Priority): Task {
  return {
    id: crypto.randomUUID(),
    title,
    description,
    status: 'todo',
    priority,
    createdAt: Date.now(),
  };
}

export function updateTaskStatus(
  projects: Project[],
  projectId: string,
  taskId: string,
  status: TaskStatus
): Project[] {
  return projects.map((p) => {
    if (p.id !== projectId) return p;
    return {
      ...p,
      tasks: p.tasks.map((t) => (t.id === taskId ? { ...t, status } : t)),
    };
  });
}

export function deleteTask(projects: Project[], projectId: string, taskId: string): Project[] {
  return projects.map((p) => {
    if (p.id !== projectId) return p;
    return { ...p, tasks: p.tasks.filter((t) => t.id !== taskId) };
  });
}

export function updateTask(
  projects: Project[],
  projectId: string,
  taskId: string,
  updates: Partial<Pick<Task, 'title' | 'description' | 'priority'>>
): Project[] {
  return projects.map((p) => {
    if (p.id !== projectId) return p;
    return {
      ...p,
      tasks: p.tasks.map((t) => (t.id === taskId ? { ...t, ...updates } : t)),
    };
  });
}

export function getStatusLabel(status: TaskStatus): string {
  const labels: Record<TaskStatus, string> = {
    todo: '📋 ต้องทำ',
    in_progress: '🔄 กำลังทำ',
    done: '✅ เสร็จแล้ว',
  };
  return labels[status];
}

export function getPriorityLabel(priority: Priority): string {
  const labels: Record<Priority, string> = {
    low: '🟢 ต่ำ',
    medium: '🟡 กลาง',
    high: '🔴 สูง',
  };
  return labels[priority];
}

export function getColorClass(color: string): string {
  const map: Record<string, string> = {
    '#a855f7': 'bg-[#a855f7]',
    '#06b6d4': 'bg-[#06b6d4]',
    '#f59e0b': 'bg-[#f59e0b]',
    '#ec4899': 'bg-[#ec4899]',
    '#10b981': 'bg-[#10b981]',
    '#3b82f6': 'bg-[#3b82f6]',
  };
  return map[color] || 'bg-[#a855f7]';
}
