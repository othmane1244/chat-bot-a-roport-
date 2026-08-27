const actions = [
  {
    icon: "✈️",
    label: "Check my flight",
    prompt: "Check my flight status",
  },
  {
    icon: "🛄",
    label: "Baggage",
    prompt: "Where can I find baggage information?",
  },
  {
    icon: "🚕",
    label: "Transport",
    prompt: "How can I get transportation from the airport?",
  },
  {
    icon: "🅿️",
    label: "Parking",
    prompt: "Tell me about airport parking",
  },
];

export default function QuickActions({ onAction }) {
  return (
    <section className="quick-actions">
      {actions.map((action) => (
        <button
          key={action.label}
          className="quick-action glass-card glass-card-hover"
          onClick={() => onAction && onAction(action.prompt)}
        >
          <span className="quick-action-icon">{action.icon}</span>
          <span>{action.label}</span>
        </button>
      ))}
    </section>
  );
}
