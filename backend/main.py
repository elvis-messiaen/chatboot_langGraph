# main.py
"""Point d'entrée de l'application FastAPI."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import chat
from app.infrastructure.database.session import init_db
from app.core.config import settings

# Créer l'instance FastAPI
app = FastAPI(
    title="Chatbot LangGraph API",
    description="API pour un chatbot de génération de leads avec LangGraph",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server
        "http://localhost:5173",  # Vite dev server
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Événement de démarrage
@app.on_event("startup")
def startup_event():
    """
    Exécuté au démarrage de l'application.

    Initialise la base de données (crée les tables si nécessaire).
    """
    print("Démarrage de l'application...")
    print(f"Environnement : {settings.ENVIRONMENT}")
    print(f"Base de données : {settings.DATABASE_URL}")

    # Initialiser la base de données
    init_db()
    print("Base de données initialisée")


# Événement d'arrêt
@app.on_event("shutdown")
def shutdown_event():
    """
    Exécuté à l'arrêt de l'application.

    Nettoyage des ressources si nécessaire.
    """
    print("Arrêt de l'application...")


# Enregistrer les routes
app.include_router(chat.router)


# Route racine (health check)
@app.get("/")
def read_root():
    """
    Route racine pour vérifier que l'API fonctionne.

    Returns:
        dict: Message de bienvenue et status
    """
    return {
        "message": "Chatbot LangGraph API",
        "status": "running",
        "version": "1.0.0",
        "docs": "/docs"
    }


# Route de santé
@app.get("/health")
def health_check():
    """
    Health check endpoint.

    Utilisé par les outils de monitoring pour vérifier que l'API répond.

    Returns:
        dict: Status de santé de l'application
    """
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT
    }


# Point d'entrée pour uvicorn
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )