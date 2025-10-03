# app/services/scoring.py
"""Services de scoring et qualification des leads."""

from typing import Optional
from app.domain.entities.lead_entity import LeadEntity


def calculer_score_lead(lead: LeadEntity) -> int:
    """
    Calcule le score de qualification d'un lead (0-100).

    Critères de scoring :
    - Complétude des informations (30 pts)
    - Urgence détectée dans le message (40 pts)
    - Budget mentionné (20 pts)
    - Contact prioritaire (email) (10 pts)

    Args:
        lead: L'entité Lead à scorer

    Returns:
        int: Score entre 0 et 100
    """
    score = 0

    # 1. Complétude des informations (30 points max)
    score += _scorer_completude(lead)

    # 2. Urgence détectée (40 points max)
    score += _scorer_urgence(lead)

    # 3. Budget mentionné (20 points max)
    score += _scorer_budget(lead)

    # 4. Contact prioritaire (10 points max)
    score += _scorer_contact(lead)

    # Assure que le score reste dans [0, 100]
    return min(100, max(0, score))


def _scorer_completude(lead: LeadEntity) -> int:
    """
    Score basé sur la complétude des informations.

    Logique :
    - Nom : +10 pts
    - Message/besoin : +10 pts
    - Email : +5 pts
    - Téléphone : +5 pts

    Max : 30 points
    """
    score = 0

    if lead.nom:
        score += 10

    if lead.message:
        score += 10

    if lead.email:
        score += 5

    if lead.telephone:
        score += 5

    return score


def _scorer_urgence(lead: LeadEntity) -> int:
    """
    Score basé sur les marqueurs d'urgence dans le message.

    Mots-clés d'urgence :
    - urgent, rapidement, vite : +40 pts (très chaud)
    - aujourd'hui, demain, cette semaine : +30 pts (chaud)
    - bientôt, prochainement : +20 pts (tiède)
    - devis, proposition : +15 pts

    Max : 40 points (prend le plus haut)
    """
    if not lead.message:
        return 0

    message_lower = lead.message.lower()

    # Mots-clés très urgents
    mots_tres_urgent = ['urgent', 'rapidement', 'vite', 'immédiat', 'tout de suite']
    if any(mot in message_lower for mot in mots_tres_urgent):
        return 40

    # Mots-clés urgents
    mots_urgent = ['aujourd\'hui', 'demain', 'cette semaine', 'au plus vite']
    if any(mot in message_lower for mot in mots_urgent):
        return 30

    # Mots-clés moyennement urgents
    mots_moyen = ['bientôt', 'prochainement', 'dans les prochains jours']
    if any(mot in message_lower for mot in mots_moyen):
        return 20

    # Intention commerciale
    mots_commercial = ['devis', 'proposition', 'tarif', 'prix', 'acheter', 'commander']
    if any(mot in message_lower for mot in mots_commercial):
        return 15

    return 0


def _scorer_budget(lead: LeadEntity) -> int:
    """
    Score basé sur la mention d'un budget.

    Logique :
    - Budget mentionné : +20 pts
    - Pas de budget : 0 pt

    Max : 20 points
    """
    if lead.budget:
        return 20
    return 0


def _scorer_contact(lead: LeadEntity) -> int:
    """
    Score basé sur le moyen de contact prioritaire.

    Logique :
    - Email disponible : +10 pts (contact prioritaire en marketing)
    - Seulement téléphone : +5 pts
    - Aucun contact : 0 pt

    Max : 10 points
    """
    if lead.email:
        return 10
    elif lead.telephone:
        return 5
    return 0


def classifier_lead(score: int) -> str:
    """
    Classifie un lead selon son score.

    Classification :
    - 0-30 : froid (peu intéressé)
    - 31-60 : tiède (intéressé mais pas urgent)
    - 61-100 : chaud (urgent et qualifié)

    Args:
        score: Le score du lead (0-100)

    Returns:
        str: Classification ("froid", "tiède", "chaud")
    """
    if score >= 61:
        return "chaud"
    elif score >= 31:
        return "tiède"
    else:
        return "froid"


def detecter_mots_negatifs(texte: str) -> bool:
    """
    Détecte des marqueurs négatifs dans le message.

    Utilité : identifier les plaintes, insatisfactions.

    Args:
        texte: Le message à analyser

    Returns:
        bool: True si marqueurs négatifs détectés
    """
    if not texte:
        return False

    texte_lower = texte.lower()

    mots_negatifs = [
        'problème', 'bug', 'erreur', 'ne fonctionne pas',
        'déçu', 'insatisfait', 'plainte', 'réclamation',
        'mauvais', 'nul', 'incompétent'
    ]

    return any(mot in texte_lower for mot in mots_negatifs)


def suggerer_action(lead: LeadEntity) -> str:
    """
    Suggère une action marketing basée sur le lead.

    Décisions :
    - Lead chaud (score > 70) : Relance immédiate
    - Lead tiède (score 40-70) : Relance sous 48h
    - Lead froid (score < 40) : Nurturing email
    - Mots négatifs : Escalade support

    Args:
        lead: L'entité Lead

    Returns:
        str: Action recommandée
    """
    if not lead.score:
        return "Continuer la qualification"

    # Détection de plainte prioritaire
    if lead.message and detecter_mots_negatifs(lead.message):
        return "Escalader au support client"

    # Basé sur le score
    classification = classifier_lead(lead.score)

    if classification == "chaud":
        if lead.est_recontactable():
            return "Relance commerciale immédiate (appel ou email)"
        else:
            return "Continuer la conversation pour obtenir contact"

    elif classification == "tiède":
        if lead.est_recontactable():
            return "Relance commerciale sous 48h"
        else:
            return "Proposer de laisser contact pour devis"

    else:  # froid
        if lead.est_recontactable():
            return "Ajouter à campagne nurturing (newsletter)"
        else:
            return "Lead à faible priorité, pas d'action immédiate"