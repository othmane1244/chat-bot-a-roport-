"""
Ingestion de documents PDF dans le RAG.

Pourquoi un module séparé de documents.py :
Le JSON (étape 2) est déjà structuré (un objet = un document = un chunk).
Un PDF est du texte brut non structuré : il faut d'abord le DÉCOUPER
intelligemment avant de pouvoir l'indexer, sinon on se retrouve avec
un seul chunk de 10 pages, ingérable par la recherche sémantique
(la similarité entre "combien coûte le parking ?" et "10 pages de texte
mélangé" sera toujours mauvaise, peu importe la qualité du modèle
d'embeddings).

Stratégie de chunking, deux modes :
1. chunk_by_article() : si le texte contient des marqueurs "Article X"
   (cas des lois, règlements, contrats) -> un article = un chunk. C'est
   la meilleure stratégie ici : chaque article est déjà une unité de
   sens autonome, on ne fait qu'exploiter une structure qui existe déjà.
2. chunk_generic() : fallback pour du texte sans structure d'articles
   (brochures, guides) -> découpage par taille fixe avec chevauchement,
   pour ne pas couper une idée en plein milieu.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional

from pypdf import PdfReader

ARTICLE_PATTERN = re.compile(
    r"(Article\s+(?:premier|\d+)\s*:[^\n]*)"
)


def extract_text_from_pdf(path: Path) -> str:
    """Extrait le texte brut de toutes les pages d'un PDF."""
    reader = PdfReader(str(path))
    pages_text = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages_text)


def chunk_by_article(text: str) -> List[Dict[str, str]]:
    """Découpe un texte juridique en chunks par article.

    Renvoie une liste de {"heading": "Article X : ...", "text": "..."}.
    Renvoie une liste vide si aucun marqueur d'article n'est trouvé
    (signal pour utiliser chunk_generic() à la place)."""
    matches = list(ARTICLE_PATTERN.finditer(text))
    if not matches:
        return []

    chunks = []
    for i, m in enumerate(matches):
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        heading = m.group(1).strip()
        body = text[start:end].strip()
        chunks.append({"heading": heading, "text": body})
    return chunks


def chunk_generic(text: str, max_chars: int = 1000, overlap: int = 150) -> List[str]:
    """Fallback : découpage par taille fixe avec chevauchement, pour du
    texte sans structure exploitable (pas d'articles détectés)."""
    text = re.sub(r"\s+", " ", text).strip()
    chunks = []
    start = 0
    while start < len(text):
        end = start + max_chars
        chunks.append(text[start:end])
        start = end - overlap
    return chunks


def pdf_to_documents(
    path: Path,
    doc_id_prefix: str,
    extra_metadata: Optional[Dict] = None,
) -> List[Dict]:
    """Transforme un PDF en documents indexables (même format que
    documents.py : {"id", "text", "metadata"}).

    extra_metadata permet de taguer la source (ex: {"audience": "interne"})
    pour pouvoir la séparer plus tard du contenu voyageur — voir la
    discussion sur le périmètre dans le README."""
    text = extract_text_from_pdf(path)
    article_chunks = chunk_by_article(text)

    base_metadata = {"type": "pdf", "source_file": path.name}
    if extra_metadata:
        base_metadata.update(extra_metadata)

    docs = []
    if article_chunks:
        for i, chunk in enumerate(article_chunks):
            docs.append({
                "id": f"{doc_id_prefix}_art_{i:03d}",
                "text": chunk["text"],
                "metadata": {**base_metadata, "heading": chunk["heading"]},
            })
    else:
        # Pas de structure "Article X" détectée -> découpage générique
        for i, chunk_text in enumerate(chunk_generic(text)):
            docs.append({
                "id": f"{doc_id_prefix}_chunk_{i:03d}",
                "text": chunk_text,
                "metadata": {**base_metadata, "heading": ""},
            })
    return docs
