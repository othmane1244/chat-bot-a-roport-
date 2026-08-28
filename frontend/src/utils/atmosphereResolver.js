export function resolveAtmosphere({ weatherCode, isDay }) {
  const hour = Number(
    new Date().toLocaleString("en-US", {
      timeZone: "Africa/Casablanca",
      hour: "2-digit",
      hour12: false,
    })
  );

  const rainyCodes = [51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82];
  const stormCodes = [95, 96, 99];
  const cloudyCodes = [1, 2, 3, 45, 48];

  if (stormCodes.includes(weatherCode)) return "storm";

  if (rainyCodes.includes(weatherCode)) {
    return isDay ? "rainy" : "rainy-night";
  }

  if (!isDay) return "night";

  if (hour >= 5 && hour < 8) return "morning";

  if (hour >= 18 && hour < 21) return "sunset";

  if (cloudyCodes.includes(weatherCode)) return "cloudy";

  return "sunny";
}
