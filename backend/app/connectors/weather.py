"""
Connecteur OpenWeatherMap — météo de la destination, comme sur le
panneau d'affichage réel (§0 du cahier des charges : "30°C" à côté
de chaque destination).

API : https://api.openweathermap.org/data/2.5/weather?q={ville}&appid={cle}&units=metric&lang=fr

⚠️ Même limite que pour AeroDataBox (voir flights.py) : api.openweathermap.org
n'est pas accessible depuis ce sandbox. Code écrit à partir du format de
réponse standard et stable d'OpenWeatherMap, testé avec un exemple JSON
réaliste, PAS avec un vrai appel réseau. À valider avec une vraie clé.
"""

import requests

from app.config import settings
from app.connectors.cache import get_cache

BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
CACHE_TTL_SECONDS = 600  # 10 min — la météo change moins vite qu'un statut de vol


class ConnectorNotConfiguredError(Exception):
    """Clé API manquante dans .env."""


class ConnectorAPIError(Exception):
    """L'API a répondu une erreur (ville introuvable, quota, 4xx/5xx...)."""


def parse_weather(raw: dict) -> dict:
    weather_list = raw.get("weather") or [{}]
    return {
        "ville": raw.get("name"),
        "pays": (raw.get("sys") or {}).get("country"),
        "temperature_c": (raw.get("main") or {}).get("temp"),
        "ressenti_c": (raw.get("main") or {}).get("feels_like"),
        "condition": weather_list[0].get("description"),
        "humidite_pct": (raw.get("main") or {}).get("humidity"),
    }


def get_weather(city: str, use_cache: bool = True) -> dict:
    if not settings.openweathermap_api_key:
        raise ConnectorNotConfiguredError(
            "OPENWEATHERMAP_API_KEY manquante dans .env — voir .env.example"
        )

    cache = get_cache() if use_cache else None
    cache_key = f"weather:{city.lower()}"

    if cache:
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

    params = {
        "q": city,
        "appid": settings.openweathermap_api_key,
        "units": "metric",
        "lang": "fr",
    }
    response = requests.get(BASE_URL, params=params, timeout=10)

    if response.status_code != 200:
        raise ConnectorAPIError(
            f"OpenWeatherMap a répondu {response.status_code} : {response.text[:200]}"
        )

    result = parse_weather(response.json())

    if cache:
        cache.set(cache_key, result, CACHE_TTL_SECONDS)

    return result
