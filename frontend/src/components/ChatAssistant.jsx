import { useState } from "react";
import { Plane, Paperclip, Send, Bot } from "lucide-react";
import ChatMessage from "./ChatMessage";
import GlassCard from "./GlassCard";
import useAutoScroll from "../hooks/useAutoScroll";

export default function ChatAssistant({ messages = [], loading = false, onSend }) {
  const [input, setInput] = useState("");

  const { containerRef, handleScroll, scrollToBottom, hasNewMessages } =
    useAutoScroll([messages, loading]);

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!input.trim() || loading) return;
    const text = input.trim();
    setInput("");
    await onSend(text);
  };

  const handleSuggestion = (prompt) => {
    if (!loading) {
      onSend(prompt);
    }
  };

  return (
    <GlassCard className="chat-assistant-card" id="assistant">
      {/* HEADER */}
      <div className="card-header-bar">
        <div className="assistant-title">
          <div className="assistant-avatar">
            <Bot size={18} />
          </div>
          <div>
            <h3 className="card-title">AI AIRPORT ASSISTANT</h3>
            <span className="online-status">● Online</span>
          </div>
        </div>
      </div>

      {/* MESSAGES */}
      <div
        ref={containerRef}
        className="chat-messages-container"
        onScroll={handleScroll}
      >
        {messages.length === 0 ? (
          <div className="chat-empty-state">
            <Plane size={38} />
            <h3>Welcome to AGA Assistant</h3>
            <p>Ask anything about your journey at Agadir Al Massira Airport.</p>
          </div>
        ) : (
          messages.map((message) => (
            <ChatMessage key={message.id} message={message} />
          ))
        )}

        {loading && (
          <div className="typing-wrapper">
            <div className="assistant-avatar">
              <Bot size={16} />
            </div>
            <div className="typing-indicator">
              <span />
              <span />
              <span />
            </div>
          </div>
        )}
      </div>

      {/* NEW MESSAGES INDICATOR */}
      {hasNewMessages && (
        <button
          type="button"
          className="scroll-to-bottom-btn"
          onClick={() => scrollToBottom("smooth")}
        >
          ↓ New messages
        </button>
      )}

      {/* SUGGESTIONS */}
      <div className="suggestion-pills-row">
        <button type="button" onClick={() => handleSuggestion("Where is security?")}>
          Security
        </button>
        <button type="button" onClick={() => handleSuggestion("What is my flight status?")}>
          Flight status
        </button>
        <button type="button" onClick={() => handleSuggestion("Where can I find parking?")}>
          Parking
        </button>
      </div>

      {/* INPUT */}
      <form className="chat-bottom-input" onSubmit={handleSubmit}>
        <button
          type="button"
          className="attach-btn"
          aria-label="Attach file"
          disabled
        >
          <Paperclip size={18} />
        </button>

        <input
          value={input}
          onChange={(event) => setInput(event.target.value)}
          placeholder="Ask anything about the airport..."
          disabled={loading}
        />

        <button
          type="submit"
          className="send-circle-btn"
          disabled={loading || !input.trim()}
          aria-label="Send message"
        >
          <Send size={18} />
        </button>
      </form>
    </GlassCard>
  );
}
