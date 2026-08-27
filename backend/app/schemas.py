"""
Schémas de données (Pydantic) pour l'endpoint /chat.

Pourquoi ce fichier existe :
FastAPI utilise ces classes pour DEUX choses automatiquement :
1. Valider ce que le frontend envoie (si un champ obligatoire manque,
   ou si le type est faux, FastAPI renvoie une erreur 422 claire
   AVANT même que notre code ne s'exécute — pas de bug silencieux).
2. Générer la documentation interactive (/docs) toute seule.

C'est le contrat entre le frontend (React) et le backend : tant que ce
contrat ne change pas, les deux équipes peuvent avancer indépendamment.
"""

from typing import Literal, Optional
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="Message de l'utilisateur")
    # Laissé optionnel : à l'étape suivante on pourra détecter la langue
    # automatiquement si le frontend ne la fournit pas encore.
    lang: Optional[Literal["ar", "fr", "en"]] = Field(
        default=None, description="Langue détectée côté frontend, si connue"
    )
    session_id: Optional[str] = Field(
        default=None, description="Identifiant de session (utile pour la mémoire multi-tour, V3)"
    )


class ChatResponse(BaseModel):
    reply: str
    lang: str
    type: str = "text"
    flight: Optional[dict] = None
    sources: list[str] = []

