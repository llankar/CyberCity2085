"""Bounded role promotions within an authored mission's enemy count."""

from dataclasses import dataclass

from .tactical_identity import profile_for_theme

ROLE_COST = {"grunt": 2, "heavy": 3, "elite": 4, "commander": 5}


@dataclass(frozen=True)
class EncounterComposition:
    roles: tuple[str, ...]
    budget: int

    @property
    def spent(self):
        return sum(ROLE_COST[role] for role in self.roles)


def compose_encounter(count, average_level, risk, theme):
    """Keep scripted headcount; spend only on a bounded set of role upgrades.

    These are composition points, not a cross-faction measure of damage or HP.
    """
    count = max(0, int(count))
    level = max(1, int(average_level))
    risk = max(1, min(10, int(risk)))
    bonus = min(count, count // 3 + (risk - 1) // 3 + (level - 1) // 3)
    budget = count * ROLE_COST["grunt"] + bonus
    roles = ["grunt"] * count
    profile = profile_for_theme(theme).key
    slots = min(count // 2, (count + 2) // 3)
    if profile == "starver":
        slots = min(slots, 1)  # A tide remains a pack, not a wall of heavy bodies.
    available = bonus
    preferences = []
    if level >= 7 and count >= 3:
        preferences.append("commander")
    if level >= 3:
        # A corporate leader needs an affordable heavy before another elite.
        elite_first = profile in {"raider", "novatek_hybrid"} or (profile == "mutant" and risk >= 7)
        first = "elite" if elite_first and level >= 4 else "heavy"
        preferences.extend([first, "elite" if level >= 4 and profile != "starver" else "heavy"] * slots)
    promoted = 0
    for role in preferences:
        if promoted >= slots:
            break
        cost = ROLE_COST[role] - ROLE_COST["grunt"]
        if cost <= available:
            roles[count - 1 - promoted] = role
            available -= cost
            promoted += 1
    return EncounterComposition(tuple(roles), budget)


def enemy_spawn_positions(count):
    """Unique fallback spawns; the battle adapter still fits them to map terrain."""
    initial = [(1152, 416), (1152, 352), (1088, 416), (1088, 352),
               (1024, 416), (1024, 352), (960, 416), (960, 352)]
    candidates = initial + [(x, y) for y in range(64, 673, 32)
                            for x in range(1152, 831, -32) if (x, y) not in initial]
    if count > len(candidates):
        raise ValueError(f"Encounter exceeds {len(candidates)} distinct fallback spawn cells")
    return tuple(candidates[:max(0, count)])
