import { useEffect, useState } from "react";
import { getWeather } from "../services/weatherService";
import { resolveWeather } from "../utils/weatherResolver";

export function useWeather() {
  const [weather, setWeather] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let isMounted = true;

    async function loadWeather() {
      try {
        setLoading(true);
        const rawWeather = await getWeather();
        const resolvedWeather = resolveWeather(
          rawWeather.weatherCode,
          rawWeather.isDay
        );

        if (!isMounted) return;

        setWeather({
          ...rawWeather,
          ...resolvedWeather,
        });

        setError(null);
      } catch (err) {
        if (!isMounted) return;
        setError(err);
        setWeather({
          temperature: 24,
          weatherCode: 0,
          isDay: true,
          condition: "Sunny",
          icon: "☀️",
          atmosphere: "sunny",
        });
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    }

    loadWeather();

    // Refresh every 15 minutes
    const interval = setInterval(loadWeather, 15 * 60 * 1000);

    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  return {
    weather,
    loading,
    error,
  };
}
