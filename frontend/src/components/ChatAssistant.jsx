import { useState, useEffect, useRef } from "react";
import ChatMessage from "./ChatMessage";
import GlassCard from "./GlassCard";
import { useChat } from "../hooks/useChat";

export default function ChatAssistant({ currentLang = "fr" }) {
  const [input, setInput] = useState("");
  const { messages, loading, send } = useChat();
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const handleSubmit = (event) => {
    event.preventDefault();
    if (!input.trim()) return;
    send(input, currentLang);
    setInput("");
  };

  const handleActionClick = (promptText) => {
    send(promptText, currentLang);
  };

  // Demo messages matching the mockup if no user messages yet
  const displayMessages = messages.length > 0 ? messages : [
    {
      id: "demo-1",
      role: "user",
      content: "Where is the baggage claim?",
      timestamp: "14:32",
    },
    {
      id: "demo-2",
      role: "assistant",
      title: "🧳 Baggage Claim",
      content: "You can find the baggage claim area in the arrivals hall of Terminal 1, after passport control and customs.\n\nFollow the signs \"Baggage Claim\" or ask our staff for assistance.",
      timestamp: "14:32",
    }
  ];

  return (
    <GlassCard className="dashboard-card col-assistant">
      <div className="card-header-bar">
        <h3 className="card-title">AI ASSISTANT</h3>
      </div>

      <div className="chat-messages-container">
        {displayMessages.map((msg) => (
          <ChatMessage key={msg.id} message={msg} />
        ))}

        {loading && (
          <div className="typing-dots">
            <span />
            <span />
            <span />
          </div>
        )}

        <div ref={endRef} />
      </div>

      <div className="suggestion-pills-row">
        <button className="sug-pill" onClick={() => handleActionClick("Where is security?")}>
          Where is security?
        </button>
        <button className="sug-pill" onClick={() => handleActionClick("Check my flight AT5432")}>
          Check my flight AT5432
        </button>
        <button className="sug-pill" onClick={() => handleActionClick("Parking information")}>
          Parking information
        </button>
      </div>

      <form className="chat-bottom-input" onSubmit={handleSubmit}>
        <button type="button" className="attach-btn" title="Attach file">📎</button>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message..."
        />
        <button type="submit" className="send-circle-btn">
          ➤
        </button>
      </form>
    </GlassCard>
  );
}
