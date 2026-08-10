"""Test de weather.py sans appel réseau réel (mock), même logique que
test_flights_mock.py.

Usage : python tests/test_weather_mock.py
"""
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import settings
from app.connectors import weather

settings.openweathermap_api_key = "fake_key_for_testing"

FAKE_RESPONSE = {
    "name": "Edinburgh",
    "sys": {"country": "GB"},
    "main": {"temp": 17.4, "feels_like": 16.8, "humidity": 72},
    "weather": [{"main": "Clouds", "description": "nuageux"}],
}


def fake_get(url, params=None, timeout=None):
    print(f"  [mock] requests.get appelé -> {url} params={params}")
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = FAKE_RESPONSE
    return resp


print("--- Test 1 : premier appel ---")
with patch("app.connectors.weather.requests.get", side_effect=fake_get) as mock_get:
    result = weather.get_weather("Edinburgh")
    assert mock_get.call_count == 1
    assert result["ville"] == "Edinburgh"
    assert result["temperature_c"] == 17.4
    assert result["condition"] == "nuageux"
    print("OK : parsing correct.\n")

print("--- Test 2 : deuxième appel (doit venir du cache) ---")
with patch("app.connectors.weather.requests.get", side_effect=fake_get) as mock_get:
    result2 = weather.get_weather("Edinburgh")
    assert mock_get.call_count == 0
    print("OK : cache fonctionne.\n")

print("--- Test 3 : clé API manquante ---")
settings.openweathermap_api_key = ""
try:
    weather.get_weather("Paris", use_cache=False)
    print("ECHEC : aurait dû lever une exception")
    sys.exit(1)
except weather.ConnectorNotConfiguredError as e:
    print(f"OK : exception levée comme attendu -> {e}\n")

print("TOUS LES TESTS PASSENT.")
