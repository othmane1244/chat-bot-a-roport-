export function resolveWeather(weatherCode, isDay) {
  // Clear sky
  if (weatherCode === 0) {
    return {
      condition: isDay ? "Sunny" : "Clear",
      icon: isDay ? "☀️" : "🌙",
      atmosphere: isDay ? "sunny" : "night",
    };
  }

  // Mainly clear / partly cloudy
  if (weatherCode === 1 || weatherCode === 2) {
    return {
      condition: "Partly cloudy",
      icon: isDay ? "🌤️" : "☁️",
      atmosphere: isDay ? "cloudy" : "night",
    };
  }

  // Overcast
  if (weatherCode === 3) {
    return {
      condition: "Cloudy",
      icon: "☁️",
      atmosphere: isDay ? "cloudy" : "night",
    };
  }

  // Fog
  if (weatherCode === 45 || weatherCode === 48) {
    return {
      condition: "Foggy",
      icon: "🌫️",
      atmosphere: isDay ? "cloudy" : "night",
    };
  }

  // Rain
  if (
    [51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82].includes(weatherCode)
  ) {
    return {
      condition: "Rain",
      icon: "🌧️",
      atmosphere: isDay ? "rainy" : "night",
    };
  }

  // Snow
  if ([71, 73, 75, 77, 85, 86].includes(weatherCode)) {
    return {
      condition: "Snow",
      icon: "❄️",
      atmosphere: isDay ? "cloudy" : "night",
    };
  }

  // Thunderstorm
  if ([95, 96, 99].includes(weatherCode)) {
    return {
      condition: "Thunderstorm",
      icon: "⛈️",
      atmosphere: "storm",
    };
  }

  return {
    condition: "Unknown",
    icon: "🌤️",
    atmosphere: isDay ? "sunny" : "night",
  };
}
