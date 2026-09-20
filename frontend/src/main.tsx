import { StrictMode, useState } from "react";
import { createRoot } from "react-dom/client";
import { Chat } from "./features/chat/Chat";
import { Notes } from "./features/notes/Notes";
import "./styles.css";

function App() {
  const [page, setPage] = useState<"chat" | "notes">("chat");
  return page === "chat" ? (
    <Chat onOpenNotes={() => setPage("notes")} />
  ) : (
    <Notes onOpenChat={() => setPage("chat")} />
  );
}

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
