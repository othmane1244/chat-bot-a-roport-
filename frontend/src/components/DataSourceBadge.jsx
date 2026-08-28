import { Radio, FlaskConical, CircleAlert } from "lucide-react";

const CONFIG = {
  live: {
    label: "LIVE",
    description: "Real-time data",
    icon: Radio,
    className: "data-source-live",
  },
  demo: {
    label: "SIMULATED",
    description: "Demonstration data",
    icon: FlaskConical,
    className: "data-source-demo",
  },
  unavailable: {
    label: "UNAVAILABLE",
    description: "Data unavailable",
    icon: CircleAlert,
    className: "data-source-unavailable",
  },
};

export default function DataSourceBadge({ type = "live", showDescription = false }) {
  const config = CONFIG[type] || CONFIG.unavailable;
  const Icon = config.icon;

  return (
    <div
      className={`data-source-badge ${config.className}`}
      title={config.description}
    >
      <Icon size={13} strokeWidth={2.5} />
      <span>{config.label}</span>
      {showDescription && <small>{config.description}</small>}
    </div>
  );
}
