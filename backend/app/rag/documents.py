"""
Transformation JSON -> documents indexables.

Pourquoi ce fichier est séparé de ingest.py :
La LOGIQUE de "comment on transforme une fiche restaurant en texte
compréhensible par le modèle d'embeddings" est quelque chose qu'on va
vouloir tester et ajuster souvent (ex: changer le format du texte pour
améliorer la pertinence des recherches). En la sortant du script
d'ingestion, on peut la tester unitairement sans avoir besoin de Chroma
ni d'un modèle d'embeddings.

Chaque fonction *_to_documents() renvoie une liste de dicts au format :
{"id": str, "text": str, "metadata": dict}
- "text"     -> ce qui sera vectorisé et montré au LLM comme contexte
- "metadata" -> ce qui permet de FILTRER une recherche (ex: uniquement
                les services "type=restaurant" près de "porte_proche=Porte 21")
                sans devoir tout faire porter par la recherche sémantique
"""

import json
from pathlib import Path
from typing import Any, Dict, List


def load_json(path: Path) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def services_to_documents(services: List[dict]) -> List[dict]:
    docs = []
    for s in services:
        parts = [f"{s['nom']} — {s['categorie']}."]

        loc = f"Situé : {s.get('zone', 'zone non précisée')}"
        if s.get("porte_proche"):
            loc += f", à proximité de {s['porte_proche']}"
        if s.get("etage"):
            loc += f" (étage {s['etage']})"
        parts.append(loc + ".")

        if s.get("horaires"):
            parts.append(f"Horaires : {s['horaires']}.")
        if s.get("halal") is True:
            parts.append("Halal.")
        if s.get("prix_moyen_mad"):
            parts.append(f"Prix moyen : {s['prix_moyen_mad']} MAD.")
        if s.get("menu"):
            items = ", ".join(f"{m['plat']} ({m['prix_mad']} MAD)" for m in s["menu"])
            parts.append(f"Menu : {items}.")
        if s.get("derniere_mise_a_jour"):
            parts.append(f"Dernière mise à jour : {s['derniere_mise_a_jour']}.")
        if s.get("verifie") is False:
            parts.append("(Donnée non encore vérifiée sur place.)")

        docs.append({
            "id": s["id"],
            "text": " ".join(parts),
            "metadata": {
                "type": "service",
                "categorie": s.get("categorie", ""),
                "zone": s.get("zone", ""),
                "porte_proche": s.get("porte_proche", ""),
                "derniere_mise_a_jour": s.get("derniere_mise_a_jour", ""),
                "verifie": bool(s.get("verifie", False)),
            },
        })
    return docs


def parking_to_documents(parking: dict) -> List[dict]:
    docs = []
    for z in parking.get("zones", []):
        parts = [f"{z['nom']} : {z.get('description', '')}."]
        if z.get("distance_terminal"):
            parts.append(f"Distance du terminal : {z['distance_terminal']}.")
        if z.get("tarifs"):
            tarifs = ", ".join(f"{t['duree']} : {t['prix_mad']} MAD" for t in z["tarifs"])
            parts.append(f"Tarifs : {tarifs}.")
        if parking.get("derniere_mise_a_jour"):
            parts.append(f"Dernière mise à jour : {parking['derniere_mise_a_jour']}.")

        docs.append({
            "id": z["id"],
            "text": " ".join(parts),
            "metadata": {
                "type": "parking",
                "zone": z.get("nom", ""),
                "derniere_mise_a_jour": parking.get("derniere_mise_a_jour", ""),
                "verifie": bool(parking.get("verifie", False)),
            },
        })
    return docs


def faq_to_documents(faq: dict) -> List[dict]:
    docs = []
    for item in faq.get("items", []):
        text = f"Question : {item['question']} Réponse : {item['reponse']}"
        docs.append({
            "id": item["id"],
            "text": text,
            "metadata": {
                "type": "faq",
                "categorie": item.get("categorie", ""),
                "source": item.get("source", ""),
                "verifie": bool(item.get("verified", False)),
            },
        })
    return docs


def build_all_documents(data_dir: Path) -> List[Dict[str, Any]]:
    """Charge les 3 fichiers JSON et renvoie une liste unique de documents
    prêts à être vectorisés et indexés."""
    services = load_json(data_dir / "services.json")
    parking = load_json(data_dir / "parking.json")
    faq = load_json(data_dir / "faq.json")

    docs: List[Dict[str, Any]] = []
    docs += services_to_documents(services)
    docs += parking_to_documents(parking)
    docs += faq_to_documents(faq)
    return docs
