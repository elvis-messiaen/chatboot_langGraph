# app/schemas/chat.py
"""Schemas Pydantic pour les endpoints de chat."""

from pydantic import BaseModel, Field, field_validator
from typing import Optional


class ChatRequest(BaseModel):
    """
    Schema de requête pour l'endpoint POST /chat.

    Représente un message envoyé par le frontend.
    """

    session_id: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Identifiant unique de la session de conversation (UUID généré côté frontend)"
    )

    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Message de l'utilisateur"
    )

    nom: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Nom de l'utilisateur (optionnel)"
    )

    @field_validator('session_id')
    @classmethod
    def session_id_non_vide(cls, v: str) -> str:
        """Valide que le session_id n'est pas juste des espaces."""
        if not v.strip():
            raise ValueError("Le session_id ne peut pas être vide")
        return v.strip()

    @field_validator('message')
    @classmethod
    def message_non_vide(cls, v: str) -> str:
        """Valide que le message n'est pas juste des espaces."""
        if not v.strip():
            raise ValueError("Le message ne peut pas être vide")
        return v.strip()

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "message": "Bonjour, je voudrais un devis pour mon site web",
                "nom": "Jean Dupont"
            }
        }


class ChatResponse(BaseModel):
    """
    Schema de réponse pour l'endpoint POST /chat.

    Représente la réponse du chatbot renvoyée au frontend.
    """

    reponse: str = Field(
        ...,
        description="Réponse générée par le chatbot"
    )

    lead_sauvegarde: bool = Field(
        default=True,
        description="Indique si les informations ont été sauvegardées en base"
    )

    score: Optional[int] = Field(
        default=None,
        ge=0,
        le=100,
        description="Score de qualification du lead (0-100). None si pas encore calculé."
    )

    informations_manquantes: Optional[list[str]] = Field(
        default=None,
        description="Liste des champs encore manquants (nom, email, etc.)"
    )

    intention_detectee: Optional[str] = Field(
        default=None,
        description="Intention détectée du message utilisateur"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "reponse": "Bonjour ! Ravi de vous aider. Pour commencer, comment vous appelez-vous ?",
                "lead_sauvegarde": True,
                "score": None,
                "informations_manquantes": ["nom", "email", "contact"],
                "intention_detectee": "devis"
            }
        }