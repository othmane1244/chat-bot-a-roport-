import SkyScene from "./SkyScene";

export default function AirportBackground({ atmosphere = "sunny" }) {
  return (
    <div className={`airport-background atmosphere-${atmosphere}`}>
      <SkyScene atmosphere={atmosphere} />
      <div className="airport-overlay" />
      <div className="airport-gradient" />
    </div>
  );
}
