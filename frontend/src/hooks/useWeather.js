import { useEffect, useState } from "react";
import { getWeather } from "../services/weatherService";
import { resolveWeather } from "../utils/weatherResolver";
import { resolveAtmosphere } from "../utils/atmosphereResolver";

export function useWeather() {
  const [weather, setWeather] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let active = true;

    async function loadWeather() {
      try {
        setLoading(true);

        const rawWeather = await getWeather();
        const weatherInfo = resolveWeather(rawWeather.weatherCode, rawWeather.isDay);
        const atmosphere = resolveAtmosphere(rawWeather);

        if (!active) return;

        setWeather({
          ...rawWeather,
          ...weatherInfo,
          atmosphere,
        });

        setError(null);
      } catch (err) {
        if (!active) return;
        setError(err);
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    loadWeather();

    const interval = setInterval(loadWeather, 15 * 60 * 1000);

    return () => {
      active = false;
      clearInterval(interval);
    };
  }, []);

  return { weather, loading, error };
}
