# app/services/extraction.py
"""Services d'extraction d'informations depuis du texte libre."""

import re
from typing import Optional, Dict, Any


def extraire_email(texte: str) -> Optional[str]:
    """
    Extrait une adresse email depuis un texte.

    Utilise une regex robuste pour détecter les emails.

    Args:
        texte: Le texte à analyser

    Returns:
        Optional[str]: L'email trouvé ou None

    Examples:
        >>> extraire_email("Mon email est jean@example.com")
        'jean@example.com'
        >>> extraire_email("Pas d'email ici")
        None
    """
    if not texte:
        return None

    # Pattern regex pour email
    # Explications :
    # [a-zA-Z0-9._%+-]+ : partie locale (avant @)
    # @ : arobase obligatoire
    # [a-zA-Z0-9.-]+ : domaine
    # \. : point obligatoire
    # [a-zA-Z]{2,} : extension (2+ lettres)
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'

    match = re.search(pattern, texte, re.IGNORECASE)

    if match:
        email = match.group(0).lower()
        # Validation supplémentaire : pas de double @
        if email.count('@') == 1:
            return email

    return None


def extraire_telephone(texte: str) -> Optional[str]:
    """
    Extrait un numéro de téléphone depuis un texte.

    Supporte formats français :
    - 06 12 34 56 78
    - 0612345678
    - +33 6 12 34 56 78
    - +33612345678

    Args:
        texte: Le texte à analyser

    Returns:
        Optional[str]: Le numéro trouvé (formaté) ou None
    """
    if not texte:
        return None

    # Patterns possibles pour téléphone français
    patterns = [
        # Format international : +33 6 12 34 56 78 ou +33612345678
        r'\+33\s*[1-9](?:\s*\d{2}){4}',
        # Format national : 06 12 34 56 78 ou 0612345678
        r'0[1-9](?:\s*\d{2}){4}',
    ]

    for pattern in patterns:
        match = re.search(pattern, texte)
        if match:
            # Nettoie le numéro (enlève espaces)
            numero = match.group(0).replace(' ', '')
            return numero

    return None


def extraire_budget(texte: str) -> Optional[str]:
    """
    Extrait un montant de budget depuis un texte.

    Détecte :
    - 5000€, 5000 euros, 5000 EUR
    - 5k€, 5K
    - entre 3000 et 8000€

    Args:
        texte: Le texte à analyser

    Returns:
        Optional[str]: Le budget extrait (texte brut) ou None
    """
    if not texte:
        return None

    texte_lower = texte.lower()

    # Pattern : montant + devise
    # Exemples : 5000€, 5000 euros, 5k€
    patterns = [
        # Montant avec k/K (milliers)
        r'\d+\s?[kK]\s?(?:€|euros?|eur)?',
        # Montant simple avec devise
        r'\d+(?:\s?\d{3})*\s?(?:€|euros?|eur)',
        # Fourchette : entre X et Y
        r'entre\s+\d+\s+et\s+\d+\s?(?:€|euros?|eur)?',
    ]

    for pattern in patterns:
        match = re.search(pattern, texte_lower)
        if match:
            return match.group(0)

    return None


def extraire_nom(texte: str) -> Optional[str]:
    """
    Extrait un nom depuis un texte.

    Détecte :
    - "Je m'appelle Jean"
    - "Mon nom est Marie Dupont"
    - "C'est Paul"

    Note : Cette fonction est basique. Pour une extraction robuste,
    utiliser le LLM (méthode extraire_informations du LLMService).

    Args:
        texte: Le texte à analyser

    Returns:
        Optional[str]: Le nom extrait ou None
    """
    if not texte:
        return None

    texte_lower = texte.lower()

    # Patterns d'introduction de nom
    patterns = [
        r"(?:je m'appelle|je suis|mon nom est|c'est)\s+([A-ZÀ-ÖØ-öø-ÿ][a-zà-öø-ÿ]+(?:\s+[A-ZÀ-ÖØ-öø-ÿ][a-zà-öø-ÿ]+)?)",
    ]

    for pattern in patterns:
        match = re.search(pattern, texte, re.IGNORECASE)
        if match:
            nom = match.group(1).strip()
            # Validation : au moins 2 caractères
            if len(nom) >= 2:
                return nom.title()  # Capitalise : "jean" → "Jean"

    return None


def nettoyer_texte(texte: str) -> str:
    """
    Nettoie un texte : supprime espaces multiples, trim, etc.

    Args:
        texte: Le texte à nettoyer

    Returns:
        str: Le texte nettoyé
    """
    if not texte:
        return ""

    # Supprime espaces multiples
    texte = re.sub(r'\s+', ' ', texte)

    # Trim
    texte = texte.strip()

    return texte


def combiner_extractions(
        texte: str,
        extractions_llm: Optional[Dict[str, Any]] = None
) -> Dict[str, Optional[str]]:
    """
    Combine extractions regex + LLM pour robustesse maximale.

    Stratégie :
    1. Extrait avec regex (rapide, gratuit)
    2. Si échec, utilise extraction LLM (si fournie)

    Args:
        texte: Le texte à analyser
        extractions_llm: Résultat optionnel de l'extraction LLM

    Returns:
        Dict avec les champs : nom, email, telephone, budget
    """
    resultat = {
        "nom": None,
        "email": None,
        "telephone": None,
        "budget": None
    }

    # Extraction regex (gratuit, rapide)
    resultat["nom"] = extraire_nom(texte)
    resultat["email"] = extraire_email(texte)
    resultat["telephone"] = extraire_telephone(texte)
    resultat["budget"] = extraire_budget(texte)

    # Si extraction LLM fournie, on complète les trous
    if extractions_llm:
        for cle in resultat.keys():
            if resultat[cle] is None and extractions_llm.get(cle):
                resultat[cle] = extractions_llm[cle]

    return resultat