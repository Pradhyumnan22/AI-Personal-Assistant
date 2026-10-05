import { FormEvent, useEffect, useState } from "react";
import { api, Conversation, Message } from "../../api/client";

const DEMO_MODE = import.meta.env.VITE_DEMO_MODE === "true";
const demoConversation: Conversation = {
  id: "portfolio-demo",
  title: "Portfolio demo",
  pinned: true,
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
};

interface ChatProps {
  onOpenNotes: () => void;
  onOpenTasks: () => void;
  onOpenCalendar: () => void;
}

export function Chat({ onOpenNotes, onOpenTasks, onOpenCalendar }: ChatProps) {
  const [conversations, setConversations] = useState<Conversation[]>(
    DEMO_MODE ? [demoConversation] : [],
  );
  const [conversationId, setConversationId] = useState<string | undefined>(
    DEMO_MODE ? demoConversation.id : undefined,
  );
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const refreshConversations = () =>
    DEMO_MODE
      ? Promise.resolve()
      : api.conversations().then(setConversations).catch(() => undefined);

  useEffect(() => {
    refreshConversations();
  }, []);

  async function openConversation(id: string) {
    setConversationId(id);
    setError("");
    if (DEMO_MODE) {
      setMessages([]);
      return;
    }
    try {
      setMessages(await api.messages(id));
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to load chat");
    }
  }

  async function togglePin(conversation: Conversation) {
    setError("");
    if (DEMO_MODE) {
      setConversations((current) =>
        current.map((item) =>
          item.id === conversation.id ? { ...item, pinned: !item.pinned } : item,
        ),
      );
      return;
    }
    try {
      await api.pinConversation(conversation.id, !conversation.pinned);
      await refreshConversations();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to update pin");
    }
  }

  async function deleteConversation(conversation: Conversation) {
    if (!window.confirm(`Delete "${conversation.title}"? This cannot be undone.`)) {
      return;
    }
    setError("");
    if (DEMO_MODE) {
      setConversations((current) =>
        current.filter((item) => item.id !== conversation.id),
      );
      setConversationId(undefined);
      setMessages([]);
      return;
    }
    try {
      await api.deleteConversation(conversation.id);
      if (conversation.id === conversationId) {
        setConversationId(undefined);
        setMessages([]);
      }
      await refreshConversations();
    } catch (reason) {
      setError(
        reason instanceof Error ? reason.message : "Unable to delete conversation",
      );
    }
  }

  async function submit(event: FormEvent) {
    event.preventDefault();
    const message = input.trim();
    if (!message || busy) return;
    setInput("");
    setError("");
    setMessages((current) => [...current, { role: "user", content: message }]);
    setBusy(true);
    if (DEMO_MODE) {
      window.setTimeout(() => {
        setMessages((current) => [
          ...current,
          {
            role: "assistant",
            content:
              "This public portfolio is running in demo mode, so no OpenAI credits are used. The full application supports LangGraph workflows, RAG over saved notes, tasks, calendar tools, and persistent conversations.",
          },
        ]);
        setBusy(false);
      }, 550);
      return;
    }
    try {
      const response = await api.chat(message, conversationId);
      setConversationId(response.conversation_id);
      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          content: response.message,
          sources: response.sources,
        },
      ]);
      refreshConversations();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Chat failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="shell">
      <aside>
        <div className="brand">Personal Assistant</div>
        <div className="section-switcher four">
          <button className="active">Chat</button>
          <button disabled={DEMO_MODE} onClick={onOpenNotes}>Notes</button>
          <button disabled={DEMO_MODE} onClick={onOpenTasks}>Tasks</button>
          <button disabled={DEMO_MODE} onClick={onOpenCalendar}>Calendar</button>
        </div>
        <button
          className="new-chat"
          onClick={() => {
            setConversationId(undefined);
            setMessages([]);
          }}
        >
          + New conversation
        </button>
        <nav aria-label="Conversations">
          {conversations.map((conversation) => (
            <div
              className={`conversation-row ${
                conversation.id === conversationId ? "active" : ""
              }`}
              key={conversation.id}
            >
              <button
                className="conversation-open"
                onClick={() => openConversation(conversation.id)}
                title={conversation.title}
              >
                {conversation.pinned && <span className="pin-indicator">◆</span>}
                <span>{conversation.title}</span>
              </button>
              <div className="conversation-actions">
                <button
                  aria-label={conversation.pinned ? "Unpin conversation" : "Pin conversation"}
                  onClick={() => togglePin(conversation)}
                  title={conversation.pinned ? "Unpin" : "Pin"}
                >
                  {conversation.pinned ? "◆" : "◇"}
                </button>
                <button
                  aria-label="Delete conversation"
                  className="delete-conversation"
                  onClick={() => deleteConversation(conversation)}
                  title="Delete"
                >
                  ×
                </button>
              </div>
            </div>
          ))}
        </nav>
      </aside>
      <section className="chat">
        <header className="page-heading">
          <div>
            <span className="eyebrow">AI workspace</span>
            <h1>How can I help?</h1>
            <p>Chat with your knowledge, tasks, and calendar.</p>
          </div>
          <span className={`status-pill ${DEMO_MODE ? "demo" : ""}`}>
            <i /> {DEMO_MODE ? "Portfolio demo · no API usage" : "Assistant online"}
          </span>
        </header>
        <div className="messages" aria-live="polite">
          {messages.length === 0 && (
            <div className="empty chat-empty">
              <div className="assistant-mark">✦</div>
              <h2>Your day, one conversation away.</h2>
              <p>Ask a question, find a note, or plan what comes next.</p>
              <div className="prompt-grid">
                {[
                  "What tasks do I have?",
                  "Summarize my saved notes",
                  "What's on my calendar?",
                ].map((prompt) => (
                  <button key={prompt} onClick={() => setInput(prompt)}>
                    {prompt}<span>→</span>
                  </button>
                ))}
              </div>
            </div>
          )}
          {messages.map((message, index) => (
            <article className={message.role} key={message.id ?? index}>
              <strong>{message.role === "user" ? "You" : "Assistant"}</strong>
              <p>{message.content}</p>
              {message.sources && message.sources.length > 0 && (
                <div className="sources">
                  <span>Sources</span>
                  {message.sources.map((source) => (
                    <details key={`${source.note_id}-${source.excerpt}`}>
                      <summary>{source.title}</summary>
                      <p>{source.excerpt}</p>
                    </details>
                  ))}
                </div>
              )}
            </article>
          ))}
          {busy && (
            <article className="assistant thinking">
              <span /><span /><span />
            </article>
          )}
        </div>
        {error && <div className="error">{error}</div>}
        <form className="chat-composer" onSubmit={submit}>
          <textarea
            aria-label="Message"
            placeholder="Message your assistant…"
            value={input}
            onChange={(event) => setInput(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter" && !event.shiftKey) {
                event.preventDefault();
                event.currentTarget.form?.requestSubmit();
              }
            }}
          />
          <button aria-label="Send message" disabled={busy || !input.trim()} type="submit">
            Send <span>↑</span>
          </button>
        </form>
        <small className="composer-hint">Enter to send · Shift + Enter for a new line</small>
      </section>
    </main>
  );
}
