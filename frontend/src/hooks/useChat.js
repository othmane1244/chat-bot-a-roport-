import { useState } from "react";
import { sendMessage } from "../services/chatService";

export function useChat() {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  const send = async (message, lang = "fr") => {
    if (!message?.trim() || loading) return;

    const userMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content: message,
    };

    setMessages((previous) => [
      ...previous,
      userMessage,
    ]);

    setLoading(true);

    try {
      const response = await sendMessage(message, lang);

      const assistantMessage = {
        id: crypto.randomUUID(),
        role: "assistant",

        content:
          response.reply ||
          response.answer ||
          response.message ||
          response.response ||
          "I couldn't find an answer.",

        sources: response.sources || [],
        data: response,
      };

      setMessages((previous) => [
        ...previous,
        assistantMessage,
      ]);
    } catch (error) {
      setMessages((previous) => [
        ...previous,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          type: "error",
          content:
            "Unable to reach the airport assistant. Please make sure the backend server is running.",
        },
      ]);
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
