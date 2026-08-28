export default function GlassCard({ children, className = "", onClick, id }) {
  return (
    <div
      className={`glass-card ${className}`}
      onClick={onClick}
      id={id}
    >
      {children}
    </div>
  );
}
