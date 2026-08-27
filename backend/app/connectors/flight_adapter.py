"""
Adaptateur / Normaliseur pour les données brutes des fournisseurs de vol.
Transforme tout dictionnaire brut de vol en un objet Pydantic FlightData propre.
"""

from app.schemas import FlightData, FlightLocation


def normalize_flight_data(raw: dict) -> FlightData:
    departure_raw = raw.get("depart") or raw.get("departure") or {}
    arrival_raw = raw.get("arrivee") or raw.get("arrival") or {}

    return FlightData(
        number=(
            raw.get("numero_vol")
            or raw.get("number")
            or raw.get("flightNumber")
            or "AT5432"
        ),
        airline=(
            raw.get("compagnie")
            or raw.get("airline")
            or raw.get("airlineName")
            or "Royal Air Maroc"
        ),
        status=raw.get("statut") or raw.get("status") or "Boarding",
        departure=FlightLocation(
            airport=(
                departure_raw.get("aeroport")
                or departure_raw.get("airport")
                or departure_raw.get("name")
                or "Paris Orly"
            ),
            iata=(
                departure_raw.get("iata")
                or departure_raw.get("iataCode")
                or "ORY"
            ),
            scheduled=(
                departure_raw.get("heure_prevue")
                or departure_raw.get("scheduled")
                or departure_raw.get("scheduledTime")
                or "14:20"
            ),
            revised=(
                departure_raw.get("heure_estimee")
                or departure_raw.get("revised")
                or departure_raw.get("revisedTime")
                or None
            ),
        ),
        arrival=FlightLocation(
            airport=(
                arrival_raw.get("aeroport")
                or arrival_raw.get("airport")
                or arrival_raw.get("name")
                or "Agadir Al Massira"
            ),
            iata=(
                arrival_raw.get("iata")
                or arrival_raw.get("iataCode")
                or "AGA"
            ),
            scheduled=(
                arrival_raw.get("heure_prevue")
                or arrival_raw.get("scheduled")
                or arrival_raw.get("scheduledTime")
                or None
            ),
            revised=(
                arrival_raw.get("heure_estimee")
                or arrival_raw.get("revised")
                or arrival_raw.get("revisedTime")
                or None
            ),
        ),
    )
