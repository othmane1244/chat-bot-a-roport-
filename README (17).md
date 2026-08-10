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

---

## Extension : ingestion de PDF (lois, règlements, guides)

### Ce qui a été ajouté

```
app/rag/pdf_loader.py     # Extraction + chunking de PDF
scripts/ingest_pdfs.py     # Indexe data/pdfs/*.pdf dans une collection Chroma séparée
```

### Comment ça marche

1. **Extraction** (`pypdf`) : texte brut de toutes les pages
2. **Chunking par article** : si le texte contient des titres du type
   `Article 9 : ...`, chaque article devient un chunk autonome —
   c'est la meilleure stratégie pour un texte juridique/réglementaire,
   qui a déjà cette structure naturelle. Sinon, repli automatique sur
   un découpage générique par taille fixe avec chevauchement.
3. **Embedding + indexation** : identique à l'étape 2 (même interface
   `get_embedder()`), mais dans une collection **`aga_documents`**,
   séparée de **`aga_knowledge`** (contenu voyageur).

### ⚠️ Pourquoi une collection séparée — le point de périmètre

Testé avec un vrai PDF fourni (une loi marocaine sur le contrôle
financier de l'État sur les entreprises publiques, dont ONDA fait
partie) : extraction et découpage fonctionnent bien (24 articles
correctement isolés, un par chunk).

**Mais ce type de contenu ne concerne pas un voyageur.** C'est de la
gouvernance interne d'ONDA (budgets, contrôleur d'État, comités
d'audit...), pas des infos de vol/douane/bagages. Si on l'indexait
dans la même collection que le contenu voyageur (`aga_knowledge`), le
garde-fou de périmètre du §11 pourrait se faire déjouer si un chunk de
ce PDF remonte par erreur dans une recherche liée à une question
voyageur.

D'où le choix : une collection à part (`aga_documents`), avec un champ
`metadata["audience"]` à qualifier manuellement pour chaque PDF ajouté
(ex: `"interne_gouvernance"`, ou `"voyageur_douane"` si tu ajoutes un
jour un vrai texte de la douane marocaine, qui lui concernerait bien
les voyageurs). Le routeur d'intention (étape 4) s'appuiera sur ce tag
pour savoir quand aller chercher dedans — pas par défaut sur toutes
les questions.

**En pratique** : dépose tes PDF dans `data/pdfs/`, lance
`python scripts/ingest_pdfs.py`, puis va corriger le tag `audience`
de chaque document selon son vrai usage. Des PDF *pertinents* pour un
voyageur (ex: règles IATA sur les bagages, texte officiel douane.gov.ma)
auraient toute leur place taggés côté voyageur.

### Tester

```bash
pip install -r requirements.txt

# Ingestion de tous les PDF dans data/pdfs/ :
python scripts/ingest_pdfs.py --offline-test   # test sans internet
python scripts/ingest_pdfs.py                   # production (BGE-M3)

# Ou un seul fichier ailleurs sur le disque :
python scripts/ingest_pdfs.py --offline-test chemin/vers/fichier.pdf
```

---

## Étape 3/8 : connecteurs API live (vols + météo) + cache

### Ce qui a été ajouté

```
app/connectors/
├── cache.py       # Cache TTL : Redis en prod, repli mémoire si indisponible
├── flights.py      # Connecteur AeroDataBox — statut de vol par numéro
└── weather.py       # Connecteur OpenWeatherMap — météo par ville

tests/
├── test_flights_mock.py   # Tests avec réponse AeroDataBox mockée
└── test_weather_mock.py    # Tests avec réponse OpenWeatherMap mockée
```

`app/routers/chat.py` détecte maintenant un numéro de vol dans le
message (regex simple, ex: "RK860") et appelle `flights.py` si trouvé —
sinon repli sur la réponse générique de l'étape 1. Ce n'est PAS encore
le vrai routeur d'intention (§12) — juste de quoi prouver que le
connecteur fonctionne bout en bout depuis /chat.

### ⚠️ Limite de test rencontrée dans CET environnement

Ni `rapidapi.com`/`aerodatabox.p.rapidapi.com`, ni
`api.openweathermap.org` ne sont accessibles depuis ce sandbox (accès
réseau restreint à une liste de domaines, orientée PyPI/npm/GitHub).
**Impossible d'appeler les vraies API ici, avec ou sans clé.**

Ce que j'ai fait à la place :
1. Recherche web pour confirmer le schéma exact des réponses
   AeroDataBox (`checkInDesk`, `gate`, `terminal`, `baggageBelt`,
   `scheduledTime`...) plutôt que de deviner.
2. Écriture des connecteurs contre ce schéma documenté.
3. Tests avec des réponses JSON d'exemple **mockées** (`unittest.mock`),
   pas de vrais appels réseau — voir `tests/`.
4. Branchement bout en bout sur `/chat` testé avec une clé factice
   (`FastAPI TestClient` + mock) : détection du numéro de vol → appel
   connecteur → réponse formatée. Fonctionne.

**Un vrai bug a été trouvé et corrigé pendant ces tests** : le cache
mémoire (`InMemoryCache`) était recréé vide à chaque appel de
`get_cache()` au lieu d'être un singleton — donc il ne servait jamais
à rien (chaque appel refaisait un appel réseau). Corrigé (voir
`cache.py`), reconfirmé par les tests.

**Ce que ça veut dire pour toi** :
1. Crée un compte gratuit sur RapidAPI, puis abonne-toi à AeroDataBox
   (offre gratuite : 600 unités/mois) → récupère ta clé `X-RapidAPI-Key`.
2. Crée un compte gratuit sur OpenWeatherMap → récupère ta clé.
3. Mets ces deux clés dans ton `.env` local (`AERODATABOX_API_KEY=...`,
   `OPENWEATHERMAP_API_KEY=...`).
4. Lance le serveur et teste avec un VRAI numéro de vol AGA (regarde
   le panneau des départs, ou le site ONDA) — vérifie que le format de
   réponse correspond à ce que `flights.py` attend. La couverture
   AeroDataBox est parfois partielle sur les aéroports régionaux
   (cf. §16 du cahier des charges) — si le format diffère pour AGA,
   ajuste `parse_flight_status()` en conséquence.

### Tester (sans clé, avec mocks)

```bash
pip install -r requirements.txt
python tests/test_flights_mock.py
python tests/test_weather_mock.py
```

## Prochaine étape (4/8)

Le vrai routeur d'intention (temps réel / RAG documentaire / graphe /
hors-sujet) — c'est là que le garde-fou de périmètre du §11 sera
vraiment implémenté, et que RAG (étape 2) + connecteurs (étape 3) +
LLM (étape 5) seront orchestrés ensemble intelligemment.

---

## Étape 4/8 : routeur d'intention + garde-fou de périmètre

### Ce qui a été ajouté

```
app/routers/
├── chat.py         # Endpoint POST /chat
├── intent.py       # Classification : FLIGHT_STATUS / DOCUMENTARY / OUT_OF_SCOPE
└── rag_query.py      # Interroge la collection Chroma 'aga_knowledge' (étape 2)
```

> **Note de structure** (ajoutée après coup) : `intent.py` et
> `rag_query.py` vivaient à l'origine dans un dossier `app/router/`
> (singulier) séparé de `app/routers/` (pluriel, qui contenait déjà
> `chat.py`) — un choix de nommage à moi qui prêtait à confusion,
> repéré en pratique lors de l'installation locale (deux dossiers au
> nom presque identique, facile de perdre le fil en copiant les
> fichiers à la main). Tout vit maintenant dans `app/routers/` (un seul
> dossier, pluriel).

`/chat` fait maintenant un vrai routage à 3 branches, dans cet ordre :
1. **Numéro de vol détecté** → connecteur AeroDataBox (étape 3)
2. **Hors périmètre** → refus poli, garde-fou du §11 **enfin implémenté en code**
3. **Sinon** → recherche RAG dans `aga_knowledge` (étape 2)

### ⚠️ Limite assumée : classification par mots-clés, pas par LLM

Sans LLM branché (étape 5), on ne peut pas juger le SENS d'une phrase
— seulement la présence de mots-clés (`IN_SCOPE_KEYWORDS` dans
`intent.py`). **Testé et confirmé** : le message *"Le bus de mon
quartier est en retard, c'est chiant"* — clairement hors-sujet — est
classé à tort "dans le périmètre" à cause du mot "bus". C'est une
limite connue et attendue de cette version, pas un bug à corriger
maintenant : l'étape 5 (LLM) réglera ça en jugeant l'intention
sémantiquement plutôt que par mot-clé.

**En attendant**, le filtre reste un vrai filet de sécurité utile :
testé aussi sur *"Quelle est la capitale de la France ?"* et *"What's
the weather in Paris?"* → correctement refusés dans les deux langues.

### La réponse "documentary" est encore BRUTE

Le chunk RAG le plus proche est renvoyé tel quel (pas reformulé en
langage naturel) — avec un préfixe explicite dans la réponse pour ne
jamais laisser croire à une réponse plus aboutie qu'elle ne l'est. La
synthèse par LLM arrive à l'étape 5, qui remplacera ce texte brut par
une vraie réponse rédigée, tout en citant ces mêmes chunks comme
source (anti-hallucination, cf. §11).

### Tester

```bash
python scripts/ingest.py --offline-test   # (re)générer la base de test

python3 -c "
from fastapi.testclient import TestClient
from app.config import settings
from app.main import app
settings.rag_offline_test_mode = True   # cohérent avec l'ingestion ci-dessus
client = TestClient(app)
print(client.post('/chat', json={'message': 'Quelle est la capitale de la France ?'}).json())
print(client.post('/chat', json={'message': 'Le wifi est-il gratuit ?'}).json())
"
```

## Prochaine étape (5/8)

Intégration LLM (Gemini 2.5 Flash + fallback Groq) avec le prompt
système du §11 — c'est ce qui transformera les chunks RAG bruts en
vraies réponses rédigées, et améliorera nettement la fiabilité du
garde-fou de périmètre par rapport au filtre par mots-clés actuel.

---

## Étape 5/8 : intégration LLM (Gemini + fallback Groq)

### Ce qui a été ajouté

```
app/llm/
├── prompt.py         # Prompt système, repris tel quel du §11
├── gemini_client.py    # Client Gemini 2.5 Flash (LLM principal, §6)
├── groq_client.py       # Client Groq (fallback rapide, §6)
└── orchestrator.py       # Essaie Gemini, bascule automatique sur Groq si échec

tests/test_llm_mock.py   # 5 tests : Gemini seul, Groq seul, bascule, double échec
```

La branche **DOCUMENTARY** de `/chat` utilise maintenant le LLM pour
reformuler les chunks RAG en réponse naturelle (au lieu du texte brut
de l'étape 4), avec le prompt système du §11 appliqué systématiquement.

### Choix de conception : la branche vol reste 100% template, sans LLM

Volontaire, pas un oubli : une heure de vol ou un numéro de porte ne
doivent **jamais** passer par une reformulation qui pourrait, même
rarement, glisser sur un chiffre. Le §11 est explicite ("ne jamais
halluciner sur les horaires/tarifs/statuts") — le moyen le plus sûr de
ne jamais halluciner un chiffre est de ne jamais le faire passer par un
LLM. Le LLM n'intervient que là où il ajoute de la valeur (reformuler
un texte informatif), jamais sur une donnée chiffrée critique.

### ⚠️ Limite de test dans CET environnement

`generativelanguage.googleapis.com` et `api.groq.com` ne sont pas
accessibles depuis ce sandbox — même limite que pour AeroDataBox/
OpenWeatherMap/BGE-M3. Testé avec des réponses mockées, format d'API
REST standard et stable des deux fournisseurs.

**Bug de test (pas de prod) trouvé et corrigé en cours de route** :
`gemini_client.py` et `groq_client.py` font tous les deux `import
requests` puis `requests.post(...)` — ils pointent donc vers le MÊME
objet en mémoire. Patcher séparément
`app.llm.gemini_client.requests.post` et
`app.llm.groq_client.requests.post` dans un test revient à patcher deux
fois la même cible : le second écrase silencieusement le premier. Il a
fallu un seul mock qui distingue par URL (`generativelanguage` vs
`groq`) pour tester correctement le mécanisme de bascule — voir
`tests/test_llm_mock.py`.

**4 comportements testés bout en bout sur `/chat`** :
1. Gemini répond → réponse rédigée naturellement, sources listées.
2. Gemini ET Groq indisponibles → repli sur le texte brut (étape 4),
   **pas de crash**, l'utilisateur a toujours une réponse.
3. Garde-fou hors-périmètre toujours actif, non affecté par le LLM.
4. Vol toujours géré par template, jamais par le LLM (voir plus haut).

### Ce que ça veut dire pour toi

1. Mets ta clé Gemini dans `.env` (`GEMINI_API_KEY=...`) — tu l'as
   déjà. Une clé Groq gratuite (console.groq.com) en fallback est
   recommandée mais pas obligatoire.
2. Lance `python scripts/ingest.py` (vraie ingestion BGE-M3, pas
   `--offline-test`) pour avoir un RAG sémantiquement pertinent — avec
   l'embedder factice utilisé dans mes tests ici, le RAG retrouve des
   chunks non pertinents (ex: question sur le wifi → chunk parking
   retourné), normal, il n'a aucune compréhension du sens.
3. Lance le serveur et teste en vrai : `curl -X POST
   http://127.0.0.1:8000/chat -d '{"message": "le wifi est-il
   gratuit ?"}'`

## Prochaine étape (6/8)

Frontend chat basique (React + Tailwind), qui peut maintenant se
brancher sur un backend qui répond vraiment de façon utile et fiable.

---

## Corrections trouvées pendant l'installation locale (post-étape 5)

Ce qui suit n'est pas une nouvelle étape numérotée, mais le résultat de
la toute première installation complète du projet chez un utilisateur
réel (pas dans mon sandbox de développement) — donc la première fois
que le guide d'installation (`GUIDE_INSTALLATION.md`) a été suivi de
bout en bout par quelqu'un d'autre que moi. Deux vrais problèmes ont
été trouvés et corrigés :

### 1. Structure `app/router/` vs `app/routers/`

Nommage à moi qui prêtait à confusion (deux dossiers presque
identiques). Consolidé : tout vit maintenant dans `app/routers/`
(pluriel) — voir la note dans la section étape 4 ci-dessus.

### 2. Chemins relatifs fragiles dans `config.py`

`chroma_persist_dir = "./chroma_data"` et `env_file=".env"`
fonctionnaient uniquement si le serveur était lancé **exactement**
depuis le dossier `backend/`. Lancé d'ailleurs (ex: depuis la racine
du projet, ou un autre dossier), le serveur ne trouvait ni les vraies
clés API ni la base Chroma déjà indexée — d'où un 500 sur la branche
RAG en pratique, malgré une ingestion réussie juste avant.

**Corrigé** : `config.py` calcule maintenant `BASE_DIR` à partir de son
propre emplacement (`Path(__file__).resolve().parent.parent`) et
résout tous les chemins relatifs par rapport à `BASE_DIR`, peu importe
d'où la commande est lancée. Un `field_validator` Pydantic normalise
`chroma_persist_dir` en chemin absolu automatiquement.

**Testé** (relancé après correction) : ingestion, tests connecteurs,
tests LLM — tous passent. Vérifié aussi que `settings.chroma_persist_dir`
reste correct même en lançant Python depuis un dossier totalement
différent de `backend/`.

**Résultat concret chez l'utilisateur qui a fait ce test** : premier
appel LLM réel réussi, avec du vrai BGE-M3 (pas l'embedder factice de
mes tests) :

> Question : "le wifi est-il gratuit ?"
> Réponse : "Oui, un réseau Wi-Fi gratuit est généralement disponible
> à l'aéroport Agadir Al Massira. Vous pouvez rechercher un réseau du
> type 'ONDA_WIFI' ou 'Maroc_Aeroports_WIFI'..."

Et le garde-fou tient sur une question hors-sujet ("quelle est la
capitale de la France ?") → refus poli, comme attendu.

**Leçon retenue pour la suite du projet** : les fichiers livrés au fil
des étapes doivent bien remplacer les anciennes versions locales à
chaque fois qu'un fichier déjà existant est modifié (ex: `config.py`
a été modifié à l'étape 4 pour ajouter `rag_offline_test_mode`) — sinon
une désynchronisation peut passer inaperçue jusqu'à un bug en
apparence random plus tard.
