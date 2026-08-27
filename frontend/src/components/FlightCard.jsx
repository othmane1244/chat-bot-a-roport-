import GlassCard from "./GlassCard";
import { getOperationalData } from "../data/simulatedOperationalData";

export default function FlightCard({ flightNumber = "AT5432" }) {
  const flight = getOperationalData(flightNumber) || {
    flightNumber: "AT5432",
    airline: "Royal Air Maroc",
    origin: "Paris ORY",
    destination: "Agadir AGA",
    scheduledDeparture: "14:20",
    status: "Boarding",
    date: "25 May 2025",
    gate: "B12",
    terminal: "1",
    boardingZone: "B",
  };

  return (
    <GlassCard className="dashboard-card col-flight">
      <div className="card-header-bar flex-between">
        <h3 className="card-title font-bold">YOUR FLIGHT</h3>
        <span className="badge-demo-data">DEMO DATA</span>
      </div>

      <div className="flight-card-body">
        <div className="flight-main-header">
          <span className="flight-plane-icon">✈</span>
          <div>
            <div className="flight-number-title">{flight.flightNumber}</div>
            <div className="flight-airline-sub">{flight.airline}</div>
          </div>
        </div>

        <div className="flight-route-display">
          <div className="route-city">
            <span className="city-name font-bold">Paris</span>
            <span className="city-iata">ORY</span>
          </div>

          <div className="route-arrow-line">
            <div className="arrow-line-track" />
            <span className="plane-on-track">✈</span>
          </div>

          <div className="route-city text-right">
            <span className="city-name font-bold">Agadir</span>
            <span className="city-iata">AGA</span>
          </div>
        </div>

        <div className="flight-meta-row">
          <div className="meta-col">
            <span className="meta-label">Departure</span>
            <span className="meta-val">{flight.scheduledDeparture}</span>
          </div>
          <div className="meta-col">
            <span className="meta-label">Status</span>
            <span className="status-pill-green">● {flight.status}</span>
          </div>
          <div className="meta-col">
            <span className="meta-label">Date</span>
            <span className="meta-val">{flight.date}</span>
          </div>
        </div>

        <div className="flight-gates-box">
          <div className="gate-item">
            <span className="gate-item-label">Gate</span>
            <div className="gate-item-val">
              {flight.gate} <span className="green-demo-pill">DEMO</span>
            </div>
          </div>

          <div className="gate-item">
            <span className="gate-item-label">Terminal</span>
            <div className="gate-item-val">
              {flight.terminal} <span className="green-demo-pill">DEMO</span>
            </div>
          </div>
        </div>

        <div className="flight-sim-note">
          Gate and terminal information are simulated.
        </div>
      </div>
    </GlassCard>
  );
}
