"""
Test du connecteur flights.py SANS appel réseau réel (impossible depuis
le sandbox où ce code a été écrit — rapidapi.com n'est pas accessible).
On mocke requests.get pour renvoyer un exemple de réponse conforme au
schéma documenté d'AeroDataBox.

Objectif : valider le PARSING et la MÉCANIQUE DE CACHE, pas la validité
de l'exemple JSON lui-même (à recontrôler avec une vraie clé API).

Usage : python tests/test_flights_mock.py
(relance-le après toute modif de app/connectors/flights.py ou cache.py)
"""
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import settings
from app.connectors import flights

settings.aerodatabox_api_key = "fake_key_for_testing"

FAKE_RESPONSE = [
    {
        "number": "RK860",
        "status": "Expected",
        "airline": {"name": "Ryanair", "iata": "FR"},
        "departure": {
            "airport": {"name": "Agadir Al Massira"},
            "scheduledTime": {"local": "2026-08-08 11:05+01:00"},
            "revisedTime": {"local": "2026-08-08 11:20+01:00"},
            "terminal": "1",
            "checkInDesk": "8,9",
            "gate": "5",
        },
        "arrival": {
            "airport": {"name": "Edinburgh"},
            "scheduledTime": {"local": "2026-08-08 15:30+00:00"},
            "terminal": "1",
            "baggageBelt": "3",
        },
        "lastUpdatedUtc": "2026-08-08T09:00:00Z",
    }
]


def fake_get(url, headers=None, timeout=None):
    print(f"  [mock] requests.get appelé -> {url}")
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = FAKE_RESPONSE
    return resp


print("--- Test 1 : premier appel (doit appeler l'API mockée) ---")
with patch("app.connectors.flights.requests.get", side_effect=fake_get) as mock_get:
    result = flights.get_flight_status("RK860")
    assert mock_get.call_count == 1
    assert result["numero_vol"] == "RK860"
    assert result["compagnie"] == "Ryanair"
    assert result["statut"] == "Expected"
    assert result["depart"]["porte"] == "5"
    assert result["depart"]["desk_enregistrement"] == "8,9"
    assert result["arrivee"]["tapis_bagages"] == "3"
    print("OK : parsing correct.\n")

print("--- Test 2 : deuxième appel immédiat (doit venir du CACHE) ---")
with patch("app.connectors.flights.requests.get", side_effect=fake_get) as mock_get:
    result2 = flights.get_flight_status("RK860")
    assert mock_get.call_count == 0, "Le cache aurait dû éviter un nouvel appel réseau"
    print("OK : cache fonctionne, pas de second appel réseau.\n")

print("--- Test 3 : clé API manquante -> doit lever ConnectorNotConfiguredError ---")
settings.aerodatabox_api_key = ""
try:
    flights.get_flight_status("RK999", use_cache=False)
    print("ECHEC : aurait dû lever une exception")
    sys.exit(1)
except flights.ConnectorNotConfiguredError as e:
    print(f"OK : exception levée comme attendu -> {e}\n")

print("TOUS LES TESTS PASSENT.")
