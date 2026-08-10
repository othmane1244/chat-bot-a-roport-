"""
Client Groq — fallback rapide recommandé au §6 (latence quasi
instantanée, utile pour la voix en V2). API compatible format OpenAI
Chat Completions.

API REST : https://api.groq.com/openai/v1/chat/completions
Modèle : llama-3.3-70b-versatile (cf. §6 — Llama 3.3 70B / Qwen3)

⚠️ Même limite que gemini_client.py : api.groq.com n'est pas accessible
depuis ce sandbox. Testé avec une réponse mockée, pas un vrai appel.
"""

import requests

from app.config import settings

BASE_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama-3.3-70b-versatile"


class ConnectorNotConfiguredError(Exception):
    """Clé API manquante dans .env."""


class ConnectorAPIError(Exception):
    """L'API a répondu une erreur, ou une réponse dans un format inattendu."""


def generate(system_prompt: str, user_message: str, context: str = "") -> str:
    if not settings.groq_api_key:
        raise ConnectorNotConfiguredError(
            "GROQ_API_KEY manquante dans .env — voir .env.example"
        )

    user_content = f"{context}\n\nQuestion de l'utilisateur : {user_message}" if context else user_message

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        "temperature": 0.3,
        "max_tokens": 500,
    }
    headers = {"Authorization": f"Bearer {settings.groq_api_key}"}

    response = requests.post(BASE_URL, json=payload, headers=headers, timeout=15)

    if response.status_code != 200:
        raise ConnectorAPIError(f"Groq a répondu {response.status_code} : {response.text[:200]}")

    data = response.json()
    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError) as e:
        raise ConnectorAPIError(f"Réponse Groq dans un format inattendu : {data}") from e
