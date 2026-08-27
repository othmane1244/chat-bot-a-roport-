/**
 * Configuration de l'application AGA Digital Terminal
 */
export const CONFIG = {
  // Mode démonstration : active les simulations locales si l'API backend ou externe n'a pas certaines données
  DEMO_MODE: true,

  // URL du backend FastAPI
  API_BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',

  // URL de l'iframe Avionio pour les départs en temps réel de l'aéroport Agadir Al Massira (AGA)
  AVIONIO_IFRAME_URL: 'https://www.avionio.com/en/airport/aga/departures',

  // Météo par défaut pour Agadir
  DEFAULT_WEATHER: {
    temp: 24,
    condition: 'Sunny', // 'Sunny' | 'Cloudy' | 'Rain' | 'Night'
    city: 'Agadir (AGA)',
    humidity: '62%',
    wind: '14 km/h',
  },

  // Délai de rafraîchissement des données de simulation de portes (en ms: 30 mins)
  SIMULATION_REFRESH_INTERVAL: 30 * 60 * 1000,
};
