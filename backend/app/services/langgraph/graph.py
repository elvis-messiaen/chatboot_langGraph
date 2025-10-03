# app/services/langgraph/graph.py
"""Définition et construction du graph LangGraph."""

from typing import Literal
from langgraph.graph import StateGraph, END
from app.services.langgraph.state import ChatState, creer_state_initial
from app.services.langgraph import nodes
from app.domain.interfaces.lead_repository import LeadRepository
from app.domain.interfaces.llm_service import LLMService


def creer_chatbot_graph(
        repository: LeadRepository,
        llm_service: LLMService
) -> StateGraph:
    """
    Crée et configure le graph LangGraph pour le chatbot.

    Architecture du graph :

    START
      ↓
    charger_lead → analyser_intention → extraire_infos
      ↓
    mettre_a_jour_lead → sauvegarder_lead → calculer_score
      ↓
    decider_action → generer_reponse
      ↓
    END

    Args:
        repository: Repository pour accéder à la DB
        llm_service: Service LLM pour génération/analyse

    Returns:
        StateGraph: Le graph compilé prêt à être exécuté
    """

    # Créer le graph avec le type de state
    workflow = StateGraph(ChatState)

    # --- Ajouter les nodes ---

    # Node 1 : Charger le lead existant ou créer nouveau
    workflow.add_node(
        "charger_lead",
        lambda state: nodes.charger_lead_node(state, repository)
    )

    # Node 2 : Analyser l'intention du message
    workflow.add_node(
        "analyser_intention",
        lambda state: nodes.analyser_intention_node(state, llm_service)
    )

    # Node 3 : Extraire les informations structurées
    workflow.add_node(
        "extraire_infos",
        lambda state: nodes.extraire_infos_node(state, llm_service)
    )

    # Node 4 : Mettre à jour l'entité Lead
    workflow.add_node(
        "mettre_a_jour_lead",
        nodes.mettre_a_jour_lead_node
    )

    # Node 5 : Sauvegarder en base de données
    workflow.add_node(
        "sauvegarder_lead",
        lambda state: nodes.sauvegarder_lead_node(state, repository)
    )

    # Node 6 : Calculer le score de qualification
    workflow.add_node(
        "calculer_score",
        nodes.calculer_score_node
    )

    # Node 7 : Décider de la prochaine action
    workflow.add_node(
        "decider_action",
        nodes.decider_prochaine_action_node
    )

    # Node 8 : Générer la réponse du chatbot
    workflow.add_node(
        "generer_reponse",
        lambda state: nodes.generer_reponse_node(state, llm_service)
    )

    # --- Définir les edges (ordre d'exécution) ---

    # Point d'entrée du graph
    workflow.set_entry_point("charger_lead")

    # Flux séquentiel principal
    workflow.add_edge("charger_lead", "analyser_intention")
    workflow.add_edge("analyser_intention", "extraire_infos")
    workflow.add_edge("extraire_infos", "mettre_a_jour_lead")
    workflow.add_edge("mettre_a_jour_lead", "sauvegarder_lead")
    workflow.add_edge("sauvegarder_lead", "calculer_score")
    workflow.add_edge("calculer_score", "decider_action")
    workflow.add_edge("decider_action", "generer_reponse")

    # Point de sortie : toujours terminer après génération de réponse
    workflow.add_edge("generer_reponse", END)

    # Compiler le graph
    return workflow.compile()


def executer_chatbot(
        graph: StateGraph,
        session_id: str,
        message: str,
        nom: str = None
) -> ChatState:
    """
    Exécute le chatbot pour un message donné.

    Flow :
    1. Crée l'état initial
    2. Exécute le graph
    3. Retourne l'état final avec la réponse

    Args:
        graph: Le graph LangGraph compilé
        session_id: Identifiant de session
        message: Message de l'utilisateur
        nom: Nom de l'utilisateur (optionnel)

    Returns:
        ChatState: État final après exécution complète du graph
    """
    # Créer l'état initial
    initial_state = creer_state_initial(session_id, message, nom)

    # Exécuter le graph
    final_state = graph.invoke(initial_state)

    return final_state