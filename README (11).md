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

- Le contenu de la réponse du `/chat` est encore **fixe** — le RAG
  (étape 2, ci-dessous) existe mais n'est pas encore branché sur
  l'endpoint, ça arrive à l'étape 4 (routeur d'intention).
- Pas de connexion aux vols/météo réels — étape 3.
- Pas de garde-fou de périmètre (refus des questions hors-sujet) —
  arrive avec le routeur d'intention, étape 3-4.
- La détection de langue est une heuristique grossière — suffisant
  pour développer le frontend en attendant.

---

## Étape 2/8 : RAG vectoriel (données fixes → Chroma)

### Ce qui a été ajouté

```
data/
├── services.json   # Restaurants/boutiques — structure du §20 du cahier des charges
├── parking.json    # Tarifs et zones de parking
└── faq.json        # Documents/douane/bagages/contacts

app/rag/
├── documents.py     # Transforme le JSON en documents texte indexables (testé isolément)
└── embeddings.py     # Abstraction du modèle d'embeddings (BGE-M3 + mode factice hors-ligne)

scripts/
└── ingest.py         # Charge data/*.json → calcule les embeddings → indexe dans Chroma
```

### ⚠️ Les données dans `data/*.json` sont des EXEMPLES

Tous les noms marqués `[EXEMPLE]` et les champs `"verifie": false` sont
des placeholders structurellement corrects, **pas de vraies informations
sur l'aéroport**. À remplacer par la collecte manuelle réelle décrite au
§5.1 du cahier des charges (visite sur place, site ONDA, etc.) avant
toute mise en production — sinon le chatbot donnerait de fausses infos
en toute confiance, exactement ce que le garde-fou du §11 doit éviter.

### ⚠️ Limite de test rencontrée dans CET environnement de développement

Le modèle recommandé au §7 (**BGE-M3**) télécharge ~2 Go de poids
depuis Hugging Face au premier lancement. Le sandbox où j'ai écrit et
testé ce code n'a **pas accès à huggingface.co** (accès réseau
restreint à une liste de domaines autorisés, orienté PyPI/npm/GitHub).

Résultat concret :
- `app/rag/embeddings.py` contient le vrai code de production
  (`BGEM3Embedder`), mais je n'ai **pas pu l'exécuter ici**.
- J'ai testé tout le reste (chunking JSON → texte, insertion Chroma,
  récupération par ID, filtrage par métadonnées, mécanique de
  recherche par similarité) avec `DummyHashEmbedder`, un embedder
  factice et déterministe qui ne fait aucune compréhension sémantique
  — il sert juste à prouver que la tuyauterie fonctionne.

**Ce que ça veut dire pour toi** : chez toi, en local, avec un accès
internet normal, lance simplement :
```bash
python scripts/ingest.py
```
(sans `--offline-test`) — `sentence-transformers` télécharger BGE-M3
automatiquement la première fois, puis le modèle sera mis en cache
localement pour les lancements suivants.

### Tester

```bash
pip install -r requirements.txt

# Test rapide de la mécanique, sans internet ni téléchargement de modèle :
python scripts/ingest.py --offline-test

# Vraie ingestion en production (nécessite internet la 1ère fois) :
python scripts/ingest.py
```

Vérifié dans ce sandbox : 14 documents construits à partir des 3 JSON
(5 services + 2 zones parking + 7 FAQ), insérés dans Chroma, et
récupérables par ID, par filtre de métadonnées, et par requête de
similarité.

## Prochaine étape (3/8)

Connecteurs API vols (AeroDataBox) + météo (OpenWeatherMap), avec cache
Redis — c'est ce qui permettra de répondre aux vraies questions de vol
en temps réel ("où en est mon vol RK860 ?").
