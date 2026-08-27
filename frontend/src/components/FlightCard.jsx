import GlassCard from "./GlassCard";
import { getOperationalData } from "../data/simulatedOperationalData";

export default function FlightCard({ flight }) {
  let flightObj = null;

  if (typeof flight === "object" && flight !== null) {
    flightObj = flight;
  } else if (typeof flight === "string") {
    flightObj = getOperationalData(flight);
  }

  if (!flightObj) {
    flightObj = getOperationalData("AT5432") || {
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
  }

  const flightNum = flightObj.flightNumber || flightObj.number || "AT5432";
  const airline = flightObj.airline || "Royal Air Maroc";
  const origin = flightObj.origin || flightObj.departure?.airport || "Paris ORY";
  const destination = flightObj.destination || "Agadir AGA";
  const scheduled = flightObj.scheduledDeparture || flightObj.departure?.scheduled || "14:20";
  const status = flightObj.status || "Boarding";
  const date = flightObj.date || "25 May 2025";
  const gate = flightObj.gate || "B12";
  const terminal = flightObj.terminal || "1";

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
            <div className="flight-number-title">{flightNum}</div>
            <div className="flight-airline-sub">{airline}</div>
          </div>
        </div>

        <div className="flight-route-display">
          <div className="route-city">
            <span className="city-name font-bold">{origin.split(" ")[0]}</span>
            <span className="city-iata">{origin.split(" ")[1] || ""}</span>
          </div>

          <div className="route-arrow-line">
            <div className="arrow-line-track" />
            <span className="plane-on-track">✈</span>
          </div>

          <div className="route-city text-right">
            <span className="city-name font-bold">{destination.split(" ")[0]}</span>
            <span className="city-iata">{destination.split(" ")[1] || "AGA"}</span>
          </div>
        </div>

        <div className="flight-meta-row">
          <div className="meta-col">
            <span className="meta-label">Departure</span>
            <span className="meta-val">{scheduled}</span>
          </div>
          <div className="meta-col">
            <span className="meta-label">Status</span>
            <span className="status-pill-green">● {status}</span>
          </div>
          <div className="meta-col">
            <span className="meta-label">Date</span>
            <span className="meta-val">{date}</span>
          </div>
        </div>

        <div className="flight-gates-box">
          <div className="gate-item">
            <span className="gate-item-label">Gate</span>
            <div className="gate-item-val">
              {gate} <span className="green-demo-pill">DEMO</span>
            </div>
          </div>

          <div className="gate-item">
            <span className="gate-item-label">Terminal</span>
            <div className="gate-item-val">
              {terminal} <span className="green-demo-pill">DEMO</span>
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
