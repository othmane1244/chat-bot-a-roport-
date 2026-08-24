"""
Module OCR Mistral — extraction de texte depuis des PDF contenant des images,
des scans, ou des tableaux complexes impossibles à lire avec pypdf/pdfplumber.

Pourquoi Mistral OCR et pas Tesseract :
- Mistral OCR (mistral-ocr-latest) comprend la mise en page globale du document
  (pas juste du texte brut) : il retourne du Markdown structuré avec tableaux,
  titres, listes — prêt à chunker directement sans post-traitement.
- Supporte nativement l'arabe (RTL), le français et l'anglais en simultané
  dans le même document — critique pour les PDF ONDA bilingues.
- Ne nécessite aucune installation locale (Tesseract + langues + pdf2image)
  — juste une clé API.

Quand ce module est utilisé :
- Automatiquement par pdf_loader.py quand le texte extrait par pymupdf4llm
  est insuffisant (< MIN_CHARS_PER_PAGE caractères en moyenne par page).
- Jamais si pymupdf4llm retourne déjà du texte de qualité — évite les appels
  API inutiles (et les coûts) sur les PDF purement textuels.

Limite connue :
- Appel API externe : nécessite internet + clé MISTRAL_API_KEY dans .env.
- Les PDF très volumineux (> 50 Mo) sont encodés intégralement en base64 et
  envoyés en une seule requête — peut être lent sur les gros rapports ONDA.
  Pour les fichiers > 20 Mo, envisager un traitement page par page (voir la
  fonction extract_pages_ocr() ci-dessous).
"""

import base64
from pathlib import Path
from typing import Optional

# MIN_CHARS_PER_PAGE : si le texte moyen extrait par pypdf est en dessous de
# ce seuil par page, on considère que le PDF est image/scan et on bascule sur OCR.
MIN_CHARS_PER_PAGE = 100

# Taille max (en octets) avant de traiter page par page plutôt qu'en une fois.
# 20 Mo = 20 * 1024 * 1024
MAX_SIZE_SINGLE_CALL = 20 * 1024 * 1024


def needs_ocr(text: str, num_pages: int) -> bool:
    """Retourne True si le texte extrait est insuffisant et nécessite l'OCR.

    Un PDF 'image' (scan ou export navigateur en image) produit soit du texte
    vide, soit quelques dizaines de caractères par page (numéros de page, URL
    de pied de page...). Un PDF textuel normal produit plusieurs centaines de
    caractères par page.
    """
    if num_pages == 0:
        return False
    avg_chars = len(text.strip()) / num_pages
    return avg_chars < MIN_CHARS_PER_PAGE


def _pdf_to_base64(path: Path) -> str:
    """Encode un PDF en base64 pour l'envoi à l'API Mistral."""
    with open(path, "rb") as f:
        return base64.standard_b64encode(f.read()).decode("utf-8")


def extract_text_with_mistral_ocr(path: Path, api_key: str) -> str:
    """Extrait le texte d'un PDF via l'API Mistral OCR.

    Retourne le texte au format Markdown (tableaux, titres, listes préservés).
    Retourne une chaîne vide en cas d'erreur API (le pipeline se rabat
    sur le texte pypdf, même insuffisant, plutôt que de crasher).

    Args:
        path: Chemin vers le fichier PDF.
        api_key: Clé API Mistral (lue depuis settings.mistral_api_key).
    """
    try:
        from mistralai.client import Mistral
    except ImportError:
        try:
            from mistralai import Mistral
        except ImportError:
            print(
                "[mistral_ocr] ⚠️  Le package 'mistralai' n'est pas installé ou mal importé. "
                "Lance : pip install mistralai"
            )
            return ""

    file_size = path.stat().st_size
    if file_size > MAX_SIZE_SINGLE_CALL:
        print(
            f"[mistral_ocr] ⚠️  {path.name} ({file_size // (1024*1024)} Mo) "
            f"dépasse la limite de traitement en une seule requête. "
            f"Traitement page par page activé."
        )
        return _extract_large_pdf_ocr(path, api_key)

    print(f"[mistral_ocr] → Appel Mistral OCR sur {path.name}...")
    try:
        client = Mistral(api_key=api_key)
        pdf_b64 = _pdf_to_base64(path)

        ocr_response = client.ocr.process(
            model="mistral-ocr-latest",
            document={
                "type": "document_url",
                "document_url": f"data:application/pdf;base64,{pdf_b64}",
            },
        )

        pages_text = [page.markdown for page in ocr_response.pages if page.markdown]
        result = "\n\n".join(pages_text)
        print(f"[mistral_ocr] ✅ {len(pages_text)} page(s) extraite(s) — {len(result)} caractères.")
        return result

    except Exception as e:
        print(f"[mistral_ocr] ❌ Erreur API Mistral sur {path.name} : {e}")
        return ""


def _extract_large_pdf_ocr(path: Path, api_key: str) -> str:
    """Traitement page par page pour les PDF volumineux (> 20 Mo).

    Utilise pypdf pour extraire chaque page en PDF temporaire, puis envoie
    chaque page séparément à Mistral OCR. Plus lent mais évite les timeouts
    et les dépassements de taille de requête.
    """
    try:
        from pypdf import PdfReader, PdfWriter
        import io
        try:
            from mistralai.client import Mistral
        except ImportError:
            from mistralai import Mistral
    except ImportError as e:
        print(f"[mistral_ocr] ⚠️  Dépendance manquante : {e}")
        return ""

    client = Mistral(api_key=api_key)
    reader = PdfReader(str(path))
    all_pages_text = []

    for page_num, page in enumerate(reader.pages, start=1):
        try:
            # Créer un PDF temporaire d'une seule page en mémoire
            writer = PdfWriter()
            writer.add_page(page)
            buffer = io.BytesIO()
            writer.write(buffer)
            page_b64 = base64.standard_b64encode(buffer.getvalue()).decode("utf-8")

            ocr_response = client.ocr.process(
                model="mistral-ocr-latest",
                document={
                    "type": "document_url",
                    "document_url": f"data:application/pdf;base64,{page_b64}",
                },
            )

            page_text = "\n".join(
                p.markdown for p in ocr_response.pages if p.markdown
            )
            if page_text.strip():
                all_pages_text.append(page_text)

            print(f"[mistral_ocr] Page {page_num}/{len(reader.pages)} OK")

        except Exception as e:
            print(f"[mistral_ocr] ⚠️  Erreur page {page_num} : {e}")
            continue

    return "\n\n".join(all_pages_text)
