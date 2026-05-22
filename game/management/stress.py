"""Small strategic stress recovery rules for the management calendar."""

from __future__ import annotations

from dataclasses import dataclass

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

    recovery_amount = 2 if character.recovery_turns > 0 else 1
    next_value = max(0, current - recovery_amount)
    amount = current - next_value
    if amount <= 0:
        return StressRecoveryResult(changed=False, amount=0)

    character.stress = next_value
    return StressRecoveryResult(changed=True, amount=amount)
