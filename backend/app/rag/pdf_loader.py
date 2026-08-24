"""
Ingestion de documents PDF dans le RAG — version complète avec :
  - pdfplumber pour l'extraction des vrais tableaux (colonnes préservées)
  - pymupdf4llm pour l'extraction du texte narratif en Markdown
  - Mistral OCR comme fallback automatique pour les PDF image/scan

Pourquoi trois extracteurs :

1. pdfplumber (extract_tables_from_pdf) :
   pypdf et pymupdf4llm aplatissent les tableaux en texte linéaire, les
   colonnes se mélangent (ex: un tarif associé à la mauvaise ligne). pdfplumber
   garde la structure ligne/colonne — essentiel pour les barèmes tarifaires,
   listes de compagnies, horaires, etc.

2. pymupdf4llm (extract_text_from_pdf) :
   Retourne le texte au format Markdown (titres, listes, paragraphes)
   de façon fiable pour les PDF textuels natifs.

3. Mistral OCR (mistral_ocr.extract_text_with_mistral_ocr) :
   Activé automatiquement quand pymupdf4llm retourne moins de
   MIN_CHARS_PER_PAGE caractères en moyenne par page — signe que le PDF
   est un scan ou un export image. Mistral retourne aussi du Markdown
   structuré (tableaux, titres), donc le même pipeline de chunking s'applique.

Stratégie de chunking, THREE modes dans cet ordre :
1. Tableaux (pdfplumber) → une ligne = un chunk auto-descriptif
2. Articles (regex)      → un article = un chunk pour textes juridiques
3. Générique (fallback)  → taille fixe avec chevauchement
"""

import re
from pathlib import Path
from typing import Dict, List, Optional

import pdfplumber
import pymupdf4llm

from app.rag.mistral_ocr import MIN_CHARS_PER_PAGE, needs_ocr

ARTICLE_PATTERN = re.compile(
    r"(Article\s+(?:premier|\d+)\s*:[^\n]*)"
)


# ---------------------------------------------------------------------------
# Extraction du texte
# ---------------------------------------------------------------------------

def extract_text_from_pdf(path: Path) -> str:
    """Extrait le texte brut d'un PDF.

    Utilise PyMuPDF (fitz) directement de manière rapide et ultra-stable,
    évitant les blocages du modèle de mise en page ONNX de pymupdf4llm.
    """
    try:
        import fitz
        doc = fitz.open(str(path))
        pages_text = [page.get_text("text") or "" for page in doc]
        doc.close()
        text = "\n\n".join(pages_text)
        if text.strip():
            return text
    except Exception as e:
        print(f"[pdf_loader] ⚠️  Erreur PyMuPDF sur {path.name} : {e}")

    try:
        return pymupdf4llm.to_markdown(str(path), page_chunks=False)
    except Exception as e:
        print(f"[pdf_loader] ⚠️  Erreur pymupdf4llm sur {path.name} : {e}")
        return ""


def extract_text_auto(path: Path, mistral_api_key: str = "") -> str:
    """Extraction automatique : pymupdf4llm d'abord, Mistral OCR si insuffisant.

    Si le texte extrait par pymupdf4llm est insuffisant (PDF image/scan),
    et qu'une clé Mistral est disponible, bascule automatiquement sur
    Mistral OCR. Sinon, retourne le texte pymupdf4llm même si court
    (plutôt que de crasher).

    Args:
        path: Chemin vers le PDF.
        mistral_api_key: Clé API Mistral (depuis settings.mistral_api_key).
                         Si vide, Mistral OCR est désactivé.
    """
    try:
        import fitz  # PyMuPDF sous-jacent de pymupdf4llm
        doc = fitz.open(str(path))
        num_pages = len(doc)
        doc.close()
    except Exception:
        num_pages = 1

    text = extract_text_from_pdf(path)

    if needs_ocr(text, num_pages):
        if mistral_api_key:
            print(
                f"[pdf_loader] Texte insuffisant ({len(text)} chars / {num_pages} pages) "
                f"→ activation Mistral OCR pour {path.name}"
            )
            from app.rag.mistral_ocr import extract_text_with_mistral_ocr
            ocr_text = extract_text_with_mistral_ocr(path, mistral_api_key)
            if ocr_text.strip():
                return ocr_text
            print(f"[pdf_loader] ⚠️  OCR vide — conservation du texte pymupdf4llm.")
        else:
            print(
                f"[pdf_loader] ⚠️  {path.name} semble être un PDF image "
                f"(avg {len(text)//max(num_pages,1)} chars/page) mais MISTRAL_API_KEY "
                f"n'est pas configurée → texte partiel conservé."
            )
    return text


# ---------------------------------------------------------------------------
# Extraction des tableaux
# ---------------------------------------------------------------------------

def extract_tables_from_pdf(path: Path, min_columns: int = 2, max_cell_length: int = 200) -> List[Dict]:
    """Extrait les tableaux d'un PDF avec pdfplumber, colonnes préservées.

    Renvoie une liste de {"page": int, "rows": list[list[str]]} -- une
    entrée par tableau détecté. Renvoie une liste vide si aucun tableau
    n'est détecté (PDF purement textuel).

    DEUX filtres anti-faux-positifs :
    1. min_columns=2 : une liste à une seule colonne (menu latéral avec
       bordures) n'est pas un tableau de données.
    2. max_cell_length=200 : une mise en page 2 colonnes (menu + contenu)
       peut être confondue avec un tableau à cellule géante. Un vrai tableau
       de données (tarifs, horaires...) a des cellules COURTES par nature.
    """
    tables_found = []
    try:
        with pdfplumber.open(str(path)) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                for table in page.extract_tables():
                    cleaned_rows = [
                        [cell.strip() if cell else "" for cell in row] for row in table
                    ]
                    if not cleaned_rows or len(cleaned_rows[0]) < min_columns:
                        continue
                    max_len = max((len(cell) for row in cleaned_rows for cell in row), default=0)
                    if max_len > max_cell_length:
                        continue
                    tables_found.append({"page": page_num, "rows": cleaned_rows})
    except Exception as e:
        print(f"[pdf_loader] ⚠️  Erreur pdfplumber sur {path.name} : {e}")
    return tables_found


def _table_rows_to_texts(rows: List[List[str]]) -> List[str]:
    """Convertit un tableau en UNE CHAÎNE PAR LIGNE (pas un seul bloc).

    Format : 'colonne1: valeur1 | colonne2: valeur2'
    Chaque ligne est auto-descriptive (contient le nom de chaque colonne)
    et peut être trouvée indépendamment dans le RAG (ex: tarif parking
    sans noyer le résultat dans les autres lignes du même tableau).
    """
    if not rows:
        return []
    header = rows[0]
    texts = []
    for row in rows[1:]:
        pairs = [
            f"{h.strip()}: {v.strip()}"
            for h, v in zip(header, row)
            if h and v
        ]
        if pairs:
            texts.append(" | ".join(pairs))
    return texts


# ---------------------------------------------------------------------------
# Chunking
# ---------------------------------------------------------------------------

def chunk_by_article(text: str) -> List[Dict[str, str]]:
    """Découpe un texte juridique en chunks par article.

    Retourne [{heading, text}]. Retourne [] si pas d'articles détectés
    (signal pour utiliser chunk_generic() à la place).
    """
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
    """Fallback : découpage par taille fixe avec chevauchement."""
    text = re.sub(r"\s+", " ", text).strip()
    chunks = []
    start = 0
    while start < len(text):
        end = start + max_chars
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start = end - overlap
    return chunks


# ---------------------------------------------------------------------------
# Point d'entrée principal
# ---------------------------------------------------------------------------

def pdf_to_documents(
    path: Path,
    doc_id_prefix: str,
    extra_metadata: Optional[Dict] = None,
    mistral_api_key: str = "",
) -> List[Dict]:
    """Transforme un PDF en documents indexables (format : {id, text, metadata}).

    Pipeline complet :
    1. pdfplumber → tableaux (chaque ligne = un chunk)
    2. pymupdf4llm → texte narratif (+ Mistral OCR si texte insuffisant)
       2a. Articles détectés → un article = un chunk
       2b. Sinon → découpage générique

    extra_metadata : tags additionnels (ex: {"audience": "voyageur"}).
    mistral_api_key : clé Mistral (vide = OCR désactivé, pas de crash).
    """
    base_metadata = {"type": "pdf", "source_file": path.name}
    if extra_metadata:
        base_metadata.update(extra_metadata)

    docs = []

    # --- 1. Tableaux ---
    tables = extract_tables_from_pdf(path)
    for t_idx, table in enumerate(tables):
        row_texts = _table_rows_to_texts(table["rows"])
        for r_idx, row_text in enumerate(row_texts):
            docs.append({
                "id": f"{doc_id_prefix}_table{t_idx:02d}_row{r_idx:03d}",
                "text": row_text,
                "metadata": {
                    **base_metadata,
                    "heading": f"Tableau page {table['page']}, ligne {r_idx + 1}",
                    "content_kind": "table_row",
                },
            })

    # --- 2. Texte narratif (avec OCR auto si nécessaire) ---
    text = extract_text_auto(path, mistral_api_key=mistral_api_key)
    article_chunks = chunk_by_article(text)

    if article_chunks:
        for i, chunk in enumerate(article_chunks):
            docs.append({
                "id": f"{doc_id_prefix}_art_{i:03d}",
                "text": chunk["text"],
                "metadata": {**base_metadata, "heading": chunk["heading"], "content_kind": "text"},
            })
    elif not tables:
        # Pas de tableaux ET pas d'articles → découpage générique
        for i, chunk_text in enumerate(chunk_generic(text)):
            docs.append({
                "id": f"{doc_id_prefix}_chunk_{i:03d}",
                "text": chunk_text,
                "metadata": {**base_metadata, "heading": "", "content_kind": "text"},
            })
    # Si tableaux présents mais pas d'articles → le texte narratif autour
    # d'un tableau PDF est souvent du bruit (en-têtes répétés), on ne
    # fait PAS de chunk_generic() en plus.

    return docs
