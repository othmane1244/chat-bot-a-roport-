"""
Script d'ingestion : JSON --> embeddings --> Chroma (base vectorielle).

Usage :
    python scripts/ingest.py                  # production (BGE-M3, nécessite internet la 1ère fois)
    python scripts/ingest.py --offline-test    # test de la mécanique, sans internet ni vrai modèle

Ce script est volontairement idempotent : on utilise `upsert` (pas `add`),
donc le relancer après avoir modifié un JSON met juste à jour les documents
concernés, sans dupliquer.
"""

import argparse
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_ROOT))

import chromadb  # noqa: E402

from app.config import settings  # noqa: E402
from app.rag.documents import build_all_documents  # noqa: E402
from app.rag.embeddings import get_embedder  # noqa: E402

DATA_DIR = BACKEND_ROOT / "data"


def main(offline_test_mode: bool = False) -> None:
    print(f"Lecture des fichiers JSON depuis {DATA_DIR}...")
    docs = build_all_documents(DATA_DIR)
    print(f"-> {len(docs)} documents construits.")

    if offline_test_mode:
        print("Mode --offline-test : embedder factice (PAS de recherche sémantique réelle).")
    embedder = get_embedder(offline_test_mode=offline_test_mode)

    texts = [d["text"] for d in docs]
    print("Calcul des embeddings...")
    vectors = embedder.embed(texts)

    print(f"Connexion à Chroma (dossier persistant : {settings.chroma_persist_dir})...")
    client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
    collection = client.get_or_create_collection("aga_knowledge")

    collection.upsert(
        ids=[d["id"] for d in docs],
        embeddings=vectors,
        documents=texts,
        metadatas=[d["metadata"] for d in docs],
    )

    print(f"-> {len(docs)} documents indexés dans la collection 'aga_knowledge'.")
    print(f"-> Total actuel dans la collection : {collection.count()} documents.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--offline-test",
        action="store_true",
        help="Utilise un embedder factice au lieu de BGE-M3 (pas besoin d'internet ni de téléchargement de modèle).",
    )
    args = parser.parse_args()
    main(offline_test_mode=args.offline_test)
