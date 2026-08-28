import { Cloud, Moon, Plane, Sun } from "lucide-react";

export default function SkyScene({ atmosphere = "sunny" }) {
  const isNight = atmosphere.includes("night");
  const isRainy = atmosphere.includes("rain") || atmosphere === "storm";
  const isStorm = atmosphere === "storm";
  const cloudCount = atmosphere === "cloudy" || isStorm ? 5 : 3;

  return (
    <div className={`sky-scene sky-${atmosphere}`} aria-hidden="true">
      {/* Celestial body */}
      {isNight ? (
        <>
          <Moon className="sky-moon" />
          <div className="stars">
            {Array.from({ length: 22 }).map((_, index) => (
              <span key={index} className={`star star-${index + 1}`} />
            ))}
          </div>
        </>
      ) : (
        <Sun className="sky-sun" />
      )}

      {/* Clouds */}
      <div className="sky-clouds">
        {Array.from({ length: cloudCount }).map((_, index) => (
          <Cloud
            key={index}
            className={`sky-cloud cloud-${index + 1}`}
            strokeWidth={1.2}
          />
        ))}
      </div>

      {/* Rain */}
      {isRainy && (
        <div className="rain-layer">
          {Array.from({ length: 40 }).map((_, index) => (
            <span key={index} className={`rain-drop rain-drop-${index + 1}`} />
          ))}
        </div>
      )}

      {/* Lightning */}
      {isStorm && <div className="lightning">⚡</div>}

      {/* Animated aircraft */}
      <div className="sky-plane-wrapper">
        <Plane className="sky-plane" size={42} strokeWidth={1.5} />
      </div>

      {/* Atmospheric overlay */}
      <div className="sky-atmosphere-overlay" />
    </div>
  );
}
