"""
Routeur d'intention — étape 4/8.

Ce module implémente pour de vrai le garde-fou de périmètre décrit au
§11 du cahier des charges : "tu réponds UNIQUEMENT à des questions
concernant l'aéroport Agadir Al Massira [...] Si la question sort de
ce périmètre [...], réponds poliment que tu es spécialisé..."

⚠️ LIMITE ASSUMÉE : sans LLM branché (étape 5), on ne peut PAS juger le
sens d'une phrase — seulement la présence de mots-clés. C'est un filtre
imparfait :
- Faux négatif possible : une vraie question sur l'aéroport formulée
  sans aucun des mots-clés listés sera classée à tort "hors-sujet".
- Faux positif possible : une question hors-sujet qui contient par
  hasard un mot-clé ("le bus de mon quartier est en retard") sera
  classée à tort "dans le périmètre".
Ce n'est PAS un défaut de conception à corriger ici — c'est la limite
inhérente au tout premier filtre par mots-clés, en attendant l'étape 5
où le LLM pourra juger l'intention sémantiquement, bien plus fiable.
Cette version sert de filet de sécurité minimal fonctionnel, pas de
solution définitive.
"""

import re
from enum import Enum
from typing import Optional

FLIGHT_NUMBER_PATTERN = re.compile(r"\b([A-Z]{2,3}\d{2,4})\b")

# Mots-clés indiquant que la question concerne le périmètre de
# l'aéroport (§11). Liste non exhaustive, à enrichir au fil de l'usage
# réel (ex: en observant les questions mal classées).
IN_SCOPE_KEYWORDS = [
    # Français
    "vol", "aéroport", "aeroport", "bagage", "bagages", "valise", "douane",
    "wifi", "wi-fi", "parking", "restaurant", "café", "boutique", "porte",
    "embarquement", "passeport", "visa", "taxi", "bus", "navette", "terminal",
    "arrivée", "arrivee", "départ", "depart", "check-in", "enregistrement",
    "correspondance", "onda", "agadir", "aga", "duty free", "duty-free",
    "cip", "salon", "salons", "service", "services", "tarif", "tarifs",
    "horaire", "horaires", "contact", "fret", "accès", "acces", "marché", "marches",
    # Anglais
    "flight", "airport", "luggage", "baggage", "customs", "gate", "boarding",
    "passport", "shuttle", "lounge", "lounges", "fee", "fees", "schedule", "schedules",
    # Arabe (formes courantes)
    "طيران", "رحلة", "مطار", "حقيبة", "أمتعة", "جمارك", "بوابة", "جواز",
    "تأشيرة", "حافلة", "أكادير", "صالون", "خدمة", "خدمات", "موقف", "أسعار",
]


class Intent(str, Enum):
    FLIGHT_STATUS = "flight_status"   # numéro de vol détecté -> connecteur AeroDataBox
    DOCUMENTARY = "documentary"        # question dans le périmètre -> RAG vectoriel
    OUT_OF_SCOPE = "out_of_scope"      # hors périmètre -> refus poli (§11)


def extract_flight_number(text: str) -> Optional[str]:
    match = FLIGHT_NUMBER_PATTERN.search(text.upper())
    return match.group(1) if match else None


def classify(text: str) -> Intent:
    """Classifie l'intention d'un message. Ordre de priorité :
    1. Numéro de vol détecté -> FLIGHT_STATUS (le plus fiable des 3 signaux)
    2. Mot-clé du périmètre trouvé -> DOCUMENTARY
    3. Sinon -> OUT_OF_SCOPE (mieux vaut refuser par prudence qu'inventer,
       cohérent avec la règle de fiabilité absolue du §11)."""
    if extract_flight_number(text):
        return Intent.FLIGHT_STATUS

    lowered = text.lower()
    if any(keyword in lowered for keyword in IN_SCOPE_KEYWORDS):
        return Intent.DOCUMENTARY

    return Intent.OUT_OF_SCOPE


OUT_OF_SCOPE_REPLIES = {
    "fr": "Je suis spécialisé sur l'aéroport Agadir Al Massira (vols, services, formalités de voyage). Peux-tu reformuler ta question dans ce cadre ?",
    "ar": "أنا متخصص فقط في مطار أكادير المسيرة (الرحلات، الخدمات، إجراءات السفر). هل يمكنك إعادة صياغة سؤالك في هذا الإطار؟",
    "en": "I'm specialized in the Agadir Al Massira airport (flights, services, travel formalities). Could you rephrase your question within that scope?",
}


def out_of_scope_reply(lang: str) -> str:
    return OUT_OF_SCOPE_REPLIES.get(lang, OUT_OF_SCOPE_REPLIES["fr"])
