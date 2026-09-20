const API_URL = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";

export interface Message {
  id?: string;
  role: "user" | "assistant";
  content: string;
  created_at?: string;
}

export interface Conversation {
  id: string;
  title: string;
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

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: { "Content-Type": "application/json", ...options?.headers },
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
  chat: (message: string, conversationId?: string) =>
    request<{ conversation_id: string; message: string }>("/api/v1/chat", {
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
};
