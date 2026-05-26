"""Small strategic stress recovery rules for the management calendar."""

from __future__ import annotations

from dataclasses import dataclass

from ..agents.sheet_calculations import compute_derived_stats
from ..character import Character


@dataclass(frozen=True)
class StressRecoveryResult:
    """Result of one daily strategic stress recovery tick."""

    changed: bool
    amount: int


def daily_stress_recovery(character: Character) -> StressRecoveryResult:
    """Apply one day of stress relief based on current agent condition.

    Recovery is intentionally conservative so mission-level stress remains meaningful:
    - Agents in medical recovery decompress faster from mandatory downtime.
    - Active agents recover slowly to avoid erasing emotional consequences.
    """
    current = max(0, min(100, int(character.stress)))
    if current <= 0:
        return StressRecoveryResult(changed=False, amount=0)

    derived = compute_derived_stats(
        character.attributes,
        character.skills,
        {},
        "steady" if current < 35 else "rattled" if current < 65 else "frayed" if current < 85 else "breaking",
    )
    base_recovery = max(1, int(derived.get("recovery_rate", 1)))
    recovery_amount = base_recovery + (1 if character.recovery_turns > 0 else 0)
    next_value = max(0, current - recovery_amount)
    amount = current - next_value
    if amount <= 0:
        return StressRecoveryResult(changed=False, amount=0)

    character.stress = next_value
    return StressRecoveryResult(changed=True, amount=amount)
