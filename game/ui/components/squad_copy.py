"""Localize legacy squad-modal chrome without changing authored agent content."""

_LABELS = {
    "RECRUITMENT WINDOW": "RECRUTEMENT",
    "HIRE": "ENGAGER",
    "DOSSIER PORTRAIT": "PORTRAIT DU DOSSIER",
    "ATTRIBUTES": "CARACTÉRISTIQUES",
    "READINESS": "ÉTAT OPÉRATIONNEL",
    "SKILLS": "COMPÉTENCES",
    "SPEND": "AMÉLIORER",
    "OWNED": "ACQUIS",
    "UNLOCK": "DÉBLOQUER",
    "LOCKED": "VERROUILLÉ",
    "FIREARMS": "ARMES À FEU",
    "CLOSE COMBAT": "CORPS À CORPS",
    "TACTICS": "TACTIQUE",
    "TECH": "TECHNIQUE",
    "MEDICINE": "MÉDECINE",
    "INFLUENCE": "INFLUENCE",
    "STEALTH": "DISCRÉTION",
    "COMPOSURE": "SANG-FROID",
    "PSYCHOKINESIS": "PSYCHOKINÉSIE",
    "CRYOKINESIS": "CRYOKINÉSIE",
    "TELEPATHY": "TÉLÉPATHIE",
    "PYROKINESIS": "PYROKINÉSIE",
    "ESC closes this sheet.": "ÉCHAP ferme cette fiche.",
}
_REPLACEMENTS = {
    "LEVEL ": "NIVEAU ",
    "Pending points ": "Points disponibles ",
    "Talent points ": "Points de talent ",
    "Recovery ": "Récupération ",
    "Stress cap ": "Seuil de stress ",
    "Role ": "Classe ",
    "SPECIALIZATION": "SPÉCIALISATION",
    "RANK  ": "RANG  ",
    "(attr)": "(caract.)",
    "(rank)": "(rang)",
    "AVAILABLE AGENTS": "AGENTS DISPONIBLES",
    "FUNDS": "FONDS",
    "N REFRESHES": "N : ACTUALISER",
    "ESC CLOSES": "ÉCHAP : FERMER",
    "Click a stat or skill card to spend 1 pending point": "Cliquez sur une caractéristique ou compétence pour dépenser un point",
    " remaining": " restants",
    "Talent points:": "Points de talent :",
}


def localized_squad_copy(text, language):
    value = str(text)
    if language != "fr":
        return value
    if value in _LABELS:
        return _LABELS[value]
    for source, target in _REPLACEMENTS.items():
        value = value.replace(source, target)
    return value


def draw_localized_squad_text(text, *args, language="fr", **kwargs):
    import arcade

    return arcade.draw_text(localized_squad_copy(text, language), *args, **kwargs)


def notification_summary(text):
    """Keep player-facing outcomes, omit internal action/result routing fields."""
    if " | Impact: " in text:
        return text.split(" | Impact: ", 1)[1].split(" | Next: ", 1)[0]
    return text.partition("] ")[2] or text
