"""Small, inspectable corporate command links and non-stacking accuracy support."""

from contextlib import contextmanager

from .battlefield import trace_sight_line
from .tactical_identity import profile_for_theme

COMMAND_RADIUS = 4 * 32
CORPORATE_DOCTRINES = {"corp_37", "corp_samurai"}


def command_link_active(unit, commander, enemies, cover_nodes=None):
    """A living, unimpaired same-doctrine leader must have a clear local link."""
    return (
        commander is not unit
        and any(enemy is commander for enemy in enemies)
        and commander.health > 0
        and commander.enemy_subtype == "commander"
        and not any(status in commander.status_effects for status in ("suppressed", "stunned", "panicked"))
        and profile_for_theme(unit.enemy_theme).key == profile_for_theme(commander.enemy_theme).key
        and unit.distance_to(commander) <= COMMAND_RADIUS
        and trace_sight_line(unit.position, commander.position, cover_nodes).clear
    )


def linked_commander(unit, enemies, cover_nodes=None):
    if unit.enemy_subtype == "commander":
        return None
    candidates = [enemy for enemy in enemies if command_link_active(unit, enemy, enemies, cover_nodes)]
    return min(candidates, key=unit.distance_to, default=None)


@contextmanager
def command_accuracy(unit, enemies, cover_nodes=None):
    """Support is checked at attack time; restore the exact stat even at its cap."""
    stats = unit.stats
    before = stats.agi if stats is not None else None
    if stats is not None and linked_commander(unit, enemies, cover_nodes) is not None:
        stats.agi = min(99, stats.agi + 1)
    try:
        yield
    finally:
        if stats is not None:
            stats.agi = before
