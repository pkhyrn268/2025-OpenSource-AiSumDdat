import React from "react";
import Header from "./components/Header.jsx";
import ChatPage from "./pages/ChatPage.jsx";
import SavedPage from "./pages/SavedPage.jsx";
import useChat from "../hooks/useChat.js";

export default function App() {
  const {
    page, setPage,
    input, setInput, messages, loading, error, onSend,
    savedList, deleteSaved, fillFromSaved
  } = useChat();

  return (
    <div className="shell">
      <Header onNavigate={(dest) => setPage(dest)} />

      {page === "chat" && (
        <ChatPage
          input={input}
          setInput={setInput}
          messages={messages}
          error={error}
          loading={loading}
          onSend={onSend}
        />
      )}

      {page === "saved" && (
        <SavedPage
          savedList={savedList}
          deleteSaved={deleteSaved}
          fillFromSaved={fillFromSaved}
        />
      )}
    </div>
  );
}
