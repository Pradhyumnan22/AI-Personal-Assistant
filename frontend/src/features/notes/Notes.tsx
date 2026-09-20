import { FormEvent, useEffect, useState } from "react";
import { api, Note } from "../../api/client";

interface NotesProps {
  onOpenChat: () => void;
}

export function Notes({ onOpenChat }: NotesProps) {
  const [notes, setNotes] = useState<Note[]>([]);
  const [selectedId, setSelectedId] = useState<string>();
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [status, setStatus] = useState("");

  async function refresh(selectId?: string) {
    const items = await api.notes();
    setNotes(items);
    if (selectId) setSelectedId(selectId);
  }

  useEffect(() => {
    refresh().catch((reason) =>
      setError(reason instanceof Error ? reason.message : "Unable to load notes"),
    );
  }, []);

  function selectNote(note: Note) {
    setSelectedId(note.id);
    setTitle(note.title);
    setContent(note.content);
    setError("");
    setStatus("");
  }

  function newNote() {
    setSelectedId(undefined);
    setTitle("");
    setContent("");
    setError("");
    setStatus("");
  }

  async function save(event: FormEvent) {
    event.preventDefault();
    if (!title.trim() || !content.trim()) return;
    setBusy(true);
    setError("");
    setStatus("");
    try {
      const note = selectedId
        ? await api.updateNote(selectedId, title.trim(), content.trim())
        : await api.createNote(title.trim(), content.trim());
      await refresh(note.id);
      setSelectedId(note.id);
      setStatus("Note saved. Index it to make it available to the assistant.");
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to save note");
    } finally {
      setBusy(false);
    }
  }

  async function indexCurrent() {
    if (!selectedId) return;
    setBusy(true);
    setError("");
    setStatus("");
    try {
      await api.indexNote(selectedId);
      setStatus("Indexed successfully. The assistant can now retrieve this note.");
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Indexing failed");
    } finally {
      setBusy(false);
    }
  }

  async function removeCurrent() {
    if (!selectedId || !window.confirm("Delete this note?")) return;
    setBusy(true);
    try {
      await api.deleteNote(selectedId);
      newNote();
      await refresh();
      setStatus("Note deleted.");
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to delete note");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="shell">
      <aside>
        <div className="brand">Personal Assistant</div>
        <div className="section-switcher">
          <button onClick={onOpenChat}>Chat</button>
          <button className="active">Notes</button>
        </div>
        <button className="new-chat" onClick={newNote}>+ New note</button>
        <nav aria-label="Notes">
          {notes.map((note) => (
            <button
              className={note.id === selectedId ? "active" : ""}
              key={note.id}
              onClick={() => selectNote(note)}
            >
              {note.title}
            </button>
          ))}
        </nav>
      </aside>
      <section className="notes-page">
        <header>
          <h1>{selectedId ? "Edit note" : "New note"}</h1>
          <p>Save knowledge, then index it for retrieval in chat.</p>
        </header>
        <form className="note-editor" onSubmit={save}>
          <label>
            Title
            <input
              maxLength={200}
              placeholder="e.g. Semester schedule"
              value={title}
              onChange={(event) => setTitle(event.target.value)}
            />
          </label>
          <label className="content-field">
            Content
            <textarea
              maxLength={100000}
              placeholder="Write or paste information for your assistant…"
              value={content}
              onChange={(event) => setContent(event.target.value)}
            />
          </label>
          {error && <div className="error">{error}</div>}
          {status && <div className="success">{status}</div>}
          <div className="note-actions">
            <button disabled={busy || !title.trim() || !content.trim()} type="submit">
              {busy ? "Working…" : "Save"}
            </button>
            <button disabled={busy || !selectedId} type="button" onClick={indexCurrent}>
              Index for RAG
            </button>
            <button
              className="danger"
              disabled={busy || !selectedId}
              type="button"
              onClick={removeCurrent}
            >
              Delete
            </button>
          </div>
        </form>
      </section>
    </main>
  );
}
