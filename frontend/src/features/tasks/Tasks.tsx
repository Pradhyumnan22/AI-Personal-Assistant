import { FormEvent, useEffect, useState } from "react";
import { api, Task } from "../../api/client";

interface TasksProps {
  onOpenChat: () => void;
  onOpenNotes: () => void;
}

export function Tasks({ onOpenChat, onOpenNotes }: TasksProps) {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [title, setTitle] = useState("");
  const [dueAt, setDueAt] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function refresh() {
    setTasks(await api.tasks());
  }

  useEffect(() => {
    refresh().catch((reason) =>
      setError(reason instanceof Error ? reason.message : "Unable to load tasks"),
    );
  }, []);

  async function create(event: FormEvent) {
    event.preventDefault();
    if (!title.trim()) return;
    setBusy(true);
    setError("");
    try {
      await api.createTask(
        title.trim(),
        dueAt ? new Date(dueAt).toISOString() : undefined,
      );
      setTitle("");
      setDueAt("");
      await refresh();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to create task");
    } finally {
      setBusy(false);
    }
  }

  async function toggle(task: Task) {
    setBusy(true);
    try {
      if (task.completed) {
        await api.updateTask({ ...task, completed: false });
      } else {
        await api.completeTask(task.id);
      }
      await refresh();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to update task");
    } finally {
      setBusy(false);
    }
  }

  async function remove(task: Task) {
    setBusy(true);
    try {
      await api.deleteTask(task.id);
      await refresh();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to delete task");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="shell">
      <aside>
        <div className="brand">Personal Assistant</div>
        <div className="section-switcher three">
          <button onClick={onOpenChat}>Chat</button>
          <button onClick={onOpenNotes}>Notes</button>
          <button className="active">Tasks</button>
        </div>
      </aside>
      <section className="tasks-page">
        <header>
          <h1>Tasks and reminders</h1>
          <p>Manage tasks here or ask the assistant in chat.</p>
        </header>
        <form className="task-form" onSubmit={create}>
          <input
            maxLength={300}
            placeholder="What needs to be done?"
            value={title}
            onChange={(event) => setTitle(event.target.value)}
          />
          <input
            aria-label="Due date"
            type="datetime-local"
            value={dueAt}
            onChange={(event) => setDueAt(event.target.value)}
          />
          <button disabled={busy || !title.trim()} type="submit">Add task</button>
        </form>
        {error && <div className="error">{error}</div>}
        <div className="task-list">
          {tasks.length === 0 && <div className="empty">No tasks yet.</div>}
          {tasks.map((task) => (
            <div className={`task-row ${task.completed ? "completed" : ""}`} key={task.id}>
              <button
                aria-label={task.completed ? "Mark incomplete" : "Mark complete"}
                className="task-check"
                disabled={busy}
                onClick={() => toggle(task)}
              >
                {task.completed ? "✓" : ""}
              </button>
              <div>
                <strong>{task.title}</strong>
                {task.due_at && (
                  <span>Due {new Date(task.due_at).toLocaleString()}</span>
                )}
              </div>
              <button className="task-delete" disabled={busy} onClick={() => remove(task)}>
                Delete
              </button>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}
