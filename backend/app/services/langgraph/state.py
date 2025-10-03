# app/services/langgraph/state.py
"""Définition de l'état du graph LangGraph."""

from typing import TypedDict, Optional, List, Dict, Any
from app.domain.entities.lead_entity import LeadEntity


class ChatState(TypedDict, total=False):
    """
    État partagé entre tous les nodes du graph LangGraph.

    Cet état est la "mémoire" du chatbot pendant une conversation.
    Chaque node peut lire et modifier cet état.

    Utilise TypedDict pour type safety + documentation.
    total=False permet des champs optionnels.
    """

    # --- Conversation ---
    messages: List[Dict[str, str]]
    """
    Historique complet de la conversation.
    Format: [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
    """

    message_utilisateur: str
    """Dernier message envoyé par l'utilisateur (pour faciliter l'accès)."""

    reponse_chatbot: str
    """Réponse générée par le chatbot (à renvoyer au frontend)."""

    # --- Identification ---
    session_id: str
    """Identifiant unique de la session (UUID généré frontend)."""

    # --- Lead ---
    lead: Optional[LeadEntity]
    """
    Entité LeadEntity du domaine.
    None si première visite, LeadEntity existant sinon.
    """

    lead_id: Optional[int]
    """ID du lead en base de données (après sauvegarde)."""

    # --- Analyse ---
    intention: Optional[str]
    """
    Intention détectée du message utilisateur.
    Exemples: "devis", "information", "plainte"
    """

    infos_extraites: Dict[str, Optional[str]]
    """
    Informations extraites du dernier message.
    Format: {"nom": "Jean", "email": "jean@...", "telephone": None, "budget": None}
    """

    # --- Qualification ---
    score: Optional[int]
    """Score de qualification du lead (0-100)."""

    classification: Optional[str]
    """Classification du lead : "chaud", "tiède", "froid"."""

    informations_manquantes: List[str]
    """
    Liste des champs encore manquants.
    Exemples: ["email", "contact"]
    """

    # --- Routing ---
    prochaine_action: str
    """
    Décision de routing pour le graph.
    Exemples: "continuer_qualification", "finaliser", "escalader_support"
    """

    # --- Métadonnées ---
    erreur: Optional[str]
    """Message d'erreur si quelque chose a échoué."""

    lead_sauvegarde: bool
    """Indique si le lead a été sauvegardé avec succès."""


def creer_state_initial(session_id: str, message: str, nom: str = None) -> ChatState:
    """
    Crée un état initial pour une nouvelle conversation ou un nouveau message.

    Args:
        session_id: Identifiant de session
        message: Message de l'utilisateur
        nom: Nom de l'utilisateur (optionnel)

    Returns:
        ChatState: État initial avec valeurs par défaut
    """
    # Si le nom est fourni, on le met déjà dans infos_extraites
    infos_extraites = {}
    if nom and nom.strip():
        infos_extraites["nom"] = nom.strip()

    return ChatState(
        messages=[],
        message_utilisateur=message,
        reponse_chatbot="",
        session_id=session_id,
        lead=None,
        lead_id=None,
        intention=None,
        infos_extraites=infos_extraites,
        score=None,
        classification=None,
        informations_manquantes=[],
        prochaine_action="continuer_qualification",
        erreur=None,
        lead_sauvegarde=False
    )