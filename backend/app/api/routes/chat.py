# app/api/routes/chat.py
"""Routes API pour le chatbot."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.chat import ChatRequest, ChatResponse
from app.infrastructure.database.session import get_db
from app.infrastructure.repositories.lead_repository import SQLAlchemyLeadRepository
from app.infrastructure.llm.azure_openai import AzureOpenAIService
from app.services.langgraph.graph import creer_chatbot_graph, executer_chatbot

# Créer le router
router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
        request: ChatRequest,
        db: Session = Depends(get_db)
) -> ChatResponse:
    """
    Endpoint principal du chatbot.

    Reçoit un message utilisateur, l'exécute dans le graph LangGraph,
    et retourne la réponse du chatbot avec les métadonnées.

    Args:
        request: ChatRequest validé par Pydantic (session_id + message)
        db: Session de base de données (injectée par FastAPI)

    Returns:
        ChatResponse: Réponse du chatbot + métadonnées (score, infos manquantes...)

    Raises:
        HTTPException: En cas d'erreur serveur
    """
    try:
        # --- 1. Initialisation des services ---

        # Repository pour accéder à la DB
        repository = SQLAlchemyLeadRepository(db)

        # Service LLM (Azure OpenAI)
        llm_service = AzureOpenAIService()

        # --- 2. Création du graph LangGraph ---

        graph = creer_chatbot_graph(
            repository=repository,
            llm_service=llm_service
        )

        # --- 3. Exécution du chatbot ---

        final_state = executer_chatbot(
            graph=graph,
            session_id=request.session_id,
            message=request.message,
            nom=request.nom
        )

        # --- 4. Construction de la réponse ---

        response = ChatResponse(
            reponse=final_state.get("reponse_chatbot", "Désolé, une erreur est survenue."),
            lead_sauvegarde=final_state.get("lead_sauvegarde", False),
            score=final_state.get("score"),
            informations_manquantes=final_state.get("informations_manquantes", []),
            intention_detectee=final_state.get("intention")
        )

        return response

    except Exception as e:
        # Retourne une erreur 500 avec message
        raise HTTPException(
            status_code=500,
            detail=f"Erreur interne du serveur : {str(e)}"
        )