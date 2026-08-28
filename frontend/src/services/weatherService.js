const AGADIR_LATITUDE = 30.4278;
const AGADIR_LONGITUDE = -9.5981;

const WEATHER_URL = "https://api.open-meteo.com/v1/forecast";

export async function getWeather() {
  const params = new URLSearchParams({
    latitude: AGADIR_LATITUDE,
    longitude: AGADIR_LONGITUDE,
    current: [
      "temperature_2m",
      "relative_humidity_2m",
      "weather_code",
      "wind_speed_10m",
      "visibility",
      "is_day",
    ].join(","),
    timezone: "Africa/Casablanca",
  });

  const response = await fetch(`${WEATHER_URL}?${params.toString()}`);

  if (!response.ok) {
    throw new Error("Unable to retrieve weather data");
  }

  const data = await response.json();
  const current = data.current;

  return {
    temperature: Math.round(current.temperature_2m),
    humidity: current.relative_humidity_2m,
    windSpeed: Math.round(current.wind_speed_10m),
    visibility: current.visibility
      ? Math.round(current.visibility / 1000)
      : null,
    weatherCode: current.weather_code,
    isDay: Boolean(current.is_day),
  };
}
