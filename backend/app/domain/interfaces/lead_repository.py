# app/domain/interfaces/lead_repository.py
"""Interface du Repository pour les Leads."""

from abc import ABC, abstractmethod
from typing import Optional, List
from app.domain.entities.lead_entity import LeadEntity


class LeadRepository(ABC):
    """
    Interface définissant le contrat pour la persistence des Leads.

    Cette interface sera implémentée par l'infrastructure (SQLAlchemy, etc.)
    Le domaine ne connaît que cette interface, pas l'implémentation.
    """

    @abstractmethod
    def creer(self, lead: LeadEntity) -> LeadEntity:
        """
        Crée un nouveau lead en base de données.

        Args:
            lead: L'entité Lead à persister

        Returns:
            Lead: L'entité avec l'ID généré par la base

        Raises:
            Exception si erreur de persistence
        """
        pass

    @abstractmethod
    def obtenir_par_id(self, lead_id: int) -> Optional[LeadEntity]:
        """
        Récupère un lead par son ID.

        Args:
            lead_id: L'identifiant unique du lead

        Returns:
            Optional[Lead]: Le lead si trouvé, None sinon
        """
        pass

    @abstractmethod
    def obtenir_par_session(self, session_id: str) -> Optional[LeadEntity]:
        """
        Récupère un lead par son session_id (identifiant de conversation).

        Args:
            session_id: L'identifiant unique de la session

        Returns:
            Optional[Lead]: Le lead si trouvé, None sinon
        """
        pass

    @abstractmethod
    def mettre_a_jour(self, lead: LeadEntity) -> LeadEntity:
        """
        Met à jour un lead existant.

        Args:
            lead: L'entité Lead avec les modifications

        Returns:
            Lead: L'entité mise à jour

        Raises:
            Exception si le lead n'existe pas
        """
        pass

    @abstractmethod
    def lister_tous(self, limite: int = 100) -> List[LeadEntity]:
        """
        Liste tous les leads avec une limite.

        Args:
            limite: Nombre maximum de leads à retourner (défaut: 100)

        Returns:
            List[Lead]: Liste des leads
        """
        pass

    @abstractmethod
    def supprimer(self, lead_id: int) -> bool:
        """
        Supprime un lead.

        Args:
            lead_id: L'identifiant du lead à supprimer

        Returns:
            bool: True si supprimé, False si inexistant
        """
        pass