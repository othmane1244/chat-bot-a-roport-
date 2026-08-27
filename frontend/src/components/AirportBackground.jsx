export default function AirportBackground({ atmosphere = "sunny" }) {
  return (
    <div className={`airport-background atmosphere-${atmosphere}`}>
      <div className="airport-overlay" />
      <div className="airport-gradient" />
    </div>
  );
}
