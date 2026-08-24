"""
Script de test rapide : pose une question au RAG et affiche les résultats.
Teste directement la collection 'aga_documents' (celle remplie par batch_ingest_pdfs.py).
"""
import sys
from pathlib import Path

# Ajouter le backend au PYTHONPATH
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import chromadb
from app.config import settings
from app.rag.embeddings import get_embedder

COLLECTION_NAME = "aga_documents"

def test_query(question: str, n_results: int = 5):
    print(f"\n{'='*70}")
    print(f"Question : {question}")
    print(f"{'='*70}")

    client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
    collection = client.get_or_create_collection(COLLECTION_NAME)
    total = collection.count()
    print(f"Collection '{COLLECTION_NAME}' : {total} chunks indexés\n")

    if total == 0:
        print("❌ Collection vide ! Lance d'abord batch_ingest_pdfs.py")
        return

    embedder = get_embedder(offline_test_mode=False)
    query_vector = embedder.embed([question])
    results = collection.query(query_embeddings=query_vector, n_results=n_results)

    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    for i, (doc, meta, dist) in enumerate(zip(docs, metas, distances), 1):
        source = meta.get("source_file", "?")
        chunk_type = meta.get("type", "?")
        print(f"--- Résultat {i} (distance={dist:.4f}, type={chunk_type}) ---")
        print(f"  Source : {source}")
        print(f"  Texte  : {doc[:300]}...")
        print()


if __name__ == "__main__":
    questions = [
        "Quels sont les horaires de l'aéroport Agadir ?",
        "Comment obtenir un visa pour le Maroc ?",
        "Quels sont les services CIP disponibles ?",
        "ما هي ساعات عمل المطار؟",
    ]

    for q in questions:
        test_query(q)
