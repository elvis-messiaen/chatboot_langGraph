# app/domain/interfaces/llm_service.py
"""Interface du service LLM pour la génération de texte."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any


class LLMService(ABC):
    """
    Interface définissant le contrat pour communiquer avec un modèle de langage.

    Cette interface sera implémentée par l'infrastructure (Azure OpenAI, etc.)
    Le domaine ne connaît que cette interface, pas le provider spécifique.
    """

    @abstractmethod
    def generer_reponse(
            self,
            messages: List[Dict[str, str]],
            temperature: float = 0.7,
            max_tokens: int = 500
    ) -> str:
        """
        Génère une réponse textuelle basée sur l'historique de messages.

        Args:
            messages: Liste de messages au format [{"role": "user", "content": "..."}]
            temperature: Contrôle la créativité (0.0 = déterministe, 1.0 = créatif)
            max_tokens: Nombre maximum de tokens dans la réponse

        Returns:
            str: La réponse générée par le modèle

        Raises:
            Exception si erreur d'appel au modèle
        """
        pass

    @abstractmethod
    def extraire_informations(
            self,
            texte: str,
            schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Extrait des informations structurées depuis un texte libre.

        Exemple : "Je m'appelle Jean, mon email est jean@example.com"
                  → {"nom": "Jean", "email": "jean@example.com"}

        Args:
            texte: Le texte brut à analyser
            schema: Le schéma JSON des informations à extraire

        Returns:
            Dict[str, Any]: Les informations extraites au format structuré
        """
        pass

    @abstractmethod
    def analyser_intention(self, message: str) -> str:
        """
        Analyse l'intention d'un message utilisateur.

        Exemples d'intentions :
        - "devis" : L'utilisateur veut un devis
        - "information" : L'utilisateur veut juste des infos
        - "plainte" : L'utilisateur a un problème

        Args:
            message: Le message utilisateur à analyser

        Returns:
            str: L'intention détectée
        """
        pass