"""
Schémas de données (Pydantic) pour l'endpoint /chat.
Définit le contrat structuré entre le frontend React et le backend FastAPI.
"""

from typing import Literal, Optional, List
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="Message de l'utilisateur")
    lang: Optional[str] = Field(default="fr", description="Langue de communication")
    session_id: Optional[str] = Field(default=None, description="Identifiant de session")


# =========================
# FLIGHT MODELS
# =========================

class FlightLocation(BaseModel):
    airport: Optional[str] = None
    iata: Optional[str] = None
    scheduled: Optional[str] = None
    revised: Optional[str] = None


class FlightData(BaseModel):
    number: str
    airline: Optional[str] = None
    status: Optional[str] = None
    departure: Optional[FlightLocation] = None
    arrival: Optional[FlightLocation] = None


# =========================
# CHAT RESPONSE
# =========================

class ChatResponse(BaseModel):
    type: Literal["text", "flight", "error"] = "text"
    reply: str
    lang: str = "fr"
    sources: List[str] = []
    flight: Optional[FlightData] = None
