"""
Configuration centralisée du backend.

Pourquoi ce fichier existe :
On va bientôt avoir plein de clés d'API (Gemini, Groq, AeroDataBox,
OpenWeatherMap...) et d'adresses de bases (Redis, Neo4j, Chroma).
Plutôt que de les éparpiller dans le code, on les déclare UNE FOIS ici,
et le reste du code importe `settings` sans jamais toucher à os.environ
directement. Ça évite les fautes de frappe sur les noms de variables et
ça centralise la doc de "ce dont ce projet a besoin pour tourner".

À ce stade (étape 1), rien n'est encore utilisé : c'est juste le
squelette, prêt à accueillir les clés au fur et à mesure des étapes
suivantes (connecteurs API, LLM, etc.).
"""

from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    # Généralités
    app_name: str = "AGA Airport Assistant"
    environment: str = "development"  # development | production

    # --- Ces clés seront utilisées à partir de l'étape 3 (connecteurs API) ---
    aerodatabox_api_key: str = ""
    openweathermap_api_key: str = ""

    # --- Ces clés seront utilisées à partir de l'étape 5 (LLM) ---
    gemini_api_key: str = ""
    groq_api_key: str = ""

    # --- Ces adresses seront utilisées à partir des étapes 3-4 (cache, RAG) ---
    redis_url: str = "redis://localhost:6379/0"
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = ""
    chroma_persist_dir: str = str(BASE_DIR / "chroma_data")
    rag_offline_test_mode: bool = False

    @field_validator("chroma_persist_dir", mode="before")
    @classmethod
    def _resolve_chroma_persist_dir(cls, value):
        path = Path(str(value))
        if path.is_absolute():
            return str(path)
        return str((BASE_DIR / path).resolve())

    model_config = SettingsConfigDict(env_file=str(BASE_DIR / ".env"), extra="ignore")


# Instance unique importée partout ailleurs dans le code
settings = Settings()
