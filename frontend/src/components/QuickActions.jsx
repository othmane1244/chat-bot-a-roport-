const actions = [
  {
    icon: "✈️",
    label: "Flight information",
    prompt: "I want information about my flight.",
  },
  {
    icon: "🧳",
    label: "Baggage services",
    prompt: "What should I do if my baggage is lost?",
  },
  {
    icon: "🛂",
    label: "Travel documents",
    prompt: "What travel documents do I need?",
  },
  {
    icon: "🚌",
    label: "Transport & Parking",
    prompt: "Where can I find airport parking and transport?",
  },
  {
    icon: "🏪",
    label: "Airport facilities",
    prompt: "What services and facilities are available at the airport?",
  },
];

export default function QuickActions({ onAction }) {
  return (
    <div className="quick-actions-bar">
      {actions.map((action) => (
        <button
          key={action.label}
          className="quick-action-pill"
          onClick={() => onAction && onAction(action.prompt)}
        >
          <span className="action-icon">{action.icon}</span>
          <span className="action-label">{action.label}</span>
        </button>
      ))}
    </div>
  );
}
