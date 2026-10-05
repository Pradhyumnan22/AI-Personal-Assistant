const API_URL = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";

export interface Message {
  id?: string;
  role: "user" | "assistant";
  content: string;
  created_at?: string;
  sources?: Source[];
}

export interface Source {
  note_id: string;
  title: string;
  excerpt: string;
}

export interface Conversation {
  id: string;
  title: string;
  pinned: boolean;
  created_at: string;
  updated_at: string;
}

export interface Note {
  id: string;
  title: string;
  content: string;
  created_at: string;
  updated_at: string;
}

export interface Task {
  id: string;
  title: string;
  due_at: string | null;
  completed: boolean;
  created_at: string;
  updated_at: string;
}

export interface CalendarStatus {
  configured: boolean;
  connected: boolean;
}

export interface CalendarEvent {
  id: string;
  title: string;
  start: string;
  end: string;
  html_link?: string;
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const isFormData = options?.body instanceof FormData;
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      ...(isFormData ? {} : { "Content-Type": "application/json" }),
      ...options?.headers,
    },
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail ?? `Request failed (${response.status})`);
  }
  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

export const api = {
  conversations: () => request<Conversation[]>("/api/v1/conversations"),
  messages: (id: string) =>
    request<Message[]>(`/api/v1/conversations/${id}/messages`),
  pinConversation: (id: string, pinned: boolean) =>
    request<Conversation>(`/api/v1/conversations/${id}/pin`, {
      method: "PATCH",
      body: JSON.stringify({ pinned }),
    }),
  deleteConversation: (id: string) =>
    request<void>(`/api/v1/conversations/${id}`, { method: "DELETE" }),
  chat: (message: string, conversationId?: string) =>
    request<{ conversation_id: string; message: string; sources: Source[] }>("/api/v1/chat", {
      method: "POST",
      body: JSON.stringify({ message, conversation_id: conversationId }),
    }),
  notes: () => request<Note[]>("/api/v1/notes"),
  createNote: (title: string, content: string) =>
    request<Note>("/api/v1/notes", {
      method: "POST",
      body: JSON.stringify({ title, content }),
    }),
  updateNote: (id: string, title: string, content: string) =>
    request<Note>(`/api/v1/notes/${id}`, {
      method: "PUT",
      body: JSON.stringify({ title, content }),
    }),
  deleteNote: (id: string) =>
    request<void>(`/api/v1/notes/${id}`, { method: "DELETE" }),
  indexNote: (id: string) =>
    request<void>(`/api/v1/notes/${id}/index`, { method: "POST" }),
  uploadDocument: (file: File) => {
    const body = new FormData();
    body.append("file", file);
    return request<Note>("/api/v1/documents", { method: "POST", body });
  },
  tasks: () => request<Task[]>("/api/v1/tasks"),
  createTask: (title: string, dueAt?: string) =>
    request<Task>("/api/v1/tasks", {
      method: "POST",
      body: JSON.stringify({ title, due_at: dueAt || null }),
    }),
  updateTask: (task: Task) =>
    request<Task>(`/api/v1/tasks/${task.id}`, {
      method: "PUT",
      body: JSON.stringify({
        title: task.title,
        due_at: task.due_at,
        completed: task.completed,
      }),
    }),
  completeTask: (id: string) =>
    request<Task>(`/api/v1/tasks/${id}/complete`, { method: "POST" }),
  deleteTask: (id: string) =>
    request<void>(`/api/v1/tasks/${id}`, { method: "DELETE" }),
  calendarStatus: () =>
    request<CalendarStatus>("/api/v1/calendar/status"),
  calendarConnectUrl: () =>
    request<{ authorization_url: string }>("/api/v1/calendar/connect"),
  disconnectCalendar: () =>
    request<void>("/api/v1/calendar/connection", { method: "DELETE" }),
  calendarEvents: () =>
    request<CalendarEvent[]>("/api/v1/calendar/events"),
  createCalendarEvent: (
    title: string,
    start: string,
    end?: string,
    description?: string,
  ) =>
    request<CalendarEvent>("/api/v1/calendar/events", {
      method: "POST",
      body: JSON.stringify({
        title,
        start,
        end: end || null,
        description: description || null,
      }),
    }),
};
