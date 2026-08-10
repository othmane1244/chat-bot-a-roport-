"""
Client Gemini 2.5 Flash — LLM principal recommandé au §6 (gratuit,
~1500 req/jour, contexte 1M tokens, bon support arabe).

API REST : https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent

⚠️ LIMITE DE TEST DANS CE SANDBOX : generativelanguage.googleapis.com
n'est pas dans la liste des domaines accessibles depuis cet
environnement (comme AeroDataBox et OpenWeatherMap avant lui). Code
écrit contre le format d'API REST standard de Gemini (bien établi et
stable), testé avec une réponse JSON mockée, PAS avec un vrai appel.
Toi seul peux le valider en vrai, avec ta clé, en local.
"""

import requests

from app.config import settings

BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"


class ConnectorNotConfiguredError(Exception):
    """Clé API manquante dans .env."""


class ConnectorAPIError(Exception):
    """L'API a répondu une erreur, ou une réponse dans un format inattendu."""


def generate(system_prompt: str, user_message: str, context: str = "") -> str:
    """Envoie system_prompt + contexte RAG + question au modèle, renvoie
    le texte de la réponse générée."""
    if not settings.gemini_api_key:
        raise ConnectorNotConfiguredError(
            "GEMINI_API_KEY manquante dans .env — voir .env.example"
        )

    user_content = f"{context}\n\nQuestion de l'utilisateur : {user_message}" if context else user_message

    payload = {
        "system_instruction": {"parts": [{"text": system_prompt}]},
        "contents": [{"role": "user", "parts": [{"text": user_content}]}],
        "generationConfig": {"temperature": 0.3, "maxOutputTokens": 500},
    }

    response = requests.post(
        f"{BASE_URL}?key={settings.gemini_api_key}", json=payload, timeout=15
    )

    if response.status_code != 200:
        raise ConnectorAPIError(f"Gemini a répondu {response.status_code} : {response.text[:200]}")

    data = response.json()
    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError) as e:
        raise ConnectorAPIError(f"Réponse Gemini dans un format inattendu : {data}") from e
