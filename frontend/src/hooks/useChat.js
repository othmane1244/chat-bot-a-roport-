import { useState } from "react";
import { sendMessage } from "../services/chatService";

export function useChat() {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  const send = async (text, lang = "fr") => {
    if (!text?.trim() || loading) return null;

    const userMessage = {
      id: crypto.randomUUID(),
      role: "user",
      type: "text",
      content: text,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((previous) => [...previous, userMessage]);
    setLoading(true);

    try {
      const response = await sendMessage(text, lang);

      const assistantMessage = {
        id: crypto.randomUUID(),
        role: "assistant",
        type: response.type || "text",
        content:
          response.reply ||
          response.answer ||
          response.message ||
          "Sorry, I couldn't find an answer.",
        sources: response.sources || [],
        flight: response.flight || null,
        data: response,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };

      setMessages((previous) => [...previous, assistantMessage]);
      return response;
    } catch (error) {
      console.error("Chat error:", error);
      const errorMessage = {
        id: crypto.randomUUID(),
        role: "assistant",
        type: "error",
        content: "Unable to contact the airport assistant. Please try again.",
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };

      setMessages((previous) => [...previous, errorMessage]);
      return null;
    } finally {
      setLoading(false);
    }
  };

  return {
    messages,
    loading,
    send,
  };
}
