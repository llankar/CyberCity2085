"""Battle rules and AI decisions separated from Arcade rendering."""

import random
from collections.abc import Callable
from dataclasses import dataclass, replace

from .character import Character
from .deployment import deployable_agents, selected_deployable_agents
from .mission_templates import MissionTemplate
from .management.equipment import Weapon
from .stats import EnemyStats, PlayerStats
from .unit import Unit

GRID_SIZE = 32


@dataclass(frozen=True)
class EnemyActionResult:
    """Summary of one enemy attack or movement decision."""

    enemy: Unit
    target: Unit | None
    damage: int = 0
    moved: bool = False
    defeated_target: bool = False


def is_occupied(
    x: int,
    y: int,
    player_units: list[Unit],
    enemy_units: list[Unit],
    *,
    exclude: Unit | None = None,
) -> bool:
    """Return whether a living unit occupies a map position."""
    for unit in [u for u in player_units + enemy_units if u is not exclude]:
        if unit.health > 0 and unit.position == (x, y):
            return True
    return False


def equipped_player_stats(character: Character) -> PlayerStats:
    """Return combat stats with loadout bonuses applied without mutating the agent."""
    stats = replace(character.stats)
    for stat_key, amount in character.loadout.total_stat_bonuses().items():
        if not hasattr(stats, stat_key):
            continue
        setattr(stats, stat_key, max(0, getattr(stats, stat_key) + amount))
    if stats.max_hp < 1:
        stats.recalculate_hp()
    stats.hp = max(0, min(stats.hp, stats.max_hp))
    return stats


def primary_attack_range(character: Character) -> int:
    """Return the longest directly equipped weapon range for initial combat setup."""
    weapons = [
        item
        for item in (character.loadout.primary_weapon, character.loadout.sidearm)
        if isinstance(item, Weapon)
    ]
    if not weapons:
        return 1
    return max(weapon.range_cells for weapon in weapons)


def create_player_units(
    characters: list[Character], selected_agent_names: list[str] | None = None
) -> list[Unit]:
    """Create battle units from selected deployable agents.

    Passing ``None`` preserves the legacy all-deployable roster path for tests and
    direct combat setup. Passing an empty list intentionally creates no units.
    """
    deployable_characters = (
        deployable_agents(characters)
        if selected_agent_names is None
        else selected_deployable_agents(characters, selected_agent_names)
    )
    player_units: list[Unit] = []
    for i, char in enumerate(deployable_characters):
        stats = equipped_player_stats(char)
        player_units.append(
            Unit(
                position=(64 + i * 64, 64),
                stats=stats,
                health=stats.hp,
                character=char,
                attack_range=primary_attack_range(char),
                available_actions=char.loadout.combat_actions(),
            )
        )
    return player_units


def create_enemy_units(
    mission: MissionTemplate | None,
    characters: list[Character],
) -> tuple[list[Unit], int]:
    """Generate enemy units scaled to the active roster and mission."""
    avg_level = (
        sum(c.stats.level for c in characters) / len(characters) if characters else 1
    )
    enemy_count = mission.starting_enemy_count if mission else random.randint(1, 3)
    enemy_units: list[Unit] = []
    for i in range(enemy_count):
        level = random.randint(1, int(avg_level))
        estats = EnemyStats(level=level, defense=level, psi=level, str=level, agi=level)
        enemy_units.append(
            Unit(position=(224 + i * 64, 224), stats=estats, health=estats.hp)
        )
    return enemy_units, enemy_count


def step_toward(attacker: Unit, target: Unit) -> tuple[int, int]:
    """Return one grid step from attacker toward target."""
    dx = (
        GRID_SIZE
        if target.position[0] > attacker.position[0]
        else -GRID_SIZE if target.position[0] < attacker.position[0] else 0
    )
    dy = (
        GRID_SIZE
        if target.position[1] > attacker.position[1]
        else -GRID_SIZE if target.position[1] < attacker.position[1] else 0
    )
    return dx, dy


def run_enemy_ai(
    player_units: list[Unit],
    enemy_units: list[Unit],
    *,
    defeated_player_units: list[Unit] | None = None,
    on_attack: Callable[[Unit, Unit, int], None] | None = None,
    on_defeated: Callable[[Unit], None] | None = None,
) -> list[EnemyActionResult]:
    """Run enemy actions and return inspectable outcomes for the view/test layer."""
    results: list[EnemyActionResult] = []
    defeated_player_units = (
        defeated_player_units if defeated_player_units is not None else []
    )

    for enemy in list(enemy_units):
        target = player_units[0] if player_units else None
        if not target:
            break
        while enemy.action_points > 0 and target.health > 0:
            damage = enemy.attack(target)
            if damage > 0:
                if on_attack:
                    on_attack(enemy, target, damage)
                defeated = target.health <= 0
                results.append(
                    EnemyActionResult(
                        enemy, target, damage=damage, defeated_target=defeated
                    )
                )
                if defeated:
                    defeated_player_units.append(target)
                    if target in player_units:
                        player_units.remove(target)
                    if on_defeated:
                        on_defeated(target)
                    break
            else:
                dx, dy = step_toward(enemy, target)
                moved = False
                if dx or dy:
                    new_x = enemy.position[0] + dx
                    new_y = enemy.position[1] + dy
                    if not is_occupied(
                        new_x, new_y, player_units, enemy_units, exclude=enemy
                    ):
                        enemy.move(dx, dy)
                        moved = True
                    else:
                        enemy.action_points -= 1
                else:
                    enemy.action_points -= 1
                results.append(EnemyActionResult(enemy, target, moved=moved))
            if enemy.health <= 0 and enemy in enemy_units:
                enemy_units.remove(enemy)
        if not player_units:
            break
    return results
