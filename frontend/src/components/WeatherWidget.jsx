import GlassCard from "./GlassCard";

export default function WeatherWidget({ weather }) {
  const {
    temp = 24,
    condition = "Sunny",
    humidity = "45%",
    wind = "18 km/h",
    visibility = "10 km",
    location = "Agadir, Morocco",
  } = weather || {};

  return (
    <GlassCard className="weather-card-hero">
      <div className="weather-hero-top">
        <span className="weather-hero-icon">☀️</span>
        <div>
          <div className="weather-hero-temp">{temp}°C</div>
          <div className="weather-hero-cond">{condition}</div>
        </div>
      </div>

      <div className="weather-hero-details">
        <div className="weather-row">
          <span>Humidity:</span>
          <strong>{humidity}</strong>
        </div>
        <div className="weather-row">
          <span>Wind:</span>
          <strong>{wind}</strong>
        </div>
        <div className="weather-row">
          <span>Visibility:</span>
          <strong>{visibility}</strong>
        </div>
      </div>

      <div className="weather-hero-location">
        {location}
      </div>
    </GlassCard>
  );
}
