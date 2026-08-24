"""
Déduplication de contenu répété entre plusieurs PDF -- pensé pour des
lots volumineux (des dizaines/centaines de PDF, ex: export d'un site
avec menu de navigation répété sur chaque page).

Pourquoi ce module existe :
Sur un lot de PDF exportés depuis un site à onglets/accordéon (chaque
fichier = une capture de page avec une seule section dépliée), le menu
de navigation, les titres de section, et le pied de page se répètent
QUASI IDENTIQUES dans tous les fichiers. Sans filtrage, un pipeline RAG
indexerait des dizaines de chunks redondants, diluant la pertinence de
la recherche et gonflant inutilement la base vectorielle.

Deux mécanismes de filtrage, appliqués aux LIGNES de texte AVANT le
chunking (pas après -- un filtrage post-chunking est cassé par les
fenêtres de découpage qui ne tombent pas pareil selon la longueur du
contenu unique de chaque fichier) :

1. Filtrage par motif (regex) : horodatages d'impression navigateur
   ("8/4/26, 9:51 AM"), URLs de pied de page, compteurs de page ("1/2").
   Ces lignes sont TOUJOURS du bruit, indépendamment du nombre de
   fichiers -- elles diffèrent légèrement à chaque fichier (heure,
   ancre d'URL) donc la déduplication par fréquence ne les attrape pas.

2. Filtrage par fréquence inter-fichiers : une ligne identique (après
   normalisation espaces/casse) apparaissant dans un grand nombre de
   fichiers DIFFÉRENTS du même lot est presque certainement un élément
   de menu/navigation, pas du contenu réel -- même sans reconnaître
   explicitement "ceci est un menu".
"""

import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

NOISE_PATTERNS = [
    re.compile(r"^\d{1,2}/\d{1,2}/\d{2,4},?\s*\d{1,2}:\d{2}\s*[AP]M"),  # horodatage d'impression
    re.compile(r"^https?://"),  # URL de pied de page
    re.compile(r"^\d+/\d+$"),  # compteur de page "1/2"
]


def _normalize(line: str) -> str:
    return " ".join(line.split()).strip().lower()


def _is_noise(line: str) -> bool:
    return any(p.search(line) for p in NOISE_PATTERNS)


def extract_lines(text: str) -> List[str]:
    return [l.strip() for l in text.split("\n") if l.strip()]


def find_boilerplate_lines(
    file_lines: Dict[str, List[str]], min_file_ratio: float = 0.4, min_files: int = 3
) -> set:
    """Identifie les lignes considérées comme boilerplate (menu/nav
    répété), selon LEQUEL des deux seuils est atteint en premier :
    - apparaît dans au moins min_file_ratio des fichiers du lot (ex: 40%)
    - OU apparaît dans au moins min_files fichiers en valeur absolue
    (utile pour les petits lots où le ratio seul serait trop permissif)."""
    line_to_files = defaultdict(set)
    for filename, lines in file_lines.items():
        for line in lines:
            if not _is_noise(line):  # le bruit par motif est géré séparément
                line_to_files[_normalize(line)].add(filename)

    total_files = len(file_lines)
    threshold = max(min_files, int(total_files * min_file_ratio))

    return {norm for norm, files in line_to_files.items() if len(files) >= threshold}


def deduplicate_batch(
    texts_by_file: Dict[str, str], min_file_ratio: float = 0.4, min_files: int = 3
) -> Tuple[Dict[str, str], Dict[str, List[str]]]:
    """Prend un lot {nom_fichier: texte_brut}, renvoie
    ({nom_fichier: texte_nettoyé}, rapport_de_lignes_retirées).

    Le texte nettoyé ne contient plus le bruit de motif (horodatages,
    URLs, compteurs de page) ni les lignes considérées boilerplate
    inter-fichiers -- prêt à être passé à chunk_by_article()/
    chunk_generic() (voir pdf_loader.py) comme si c'était le texte
    original."""
    file_lines = {fname: extract_lines(text) for fname, text in texts_by_file.items()}
    boilerplate = find_boilerplate_lines(file_lines, min_file_ratio, min_files)

    cleaned = {}
    removed_report = {}
    for fname, lines in file_lines.items():
        kept, removed = [], []
        for line in lines:
            if _is_noise(line) or _normalize(line) in boilerplate:
                removed.append(line)
            else:
                kept.append(line)
        cleaned[fname] = "\n".join(kept)
        removed_report[fname] = removed

    return cleaned, removed_report
