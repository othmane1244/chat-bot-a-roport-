import { Clock3, Droplets, Eye, MapPin, Wind } from "lucide-react";
import GlassCard from "./GlassCard";
import DataSourceBadge from "./DataSourceBadge";
import { useLocalTime } from "../hooks/useLocalTime";

export default function AirportToday({ weather, loading = false, error = false }) {
  const time = useLocalTime();
  const hasWeather = weather && !error;

  return (
    <GlassCard className="airport-today">
      <div className="airport-today-top">
        <div>
          <span className="section-eyebrow">AIRPORT TODAY</span>
          <h3>Agadir Al Massira</h3>
        </div>
        <DataSourceBadge type={hasWeather ? "live" : "unavailable"} />
      </div>

      <div className="airport-today-main">
        <div className="today-weather">
          <div className="today-weather-icon">
            {loading ? "..." : hasWeather ? weather.icon : "—"}
          </div>
          <div className="today-weather-content">
            <strong>
              {hasWeather ? `${weather.temperature}°C` : "—"}
            </strong>
            <span>
              {loading
                ? "Loading weather..."
                : hasWeather
                ? weather.condition
                : "Weather unavailable"}
            </span>
          </div>
        </div>

        <div className="today-time">
          <Clock3 size={19} />
          <div>
            <strong>{time}</strong>
            <span>Local time</span>
          </div>
        </div>
      </div>

      {hasWeather && (
        <div className="airport-weather-stats">
          <div className="weather-stat">
            <Droplets size={16} />
            <div>
              <span>Humidity</span>
              <strong>{weather.humidity}%</strong>
            </div>
          </div>

          <div className="weather-stat">
            <Wind size={16} />
            <div>
              <span>Wind</span>
              <strong>{weather.windSpeed} km/h</strong>
            </div>
          </div>

          {weather.visibility !== null && weather.visibility !== undefined && (
            <div className="weather-stat">
              <Eye size={16} />
              <div>
                <span>Visibility</span>
                <strong>{weather.visibility} km</strong>
              </div>
            </div>
          )}
        </div>
      )}

      <div className="airport-location">
        <MapPin size={15} />
        <span>Agadir, Morocco</span>
      </div>
    </GlassCard>
  );
}
