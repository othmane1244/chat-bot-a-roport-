import { useState } from "react";
import GlassCard from "./GlassCard";

const initialDepartures = [
  { time: "14:20", flight: "AT5432", destination: "Paris ORY", status: "Boarding", statusType: "boarding" },
  { time: "15:10", flight: "FR6387", destination: "Marseille MRS", status: "Delayed 15:40", statusType: "delayed" },
  { time: "15:35", flight: "AT7012", destination: "Casablanca CMN", status: "On Time", statusType: "ontime" },
  { time: "16:20", flight: "VY1481", destination: "Barcelona BCN", status: "On Time", statusType: "ontime" },
  { time: "16:45", flight: "AT205", destination: "Toulouse TLS", status: "On Time", statusType: "ontime" },
];

export default function DeparturesBoard() {
  const [showIframe, setShowIframe] = useState(false);
  const avionioUrl = import.meta.env.VITE_AVIONIO_URL || "https://www.avionio.com/en/aga/departures";

  return (
    <GlassCard className="dashboard-card col-departures">
      <div className="card-header-bar flex-between">
        <div>
          <h3 className="card-title flex-items-center gap-2">
            <span className="departures-icon">🛫</span> Departures
          </h3>
          <span className="card-subtitle">Agadir Al Massira Airport</span>
        </div>

        <div className="departures-header-right">
          <span className="live-timestamp">14:35<br /><small>Sunday, 25 May</small></span>
          <span className="live-indicator-pill">● LIVE</span>
        </div>
      </div>

      {!showIframe ? (
        <div className="departures-table-wrapper">
          <table className="departures-table">
            <thead>
              <tr>
                <th>Time</th>
                <th>Flight ▾</th>
                <th>Destination</th>
                <th>Status ▾</th>
              </tr>
            </thead>
            <tbody>
              {initialDepartures.map((dep, idx) => (
                <tr key={idx}>
                  <td className="font-mono">{dep.time}</td>
                  <td className="font-bold">{dep.flight}</td>
                  <td>{dep.destination}</td>
                  <td>
                    <span className={`status-badge-table ${dep.statusType}`}>
                      {dep.statusType === 'boarding' && '● '}
                      {dep.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          <div className="avionio-footer-bar">
            <span>Powered by <strong className="avionio-brand">avionio</strong></span>
            <button 
              className="open-iframe-btn"
              onClick={() => setShowIframe(true)}
              title="Open Live Board Iframe"
            >
              ↗
            </button>
          </div>
        </div>
      ) : (
        <div className="iframe-container-box">
          <div className="iframe-top-controls">
            <span className="text-xs text-white/70">Avionio Live Departures</span>
            <button onClick={() => setShowIframe(false)} className="close-iframe-btn">
              ✕ Back to Table
            </button>
          </div>
          <iframe
            title="AGA Live Departures"
            src={avionioUrl}
            className="avionio-frame"
          />
        </div>
      )}
    </GlassCard>
  );
}
