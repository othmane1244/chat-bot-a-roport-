"""
Orchestrateur LLM — essaie Gemini (principal, §6), bascule automatique
sur Groq si Gemini échoue (non configuré, quota, panne...).

Pourquoi séparé des clients : ni chat.py ni les clients individuels ne
devraient savoir "qui est le principal / qui est le fallback" — cette
décision vit à un seul endroit, modifiable sans toucher au reste.
"""

from app.llm import gemini_client, groq_client
from app.llm.prompt import SYSTEM_PROMPT


class AllProvidersFailedError(Exception):
    """Ni Gemini ni Groq n'ont pu répondre."""


def generate_reply(user_message: str, context: str = "") -> tuple[str, str]:
    """Renvoie (texte_généré, moteur_utilisé). moteur_utilisé vaut
    'gemini' ou 'groq', utile pour le debug/logs (pas affiché à
    l'utilisateur)."""
    errors = []

    try:
        text = gemini_client.generate(SYSTEM_PROMPT, user_message, context)
        return text, "gemini"
    except (gemini_client.ConnectorNotConfiguredError, gemini_client.ConnectorAPIError) as e:
        errors.append(f"Gemini: {e}")

    try:
        text = groq_client.generate(SYSTEM_PROMPT, user_message, context)
        return text, "groq"
    except (groq_client.ConnectorNotConfiguredError, groq_client.ConnectorAPIError) as e:
        errors.append(f"Groq: {e}")

    raise AllProvidersFailedError(" | ".join(errors))
