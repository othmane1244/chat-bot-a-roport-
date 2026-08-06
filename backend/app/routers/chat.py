"""
Endpoint /chat — version squelette (étape 1/8).

Ce que fait CE fichier aujourd'hui :
- Il reçoit un message, détecte grossièrement la langue si elle n'est
  pas fournie, et renvoie une réponse fixe pour prouver que le circuit
  frontend -> backend -> réponse fonctionne.

Ce que ce fichier NE fait PAS encore (volontairement) :
- Pas de routeur d'intention (temps réel / RAG / graphe / hors-sujet)
  -> arrivera à l'étape 3 (connecteurs API) et 4 (RAG hybride).
- Pas d'appel à un LLM -> arrivera à l'étape 5.
- Pas de vraie détection de langue -> on utilise une heuristique très
  simple ici, juste pour ne pas bloquer le développement du frontend
  qui a besoin d'un champ `lang` dans la réponse dès maintenant.

L'idée : le frontend peut être développé et testé dès maintenant contre
CET endpoint, sans attendre que le RAG/LLM soit prêt.
"""

from fastapi import APIRouter
from backend.app.schemas import ChatRequest, ChatResponse

router = APIRouter(prefix="/chat", tags=["chat"])


def _detect_lang_heuristic(text: str) -> str:
    """Heuristique temporaire : arabe si caractères arabes détectés,
    sinon français par défaut (à remplacer par une vraie détection
    plus tard si besoin — Gemini gère déjà bien le routage linguistique
    en pratique, donc ce n'est pas critique)."""
    if any("\u0600" <= ch <= "\u06FF" for ch in text):
        return "ar"
    return "fr"


@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    lang = request.lang or _detect_lang_heuristic(request.message)

    placeholder_replies = {
        "ar": "مرحبا! أنا مساعد مطار أكادير المسيرة (نسخة تجريبية قيد التطوير). سؤالك تم استلامه.",
        "fr": "Bonjour ! Je suis l'assistant de l'aéroport Agadir Al Massira (version squelette en cours de construction). Ton message a bien été reçu.",
        "en": "Hello! I'm the Agadir Al Massira airport assistant (skeleton version, work in progress). Your message was received.",
    }

    return ChatResponse(
        reply=placeholder_replies.get(lang, placeholder_replies["fr"]),
        lang=lang,
        sources=[],
    )
