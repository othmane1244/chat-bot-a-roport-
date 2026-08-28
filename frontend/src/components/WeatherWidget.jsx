import GlassCard from "./GlassCard";

export default function WeatherWidget({ weather, loading }) {
  return (
    <GlassCard className="weather-widget weather-card-hero">
      <div className="weather-hero-top">
        <span className="weather-hero-icon">
          {loading ? "..." : weather?.icon || "—"}
        </span>
        <div>
          <div className="weather-hero-temp">
            {weather ? `${weather.temperature}°C` : "—"}
          </div>
          <div className="weather-hero-cond">
            {loading
              ? "Loading weather..."
              : weather?.condition || "Unavailable"}
          </div>
        </div>
      </div>
      <div className="weather-hero-location">Agadir, Morocco</div>
    </GlassCard>
  );
}
