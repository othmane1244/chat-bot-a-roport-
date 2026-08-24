"""
Requête RAG — interroge la collection Chroma 'aga_knowledge' (contenu
voyageur, cf. étape 2) pour trouver les chunks les plus pertinents.

Séparé de app/rag/ (qui s'occupe de l'INGESTION) parce que la requête a
un cycle de vie différent : appelée à chaque message utilisateur, pas
juste au moment d'indexer les données.
"""

from typing import Optional

import chromadb

from app.config import settings
from app.rag.embeddings import get_embedder

COLLECTION_NAME = "aga_documents"


def query_knowledge(
    query_text: str, n_results: int = 3, offline_test_mode: Optional[bool] = None
) -> list[dict]:
    """Renvoie les n_results chunks les plus proches sémantiquement de
    query_text, sous la forme [{"text":..., "metadata":...}, ...].
    Renvoie une liste vide si la collection n'existe pas encore ou est
    vide (ex: ingest.py pas encore lancé) — le futur code appelant doit
    gérer ce cas selon la règle du §11 (ne jamais inventer une réponse)."""
    if offline_test_mode is None:
        offline_test_mode = settings.rag_offline_test_mode

    client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
    collection = client.get_or_create_collection(COLLECTION_NAME)
    if collection.count() == 0:
        return []

    embedder = get_embedder(offline_test_mode=offline_test_mode)
    query_vector = embedder.embed([query_text])
    results = collection.query(query_embeddings=query_vector, n_results=n_results)

    docs = results.get("documents") or [[]]
    metas = results.get("metadatas") or [[]]
    return [{"text": d, "metadata": m} for d, m in zip(docs[0], metas[0])]
