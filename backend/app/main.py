"""
Point d'entrée de l'application.

Pourquoi ce fichier est volontairement court :
`main.py` ne doit faire QUE l'assemblage (créer l'app, brancher les
middlewares, inclure les routers). Toute la logique métier vit ailleurs
(schemas.py, routers/, et bientôt services/). Ça garde le projet lisible
même quand il grossira aux étapes 3 à 8.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import chat

app = FastAPI(
    title=settings.app_name,
    description="API du chatbot de l'aéroport Agadir Al Massira (AGA)",
    version="0.1.0",
)

# CORS : le frontend React (autre port en dev, autre domaine en prod)
# doit pouvoir appeler cette API depuis le navigateur. En production,
# remplacer "*" par le vrai domaine du frontend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)


@app.get("/health", tags=["health"])
def health():
    """Endpoint de contrôle simple : si ça répond, le serveur est vivant.
    Utile pour Render/Fly.io/Railway (déploiement) et pour vérifier
    rapidement en développement que tout tourne."""
    return {"status": "ok", "app": settings.app_name, "env": settings.environment}
