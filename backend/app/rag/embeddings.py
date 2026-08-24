"""
Abstraction du modèle d'embeddings.

Pourquoi une abstraction plutôt qu'un appel direct au modèle :
On veut pouvoir changer de modèle d'embeddings (§7 recommande BGE-M3)
sans toucher au script d'ingestion ni au futur code de recherche.
Les deux classes ci-dessous respectent la même interface : .embed(texts).

IMPORTANT — limite connue de cet environnement de développement :
BGEM3Embedder télécharge les poids du modèle (~2 Go) depuis Hugging Face
la première fois qu'il est utilisé. Le sandbox dans lequel ce code a été
écrit et testé n'a PAS accès à huggingface.co (accès réseau restreint à
une liste de domaines autorisés). Le code ci-dessous est donc écrit pour
la production, mais n'a été testé ici qu'avec DummyHashEmbedder (mode
--offline-test). Teste BGEM3Embedder chez toi, en local, où l'accès
internet est complet — voir le README pour la marche à suivre.
"""

import hashlib
import logging
from typing import List, Protocol

logger = logging.getLogger(__name__)


class Embedder(Protocol):
    def embed(self, texts: List[str]) -> List[List[float]]: ...


class DummyHashEmbedder:
    """Embedder déterministe basé sur un hash, SANS AUCUNE compréhension
    sémantique du texte. Sert uniquement à tester la mécanique
    d'ingestion (Chroma, dimensions de vecteurs, requêtes) sans
    connexion internet ni téléchargement de modèle.

    NE JAMAIS utiliser en production : deux phrases avec un sens proche
    n'auront PAS forcément des vecteurs proches. Seule la reproductibilité
    (même texte -> même vecteur) est garantie.
    """

    dim = 384

    def embed(self, texts: List[str]) -> List[List[float]]:
        import random

        vectors = []
        for t in texts:
            seed = int(hashlib.sha256(t.encode("utf-8")).hexdigest(), 16) % (2**32)
            rng = random.Random(seed)
            vectors.append([rng.uniform(-1, 1) for _ in range(self.dim)])
        return vectors


class BGEM3Embedder:
    """Modèle de production recommandé au §7 du cahier des charges :
    BAAI/bge-m3, multilingue (100+ langues dont arabe), open source,
    auto-hébergeable gratuitement, mode hybride dense+sparse.

    Nécessite : pip install sentence-transformers
    Nécessite un accès internet la première fois (téléchargement des
    poids), puis fonctionne hors-ligne (poids mis en cache localement).
    """

    def __init__(self, model_name: str = "BAAI/bge-m3", device: str | None = None):
        import torch
        from sentence_transformers import SentenceTransformer

        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
        self._device = device
        self.model = SentenceTransformer(model_name, device=device)

    def embed(self, texts: List[str], batch_size: int = 4) -> List[List[float]]:
        """Encode texts with automatic CPU fallback on CUDA OOM."""
        try:
            return self.model.encode(
                texts,
                batch_size=batch_size,
                normalize_embeddings=True,
                show_progress_bar=True,
            ).tolist()
        except RuntimeError as exc:
            if "out of memory" in str(exc).lower() and self._device != "cpu":
                import torch
                logger.warning(
                    "CUDA OOM avec batch_size=%d — vidage cache GPU et bascule CPU.",
                    batch_size,
                )
                torch.cuda.empty_cache()
                self.model = self.model.to("cpu")
                self._device = "cpu"
                return self.model.encode(
                    texts,
                    batch_size=batch_size,
                    normalize_embeddings=True,
                    show_progress_bar=True,
                ).tolist()
            raise


def get_embedder(offline_test_mode: bool = False) -> Embedder:
    if offline_test_mode:
        return DummyHashEmbedder()
    return BGEM3Embedder()
