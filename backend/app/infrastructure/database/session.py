# app/infrastructure/database/session.py
"""Configuration de la session SQLAlchemy."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from app.core.config import settings

# Création de l'engine (connexion DB)
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
    echo=False,
    pool_pre_ping=True
)

# Factory de sessions
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db() -> Generator[Session, None, None]:
    """
    Générateur de session DB pour dependency injection FastAPI.

    Usage dans une route FastAPI :
        @app.get("/leads")
        def get_leads(db: Session = Depends(get_db)):
            ...

    La session est automatiquement fermée après la requête.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Initialise la base de données.
    Crée toutes les tables si elles n'existent pas.

    À appeler au démarrage de l'application.
    """
    from app.infrastructure.database.models import Base
    Base.metadata.create_all(bind=engine)