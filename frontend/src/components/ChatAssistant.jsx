import { useState, useEffect, useRef } from "react";
import ChatMessage from "./ChatMessage";
import GlassCard from "./GlassCard";

export default function ChatAssistant({
  messages = [],
  loading = false,
  onSend,
}) {
  const [input, setInput] = useState("");
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages, loading]);

  const handleSubmit = async (event) => {
    event.preventDefault();

    if (!input.trim() || loading) return;

    await onSend(input);

    setInput("");
  };

  const handleSuggestionClick = async (prompt) => {
    if (loading) return;
    await onSend(prompt);
  };

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
    <GlassCard className="dashboard-card col-assistant" id="assistant">
      <div className="card-header-bar flex-between">
        <div className="assistant-title flex-items-center gap-2">
          <div className="assistant-icon">✈</div>
          <div>
            <h3 className="card-title">AI AIRPORT ASSISTANT</h3>
            <span className="online-status">● Online</span>
          </div>
        </div>
      </div>

      <div className="messages chat-messages-container">
        {displayMessages.map((message) => (
          <ChatMessage
            key={message.id}
            message={message}
          />
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
        <button className="sug-pill" onClick={() => handleSuggestionClick("Where is security?")}>
          Where is security?
        </button>
        <button className="sug-pill" onClick={() => handleSuggestionClick("Check my flight AT5432")}>
          Check my flight AT5432
        </button>
        <button className="sug-pill" onClick={() => handleSuggestionClick("Parking information")}>
          Parking information
        </button>
      </div>

      <form
        className="chat-bottom-input"
        onSubmit={handleSubmit}
      >
        <button type="button" className="attach-btn" title="Attach file">📎</button>
        <input
          value={input}
          onChange={(event) =>
            setInput(event.target.value)
          }
          placeholder="Ask anything about the airport..."
          disabled={loading}
        />

        <button
          type="submit"
          className="send-circle-btn"
          disabled={loading}
        >
          {loading ? "..." : "➤"}
        </button>
      </form>
    </GlassCard>
  );
}
