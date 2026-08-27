"""
Endpoint /chat — étape 5/8 : synthèse par LLM (Gemini + fallback Groq).

Historique :
- Étape 1 : squelette, réponse fixe.
- Étape 3 : connecteur AeroDataBox branché.
- Étape 4 : routeur d'intention (flight / documentary / out_of_scope).
- Étape 5 (ici) : la branche DOCUMENTARY utilise maintenant le LLM pour
  reformuler les chunks RAG en réponse naturelle, au lieu de renvoyer
  le texte brut. Le prompt système (§11) est appliqué à chaque appel.

CHOIX DE CONCEPTION : la branche FLIGHT_STATUS reste volontairement
TEMPLATE (pas de LLM) -- une heure de vol ou un numéro de porte ne
doivent jamais passer par une reformulation qui pourrait, même
rarement, altérer un chiffre. Le §11 dit "ne jamais halluciner sur les
horaires/tarifs/statuts" ; le moyen le plus sûr de ne jamais halluciner
un chiffre est de ne jamais le faire passer par un LLM. Le LLM est
utilisé uniquement là où il apporte de la valeur (reformulation d'un
texte informatif) et jamais là où il pourrait introduire un risque
(données chiffrées critiques).
"""

from fastapi import APIRouter

from app.connectors import flights
from app.connectors.flight_adapter import normalize_flight_data
from app.connectors.flights import ConnectorAPIError, ConnectorNotConfiguredError
from app.llm.orchestrator import AllProvidersFailedError, generate_reply
from app.routers import intent
from app.routers.rag_query import query_knowledge
from app.schemas import ChatRequest, ChatResponse

router = APIRouter(prefix="/chat", tags=["chat"])


def _detect_lang_heuristic(text: str) -> str:
    """Heuristique temporaire : arabe si caractères arabes détectés,
    sinon français par défaut (à remplacer par une vraie détection
    plus tard si besoin — Gemini gère déjà bien le routage linguistique
    en pratique, donc ce n'est pas critique)."""
    if any("\u0600" <= ch <= "\u06FF" for ch in text):
        return "ar"
    return "fr"


def _format_flight_reply(status: dict, lang: str) -> str:
    depart = status.get("depart", {})
    templates = {
        "fr": (
            f"Vol {status.get('numero_vol')} ({status.get('compagnie')}) : "
            f"statut {status.get('statut')}. "
            f"Départ prévu {depart.get('heure_prevue')}, porte {depart.get('porte') or 'non communiquée'}, "
            f"desk d'enregistrement {depart.get('desk_enregistrement') or 'non communiqué'}."
        ),
        "ar": (
            f"الرحلة {status.get('numero_vol')} ({status.get('compagnie')}): الحالة {status.get('statut')}. "
            f"موعد الإقلاع {depart.get('heure_prevue')}، البوابة {depart.get('porte') or 'غير محددة'}."
        ),
        "en": (
            f"Flight {status.get('numero_vol')} ({status.get('compagnie')}): status {status.get('statut')}. "
            f"Scheduled departure {depart.get('heure_prevue')}, gate {depart.get('porte') or 'not communicated'}."
        ),
    }
    return templates.get(lang, templates["fr"])


def _not_configured_reply(lang: str) -> str:
    return {
        "fr": "La recherche de vol en temps réel n'est pas encore configurée sur ce serveur (clé API manquante). Réessaie plus tard, ou contacte l'aéroport directement.",
        "ar": "بحث الرحلات في الوقت الفعلي غير مفعل بعد على هذا الخادم. حاول لاحقًا أو تواصل مباشرة مع المطار.",
        "en": "Real-time flight lookup isn't configured on this server yet (missing API key). Try again later, or contact the airport directly.",
    }.get(lang, "")


def _flight_not_found_reply(flight_number: str, lang: str) -> str:
    return {
        "fr": f"Je n'ai pas trouvé le vol {flight_number}. Vérifie le numéro, ou contacte l'aéroport directement.",
        "ar": f"لم أجد الرحلة {flight_number}. تحقق من الرقم أو تواصل مباشرة مع المطار.",
        "en": f"I couldn't find flight {flight_number}. Double-check the number, or contact the airport directly.",
    }.get(lang, "")


def _no_documentary_result_reply(lang: str) -> str:
    """Cas où la question est dans le périmètre mais rien de pertinent
    n'a été trouvé dans le RAG -- règle du §11 : ne JAMAIS inventer,
    dire clairement qu'on n'a pas l'info."""
    return {
        "fr": "Je n'ai pas cette information dans ma base pour le moment. Contacte directement l'aéroport pour être sûr.",
        "ar": "ليست لدي هذه المعلومة حاليًا. يرجى التواصل مباشرة مع المطار للتأكد.",
        "en": "I don't have that information right now. Please contact the airport directly to be sure.",
    }.get(lang, "")


def _build_rag_context(chunks: list[dict]) -> str:
    """Assemble les chunks retrouvés en un contexte texte pour le LLM,
    conforme au §11 : 'appuie-toi UNIQUEMENT sur le contexte fourni'."""
    lines = ["Contexte (extraits de la base de connaissances AGA) :"]
    for c in chunks:
        lines.append(f"- {c['text']}")
    return "\n".join(lines)


def _fallback_raw_reply(chunks: list[dict], lang: str) -> str:
    """Repli si Gemini ET Groq échouent tous les deux : on ne laisse
    jamais le voyageur sans réponse, on revient au texte brut de
    l'étape 4 plutôt que de planter."""
    prefixes = {
        "fr": "(Service de reformulation temporairement indisponible — extrait brut) ",
        "ar": "(خدمة إعادة الصياغة غير متوفرة مؤقتًا — نص خام) ",
        "en": "(Rephrasing service temporarily unavailable — raw excerpt) ",
    }
    return prefixes.get(lang, prefixes["fr"]) + chunks[0]["text"]


@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    lang = request.lang or _detect_lang_heuristic(request.message)
    detected_intent = intent.classify(request.message)

    if detected_intent == intent.Intent.FLIGHT_STATUS:
        flight_number = intent.extract_flight_number(request.message)
        try:
            raw_status = flights.get_flight_status(flight_number)
            flight_data = normalize_flight_data(raw_status)
            return ChatResponse(
                type="flight",
                reply=_format_flight_reply(raw_status, lang),
                lang=lang,
                flight=flight_data,
                sources=[f"AeroDataBox (vol {flight_number})"],
            )
        except ConnectorNotConfiguredError:
            return ChatResponse(type="text", reply=_not_configured_reply(lang), lang=lang, sources=[])
        except ConnectorAPIError:
            return ChatResponse(
                type="text", reply=_flight_not_found_reply(flight_number, lang), lang=lang, sources=[]
            )

    if detected_intent == intent.Intent.OUT_OF_SCOPE:
        return ChatResponse(type="text", reply=intent.out_of_scope_reply(lang), lang=lang, sources=[])

    # DOCUMENTARY
    chunks = query_knowledge(request.message, n_results=3)
    if not chunks:
        return ChatResponse(type="text", reply=_no_documentary_result_reply(lang), lang=lang, sources=[])

    sources = [c["metadata"].get("type", "inconnu") for c in chunks]
    context = _build_rag_context(chunks)

    try:
        reply_text, engine_used = generate_reply(request.message, context=context)
        return ChatResponse(type="text", reply=reply_text, lang=lang, sources=sources)
    except AllProvidersFailedError:
        return ChatResponse(
            type="text", reply=_fallback_raw_reply(chunks, lang), lang=lang, sources=sources
        )
