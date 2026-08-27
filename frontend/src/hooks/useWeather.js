import { useState, useEffect } from "react";
import { fetchAgadirWeather } from "../services/weatherService";

export function useWeather() {
  const [weather, setWeather] = useState({
    temp: 24,
    condition: "Sunny",
    humidity: "45%",
    wind: "18 km/h",
    visibility: "10 km",
    location: "Agadir, Morocco",
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    fetchAgadirWeather()
      .then((data) => {
        if (mounted && data) {
          setWeather(data);
        }
      })
      .finally(() => {
        if (mounted) setLoading(false);
      });

    return () => {
      mounted = false;
    };
  }, []);

  const setCondition = (condition) => {
    setWeather((prev) => ({ ...prev, condition }));
  };

  return {
    weather,
    loading,
    setCondition,
  };
}
