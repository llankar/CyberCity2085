"""Irreversible fictional Starver infection carried by a campaign agent."""

TRANSMISSION_CHANCE = 0.005
INCUBATION_DAYS = 3


def infection_label(character):
    if getattr(character, "starver_transformed", False):
        return "STARVER — LOST TO THE SQUAD"
    days = getattr(character, "starver_infection_days", None)
    return f"INCURABLE INFECTION — {days}d" if days is not None else ""


def transmit_bite(attacker, defender, rng):
    from .character import Character
    from .enemy_themes import normalize_enemy_theme
    character = defender.character
    if (attacker.unit_type != "enemy" or normalize_enemy_theme(attacker.enemy_theme) != "starver"
            or not isinstance(character, Character) or defender.spec_ops_asset is not None
            or defender.health <= 0 or character.starver_transformed
            or character.starver_infection_days is not None):
        return False
    if rng() >= TRANSMISSION_CHANCE:
        return False
    character.starver_infection_days = INCUBATION_DAYS
    character.history.append("Starver bite: infection confirmed. No cure; conversion in 3 strategic days.")
    return True


def advance_infection(character):
    """Return a persistent narrative beat; HP healing never clears this state."""
    if character.starver_transformed or character.starver_infection_days is None or character.stats.hp <= 0:
        return None
    character.starver_infection_days = max(0, character.starver_infection_days - 1)
    if character.starver_infection_days > 0:
        return f"{character.name}: incurable Starver infection — {character.starver_infection_days} days until conversion."
    original_role = character.role
    character.starver_transformed = True
    character.role = "starver"
    text = f"{character.name} has become a Starver. Former {original_role}; permanently lost to the squad."
    character.history.append(text)
    return text
