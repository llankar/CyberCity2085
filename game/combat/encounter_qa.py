"""Deterministic developer simulations, using the real reference combat engine."""

from collections import Counter
from pathlib import Path
import random

from game.character import Character
from game.combat_system import create_enemy_units
from game.cover_system import CoverNode
from game.management.equipment import Weapon
from game.mission_templates import MissionTemplate
from game.mission_objectives import create_battle_objective
from game.stats import PlayerStats
from game.unit import Unit
from .attack_resolution import build_attack_context
from .engine import CombatEngine
from .pack_maneuvers import neighbors, approach_step
from .state import CombatState


def first_reachable_approach(actor, destinations, legal, *, width, height):
    """QA policy: do not guard forever because its first candidate is sealed."""
    for destination in destinations:
        step = approach_step(actor, destination, legal, width=width, height=height)
        if step is not None:
            return destination, step
    return None, None


def objective_threat_distance(enemy, objective):
    """Sort defensive QA targets by the danger they pose to the objective."""
    if objective is None:
        return 0
    if objective.kind == "containment" and objective.breach_y is not None:
        return enemy.position[1] - objective.breach_y
    if objective.kind == "defend":
        return enemy.distance_to(objective)
    return 0


def synthetic_enemy_position(index, objective_kind):
    """Place synthetic QA enemies with the same containment response margin as authored maps."""
    if objective_kind == "containment":
        return 288 + (index // 2) * 32, 320 + (index % 2) * 32
    return 288 + (index // 4) * 64, 64 + (index % 4) * 64


def simulate_encounter(*, theme, level, risk, count, seed, policy="focus", layout="open", max_turns=30, objective_kind="eliminate", map_path=None, mission_template=None):
    if mission_template is not None:
        mission_template = MissionTemplate.from_dict(mission_template.to_dict())
        theme, risk, count = mission_template.enemy_theme, mission_template.risk_level, mission_template.starting_enemy_count
        objective_kind = mission_template.objective_type
    if policy not in {"focus", "counterplay", "objective", "objective_counterplay"} or layout not in {"open", "cover"}:
        raise ValueError("Unknown QA policy/layout")
    if not 1 <= count <= 12 or not 1 <= max_turns <= 100:
        raise ValueError("QA supports 1..12 enemies and 1..100 turns")
    saved_rng = random.getstate()
    try:
        random.seed(seed)
        return _simulate(theme, level, risk, count, seed, policy, layout, max_turns, objective_kind, map_path, mission_template)
    finally:
        random.setstate(saved_rng)


def _simulate(theme, level, risk, count, seed, policy, layout, max_turns, objective_kind, map_path, mission_template=None):
    characters = [Character(name) for name in ("Rook", "Echo", "Nyx", "Mara")]
    allies = []
    for i, character in enumerate(characters):
        character.stats = PlayerStats(level=level, agi=level + 3, str=level + 3, defense=max(1, level // 2))
        character.loadout.primary_weapon = Weapon("qa_rifle", "QA Rifle", "primary_weapon", range_cells=6)
        allies.append(Unit(position=(64, 64 + i * 64), stats=character.stats,
                           health=character.stats.hp, character=character, attack_range=6))
    mission = mission_template or MissionTemplate("encounter_qa", "Encounter QA", "Eliminate hostiles", "", "", {}, count,
                              enemy_theme=theme, risk_level=risk, objective_type=objective_kind)
    objective = create_battle_objective(mission, position=(128, 192) if objective_kind == "defend" else (256, 192))
    enemies, _ = create_enemy_units(mission, characters, rng=random.Random(seed))
    for i, enemy in enumerate(enemies):
        enemy.position = synthetic_enemy_position(i, objective_kind)
    original_allies, original_enemies = list(allies), list(enemies)
    cover = [CoverNode(6, 4, "high", False), CoverNode(7, 6, "low")] if layout == "cover" else []
    state = CombatState(mission, allies, enemies, objective=objective)
    if objective_kind == "defend" and mission_template is not None:
        state.tactical_flags["defend_turns_required"] = max(4, (mission.duration_days or 1) * 4)
    width, height, terrain = 640, 384, None
    if map_path is not None:
        from game.map_terrain import build_terrain_profile
        from .encounter_placement import fit_encounter
        from .battlefield import build_battlefield_plan
        from game.battle_maps import build_battle_map_catalog, battle_map_pool_for_environment
        width, height = 1280, 720
        terrain = build_terrain_profile(str(map_path), width, height)
        if terrain.source != "manual_wall_traces_v1":
            raise ValueError("Authored QA requires a valid reviewed manual survey")
        objective = create_battle_objective(mission)
        enemies, _ = create_enemy_units(mission, characters, rng=random.Random(seed))
        state.enemy_units, state.objective = enemies, objective
        fitted = fit_encounter(terrain, [(96+i*64, 64) for i in range(len(allies))],
                               [e.position for e in enemies], objective.marker_positions if objective else (),
                               objective_kind=objective_kind, breach_y=getattr(objective, "breach_y", None))
        for units, positions in ((allies, fitted.allies), (enemies, fitted.enemies)):
            for unit, position in zip(units, positions):
                unit.position = position
        if objective:
            objective.marker_positions = list(fitted.objectives)
            objective.position = fitted.objectives[0]
            objective.breach_y = fitted.breach_y
        entry = next(e for e in build_battle_map_catalog() if Path(e.path).name == Path(map_path).name)
        map_index = next(i for i, e in enumerate(battle_map_pool_for_environment(entry.environment)) if e.key == entry.key)
        plan = build_battlefield_plan(map_index=map_index, width=width, height=height, terrain_profile=terrain,
                                      objective_kind=objective_kind,
                                      reserved_positions=(*fitted.allies, *fitted.enemies, *fitted.objectives))
        cover = list(plan.cover_nodes)
        state.tactical_flags["hazards"] = plan.hazards
        original_enemies = list(enemies)
    if objective_kind == "assassination":
        priority = {"commander": 4, "elite": 3, "heavy": 2, "grunt": 1}
        state.tactical_flags["assassination_target"] = max(enemies, key=lambda unit: priority[unit.enemy_subtype])
    blocked_cover = {(node.world_x, node.world_y) for node in cover if not node.passable}

    def legal(x, y):
        return (0 <= x < width and 0 <= y < height
                and (terrain is None or terrain.is_walkable(x, y))
                and not any(u.health > 0 and u.position == (x, y) for u in [*allies, *enemies])
                and (x, y) not in blocked_cover)

    engine = CombatEngine(state, can_enter=legal, cover_nodes=cover, terrain_profile=terrain)
    def check_geometry():
        living = [unit.position for unit in [*allies, *enemies] if unit.health > 0]
        assert len(living) == len(set(living)), "Overlapping living units"
        assert terrain is None or all(terrain.is_walkable(*cell) for cell in living), "Unit entered authored obstacle"
    initial_hp = sum(unit.health for unit in allies)
    announced = Counter()
    dodges = 0
    def snapshot():
        units = tuple((unit.position, unit.health, tuple(sorted(unit.status_effects)))
                      for unit in [*original_allies, *original_enemies])
        goal = (objective.position, objective.progress, objective.completed) if objective else None
        return units, goal
    previous_snapshot = snapshot()
    unchanged_rounds = longest_unchanged_rounds = consecutive_unchanged = 0
    outcome = "turn_limit"
    for turn in range(1, max_turns + 1):
        result = engine.start_player_turn()
        if result.ended:
            outcome = result.outcome
            break
        announced.update(intent.action for intent in engine.enemy_intents())
        for actor in list(allies):
            while actor.health > 0 and actor.action_points > 0 and not engine.end_battle_check().ended:
                before = actor.action_points
                objective_blocked = False
                if policy.startswith("objective") and objective is not None and objective.kind not in {"defend", "containment", "assassination"} and not objective.completed:
                    interaction = engine.interact_with_objective(actor)
                    if interaction.consumed_ap:
                        continue
                    objective_blocked = interaction.reason in {"objective_contested", "interaction_already_used_this_turn"}
                threats = engine.enemy_intents()
                marked = policy in {"counterplay", "objective_counterplay"} and any(
                    (intent.action == "LOCK" and intent.target is actor)
                    or (intent.action == "TOXIN" and intent.destination == actor.position)
                    for intent in threats)
                safe = [cell for cell in neighbors(actor.position) if legal(*cell)
                        and not any(intent.action == "TOXIN" and intent.destination == cell for intent in threats)
                        and not any(zone.contains(cell) for zone in state.tactical_flags.get("hazards", ()))]
                if marked and safe:
                    cell = min(safe, key=lambda c: (abs(c[0] - 64), c))
                    action = engine.perform_action("move", actor=actor,
                                                   move_delta=(cell[0]-actor.position[0], cell[1]-actor.position[1]))
                    dodges += int(action.success)
                else:
                    defensive_objective = (
                        objective
                        if policy.startswith("objective") and objective is not None
                        and objective.kind in {"defend", "containment"}
                        else None
                    )
                    targets = sorted(
                        (e for e in enemies if e.health > 0),
                        key=lambda e: (
                            objective_threat_distance(e, defensive_objective),
                            e.health,
                            actor.distance_to(e),
                        ),
                    )
                    hvt = state.tactical_flags.get("assassination_target")
                    if policy.startswith("objective") and hvt is not None and hvt.health > 0:
                        targets.sort(key=lambda e: e is not hvt)
                    advance_objective = (policy.startswith("objective") and objective is not None
                                         and not objective.completed and not objective_blocked
                                         and objective.kind not in {"defend", "containment", "assassination"})
                    shootable = [e for e in targets if (ctx := build_attack_context(actor, e, "fire", cover_nodes=cover)).in_range and not ctx.line_blocked]
                    step = None
                    if advance_objective:
                        _, step = first_reachable_approach(actor, [objective], legal, width=width, height=height)
                    if step is not None:
                        engine.perform_action("move", actor=actor, move_delta=step)
                    elif shootable:
                        engine.perform_action("fire", actor=actor, target=shootable[0])
                    elif targets:
                        destinations = sorted(targets, key=lambda target: (
                            target is not hvt if policy.startswith("objective") and hvt else False,
                            actor.distance_to(target)))
                        _, step = first_reachable_approach(actor, destinations, legal, width=width, height=height)
                        if step:
                            engine.perform_action("move", actor=actor, move_delta=step)
                if actor.action_points >= before:
                    engine.perform_action("defend", actor=actor)
                    break
                check_geometry()
        result = engine.end_battle_check()
        if not result.ended:
            result = engine.start_enemy_turn()
        check_geometry()
        current_snapshot = snapshot()
        if current_snapshot == previous_snapshot:
            unchanged_rounds += 1
            consecutive_unchanged += 1
            longest_unchanged_rounds = max(longest_unchanged_rounds, consecutive_unchanged)
        else:
            consecutive_unchanged = 0
        previous_snapshot = current_snapshot
        if result.ended:
            outcome = result.outcome
            break
    return dict(theme=theme, level=level, risk=risk, count=count, seed=seed, policy=policy, layout=layout, objective_kind=objective_kind,
                mission_id=mission.id,
                map_file=Path(map_path).name if map_path is not None else None,
                terrain_source=terrain.source if terrain else "synthetic", geometry_checked=True,
                map_survey_sha256=terrain.survey_sha256 if terrain else None,
                unchanged_rounds=unchanged_rounds, longest_unchanged_rounds=longest_unchanged_rounds,
                outcome=outcome, turns=turn, roles=dict(Counter(e.enemy_subtype for e in original_enemies)),
                objective_progress=objective.progress if objective else 0,
                objective_reason=engine.objective_result().reason,
                assassination_target_role=getattr(state.tactical_flags.get("assassination_target"), "enemy_subtype", None),
                contributions=dict(state.tactical_flags.get("objective_contributions", {})),
                allied_hp_lost=initial_hp-sum(max(0, u.health) for u in original_allies),
                allied_losses=sum(u.health <= 0 for u in original_allies),
                enemy_survivors=sum(u.health > 0 for u in original_enemies),
                infections=sum(c.starver_infection_days is not None for c in characters),
                announced=dict(announced), dodges=dodges,
                interruptions=sum("Enemy plan interrupted" in line for line in state.logs))
