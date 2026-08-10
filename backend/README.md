# AGA Airport Assistant — Backend (Étape 1/8 : squelette)

## Où on en est

Cette étape correspond au point (1) du §12 du cahier des charges :
> « squelette backend + un seul endpoint de test »

Ce backend ne fait **volontairement pas encore** de RAG, de LLM, ni de
connexion aux API de vols/météo. Le but est uniquement de valider que
le circuit **requête → validation → réponse structurée** fonctionne
de bout en bout, avant d'ajouter la moindre intelligence.

## Structure du projet

```
backend/
├── app/
│   ├── main.py          # Point d'entrée : crée l'app, branche CORS + routers
│   ├── config.py         # Toutes les variables d'environnement du projet, centralisées
│   ├── schemas.py         # Contrat de données entre frontend et backend (Pydantic)
│   └── routers/
│       └── chat.py        # Endpoint POST /chat (logique métier de cet endpoint)
├── requirements.txt
├── .env.example           # À copier en .env, à remplir au fur et à mesure des étapes
└── README.md
```

**Pourquoi cette organisation ?** Chaque fichier a une seule responsabilité :
- `main.py` = assemblage uniquement (jamais de logique métier dedans)
- `schemas.py` = le contrat/API, séparé de l'implémentation
- `routers/` = un fichier par domaine fonctionnel (chat, puis plus tard
  peut-être `flights.py`, `services.py`...) — ça évite d'avoir un seul
  fichier de 2000 lignes à l'étape 8.

## Installation et lancement

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env          # rien à remplir pour l'instant, c'est pour plus tard
uvicorn app.main:app --reload
```

Le serveur démarre sur `http://127.0.0.1:8000`.

## Corrections de validation déjà intégrées

Deux ajustements ont été appliqués pendant les tests pour rendre le backend
plus robuste sur Windows et quel que soit le dossier de lancement :

- `app/config.py` contient maintenant `rag_offline_test_mode`, utilisé par
  la branche RAG/test quand l'embedder offline est requis.
- Les chemins `.env` et `chroma_data` sont résolus à partir de l'emplacement
  de `app/config.py`, pas du répertoire courant, ce qui évite les échecs si
  `uvicorn` est lancé depuis la racine du workspace plutôt que depuis `backend/`.

## Tester

**Documentation interactive** (générée automatiquement par FastAPI) :
ouvre `http://127.0.0.1:8000/docs` dans un navigateur — tu peux y
tester les endpoints directement, sans écrire de curl.

**En ligne de commande** :
```bash
curl http://127.0.0.1:8000/health

curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Bonjour, où est mon vol RK860 ?"}'
```

Réponse attendue (exemple) :
```json
{
  "reply": "Bonjour ! Je suis l'assistant de l'aéroport Agadir Al Massira (version squelette en cours de construction). Ton message a bien été reçu.",
  "lang": "fr",
  "sources": []
}
```

✅ Testé et validé : `/health`, `/chat` en français, et `/chat` avec
détection automatique de l'arabe fonctionnent tous les trois.

## Ce qui n'est PAS encore fait (normal à ce stade)

- Le contenu de la réponse est **fixe** (pas de vraie réflexion) —
  arrive à l'étape 4-5.
- Pas de connexion aux vols/météo réels — étape 3.
- Pas de garde-fou de périmètre (refus des questions hors-sujet) —
  arrive avec le routeur d'intention, étape 3-4.
- La détection de langue est une heuristique grossière (arabe vs
  français par défaut) — suffisant pour développer le frontend en
  attendant, sera affiné plus tard si besoin.

## Prochaine étape (2/8)

Ingestion des données fixes : créer `services.json`, `parking.json`,
`faq.json` et le script qui les charge dans Chroma (recherche
vectorielle) — c'est ce qui permettra de répondre à des vraies
questions documentaires.
