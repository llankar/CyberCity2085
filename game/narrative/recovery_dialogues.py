"""Compact mentor/support dialogue generation for recovery room scenes."""

from __future__ import annotations

from dataclasses import dataclass, field

from ..character import Character

STRESS_TRIGGER_THRESHOLD = 65
MAX_DIALOGUES_PER_TICK = 3

_COMPLEMENTARY_ROLES = {
    frozenset({"samurai", "netrunner"}),
    frozenset({"medic", "samurai"}),
    frozenset({"medic", "heavy"}),
    frozenset({"netrunner", "scout"}),
}

_LINE_TEMPLATES = (
    "{mentor} stays with {partner} until the breathing steadies.",
    "{mentor} reminds {partner} that the squad holds together.",
    "{mentor} shares a calm silence with {partner} in the recovery room.",
)


@dataclass(frozen=True)
class RecoveryDialogue:
    """Neutral payload for later UI rendering."""

    pair: tuple[str, str]
    line: str
    stress_snapshot: dict[str, int]
    affinity_reason: str

    def to_output(self) -> dict:
        return {
            "line": self.line,
            "pair": list(self.pair),
            "stress_snapshot": dict(self.stress_snapshot),
            "affinity_reason": self.affinity_reason,
        }


@dataclass
class RecoveryNarrativeMemory:
    """Light persistence for anti-repetition across consecutive days."""

    last_day: int = 0
    last_pairs: list[tuple[str, str]] = field(default_factory=list)
    last_lines: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "last_day": self.last_day,
            "last_pairs": [list(pair) for pair in self.last_pairs],
            "last_lines": list(self.last_lines),
        }

    @classmethod
    def from_dict(cls, data: dict | None) -> "RecoveryNarrativeMemory":
        if not isinstance(data, dict):
            return cls()
        pairs = []
        for pair in data.get("last_pairs", []):
            if isinstance(pair, list) and len(pair) == 2:
                pairs.append((str(pair[0]), str(pair[1])))
        return cls(
            last_day=int(data.get("last_day", 0)),
            last_pairs=pairs,
            last_lines=[str(line) for line in data.get("last_lines", [])],
        )


def _pair_affinity_score(
    left: Character,
    right: Character,
    squad_by_agent: dict[str, str],
) -> tuple[int, str]:
    left_squad = squad_by_agent.get(left.name)
    right_squad = squad_by_agent.get(right.name)
    if left_squad and right_squad and left_squad == right_squad:
        return 3, "same_squad"

    if frozenset({left.role, right.role}) in _COMPLEMENTARY_ROLES:
        return 2, "complementary_roles"

    return 1, "baseline"


def generate_recovery_dialogues(
    agents: list[Character],
    recovery_state: dict,
) -> list[dict]:
    """Generate 0..N short support dialogues from stress/recovery context."""
    day = int(recovery_state.get("day", 0))
    max_dialogues = int(recovery_state.get("max_dialogues", MAX_DIALOGUES_PER_TICK))
    stress_threshold = int(
        recovery_state.get("stress_threshold", STRESS_TRIGGER_THRESHOLD)
    )
    squad_by_agent = dict(recovery_state.get("squad_by_agent", {}))
    memory = RecoveryNarrativeMemory.from_dict(recovery_state.get("memory"))

    stressed = [agent for agent in agents if agent.stress >= stress_threshold]
    if len(stressed) < 2 or max_dialogues <= 0:
        return []

    scored_pairs: list[tuple[int, str, Character, Character]] = []
    for i, left in enumerate(stressed):
        for right in stressed[i + 1 :]:
            score, reason = _pair_affinity_score(left, right, squad_by_agent)
            scored_pairs.append((score, reason, left, right))
    scored_pairs.sort(key=lambda item: (-item[0], -(item[2].stress + item[3].stress)))

    blocked_pairs = set(memory.last_pairs) if memory.last_day == day - 1 else set()
    blocked_lines = set(memory.last_lines) if memory.last_day == day - 1 else set()

    output: list[RecoveryDialogue] = []
    for score, reason, left, right in scored_pairs:
        if len(output) >= max_dialogues:
            break
        pair = (left.name, right.name)
        if pair in blocked_pairs:
            continue
        line = _LINE_TEMPLATES[len(output) % len(_LINE_TEMPLATES)].format(
            mentor=left.name,
            partner=right.name,
        )
        if line in blocked_lines:
            continue
        output.append(
            RecoveryDialogue(
                pair=pair,
                line=line,
                stress_snapshot={left.name: left.stress, right.name: right.stress},
                affinity_reason=reason,
            )
        )

    if not output:
        return []

    memory.last_day = day
    memory.last_pairs = [dialogue.pair for dialogue in output]
    memory.last_lines = [dialogue.line for dialogue in output]
    recovery_state["memory"] = memory.to_dict()

    return [dialogue.to_output() for dialogue in output]
