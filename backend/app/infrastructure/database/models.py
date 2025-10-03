# app/infrastructure/database/models.py
"""Modèles SQLAlchemy pour la persistence."""

from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class LeadModel(Base):
    """
    Modèle SQLAlchemy représentant un Lead en base de données.

    Cette classe est liée à l'infrastructure (SQLAlchemy).
    Elle est distincte de l'entité Lead du domaine.
    """
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(String(255), unique=True, index=True, nullable=False)

    nom = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    telephone = Column(String(50), nullable=True)
    budget = Column(String(100), nullable=True)
    message = Column(Text, nullable=True)

    score = Column(Integer, nullable=True)

    cree_le = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    modifie_le = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)