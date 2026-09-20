import { StrictMode, useState } from "react";
import { createRoot } from "react-dom/client";
import { Chat } from "./features/chat/Chat";
import { Notes } from "./features/notes/Notes";
import { Tasks } from "./features/tasks/Tasks";
import "./styles.css";

function App() {
  const [page, setPage] = useState<"chat" | "notes" | "tasks">("chat");
  if (page === "chat") {
    return (
      <Chat
        onOpenNotes={() => setPage("notes")}
        onOpenTasks={() => setPage("tasks")}
      />
    );
  }
  if (page === "notes") {
    return (
      <Notes
        onOpenChat={() => setPage("chat")}
        onOpenTasks={() => setPage("tasks")}
      />
    );
  }
  return (
    <Tasks
      onOpenChat={() => setPage("chat")}
      onOpenNotes={() => setPage("notes")}
    />
  );
}

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
