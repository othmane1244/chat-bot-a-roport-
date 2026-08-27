import GlassCard from "./GlassCard";

export default function WeatherWidget({ weather, loading }) {
  if (loading) {
    return (
      <GlassCard className="weather-widget weather-loading weather-card-hero">
        <div className="weather-hero-top">
          <span className="weather-hero-icon">🌤️</span>
          <div>
            <div className="weather-hero-temp">--°C</div>
            <div className="weather-hero-cond">Loading weather...</div>
          </div>
        </div>
      </GlassCard>
    );
  }

  if (!weather) {
    return null;
  }

  const temp = weather.temperature ?? weather.temp ?? 24;
  const condition = weather.condition || "Sunny";
  const icon = weather.icon || "☀️";

  return (
    <GlassCard className="weather-widget weather-card-hero">
      <div className="weather-hero-top">
        <span className="weather-hero-icon">{icon}</span>
        <div>
          <div className="weather-hero-temp">{temp}°C</div>
          <div className="weather-hero-cond">{condition}</div>
        </div>
      </div>

      <div className="weather-hero-details">
        <div className="weather-row">
          <span>Humidity:</span>
          <strong>45%</strong>
        </div>
        <div className="weather-row">
          <span>Wind:</span>
          <strong>18 km/h</strong>
        </div>
        <div className="weather-row">
          <span>Visibility:</span>
          <strong>10 km</strong>
        </div>
      </div>

      <div className="weather-hero-location">
        Agadir, Morocco
      </div>
    </GlassCard>
  );
}
