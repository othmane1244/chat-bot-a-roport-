"""
Connecteur AeroDataBox — statut de vol en temps réel (§5.2).

API : https://aerodatabox.p.rapidapi.com (via RapidAPI)
Auth : headers X-RapidAPI-Key + X-RapidAPI-Host
Endpoint utilisé : GET /flights/number/{flightNumber}
  -> renvoie une LISTE (un même numéro de vol peut correspondre à
     plusieurs occurrences/dates) ; on prend la première par simplicité,
     à affiner plus tard (ex: filtrer sur la date du jour) si besoin.

⚠️ LIMITE DE TEST DANS CE SANDBOX :
Ni rapidapi.com ni aerodatabox.p.rapidapi.com ne sont dans la liste des
domaines accessibles depuis cet environnement de développement (accès
réseau restreint). Impossible d'appeler la vraie API ici, avec ou sans
clé. Le code ci-dessous est écrit à partir du schéma de réponse
documenté par AeroDataBox (vérifié via recherche web : champs
`checkInDesk`, `gate`, `terminal`, `baggageBelt`, `scheduledTime`,
`revisedTime`, `status`...), et testé avec une réponse JSON d'exemple
réaliste (voir tests plus bas dans le README), PAS avec un vrai appel
réseau. À valider toi-même avec une vraie clé API avant la mise en
production.
"""

from typing import Optional

import requests

from app.config import settings
from app.connectors.cache import get_cache

BASE_URL = "https://aerodatabox.p.rapidapi.com"
CACHE_TTL_SECONDS = 180  # 3 minutes, cf. §5.2 du cahier des charges


class ConnectorNotConfiguredError(Exception):
    """Clé API manquante dans .env."""


class ConnectorAPIError(Exception):
    """L'API a répondu une erreur (quota dépassé, 4xx/5xx, vol introuvable...)."""


def _headers() -> dict:
    if not settings.aerodatabox_api_key:
        raise ConnectorNotConfiguredError(
            "AERODATABOX_API_KEY manquante dans .env — voir .env.example"
        )
    return {
        "X-RapidAPI-Key": settings.aerodatabox_api_key,
        "X-RapidAPI-Host": "aerodatabox.p.rapidapi.com",
    }


def _parse_movement(movement: Optional[dict]) -> dict:
    """Normalise une section 'departure' ou 'arrival' de la réponse brute."""
    if not movement:
        return {}
    scheduled = movement.get("scheduledTime") or {}
    revised = movement.get("revisedTime") or {}
    return {
        "aeroport": (movement.get("airport") or {}).get("name"),
        "heure_prevue": scheduled.get("local"),
        "heure_revisee": revised.get("local"),
        "terminal": movement.get("terminal"),
        "porte": movement.get("gate"),
        "desk_enregistrement": movement.get("checkInDesk"),
        "tapis_bagages": movement.get("baggageBelt"),
    }


def parse_flight_status(raw: dict) -> dict:
    """Transforme une entrée brute AeroDataBox en dict simplifié, aligné
    sur les champs du panneau d'affichage réel (§0 du cahier des charges) :
    heure, n° de vol, compagnie, destination, statut, portes/desk."""
    return {
        "numero_vol": raw.get("number"),
        "compagnie": (raw.get("airline") or {}).get("name"),
        "statut": raw.get("status"),
        "depart": _parse_movement(raw.get("departure")),
        "arrivee": _parse_movement(raw.get("arrival")),
        "derniere_maj_utc": raw.get("lastUpdatedUtc"),
    }


def get_flight_status(flight_number: str, use_cache: bool = True) -> dict:
    """Récupère le statut d'un vol par son numéro (ex: 'RK860').

    Cache : 3 minutes, pour économiser le quota gratuit (600 unités/mois)."""
    cache = get_cache() if use_cache else None
    cache_key = f"flight:{flight_number.upper()}"

    if cache:
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

    url = f"{BASE_URL}/flights/number/{flight_number.upper()}"
    response = requests.get(url, headers=_headers(), timeout=10)

    if response.status_code != 200:
        raise ConnectorAPIError(
            f"AeroDataBox a répondu {response.status_code} : {response.text[:200]}"
        )

    raw_list = response.json()
    if not raw_list:
        raise ConnectorAPIError(f"Aucun vol trouvé pour le numéro {flight_number}")

    result = parse_flight_status(raw_list[0])

    if cache:
        cache.set(cache_key, result, CACHE_TTL_SECONDS)

    return result
