# app/infrastructure/repositories/lead_repository.py
"""Implémentation concrète du LeadRepository avec SQLAlchemy."""

from typing import Optional, List
from sqlalchemy.orm import Session
from app.domain.entities.lead_entity import LeadEntity
from app.domain.interfaces.lead_repository import LeadRepository
from app.infrastructure.database.models import LeadModel


class SQLAlchemyLeadRepository(LeadRepository):
    """
    Implémentation SQLAlchemy de l'interface LeadRepository.

    Cette classe traduit entre :
    - L'entité Lead (domaine)
    - Le modèle LeadModel (infrastructure SQLAlchemy)
    """

    def __init__(self, db: Session):
        """
        Initialise le repository avec une session DB.

        Args:
            db: Session SQLAlchemy active
        """
        self.db = db

    def _to_entity(self, model: LeadModel) -> LeadEntity:
        """
        Convertit un LeadModel (DB) en LeadEntity (domaine).

        Mapping infrastructure → domaine.
        """
        return LeadEntity(
            id=model.id,
            session_id=model.session_id,
            nom=model.nom,
            email=model.email,
            telephone=model.telephone,
            budget=model.budget,
            message=model.message,
            score=model.score,
            cree_le=model.cree_le,
            modifie_le=model.modifie_le
        )

    def _to_model(self, entity: LeadEntity) -> LeadModel:
        """
        Convertit une entité LeadEntity (domaine) en LeadModel (DB).

        Mapping domaine → infrastructure.
        """
        return LeadModel(
            id=entity.id,
            session_id=entity.session_id,
            nom=entity.nom,
            email=entity.email,
            telephone=entity.telephone,
            budget=entity.budget,
            message=entity.message,
            score=entity.score
        )

    def creer(self, lead: LeadEntity) -> LeadEntity:
        """Crée un nouveau lead en base de données."""
        model = self._to_model(lead)
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return self._to_entity(model)

    def obtenir_par_id(self, lead_id: int) -> Optional[LeadEntity]:
        """Récupère un lead par son ID."""
        model = self.db.query(LeadModel).filter(LeadModel.id == lead_id).first()
        return self._to_entity(model) if model else None

    def obtenir_par_session(self, session_id: str) -> Optional[LeadEntity]:
        """Récupère un lead par son session_id."""
        model = self.db.query(LeadModel).filter(LeadModel.session_id == session_id).first()
        return self._to_entity(model) if model else None

    def mettre_a_jour(self, lead: LeadEntity) -> LeadEntity:
        """Met à jour un lead existant."""
        model = self.db.query(LeadModel).filter(LeadModel.id == lead.id).first()
        if not model:
            raise ValueError(f"Lead avec ID {lead.id} introuvable")

        # Mise à jour des champs
        model.nom = lead.nom
        model.email = lead.email
        model.telephone = lead.telephone
        model.budget = lead.budget
        model.message = lead.message
        model.score = lead.score

        self.db.commit()
        self.db.refresh(model)
        return self._to_entity(model)

    def lister_tous(self, limite: int = 100) -> List[LeadEntity]:
        """Liste tous les leads avec une limite."""
        models = self.db.query(LeadModel).limit(limite).all()
        return [self._to_entity(model) for model in models]

    def supprimer(self, lead_id: int) -> bool:
        """Supprime un lead."""
        model = self.db.query(LeadModel).filter(LeadModel.id == lead_id).first()
        if not model:
            return False

        self.db.delete(model)
        self.db.commit()
        return True