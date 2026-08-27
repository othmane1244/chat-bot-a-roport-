export async function fetchAgadirWeather() {
  try {
    const res = await fetch(
      "https://api.open-meteo.com/v1/forecast?latitude=30.3833&longitude=-9.5497&current=temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code"
    );
    if (!res.ok) throw new Error("Weather API status not OK");
    const data = await res.json();
    const curr = data.current;

    let condition = "Sunny";
    const code = curr.weather_code;
    if (code >= 1 && code <= 3) condition = "Cloudy";
    else if (code >= 51 && code <= 99) condition = "Rain";

    return {
      temp: Math.round(curr.temperature_2m),
      condition,
      humidity: `${curr.relative_humidity_2m}%`,
      wind: `${Math.round(curr.wind_speed_10m)} km/h`,
      visibility: "10 km",
      location: "Agadir, Morocco",
    };
  } catch (error) {
    return {
      temp: 24,
      condition: "Sunny",
      humidity: "45%",
      wind: "18 km/h",
      visibility: "10 km",
      location: "Agadir, Morocco",
    };
  }
}
