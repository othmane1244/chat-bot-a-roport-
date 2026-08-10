"""Tests des clients LLM (Gemini/Groq) et de l'orchestrateur, avec
réponses mockées -- generativelanguage.googleapis.com et api.groq.com
ne sont pas accessibles depuis ce sandbox (voir docstrings des clients).

Usage : python tests/test_llm_mock.py
"""
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import settings
from app.llm import gemini_client, groq_client, orchestrator

# --- Test 1 : Gemini seul, réponse correcte ---
print("--- Test 1 : gemini_client.generate() avec réponse mockée ---")
settings.gemini_api_key = "fake_gemini_key"

FAKE_GEMINI_RESPONSE = {
    "candidates": [{"content": {"parts": [{"text": "Le wifi est gratuit dans tout l'aéroport."}]}}]
}


def fake_post_gemini(url, json=None, timeout=None):
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = FAKE_GEMINI_RESPONSE
    return resp


with patch("app.llm.gemini_client.requests.post", side_effect=fake_post_gemini):
    text = gemini_client.generate("system prompt", "le wifi est gratuit ?", context="contexte RAG ici")
    assert text == "Le wifi est gratuit dans tout l'aéroport."
    print("OK :", text, "\n")

# --- Test 2 : Groq seul, réponse correcte ---
print("--- Test 2 : groq_client.generate() avec réponse mockée ---")
settings.groq_api_key = "fake_groq_key"

FAKE_GROQ_RESPONSE = {
    "choices": [{"message": {"content": "Oui, le wifi est gratuit."}}]
}


def fake_post_groq(url, json=None, headers=None, timeout=None):
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = FAKE_GROQ_RESPONSE
    return resp


with patch("app.llm.groq_client.requests.post", side_effect=fake_post_groq):
    text = groq_client.generate("system prompt", "le wifi est gratuit ?")
    assert text == "Oui, le wifi est gratuit."
    print("OK :", text, "\n")

# --- Test 3 : orchestrateur, Gemini répond -> pas d'appel à Groq ---
print("--- Test 3 : orchestrateur, Gemini OK -> Groq jamais appelé ---")
# IMPORTANT : gemini_client et groq_client font tous deux `import requests` puis
# `requests.post(...)` -> ils pointent vers le MÊME objet requests.post en mémoire.
# Patcher séparément 'app.llm.gemini_client.requests.post' et
# 'app.llm.groq_client.requests.post' revient à patcher deux fois LA MÊME cible :
# le second patch écrase silencieusement le premier. Un seul mock qui distingue
# par URL est nécessaire pour tester les deux clients dans le même test.


def fake_post_dispatch(url, json=None, headers=None, timeout=None):
    resp = MagicMock()
    resp.status_code = 200
    if "generativelanguage" in url:
        resp.json.return_value = FAKE_GEMINI_RESPONSE
    elif "groq" in url:
        resp.json.return_value = FAKE_GROQ_RESPONSE
    else:
        raise ValueError(f"URL inattendue dans le mock : {url}")
    return resp


with patch("requests.post", side_effect=fake_post_dispatch) as mock_post:
    text, engine = orchestrator.generate_reply("le wifi est gratuit ?", context="ctx")
    assert engine == "gemini"
    assert mock_post.call_count == 1  # un seul appel : Gemini a répondu du premier coup
    print(f"OK : réponse via {engine}, Groq jamais sollicité.\n")

# --- Test 4 : orchestrateur, Gemini échoue -> bascule automatique sur Groq ---
print("--- Test 4 : orchestrateur, Gemini en panne -> bascule sur Groq ---")


def fake_post_gemini_fails_groq_ok(url, json=None, headers=None, timeout=None):
    resp = MagicMock()
    if "generativelanguage" in url:
        resp.status_code = 503
        resp.text = "Service unavailable"
    elif "groq" in url:
        resp.status_code = 200
        resp.json.return_value = FAKE_GROQ_RESPONSE
    return resp


with patch("requests.post", side_effect=fake_post_gemini_fails_groq_ok) as mock_post:
    text, engine = orchestrator.generate_reply("le wifi est gratuit ?")
    assert engine == "groq"
    assert mock_post.call_count == 2  # Gemini tenté (échec), puis Groq (succès)
    print(f"OK : bascule automatique confirmée, réponse via {engine}.\n")

# --- Test 5 : les deux échouent -> exception claire ---
print("--- Test 5 : Gemini ET Groq indisponibles -> AllProvidersFailedError ---")
settings.gemini_api_key = ""
settings.groq_api_key = ""
try:
    orchestrator.generate_reply("le wifi est gratuit ?")
    print("ECHEC : aurait dû lever une exception")
    sys.exit(1)
except orchestrator.AllProvidersFailedError as e:
    print(f"OK : exception levée comme attendu -> {e}\n")

print("TOUS LES TESTS PASSENT.")
