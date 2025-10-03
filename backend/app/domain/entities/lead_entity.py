# app/domain/entities/lead_entity.py
"""Entité métier Lead - Représente un prospect."""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class LeadEntity:
    """
    Entité Lead du domaine métier.
    Représente un prospect qui interagit avec le chatbot.
    Peut être un particulier ou une entreprise.
    """

    id: Optional[int] = None
    session_id: str = ""

    # Informations collectées
    nom: Optional[str] = None
    email: Optional[str] = None
    telephone: Optional[str] = None
    budget: Optional[str] = None
    message: Optional[str] = None

    # Qualification
    score: Optional[int] = None

    # Audit
    cree_le: Optional[datetime] = None
    modifie_le: Optional[datetime] = None

    def est_complet(self) -> bool:
        """
        Vérifie si le lead a les informations minimales exploitables.

        Un lead est exploitable s'il a :
        - Un message (comprendre le besoin)
        - Un moyen de contact (email ou téléphone)

        Le nom est optionnel.
        """
        return self.message is not None and self.est_recontactable()

    def est_recontactable(self) -> bool:
        """
        Vérifie si on peut recontacter le lead.

        Retourne True si on a au moins l'email OU le téléphone.
        """
        return self.email is not None or self.telephone is not None

    def champs_manquants(self) -> list[str]:
        """
        Retourne la liste des champs prioritaires manquants.

        Ordre de priorité métier marketing :
        1. message (comprendre le besoin) - OBLIGATOIRE
        2. email ou téléphone (follow-up) - OBLIGATOIRE
        3. nom (personnalisation) - OPTIONNEL

        Note : Le budget n'est PAS dans cette liste car c'est un bonus.
        Le chatbot peut le demander en fin de conversation si tout le reste est collecté.
        """
        manquants = []

        # Champs obligatoires
        if not self.message:
            manquants.append("message")

        # Au moins un moyen de contact obligatoire
        if not self.email and not self.telephone:
            manquants.append("contact")

        return manquants

    def a_moyen_contact_prioritaire(self) -> bool:
        """
        Vérifie si on a l'email (moyen de contact prioritaire).
        """
        return self.email is not None