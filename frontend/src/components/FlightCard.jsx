import { Plane, Clock, CircleAlert, MapPin } from "lucide-react";
import GlassCard from "./GlassCard";
import { useOperationalData } from "../hooks/useOperationalData";

function getStatusClass(status = "") {
  const value = String(status).toLowerCase();
  if (value.includes("board")) return "status-boarding";
  if (value.includes("delay")) return "status-delayed";
  if (value.includes("cancel")) return "status-cancelled";
  return "status-normal";
}

export default function FlightCard({ flight }) {
  const operational = useOperationalData(flight?.number);

  // EMPTY STATE — no fake flight
  if (!flight) {
    return (
      <GlassCard className="flight-empty-card">
        <Plane size={42} strokeWidth={1.5} />
        <h3>Flight Information</h3>
        <p>Search for a flight to see its available information.</p>
      </GlassCard>
    );
  }

  const departure = flight.departure || {};
  const arrival = flight.arrival || {};

  return (
    <GlassCard className="flight-card">
      {/* HEADER */}
      <div className="flight-card-header">
        <div>
          <span className="flight-label">FLIGHT INFORMATION</span>
          <h2 className="flight-number-heading">
            <Plane size={22} />
            {flight.number}
          </h2>
          <p>{flight.airline || "Airline unavailable"}</p>
        </div>
        <span className="live-status">● LIVE</span>
      </div>

      {/* ROUTE */}
      <div className="flight-route">
        <div className="airport-point">
          <strong>{departure.iata || "---"}</strong>
          <span>{departure.airport || "Departure"}</span>
        </div>
        <div className="route-line">
          <Plane size={18} />
        </div>
        <div className="airport-point airport-arrival">
          <strong>{arrival.iata || "---"}</strong>
          <span>{arrival.airport || "Arrival"}</span>
        </div>
      </div>

      {/* REAL DATA */}
      <div className="flight-details">
        <div>
          <Clock size={16} />
          <span>Departure</span>
          <strong>
            {departure.revised || departure.scheduled || "--:--"}
          </strong>
        </div>
        <div>
          <CircleAlert size={16} />
          <span>Status</span>
          <strong className={getStatusClass(flight.status)}>
            ● {flight.status || "Unknown"}
          </strong>
        </div>
      </div>

      {/* SIMULATED OPERATIONAL DATA */}
      {operational && (
        <div className="operational-section">
          <div className="operational-title">
            <span>Operational information</span>
            <small>🟡 SIMULATED</small>
          </div>
          <div className="operational-grid">
            <div>
              <MapPin size={16} />
              <span>Gate</span>
              <strong>{operational.gate}</strong>
            </div>
            <div>
              <span>Terminal</span>
              <strong>{operational.terminal}</strong>
            </div>
            {operational.boardingZone && (
              <div>
                <span>Boarding zone</span>
                <strong>{operational.boardingZone}</strong>
              </div>
            )}
          </div>
        </div>
      )}
    </GlassCard>
  );
}
