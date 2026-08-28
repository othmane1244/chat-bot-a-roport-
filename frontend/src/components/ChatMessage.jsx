import ReactMarkdown from "react-markdown";
import { Bot, User } from "lucide-react";

export default function ChatMessage({ message }) {
  const isUser = message.role === "user";

  return (
    <div
      className={`chat-msg-row ${
        isUser ? "msg-user-row" : "msg-assistant-row"
      } animate-message`}
    >
      {!isUser && (
        <div className="avatar-circle bot-avatar">
          <Bot size={18} />
        </div>
      )}

      <div className="msg-bubble">
        {message.title && (
          <div className="msg-title">{message.title}</div>
        )}

        <div className="msg-body">
          <ReactMarkdown>{message.content}</ReactMarkdown>
        </div>

        {message.sources?.length > 0 && (
          <div className="msg-sources">
            <span>Sources: </span>
            {message.sources.join(", ")}
          </div>
        )}

        <div className="msg-timestamp">{message.timestamp}</div>
      </div>

      {isUser && (
        <div className="avatar-circle user-avatar">
          <User size={18} />
        </div>
      )}
    </div>
  );
}
