"""
Ingestion PDF EN LOT avec déduplication — conçu pour un grand nombre
de fichiers (des dizaines à des centaines), typiquement un export de
site web où le menu/navigation se répète sur chaque page.

Différence avec scripts/ingest_pdfs.py (l'original) :
- ingest_pdfs.py traite chaque PDF indépendamment — correct pour quelques
  fichiers isolés, mais gaspille énormément d'espace d'index si le même
  menu de navigation apparaît identique dans 100+ fichiers.
- Ce script déduplique D'ABORD le texte de navigation répété À TRAVERS
  tout le lot, PUIS découpe et indexe. Voir app/rag/dedup.py pour le
  détail de la méthode.

Nouveauté : intégration Mistral OCR automatique pour les PDF image/scan.
Si MISTRAL_API_KEY est configurée dans .env, les PDF dont le texte est
insuffisant (< 100 chars/page en moyenne) sont envoyés à Mistral OCR
avant la déduplication et le chunking.

Usage :
    python scripts/batch_ingest_pdfs.py --audience voyageur           # tout data/pdfs/
    python scripts/batch_ingest_pdfs.py --audience voyageur --offline-test
    python scripts/batch_ingest_pdfs.py --audience voyageur --dry-run  # rapport SANS indexer
    python scripts/batch_ingest_pdfs.py --audience voyageur chemin/vers/sous-dossier/*.pdf
"""

import argparse
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BACKEND_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_ROOT))

import chromadb  # noqa: E402

from app.config import settings  # noqa: E402
from app.rag.dedup import deduplicate_batch  # noqa: E402
from app.rag.embeddings import get_embedder  # noqa: E402
from app.rag.pdf_loader import (  # noqa: E402
    chunk_by_article,
    chunk_generic,
    extract_tables_from_pdf,
    extract_text_auto,
    _table_rows_to_texts,
)

PDF_DIR = BACKEND_ROOT / "data" / "pdfs"
COLLECTION_NAME = "aga_documents"


def slugify(name: str) -> str:
    return "".join(c if c.isalnum() else "_" for c in name.lower()).strip("_")


def build_documents_from_cleaned_text(
    text: str, doc_id_prefix: str, base_metadata: dict
) -> list[dict]:
    """Découpe un texte déjà nettoyé (dédupliqué) en chunks indexables.

    Même logique que pdf_to_documents() : articles → générique.
    Séparé car ici le texte provient de la dédup (pas directement du PDF).
    """
    docs = []
    article_chunks = chunk_by_article(text)
    if article_chunks:
        for i, chunk in enumerate(article_chunks):
            docs.append({
                "id": f"{doc_id_prefix}_art_{i:03d}",
                "text": chunk["text"],
                "metadata": {**base_metadata, "heading": chunk["heading"], "content_kind": "text"},
            })
    else:
        for i, chunk_text in enumerate(chunk_generic(text)):
            if chunk_text.strip():
                docs.append({
                    "id": f"{doc_id_prefix}_chunk_{i:03d}",
                    "text": chunk_text,
                    "metadata": {**base_metadata, "heading": "", "content_kind": "text"},
                })
    return docs


def main(
    pdf_paths: list[Path],
    offline_test_mode: bool,
    audience: str,
    dry_run: bool,
) -> None:
    if not pdf_paths:
        print("Aucun PDF à traiter.")
        return

    mistral_api_key = settings.mistral_api_key if not offline_test_mode else ""
    if mistral_api_key:
        print(f"✅ Mistral OCR activé (clé configurée) — les PDF image/scan seront traités.")
    else:
        print(f"⚠️  Mistral OCR désactivé (mode offline-test ou clé manquante) — PDF image/scan ignorés.")

    # --- Étape 1 : Extraction du texte brut (+ OCR si nécessaire) ---
    print(f"\n=== 1. Extraction du texte brut de {len(pdf_paths)} PDF ===")
    texts_by_file: dict[str, str] = {}
    tables_by_file: dict[str, list] = {}

    for path in pdf_paths:
        print(f"  Extraction : {path.name}", flush=True)
        texts_by_file[path.name] = extract_text_auto(path, mistral_api_key=mistral_api_key)
        tables_by_file[path.name] = extract_tables_from_pdf(path)

    total_tables = sum(len(t) for t in tables_by_file.values())
    print(f"-> {total_tables} tableau(x) détecté(s) au total (traités séparément, non affectés par la dédup)")

    # --- Étape 2 : Déduplication inter-fichiers ---
    print(f"\n=== 2. Déduplication du texte narratif à travers les {len(pdf_paths)} fichiers ===")
    cleaned_texts, removed_report = deduplicate_batch(texts_by_file)
    lines_before = sum(len(t.split("\n")) for t in texts_by_file.values())
    lines_after = sum(len(t.split("\n")) for t in cleaned_texts.values())
    lines_removed = sum(len(v) for v in removed_report.values())
    pct = 100 * lines_removed // max(lines_before, 1)
    print(f"-> {lines_before} lignes avant, {lines_after} après ({lines_removed} retirées, {pct}% de bruit/boilerplate)")

    # --- Étape 3 : Découpage en chunks ---
    print(f"\n=== 3. Découpage en chunks ===")
    all_docs = []
    path_by_name = {p.name: p for p in pdf_paths}

    for filename, cleaned_text in cleaned_texts.items():
        path = path_by_name[filename]
        prefix = slugify(path.stem)
        base_metadata = {
            "type": "pdf",
            "source_file": filename,
            "audience": audience,
        }

        # Tableaux (non affectés par la dédup)
        for t_idx, table in enumerate(tables_by_file[filename]):
            row_texts = _table_rows_to_texts(table["rows"])
            for r_idx, row_text in enumerate(row_texts):
                all_docs.append({
                    "id": f"{prefix}_table{t_idx:02d}_row{r_idx:03d}",
                    "text": row_text,
                    "metadata": {
                        **base_metadata,
                        "heading": f"Tableau page {table['page']}, ligne {r_idx + 1}",
                        "content_kind": "table_row",
                    },
                })

        # Texte narratif nettoyé
        all_docs.extend(
            build_documents_from_cleaned_text(cleaned_text, prefix, base_metadata)
        )

    print(f"-> {len(all_docs)} documents/chunks générés au total")

    # --- Mode dry-run : affiche le rapport SANS indexer ---
    if dry_run:
        print("\n=== MODE --dry-run : rien n'est indexé ===")
        print("\nExemple de lignes retirées (5 premières, 1er fichier concerné) :")
        for fname, removed in removed_report.items():
            if removed:
                for line in removed[:5]:
                    print(f"  [{fname}] {line[:100]}")
                break
        return

    # --- Étape 4 : Embeddings + indexation ---
    print(f"\n=== 4. Embeddings + indexation dans '{COLLECTION_NAME}' (audience={audience}) ===")
    embedder = get_embedder(offline_test_mode=offline_test_mode)
    if offline_test_mode:
        print("Mode --offline-test : embedder factice (PAS de recherche sémantique réelle).")

    texts_to_embed = [d["text"] for d in all_docs]
    vectors = embedder.embed(texts_to_embed)

    client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
    collection = client.get_or_create_collection(COLLECTION_NAME)

    batch_size = 1000
    total_docs = len(all_docs)
    ids = [d["id"] for d in all_docs]
    documents = [d["text"] for d in all_docs]
    metadatas = [d["metadata"] for d in all_docs]

    print(f"-> Indexation de {total_docs} chunks par lots de {batch_size} dans ChromaDB...", flush=True)
    for i in range(0, total_docs, batch_size):
        end = i + batch_size
        collection.upsert(
            ids=ids[i:end],
            embeddings=vectors[i:end],
            documents=documents[i:end],
            metadatas=metadatas[i:end],
        )
        print(f"   Lots indexés : {min(end, total_docs)}/{total_docs}", flush=True)

    print(f"-> ✅ {total_docs} chunks indexés avec succès. Total dans la collection : {collection.count()}.")
    print()
    print("Rappel : vérifie que le tag audience de chaque chunk est correct.")
    print("Lance avec --dry-run sur un nouveau lot avant d'indexer pour valider la dédup.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "paths",
        nargs="*",
        help="Chemins de PDF spécifiques ou globs. Si omis, scanne data/pdfs/ entier.",
    )
    parser.add_argument("--offline-test", action="store_true", help="Embedder factice, OCR Mistral désactivé.")
    parser.add_argument(
        "--audience",
        default="a_qualifier",
        choices=["a_qualifier", "voyageur", "interne_gouvernance", "professionnel"],
        help="Tag audience appliqué à tous les PDF du lot.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Affiche le rapport de déduplication SANS indexer — à lancer en premier sur un nouveau lot.",
    )
    args = parser.parse_args()

    if args.paths:
        pdf_paths = [Path(p) for p in args.paths]
    else:
        PDF_DIR.mkdir(parents=True, exist_ok=True)
        pdf_paths = sorted(PDF_DIR.glob("*.pdf"))
        if not pdf_paths:
            print(f"Aucun PDF dans {PDF_DIR}. Dépose tes fichiers ici ou passe un chemin en argument.")
            sys.exit(0)

    main(
        pdf_paths,
        offline_test_mode=args.offline_test,
        audience=args.audience,
        dry_run=args.dry_run,
    )
