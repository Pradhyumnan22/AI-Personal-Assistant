import { FormEvent, useEffect, useState } from "react";
import { api, CalendarEvent, CalendarStatus } from "../../api/client";

interface CalendarProps {
  onOpenChat: () => void;
  onOpenNotes: () => void;
  onOpenTasks: () => void;
}

export function Calendar({
  onOpenChat,
  onOpenNotes,
  onOpenTasks,
}: CalendarProps) {
  const [status, setStatus] = useState<CalendarStatus>();
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [title, setTitle] = useState("");
  const [start, setStart] = useState("");
  const [end, setEnd] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function refresh() {
    const current = await api.calendarStatus();
    setStatus(current);
    setEvents(current.connected ? await api.calendarEvents() : []);
  }

  useEffect(() => {
    refresh().catch((reason) =>
      setError(reason instanceof Error ? reason.message : "Unable to load Calendar"),
    );
  }, []);

  async function connect() {
    setBusy(true);
    setError("");
    try {
      const response = await api.calendarConnectUrl();
      window.location.href = response.authorization_url;
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to connect");
      setBusy(false);
    }
  }

  async function disconnect() {
    setBusy(true);
    try {
      await api.disconnectCalendar();
      await refresh();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to disconnect");
    } finally {
      setBusy(false);
    }
  }

  async function createEvent(event: FormEvent) {
    event.preventDefault();
    if (!title.trim() || !start) return;
    setBusy(true);
    setError("");
    try {
      await api.createCalendarEvent(
        title.trim(),
        new Date(start).toISOString(),
        end ? new Date(end).toISOString() : undefined,
      );
      setTitle("");
      setStart("");
      setEnd("");
      await refresh();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to create event");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="shell">
      <aside>
        <div className="brand">Personal Assistant</div>
        <div className="section-switcher four">
          <button onClick={onOpenChat}>Chat</button>
          <button onClick={onOpenNotes}>Notes</button>
          <button onClick={onOpenTasks}>Tasks</button>
          <button className="active">Calendar</button>
        </div>
      </aside>
      <section className="calendar-page">
        <header>
          <h1>Google Calendar</h1>
          <p>View and create events here or through assistant chat.</p>
        </header>
        {!status?.configured && (
          <div className="setup-card">
            Add <code>GOOGLE_CLIENT_ID</code> and <code>GOOGLE_CLIENT_SECRET</code>
            to <code>.env</code>, then restart the backend.
          </div>
        )}
        {status?.configured && !status.connected && (
          <div className="setup-card">
            <p>Connect your Google account to enable Calendar tools.</p>
            <button disabled={busy} onClick={connect}>Connect Google Calendar</button>
          </div>
        )}
        {status?.connected && (
          <>
            <div className="calendar-toolbar">
              <span>Connected to Google Calendar</span>
              <button disabled={busy} onClick={disconnect}>Disconnect</button>
            </div>
            <form className="event-form" onSubmit={createEvent}>
              <input
                maxLength={300}
                placeholder="Event title"
                value={title}
                onChange={(event) => setTitle(event.target.value)}
              />
              <label>
                Starts
                <input
                  type="datetime-local"
                  value={start}
                  onChange={(event) => setStart(event.target.value)}
                />
              </label>
              <label>
                Ends (optional)
                <input
                  type="datetime-local"
                  value={end}
                  onChange={(event) => setEnd(event.target.value)}
                />
              </label>
              <button disabled={busy || !title.trim() || !start} type="submit">
                Add event
              </button>
            </form>
            <div className="event-list">
              {events.length === 0 && <div className="empty">No upcoming events.</div>}
              {events.map((event) => (
                <article className="event-row" key={event.id}>
                  <strong>{event.title}</strong>
                  <span>{new Date(event.start).toLocaleString()}</span>
                  {event.html_link && (
                    <a href={event.html_link} rel="noreferrer" target="_blank">
                      Open in Google Calendar
                    </a>
                  )}
                </article>
              ))}
            </div>
          </>
        )}
        {error && <div className="error">{error}</div>}
      </section>
    </main>
  );
}
