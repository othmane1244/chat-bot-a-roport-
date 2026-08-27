import GlassCard from "./GlassCard";
import { useOperationalData } from "../hooks/useOperationalData";

function getStatusClass(status = "") {
  const value = String(status).toLowerCase();

  if (value.includes("board")) {
    return "status-boarding";
  }

  if (value.includes("delay")) {
    return "status-delayed";
  }

  if (value.includes("cancel")) {
    return "status-cancelled";
  }

  return "status-normal";
}

export default function FlightCard({ flight }) {
  const flightNumber = flight?.number || flight?.flightNumber || "AT5432";
  const operational = useOperationalData(flightNumber);

  const currentFlight = flight || {
    number: "AT5432",
    airline: "Royal Air Maroc",
    status: "Boarding",
    departure: {
      airport: "Paris Orly",
      iata: "ORY",
      scheduled: "14:20",
    },
    arrival: {
      airport: "Agadir Al Massira",
      iata: "AGA",
    },
  };

  const departure = currentFlight.departure || {};
  const arrival = currentFlight.arrival || {};

  return (
    <GlassCard className="dashboard-card col-flight flight-card">
      {/* HEADER */}
      <div className="flight-card-header">
        <div>
          <span className="flight-label">YOUR FLIGHT</span>
          <h2>✈ {currentFlight.number || flightNumber}</h2>
          <p>{currentFlight.airline || "Airline unavailable"}</p>
        </div>

        {operational && (
          <span className="demo-badge">DEMO DATA</span>
        )}
      </div>

      {/* ROUTE */}
      <div className="flight-route">
        <div className="airport-point">
          <strong>{departure.iata || "ORY"}</strong>
          <span>{departure.airport || "Paris Orly"}</span>
        </div>

        <div className="route-line">
          <span>✈</span>
        </div>

        <div className="airport-point">
          <strong>{arrival.iata || "AGA"}</strong>
          <span>{arrival.airport || "Agadir Al Massira"}</span>
        </div>
      </div>

      {/* REAL FLIGHT DATA */}
      <div className="flight-details">
        <div>
          <span>Departure</span>
          <strong>
            {departure.revised || departure.scheduled || "--:--"}
          </strong>
        </div>

        <div>
          <span>Status</span>
          <strong className={getStatusClass(currentFlight.status)}>
            ● {currentFlight.status || "Unknown"}
          </strong>
        </div>
      </div>

      {/* SIMULATED DATA */}
      {operational && (
        <div className="operational-section">
          <div className="operational-title">
            <span>Operational information</span>
            <small>SIMULATED</small>
          </div>

          <div className="operational-grid">
            <div>
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

      {/* TRANSPARENCY */}
      {operational && (
        <p className="simulation-note">
          Gate and terminal information are simulated for demonstration.
        </p>
      )}
    </GlassCard>
  );
}
