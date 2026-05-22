"""Post-battle outcome resolution for tactical engagements."""

from __future__ import annotations

import random
from typing import Callable

from .character import Character
from .narrative.temporary_scars import apply_temporary_scar_from_injury

CRITICAL_INJURY_RECOVERY_TURNS = 2
CAPTURED_RECOVERY_TURNS = 4


DEFEATED_AGENT_OUTCOMES = (
    "killed",
    "critically injured",
    "captured",
    "traumatized but extracted",
)


def resolve_defeated_agent_outcome(
    character: Character,
    *,
    remove_character: Callable[[Character], None],
    record_event: Callable[[str], None],
) -> str:
    """Apply and record a vertical-slice outcome for a downed agent."""
    outcome = random.choice(DEFEATED_AGENT_OUTCOMES)
    if outcome == "killed":
        character.history.append("Killed in action during a failed tactical engagement.")
        remove_character(character)
        record_event(f"{character.name} was killed in action.")
        return outcome

    character.stats.hp = max(1, character.stats.max_hp // 4)
    if outcome == "critically injured":
        character.recovery_turns = max(
            character.recovery_turns, CRITICAL_INJURY_RECOVERY_TURNS
        )
        character.injuries.append("Critical battle trauma")
        character.history.append(
            "Evacuated with critical injuries after being downed in battle. "
            f"Recovery required: {character.recovery_turns} turns."
        )
        scar = apply_temporary_scar_from_injury(character, "Critical battle trauma")
        record_event(
            f"{character.name} survived with critical injuries "
            f"and needs {character.recovery_turns} turns to recover."
        )
        if scar:
            record_event(
                f"{character.name} gains temporary scar '{scar['title']}' "
                f"for {scar['days_remaining']} days."
            )
    elif outcome == "captured":
        character.recovery_turns = max(character.recovery_turns, CAPTURED_RECOVERY_TURNS)
        character.history.append(
            "Captured by hostile forces after being downed in battle. "
            f"Recovery required: {character.recovery_turns} turns."
        )
        record_event(
            f"{character.name} was captured and cannot deploy for "
            f"{character.recovery_turns} turns."
        )
    else:
        character.trauma.append("Combat shock")
        character.history.append("Extracted alive but traumatized after being downed in battle.")
        record_event(f"{character.name} was extracted with lasting trauma.")
    return outcome
