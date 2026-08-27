export default function ChatMessage({ message }) {
  const isUser = message.role === "user";

  return (
    <div className={`chat-msg-row ${isUser ? "msg-user-row" : "msg-assistant-row"}`}>
      {!isUser && (
        <div className="avatar-circle bot-avatar">
          🤖
        </div>
      )}

      <div className="msg-bubble">
        {message.title && <div className="msg-title">{message.title}</div>}
        <div className="msg-body">{message.content}</div>

        {message.sources && message.sources.length > 0 && (
          <div className="msg-sources">
            <span>Sources: </span>{message.sources.join(", ")}
          </div>
        )}

        <div className="msg-timestamp">{message.timestamp || "14:32"}</div>
      </div>

      {isUser && (
        <div className="avatar-circle user-avatar">
          👤
        </div>
      )}
    </div>
  );
}
