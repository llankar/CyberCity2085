"""Battle rules and AI decisions separated from Arcade rendering."""

import random
from collections.abc import Callable
from dataclasses import dataclass, replace

from .agents.sheet_calculations import compute_derived_stats
from .character import Character
from .combat.movement import MovementMode, can_enter_cell
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
from .cover_system import is_flanking
from .combat.attack_resolution import resolve_attack
from .combat.tactical_identity import profile_for_theme, tactical_target_score

GRID_SIZE = 32


@dataclass(frozen=True)
class EnemyActionResult:
    """Summary of one enemy attack or movement decision."""

    enemy: Unit
    target: Unit | None
    damage: int = 0
    moved: bool = False
    defeated_target: bool = False
    decision_reason: str = ""


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
    cover_nodes: list | None = None,
) -> bool:
    """Fire any player overwatch shots triggered by *moving_unit* entering range.

    Returns True if *moving_unit* was killed by overwatch fire.
    """
    for watcher in list(player_units):
        if not watcher.on_overwatch:
            continue
        if watcher.distance_to(moving_unit) <= watcher.attack_range * GRID_SIZE:
            from game.combat.battlefield import trace_sight_line
            if not trace_sight_line(watcher.position, moving_unit.position, cover_nodes).clear:
                continue
            watcher.on_overwatch = False
            resolution = resolve_attack(
                watcher,
                moving_unit,
                "fire",
                cover_nodes=cover_nodes,
                allies=player_units,
                spend_ap=False,
            )
            dmg = resolution.damage
            if on_overwatch_shot:
                on_overwatch_shot(watcher, moving_unit, dmg)
            if moving_unit.health <= 0:
                if moving_unit in enemy_units:
                    enemy_units.remove(moving_unit)
                if on_defeated:
                    on_defeated(moving_unit)
                return True
    return False


def _target_score(enemy: Unit, unit: Unit) -> int:
    """Score how attractive a player unit is as an enemy target."""
    return tactical_target_score(enemy, unit)


def _pick_target(enemy: Unit, player_units: list[Unit]) -> Unit | None:
    """Score and pick the highest-priority target for an enemy unit."""
    player_units = [unit for unit in player_units if unit.health > 0]
    if not player_units:
        return None
    if len(player_units) == 1:
        return player_units[0]
    return max(player_units, key=lambda unit: _target_score(enemy, unit))


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


def _candidate_steps_toward(enemy: Unit, target_position: tuple[int, int]) -> list[tuple[int, int]]:
    """Return orthogonal one-cell steps that reduce distance to a target position."""
    current = abs(enemy.position[0] - target_position[0]) + abs(enemy.position[1] - target_position[1])
    candidates: list[tuple[int, tuple[int, int]]] = []
    for step in ((GRID_SIZE, 0), (-GRID_SIZE, 0), (0, GRID_SIZE), (0, -GRID_SIZE)):
        new_pos = (enemy.position[0] + step[0], enemy.position[1] + step[1])
        distance = abs(new_pos[0] - target_position[0]) + abs(new_pos[1] - target_position[1])
        if distance < current:
            candidates.append((distance, step))
    candidates.sort(key=lambda item: item[0])
    return [step for _, step in candidates]


def _flanking_step(
    enemy: Unit,
    target: Unit,
    cover_nodes: list | None,
    player_units: list[Unit],
    enemy_units: list[Unit],
    *,
    can_enter: Callable[[int, int], bool] | None = None,
    terrain_profile=None,
    movement_mode: MovementMode = "tactical_grid",
) -> tuple[int, int] | None:
    """Return a legal one-cell step that creates a flank on a covered target."""
    if not cover_nodes or target.in_cover_bonus <= 0:
        return None
    original_position = enemy.position
    for step in _candidate_steps_toward(enemy, target.position):
        new_x = original_position[0] + step[0]
        new_y = original_position[1] + step[1]
        if not _can_enter_ai_cell(
            new_x,
            new_y,
            player_units,
            enemy_units,
            exclude=enemy,
            terrain_profile=terrain_profile,
            movement_mode=movement_mode,
            legacy_can_enter=can_enter,
        ):
            continue
        enemy.position = (new_x, new_y)
        try:
            if is_flanking(enemy, target, cover_nodes):
                return step
        finally:
            enemy.position = original_position
    enemy.position = original_position
    return None


def _objective_pressure_step(enemy: Unit, objective: object | None) -> tuple[int, int] | None:
    """Return a one-cell step that pressures or contests an objective."""
    if objective is None or getattr(objective, "completed", False):
        return None
    kind = getattr(objective, "kind", "")
    if kind == "containment":
        breach_y = getattr(objective, "breach_y", None)
        if breach_y is not None and enemy.position[1] > breach_y:
            return (0, -GRID_SIZE)
    if kind in {
        "defend",
        "sabotage",
        "data_theft",
        "extract",
        "civilian_rescue",
        "recon",
    }:
        steps = _candidate_steps_toward(enemy, getattr(objective, "position", enemy.position))
        return steps[0] if steps else None
    return None


def _apply_commander_buffs(enemy_units: list[Unit]) -> dict[int, tuple[Unit, int]]:
    """Temporarily boost AGI for enemies adjacent to a commander."""
    commanders = [e for e in enemy_units if e.enemy_subtype == "commander" and e.health > 0]
    bonuses: dict[int, tuple[Unit, int]] = {}
    if not commanders:
        return bonuses
    for commander in commanders:
        for enemy in enemy_units:
            if enemy is commander or enemy.enemy_subtype == "commander":
                continue
            if enemy.health > 0 and enemy.distance_to(commander) <= GRID_SIZE * 2:
                if id(enemy) not in bonuses:
                    bonuses[id(enemy)] = (enemy, 0)
                _, current_bonus = bonuses[id(enemy)]
                bonuses[id(enemy)] = (enemy, current_bonus + 1)
                if enemy.stats:
                    enemy.stats.agi = min(99, enemy.stats.agi + 1)
    return bonuses


def _remove_commander_buffs(bonuses: dict[int, tuple[Unit, int]]) -> None:
    """Restore stats after the phase so commander auras never stack by turn."""

    for enemy, bonus in bonuses.values():
        if enemy.stats:
            enemy.stats.agi = max(0, enemy.stats.agi - bonus)



def _can_enter_ai_cell(
    x: int,
    y: int,
    player_units: list[Unit],
    enemy_units: list[Unit],
    *,
    exclude: Unit | None = None,
    terrain_profile=None,
    movement_mode: MovementMode = "tactical_grid",
    legacy_can_enter: Callable[[int, int], bool] | None = None,
) -> bool:
    """Apply the shared movement rule plus legacy view gates for enemy AI."""
    if legacy_can_enter is not None and not legacy_can_enter(x, y):
        return False
    return can_enter_cell(
        x,
        y,
        terrain_profile=terrain_profile,
        allied_units=player_units,
        enemy_units=enemy_units,
        exclude=exclude,
        movement_mode=movement_mode,
    )

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
    terrain_profile=None,
    movement_mode: MovementMode = "tactical_grid",
    objective: object | None = None,
) -> list[EnemyActionResult]:
    """Run enemy actions and return inspectable outcomes for the view/test layer."""
    results: list[EnemyActionResult] = []
    defeated_player_units = (
        defeated_player_units if defeated_player_units is not None else []
    )

    # Commander buff: boost adjacent grunt/heavy AGI +1 this turn.
    commander_bonuses = _apply_commander_buffs(enemy_units)

    for enemy in list(enemy_units):
        # Skip enemies already killed (e.g. by overwatch during this same AI pass)
        if enemy.health <= 0:
            continue
        target = _pick_target(enemy, player_units)
        profile = profile_for_theme(enemy.enemy_theme)
        if not target:
            break
        while enemy.action_points > 0 and target.health > 0:
            # ── Choose attack type: ranged if enemy has range and target reachable ──
            dist = enemy.distance_to(target)
            can_ranged = (
                enemy.attack_range > 1
                and dist <= enemy.attack_range * GRID_SIZE
            )
            from game.combat.battlefield import trace_sight_line
            can_ranged = can_ranged and trace_sight_line(
                enemy.position, target.position, cover_nodes
            ).clear
            can_melee = dist <= 1 * GRID_SIZE

            if can_melee:
                damage = resolve_attack(
                    enemy,
                    target,
                    "melee",
                    cover_nodes=cover_nodes,
                    allies=enemy_units,
                ).damage
            elif can_ranged:
                flank_step = _flanking_step(
                    enemy,
                    target,
                    cover_nodes,
                    player_units,
                    enemy_units,
                    can_enter=can_enter,
                    terrain_profile=terrain_profile,
                    movement_mode=movement_mode,
                )
                if flank_step and enemy.action_points > 1 and profile.flank_bias >= 1.0:
                    enemy.move(*flank_step)
                    results.append(
                        EnemyActionResult(
                            enemy,
                            target,
                            moved=True,
                            decision_reason="flanking",
                        )
                    )
                    continue
                damage = resolve_attack(
                    enemy,
                    target,
                    "fire",
                    cover_nodes=cover_nodes,
                    allies=enemy_units,
                ).damage
            else:
                damage = 0  # out of range — will move below

            if damage > 0:
                if on_attack:
                    on_attack(enemy, target, damage)
                defeated = target.health <= 0
                results.append(
                    EnemyActionResult(
                        enemy, target, damage=damage, defeated_target=defeated,
                        decision_reason="melee" if can_melee else "ranged_fire",
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
                results.append(EnemyActionResult(enemy, target, moved=False, decision_reason="attack_missed"))
            else:
                objective_step = _objective_pressure_step(enemy, objective)
                if objective_step and objective_step != (0, 0) and profile.objective_bias >= 1.1:
                    new_x = enemy.position[0] + objective_step[0]
                    new_y = enemy.position[1] + objective_step[1]
                    if _can_enter_ai_cell(
                        new_x,
                        new_y,
                        player_units,
                        enemy_units,
                        exclude=enemy,
                        terrain_profile=terrain_profile,
                        movement_mode=movement_mode,
                        legacy_can_enter=can_enter,
                    ):
                        enemy.move(*objective_step)
                        results.append(
                            EnemyActionResult(
                                enemy,
                                target,
                                moved=True,
                                decision_reason="objective_pressure",
                            )
                        )
                        continue

                # Cover-seeking: if not in cover and cover nodes available, seek cover first
                cover_step: tuple[int, int] | None = None
                if (
                    cover_nodes
                    and profile.cover_bias >= 1.0
                    and enemy.action_points > 1
                    and enemy.in_cover_bonus == 0
                    and dist > GRID_SIZE * 3  # only seek cover when not too close to target
                ):
                    cover_step = _nearest_cover_step(enemy, cover_nodes, player_units, enemy_units)

                if cover_step and cover_step != (0, 0):
                    step_dx, step_dy = cover_step
                    new_x = enemy.position[0] + step_dx
                    new_y = enemy.position[1] + step_dy
                    can_enter_destination = _can_enter_ai_cell(
                        new_x,
                        new_y,
                        player_units,
                        enemy_units,
                        exclude=enemy,
                        terrain_profile=terrain_profile,
                        movement_mode=movement_mode,
                        legacy_can_enter=can_enter,
                    )
                    if can_enter_destination:
                        enemy.move(step_dx, step_dy)
                        results.append(
                            EnemyActionResult(
                                enemy,
                                target,
                                moved=True,
                                decision_reason="cover_seeking",
                            )
                        )
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
                        if not _can_enter_ai_cell(
                            new_x,
                            new_y,
                            player_units,
                            enemy_units,
                            exclude=enemy,
                            terrain_profile=terrain_profile,
                            movement_mode=movement_mode,
                            legacy_can_enter=can_enter,
                        ):
                            continue
                        enemy.move(step_dx, step_dy)
                        moved = True
                        # ?? Overwatch check after each enemy step ??????????
                        killed = _check_overwatch(
                            enemy, player_units, enemy_units,
                            on_overwatch_shot, on_defeated, cover_nodes,
                        )
                        if killed:
                            break
                        break
                    if not moved:
                        enemy.action_points -= 1
                else:
                    enemy.action_points -= 1
                results.append(
                    EnemyActionResult(
                        enemy,
                        target,
                        moved=moved,
                        decision_reason="advance" if moved else "",
                    )
                )
            if enemy.health <= 0 and enemy in enemy_units:
                enemy_units.remove(enemy)
        if not player_units:
            break
    _remove_commander_buffs(commander_bonuses)
    return results
