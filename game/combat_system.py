"""Battle rules and AI decisions separated from Arcade rendering."""

import random
from collections.abc import Callable
from dataclasses import dataclass, replace

from .agents.sheet_calculations import compute_derived_stats
from .character import Character
from .agent_specializations import apply_talent_bonuses
from .deployment import (
    deployable_agents,
    selected_deployment_manifest,
)
from .enemy_themes import (
    enemy_theme_stat_scale,
    mission_enemy_theme,
)
from .mission_templates import MissionTemplate
from .management.equipment import Weapon
from .management.spec_ops_assets import SpecOpsAsset
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
    stats = apply_talent_bonuses(stats, character.specializations)
    derived = compute_derived_stats(
        character.attributes,
        character.skills,
        character.loadout.total_stat_bonuses(),
        "steady" if character.stress < 35 else "rattled" if character.stress < 65 else "frayed" if character.stress < 85 else "breaking",
    )
    stats.defense = max(0, int(derived.get("defense", stats.defense)))
    stats.max_hp = max(1, int(derived.get("hp", stats.max_hp)))
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


def create_asset_unit(asset: SpecOpsAsset, index: int) -> Unit:
    """Convert one robot or power armor asset into a tactical combat unit."""
    stats = asset.combat_stats()
    return Unit(
        position=(64 + index * 64, 64),
        stats=stats,
        health=stats.hp,
        spec_ops_asset=asset,
        unit_type=asset.asset_type,
        attack_range=asset.primary_range,
        action_points=asset.action_points,
        available_actions=asset.combat_actions,
        equipment_summary=[
            *(hardpoint.name for hardpoint in asset.hardpoints),
            f"Missiles x{asset.missile_capacity}",
            f"Armor {asset.armor.defense_bonus}",
        ],
    )


def create_player_units(
    characters: list[Character],
    selected_agent_names: list[str] | None = None,
    assets: list[SpecOpsAsset] | None = None,
    selected_asset_ids: list[str] | None = None,
) -> list[Unit]:
    """Create battle units from selected deployable agents and support assets.

    Passing ``None`` for ``selected_agent_names`` preserves the legacy all-agent
    roster path for tests and direct combat setup. Passing an empty agent list
    intentionally creates no agent units; selected assets may still be supplied.
    """
    if selected_agent_names is None:
        deployable_characters = deployable_agents(characters)
        deployable_assets = []
    else:
        manifest = selected_deployment_manifest(
            characters, selected_agent_names, assets, selected_asset_ids
        )
        deployable_characters = manifest.agents
        deployable_assets = manifest.assets

    # Identify agents assigned as pilots to power armors (they merge into the armor unit)
    piloted_by_armor: dict[str, "SpecOpsAsset"] = {}
    for asset in deployable_assets:
        pilot_name = getattr(asset, "pilot_agent_name", None)
        if pilot_name:
            piloted_by_armor[pilot_name] = asset

    pilot_chars: dict[str, "Character"] = {
        c.name: c for c in deployable_characters if c.name in piloted_by_armor
    }

    # Staggered formation on the left-center of the map
    _PLAYER_SPAWN = [
        (96, 416), (96, 352), (160, 416), (160, 352), (96, 480), (160, 480),
    ]

    player_units: list[Unit] = []
    for i, char in enumerate(c for c in deployable_characters if c.name not in piloted_by_armor):
        stats = equipped_player_stats(char)
        pos   = _PLAYER_SPAWN[len(player_units) % len(_PLAYER_SPAWN)]
        player_units.append(
            Unit(
                position=pos,
                stats=stats,
                health=stats.hp,
                character=char,
                unit_type="agent",
                attack_range=primary_attack_range(char),
                available_actions=char.loadout.combat_actions(),
                equipment_summary=char.loadout.summary_lines(),
            )
        )
    for asset in deployable_assets:
        pos   = _PLAYER_SPAWN[len(player_units) % len(_PLAYER_SPAWN)]
        stats = asset.combat_stats()
        pilot_char = pilot_chars.get(getattr(asset, "pilot_agent_name", "") or "")
        u = Unit(
            position=pos,
            stats=stats,
            health=stats.hp,
            spec_ops_asset=asset,
            unit_type=asset.asset_type,
            attack_range=asset.primary_range,
            action_points=asset.action_points,
            available_actions=asset.combat_actions,
            equipment_summary=[
                *(hp.name for hp in asset.hardpoints),
                f"Missiles x{asset.missile_capacity}",
                f"Armor {asset.armor.defense_bonus}",
            ],
        )
        if pilot_char:
            u.character = pilot_char  # pilot's portrait/name shows in the strip
        player_units.append(u)
    return player_units


def _enemy_subtype_for_index(i: int, total: int, avg_level: float) -> str:
    """Assign enemy subtypes for a battle roster.

    Distribution (XCOM-style):
      - 0th enemy is always at least a grunt
      - Last enemy (if high level enough) may be an elite/commander
      - Mix of grunt/heavy for the rest
    """
    if total >= 2 and i == total - 1 and avg_level >= 4:
        return "commander" if avg_level >= 7 else "elite"
    if avg_level >= 3 and i % 3 == 1:
        return "heavy"
    if avg_level >= 5 and i % 4 == 2:
        return "elite"
    return "grunt"


_SUBTYPE_STAT_SCALE: dict[str, dict[str, float]] = {
    "grunt":     {"hp": 1.0, "str": 1.0, "agi": 1.0, "def": 1.0, "range": 3},
    "heavy":     {"hp": 1.6, "str": 1.4, "agi": 0.8, "def": 1.3, "range": 2},
    "elite":     {"hp": 1.3, "str": 1.3, "agi": 1.4, "def": 1.2, "range": 4},
    "commander": {"hp": 1.8, "str": 1.5, "agi": 1.2, "def": 1.5, "range": 5},
}


def create_enemy_units(
    mission: MissionTemplate | None,
    characters: list[Character],
) -> tuple[list[Unit], int]:
    """Generate enemy units scaled to the active roster and mission.

    Enemies are now typed (grunt / heavy / elite / commander) with scaled
    stats and distinct combat behaviour.
    """
    avg_level = (
        sum(c.stats.level for c in characters) / len(characters) if characters else 1
    )
    enemy_count = mission.starting_enemy_count if mission else random.randint(1, 3)
    enemy_units: list[Unit] = []
    theme = mission_enemy_theme(mission) if mission else "generic"
    theme_scale = enemy_theme_stat_scale(theme)

    # Staggered formation on the right-center of the map (far from player)
    _ENEMY_SPAWN = [
        (1152, 416), (1152, 352), (1088, 416), (1088, 352),
        (1024, 416), (1024, 352), (960, 416),  (960, 352),
    ]

    for i in range(enemy_count):
        level = random.randint(1, max(1, int(avg_level)))
        subtype = _enemy_subtype_for_index(i, enemy_count, avg_level)
        scale = _SUBTYPE_STAT_SCALE[subtype]
        stat_scale = {
            "hp": scale["hp"] * theme_scale["hp"],
            "str": scale["str"] * theme_scale["str"],
            "agi": scale["agi"] * theme_scale["agi"],
            "def": scale["def"] * theme_scale["def"],
        }
        attack_range = max(int(scale["range"]), int(theme_scale["range"]))

        base = level
        estats = EnemyStats(
            level=level,
            defense=max(1, int(base * stat_scale["def"])),
            psi=max(1, base),
            str=max(1, int(base * stat_scale["str"])),
            agi=max(1, int(base * stat_scale["agi"])),
        )
        # Scale max_hp by subtype
        estats.max_hp = max(1, int(estats.max_hp * stat_scale["hp"]))
        estats.hp     = estats.max_hp

        pos = _ENEMY_SPAWN[i % len(_ENEMY_SPAWN)]
        enemy_units.append(Unit(
            position=pos,
            stats=estats,
            health=estats.hp,
            unit_type="enemy",
            enemy_subtype=subtype,
            enemy_theme=theme,
            attack_range=attack_range,
        ))

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


def _check_overwatch(
    moving_unit: Unit,
    player_units: list[Unit],
    enemy_units: list[Unit],
    on_overwatch_shot: Callable[[Unit, Unit, int], None] | None,
    on_defeated: Callable[[Unit], None] | None,
) -> bool:
    """Fire any player overwatch shots triggered by *moving_unit* entering range.

    Returns True if *moving_unit* was killed by overwatch fire.
    """
    for watcher in list(player_units):
        if not watcher.on_overwatch:
            continue
        if watcher.distance_to(moving_unit) <= watcher.attack_range * GRID_SIZE:
            dmg = watcher.trigger_overwatch_shot(moving_unit)
            if on_overwatch_shot:
                on_overwatch_shot(watcher, moving_unit, dmg)
            if moving_unit.health <= 0:
                if moving_unit in enemy_units:
                    enemy_units.remove(moving_unit)
                if on_defeated:
                    on_defeated(moving_unit)
                return True
    return False


def _pick_target(enemy: Unit, player_units: list[Unit]) -> Unit | None:
    """Score and pick the highest-priority target for an enemy unit.

    Priority: near-dead units first (finish them), then high-threat roles
    (psi agents, snipers), then squishiest defense.
    """
    if not player_units:
        return None
    if len(player_units) == 1:
        return player_units[0]

    def _score(unit: Unit) -> int:
        score = 0
        # Near-death: finish off wounded targets
        if unit.stats and unit.health < unit.stats.max_hp * 0.40:
            score += 20
        # Threat role
        role = getattr(unit.character, "role", "") if unit.character else ""
        if role in ("psi", "sniper", "commander"):
            score += 15
        elif role in ("assault", "heavy"):
            score += 8
        # Soft target (low defense)
        if unit.stats and getattr(unit.stats, "defense", 3) < 3:
            score += 10
        # Prefer closer targets (distance tie-breaker)
        dist = enemy.distance_to(unit)
        score -= int(dist / GRID_SIZE) * 2
        return score

    return max(player_units, key=_score)


def _nearest_cover_step(
    enemy: Unit,
    cover_nodes: list,
    player_units: list[Unit],
    enemy_units: list[Unit],
) -> tuple[int, int] | None:
    """Return (dx, dy) step toward the nearest unoccupied cover node, or None."""
    best_dist = float("inf")
    best_node = None
    for node in cover_nodes:
        # CoverNode stores grid_x/grid_y (tile coords); pixel pos = grid * GRID_SIZE
        nx = node.grid_x * GRID_SIZE
        ny = node.grid_y * GRID_SIZE
        if is_occupied(nx, ny, player_units, enemy_units, exclude=enemy):
            continue
        dist = abs(nx - enemy.position[0]) + abs(ny - enemy.position[1])
        if dist < best_dist:
            best_dist = dist
            best_node = node
    if best_node is None or best_dist > GRID_SIZE * 4:
        return None
    target_x = best_node.grid_x * GRID_SIZE
    target_y = best_node.grid_y * GRID_SIZE
    dx = target_x - enemy.position[0]
    dy = target_y - enemy.position[1]
    # Clamp to one-cell step
    step_x = min(GRID_SIZE, max(-GRID_SIZE, dx)) if dx else 0
    step_y = min(GRID_SIZE, max(-GRID_SIZE, dy)) if dy else 0
    return (step_x or 0, step_y or 0)


def _apply_commander_buffs(enemy_units: list[Unit]) -> dict[int, int]:
    """Temporarily boost AGI for enemies adjacent to a commander. Returns {id: bonus}."""
    commanders = [e for e in enemy_units if e.enemy_subtype == "commander" and e.health > 0]
    bonuses: dict[int, int] = {}
    if not commanders:
        return bonuses
    for commander in commanders:
        for enemy in enemy_units:
            if enemy is commander or enemy.enemy_subtype == "commander":
                continue
            if enemy.health > 0 and enemy.distance_to(commander) <= GRID_SIZE * 2:
                if id(enemy) not in bonuses:
                    bonuses[id(enemy)] = 0
                bonuses[id(enemy)] += 1
                if enemy.stats:
                    enemy.stats.agi = min(99, enemy.stats.agi + 1)
    return bonuses


def run_enemy_ai(
    player_units: list[Unit],
    enemy_units: list[Unit],
    *,
    defeated_player_units: list[Unit] | None = None,
    on_attack: Callable[[Unit, Unit, int], None] | None = None,
    on_defeated: Callable[[Unit], None] | None = None,
    on_overwatch_shot: Callable[[Unit, Unit, int], None] | None = None,
    can_enter: Callable[[int, int], bool] | None = None,
    cover_nodes: list | None = None,
) -> list[EnemyActionResult]:
    """Run enemy actions and return inspectable outcomes for the view/test layer."""
    results: list[EnemyActionResult] = []
    defeated_player_units = (
        defeated_player_units if defeated_player_units is not None else []
    )

    # Commander buff: boost adjacent grunt/heavy AGI +1 this turn
    _commander_buffed: set[int] = set()
    if cover_nodes is not None:
        for buf_id in _apply_commander_buffs(enemy_units):
            _commander_buffed.add(buf_id)

    for enemy in list(enemy_units):
        # Skip enemies already killed (e.g. by overwatch during this same AI pass)
        if enemy.health <= 0:
            continue
        target = _pick_target(enemy, player_units)
        if not target:
            break
        while enemy.action_points > 0 and target.health > 0:
            # ── Choose attack type: ranged if enemy has range and target reachable ──
            dist = enemy.distance_to(target)
            can_ranged = (
                enemy.attack_range > 1
                and dist <= enemy.attack_range * GRID_SIZE
            )
            can_melee = dist <= 1 * GRID_SIZE

            if can_melee:
                damage = enemy.melee_attack(target)
            elif can_ranged:
                damage = enemy.shoot(target)
            else:
                damage = 0  # out of range — will move below

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
            elif can_melee or can_ranged:
                # In range but missed — costs the action, stay put
                enemy.action_points -= 1
                results.append(EnemyActionResult(enemy, target, moved=False))
            else:
                # Cover-seeking: if not in cover and cover nodes available, seek cover first
                cover_step: tuple[int, int] | None = None
                if (
                    cover_nodes
                    and enemy.action_points > 1
                    and enemy.in_cover_bonus == 0
                    and dist > GRID_SIZE * 3  # only seek cover when not too close to target
                ):
                    cover_step = _nearest_cover_step(enemy, cover_nodes, player_units, enemy_units)

                if cover_step and cover_step != (0, 0):
                    step_dx, step_dy = cover_step
                    new_x = enemy.position[0] + step_dx
                    new_y = enemy.position[1] + step_dy
                    blocked = is_occupied(new_x, new_y, player_units, enemy_units, exclude=enemy)
                    if can_enter is not None and not can_enter(new_x, new_y):
                        blocked = True
                    if not blocked:
                        enemy.move(step_dx, step_dy)
                        results.append(EnemyActionResult(enemy, target, moved=True))
                        continue

                # Default: step toward target
                dx, dy = step_toward(enemy, target)
                moved = False
                if dx or dy:
                    step_candidates = [(dx, dy)]
                    if dx and dy:
                        step_candidates = [(dx, 0), (0, dy), (dx, dy)]
                    for step_dx, step_dy in step_candidates:
                        new_x = enemy.position[0] + step_dx
                        new_y = enemy.position[1] + step_dy
                        blocked = is_occupied(
                            new_x, new_y, player_units, enemy_units, exclude=enemy
                        )
                        if can_enter is not None and not can_enter(new_x, new_y):
                            blocked = True
                        if blocked:
                            continue
                        enemy.move(step_dx, step_dy)
                        moved = True
                        # ?? Overwatch check after each enemy step ??????????
                        killed = _check_overwatch(
                            enemy, player_units, enemy_units,
                            on_overwatch_shot, on_defeated,
                        )
                        if killed:
                            break
                        break
                    if not moved:
                        enemy.action_points -= 1
                else:
                    enemy.action_points -= 1
                results.append(EnemyActionResult(enemy, target, moved=moved))
            if enemy.health <= 0 and enemy in enemy_units:
                enemy_units.remove(enemy)
        if not player_units:
            break
    return results
