import { FormEvent, useEffect, useState } from "react";
import { api, Conversation, Message } from "../../api/client";

interface ChatProps {
  onOpenNotes: () => void;
}

export function Chat({ onOpenNotes }: ChatProps) {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [conversationId, setConversationId] = useState<string>();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const refreshConversations = () =>
    api.conversations().then(setConversations).catch(() => undefined);

  useEffect(() => {
    refreshConversations();
  }, []);

  async function openConversation(id: string) {
    setConversationId(id);
    setError("");
    try {
      setMessages(await api.messages(id));
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to load chat");
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
        <div className="section-switcher">
          <button className="active">Chat</button>
          <button onClick={onOpenNotes}>Notes</button>
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
            <button
              className={conversation.id === conversationId ? "active" : ""}
              key={conversation.id}
              onClick={() => openConversation(conversation.id)}
            >
              {conversation.title}
            </button>
          ))}
        </nav>
      </aside>
      <section className="chat">
        <header>
          <h1>How can I help?</h1>
          <p>Ask a question or work with your saved notes.</p>
        </header>
        <div className="messages" aria-live="polite">
          {messages.length === 0 && (
            <div className="empty">Start a conversation with your assistant.</div>
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
          {busy && <article className="assistant">Thinking…</article>}
        </div>
        {error && <div className="error">{error}</div>}
        <form onSubmit={submit}>
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
          <button disabled={busy || !input.trim()} type="submit">Send</button>
        </form>
      </section>
    </main>
  );
}
