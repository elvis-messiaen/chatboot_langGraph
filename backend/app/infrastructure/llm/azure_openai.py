# app/infrastructure/llm/azure_openai.py
"""Implémentation du LLMService avec Azure OpenAI."""

from typing import List, Dict, Any
import json
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from app.domain.interfaces.llm_service import LLMService
from app.core.config import settings


class AzureOpenAIService(LLMService):
    """
    Implémentation Azure OpenAI de l'interface LLMService.

    Utilise LangChain pour simplifier les appels à Azure OpenAI.
    """

    def __init__(self):
        """
        Initialise le client Azure OpenAI via LangChain.
        Configuration chargée depuis settings (variables d'environnement).
        """
        self.llm = AzureChatOpenAI(
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
            api_key=settings.AZURE_OPENAI_API_KEY,
            deployment_name=settings.AZURE_OPENAI_DEPLOYMENT,
            api_version=settings.AZURE_OPENAI_API_VERSION,
            temperature=0.7
        )

    def generer_reponse(
            self,
            messages: List[Dict[str, str]],
            temperature: float = 0.7,
            max_tokens: int = 500
    ) -> str:
        """
        Génère une réponse basée sur l'historique de messages.

        Convertit le format dict en objets LangChain Messages.
        """
        # Conversion dict → LangChain Messages
        langchain_messages = []
        for msg in messages:
            role = msg.get("role")
            content = msg.get("content", "")

            if role == "system":
                langchain_messages.append(SystemMessage(content=content))
            elif role == "user":
                langchain_messages.append(HumanMessage(content=content))
            elif role == "assistant":
                langchain_messages.append(AIMessage(content=content))

        # Configure le LLM avec les paramètres
        llm_configured = self.llm.bind(temperature=temperature, max_completion_tokens=max_tokens)

        # Appel au LLM
        response = llm_configured.invoke(langchain_messages)

        return response.content

    def extraire_informations(
            self,
            texte: str,
            schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Extrait des informations structurées depuis un texte libre.

        Utilise un prompt spécialisé pour l'extraction.
        """
        # Construction du prompt d'extraction
        schema_json = json.dumps(schema, ensure_ascii=False, indent=2)

        prompt = f"""Tu es un assistant spécialisé dans l'extraction d'informations.

Texte à analyser :
{texte}

Schéma des informations à extraire :
{schema_json}

Instructions :
- Extrais uniquement les informations présentes dans le texte
- Si une information n'est pas présente, utilise null
- Retourne UNIQUEMENT un objet JSON valide, sans texte additionnel
- Respecte exactement le schéma fourni

Réponds avec le JSON :"""

        messages = [
            SystemMessage(content="Tu es un assistant d'extraction de données précis."),
            HumanMessage(content=prompt)
        ]

        # Appel avec temperature=0 pour plus de déterminisme
        llm_configured = self.llm.bind(temperature=0, max_completion_tokens=300)
        response = llm_configured.invoke(messages)

        # Parse du JSON retourné
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            # Fallback si le LLM n'a pas retourné du JSON valide
            return {key: None for key in schema.keys()}

    def analyser_intention(self, message: str) -> str:
        """
        Analyse l'intention d'un message utilisateur.

        Catégorise le message en intention prédéfinie.
        """
        prompt = f"""Analyse l'intention du message suivant :

Message : "{message}"

Intentions possibles :
- devis : L'utilisateur veut obtenir un devis, une proposition commerciale
- information : L'utilisateur cherche des informations générales
- rendez_vous : L'utilisateur veut planifier un rendez-vous ou un appel
- question_technique : Question sur un produit/service spécifique
- plainte : L'utilisateur exprime une insatisfaction
- autre : Aucune intention claire

Réponds avec UN SEUL MOT parmi les intentions ci-dessus."""

        messages = [
            SystemMessage(content="Tu es un classificateur d'intentions précis."),
            HumanMessage(content=prompt)
        ]

        llm_configured = self.llm.bind(temperature=0, max_completion_tokens=50)
        response = llm_configured.invoke(messages)

        # Nettoie la réponse (enlève espaces, minuscules)
        intention = response.content.strip().lower()

        # Validation : retourne "autre" si intention non reconnue
        intentions_valides = ["devis", "information", "rendez_vous", "question_technique", "plainte", "autre"]
        return intention if intention in intentions_valides else "autre"