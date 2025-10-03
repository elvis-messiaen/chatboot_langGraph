# app/services/langgraph/nodes.py
"""Nodes du graph LangGraph pour le chatbot."""

from typing import Dict, Any
from sqlalchemy.orm import Session
from app.services.langgraph.state import ChatState
from app.domain.entities.lead_entity import LeadEntity
from app.domain.interfaces.lead_repository import LeadRepository
from app.domain.interfaces.llm_service import LLMService
from app.services import extraction, scoring


def charger_lead_node(
        state: ChatState,
        repository: LeadRepository
) -> ChatState:
    """
    Node 1 : Charge le lead existant depuis la DB (ou crée un nouveau).

    Flow :
    1. Récupère session_id depuis state
    2. Cherche lead en DB via repository
    3. Si trouvé → charge dans state
    4. Sinon → crée nouveau Lead avec session_id

    Args:
        state: L'état actuel
        repository: Repository pour accéder à la DB

    Returns:
        ChatState: État avec lead chargé
    """
    session_id = state["session_id"]

    # Cherche lead existant
    lead = repository.obtenir_par_session(session_id)

    if lead is None:
        # Première visite : créer nouveau lead
        lead = LeadEntity(
            session_id=session_id,
            message=""
        )

    # Met le lead dans le state
    state["lead"] = lead
    state["lead_id"] = lead.id

    return state


def analyser_intention_node(
        state: ChatState,
        llm_service: LLMService
) -> ChatState:
    """
    Node 2 : Analyse l'intention du message utilisateur.

    Utilise le LLM pour classifier l'intention.
    Exemples : "devis", "information", "plainte"

    Args:
        state: L'état actuel
        llm_service: Service LLM pour l'analyse

    Returns:
        ChatState: État avec intention détectée
    """
    message = state["message_utilisateur"]

    try:
        # Appel au LLM pour détecter l'intention
        intention = llm_service.analyser_intention(message)
        state["intention"] = intention
    except Exception as e:
        # En cas d'erreur, on continue sans intention
        state["intention"] = "autre"
        state["erreur"] = f"Erreur analyse intention : {str(e)}"

    return state


def extraire_infos_node(
        state: ChatState,
        llm_service: LLMService
) -> ChatState:
    """
    Node 3 : Extrait les informations structurées du message.

    Stratégie hybride :
    1. Extraction regex (rapide, gratuit)
    2. Extraction LLM (précis, payant) en complément
    3. Combine les deux résultats

    Args:
        state: L'état actuel
        llm_service: Service LLM pour extraction

    Returns:
        ChatState: État avec infos_extraites rempli
    """
    message = state["message_utilisateur"]

    # Extraction LLM avec schema
    schema = {
        "nom": "string",
        "email": "string",
        "telephone": "string",
        "budget": "string"
    }

    try:
        # Appel LLM pour extraction structurée
        extractions_llm = llm_service.extraire_informations(message, schema)
    except Exception as e:
        extractions_llm = None
        state["erreur"] = f"Erreur extraction LLM : {str(e)}"

    # Combine regex + LLM
    infos = extraction.combiner_extractions(message, extractions_llm)

    state["infos_extraites"] = infos

    return state


def mettre_a_jour_lead_node(state: ChatState) -> ChatState:
    """
    Node 4 : Met à jour l'entité Lead avec les infos extraites.

    Flow :
    1. Récupère lead et infos_extraites du state
    2. Merge les nouvelles infos dans le lead
    3. Concatène le message à l'historique
    4. Remet le lead dans le state

    Args:
        state: L'état actuel

    Returns:
        ChatState: État avec lead mis à jour
    """
    lead = state["lead"]
    infos = state["infos_extraites"]
    message = state["message_utilisateur"]

    # Met à jour uniquement les champs non-None
    if infos.get("nom") and not lead.nom:
        lead.nom = infos["nom"]

    if infos.get("email") and not lead.email:
        lead.email = infos["email"]

    if infos.get("telephone") and not lead.telephone:
        lead.telephone = infos["telephone"]

    if infos.get("budget") and not lead.budget:
        lead.budget = infos["budget"]

    # Concatène le message
    if lead.message:
        lead.message += f"\n{message}"
    else:
        lead.message = message

    # Remet le lead dans le state
    state["lead"] = lead

    return state


def sauvegarder_lead_node(
        state: ChatState,
        repository: LeadRepository
) -> ChatState:
    """
    Node 5 : Sauvegarde le lead en base de données.

    Flow :
    1. Récupère lead du state
    2. Si lead.id existe → UPDATE
    3. Sinon → INSERT
    4. Met à jour state avec lead sauvegardé (avec ID)

    Args:
        state: L'état actuel
        repository: Repository pour sauvegarder

    Returns:
        ChatState: État avec lead sauvegardé
    """
    lead = state["lead"]

    try:
        if lead.id is None:
            # Nouveau lead : créer
            lead = repository.creer(lead)
        else:
            # Lead existant : mettre à jour
            lead = repository.mettre_a_jour(lead)

        state["lead"] = lead
        state["lead_id"] = lead.id
        state["lead_sauvegarde"] = True

    except Exception as e:
        state["lead_sauvegarde"] = False
        state["erreur"] = f"Erreur sauvegarde : {str(e)}"

    return state


def calculer_score_node(state: ChatState) -> ChatState:
    """
    Node 6 : Calcule le score de qualification du lead.

    Utilise les services de scoring pour :
    1. Calculer score 0-100
    2. Classifier (chaud/tiède/froid)
    3. Identifier champs manquants

    Args:
        state: L'état actuel

    Returns:
        ChatState: État avec score et classification
    """
    lead = state["lead"]

    # Calcul du score
    score = scoring.calculer_score_lead(lead)
    lead.score = score
    state["score"] = score

    # Classification
    classification = scoring.classifier_lead(score)
    state["classification"] = classification

    # Champs manquants
    manquants = lead.champs_manquants()
    state["informations_manquantes"] = manquants

    # Met à jour le lead avec le score
    state["lead"] = lead

    return state


def decider_prochaine_action_node(state: ChatState) -> ChatState:
    """
    Node 7 : Décide de la prochaine action (routing).

    Logique de décision :
    1. Si plainte détectée → escalader_support
    2. Si lead complet → finaliser
    3. Sinon → continuer_qualification

    Args:
        state: L'état actuel

    Returns:
        ChatState: État avec prochaine_action définie
    """
    lead = state["lead"]

    # Détection de plainte
    if lead.message and scoring.detecter_mots_negatifs(lead.message):
        state["prochaine_action"] = "escalader_support"
        return state

    # Lead complet
    if lead.est_complet() and lead.est_recontactable():
        state["prochaine_action"] = "finaliser"
        return state

    # Par défaut : continuer
    state["prochaine_action"] = "continuer_qualification"
    return state


def generer_reponse_node(
        state: ChatState,
        llm_service: LLMService
) -> ChatState:
    """
    Node 8 : Génère la réponse du chatbot.

    Logique :
    1. Répond TOUJOURS à la question de l'utilisateur
    2. Si des infos manquent, demande de manière naturelle et optionnelle à la fin

    Args:
        state: L'état actuel
        llm_service: Service LLM pour génération

    Returns:
        ChatState: État avec reponse_chatbot générée
    """
    lead = state["lead"]
    prochaine_action = state["prochaine_action"]
    manquants = state["informations_manquantes"]

    # Construction du prompt système
    if prochaine_action == "escalader_support":
        prompt_systeme = """Tu es un assistant empathique.
L'utilisateur semble avoir un problème. Excuse-toi et propose de le mettre en relation avec le support."""

    elif prochaine_action == "finaliser":
        nom_display = f" {lead.nom}" if lead.nom else ""
        prompt_systeme = f"""Tu es un assistant commercial expert et sympathique.
Réponds à la question de l'utilisateur de manière complète et professionnelle.
L'utilisateur{nom_display} a fourni son contact ({lead.email or lead.telephone}).
À la fin de ta réponse, remercie-le et confirme qu'il sera recontacté rapidement."""

    else:  # continuer_qualification
        # Toujours répondre à la question d'abord
        instruction_contact = ""

        if "contact" in manquants:
            # Demande le contact de manière naturelle
            instruction_contact = """

À la fin de ta réponse, demande poliment un moyen de contact (email ou téléphone) pour un suivi personnalisé."""

        prompt_systeme = f"""Tu es un assistant commercial professionnel spécialisé dans les services numériques et solutions web.

RÈGLES DE RÉDACTION :
- Ton professionnel et concis
- Structuré avec des paragraphes courts
- Pas d'exclamations excessives
- Réponses claires et directes{instruction_contact}

Réponds de manière complète et utile à la question de l'utilisateur."""

    # Construction de l'historique
    messages = [
        {"role": "system", "content": prompt_systeme}
    ]

    # Ajoute messages précédents si existent
    if state.get("messages"):
        messages.extend(state["messages"])

    # Ajoute le message actuel
    messages.append({
        "role": "user",
        "content": state["message_utilisateur"]
    })

    try:
        # Génération de la réponse
        reponse = llm_service.generer_reponse(
            messages,
            temperature=0.7,
            max_tokens=300
        )
        state["reponse_chatbot"] = reponse

        # Met à jour l'historique
        messages.append({
            "role": "assistant",
            "content": reponse
        })
        state["messages"] = messages

    except Exception as e:
        state["reponse_chatbot"] = "Désolé, j'ai rencontré une erreur. Peux-tu répéter ?"
        state["erreur"] = f"Erreur génération réponse : {str(e)}"

    return state