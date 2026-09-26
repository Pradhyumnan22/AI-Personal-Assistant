import { StrictMode, useState } from "react";
import { createRoot } from "react-dom/client";
import { Chat } from "./features/chat/Chat";
import { Calendar } from "./features/calendar/Calendar";
import { Notes } from "./features/notes/Notes";
import { Tasks } from "./features/tasks/Tasks";
import "./styles.css";

function App() {
  const [page, setPage] = useState<"chat" | "notes" | "tasks" | "calendar">(
    window.location.search.includes("calendar=connected") ? "calendar" : "chat",
  );
  if (page === "chat") {
    return (
      <Chat
        onOpenNotes={() => setPage("notes")}
        onOpenTasks={() => setPage("tasks")}
        onOpenCalendar={() => setPage("calendar")}
      />
    );
  }
  if (page === "notes") {
    return (
      <Notes
        onOpenChat={() => setPage("chat")}
        onOpenTasks={() => setPage("tasks")}
        onOpenCalendar={() => setPage("calendar")}
      />
    );
  }
  if (page === "tasks") return (
    <Tasks
      onOpenChat={() => setPage("chat")}
      onOpenNotes={() => setPage("notes")}
      onOpenCalendar={() => setPage("calendar")}
    />
  );
  return (
    <Calendar
      onOpenChat={() => setPage("chat")}
      onOpenNotes={() => setPage("notes")}
      onOpenTasks={() => setPage("tasks")}
    />
  );
}

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
