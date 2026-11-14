"""Behavioral scenarios for cover, occlusion, and environmental pressure."""

from game.combat import CombatEngine, CombatState
from game.combat.attack_resolution import resolve_attack
from game.combat.battlefield import HazardZone, build_battlefield_plan, trace_sight_line, reachable_objective_positions
from game.combat_preview import estimate_attack_preview
from game.cover_system import CoverNode, directional_cover, is_flanking
from game.stats import PlayerStats
from game.unit import Unit
from game.map_terrain import TerrainProfile
from game.combat.battlefield import connect_inferred_terrain
from game.combat_system import _pick_target


def operative(position):
    stats = PlayerStats(con=3, agi=8)
    return Unit(position=position, stats=stats, health=stats.hp, action_points=2, attack_range=8)


def test_rotating_around_cover_changes_protection_and_flank():
    defender = operative((96, 96))
    cover = [CoverNode(3, 4, "high"), CoverNode(4, 3, "low")]
    assert directional_cover(operative((96, 256)), defender, cover)[1] == 2
    assert directional_cover(operative((256, 96)), defender, cover)[1] == 1
    assert is_flanking(operative((0, 96)), defender, cover)


def test_intervening_high_cover_blocks_preview_and_execution_without_cost():
    attacker, defender = operative((0, 0)), operative((128, 0))
    cover = [CoverNode(2, 0, "high")]
    preview = estimate_attack_preview(attacker, defender, "fire", cover_nodes=cover)
    before_hp = defender.health
    result = resolve_attack(attacker, defender, "fire", cover_nodes=cover)
    assert preview.warning == "LINE BLOCKED"
    assert result.reason == "line_blocked"
    assert attacker.action_points == 2
    assert defender.health == before_hp
    assert trace_sight_line((0, 0), (128, 0), [CoverNode(2, 0, "low")]).clear
    assert trace_sight_line((0, 0), (128, 0), [CoverNode(3, 0, "high")]).clear


def test_allied_line_warning_does_not_damage_an_ally():
    attacker, defender, ally = operative((0, 0)), operative((128, 0)), operative((64, 0))
    before = ally.health
    result = resolve_attack(attacker, defender, "fire", allies=[attacker, ally], rng=lambda: 0.0)
    assert result.context.line_warning == "ALLY IN LINE"
    assert result.success
    assert ally.health == before


def test_hazards_apply_symmetrically_at_phase_start():
    ally, enemy = operative((64, 64)), operative((256, 64))
    state = CombatState(None, [ally], [enemy])
    state.tactical_flags["hazards"] = (
        HazardZone("fire", ally.position), HazardZone("blackout", enemy.position)
    )
    engine = CombatEngine(state)
    before = ally.health
    engine.start_player_turn()
    engine.apply_battlefield_exposure([enemy])
    assert ally.health == before - 2
    assert ally.has_status("burning")
    assert enemy.action_points == 1
    assert any("FIRE" in line for line in state.logs)


def test_generated_plan_respects_reserved_anchors_across_map_seeds():
    reserved = ((96, 64), (160, 64), (448, 320), (320, 224))
    for seed in range(20):
        kwargs = dict(map_index=seed, width=1280, height=720, reserved_positions=reserved)
        plan = build_battlefield_plan(**kwargs)
        assert plan == build_battlefield_plan(**kwargs)
        assert all((node.world_x, node.world_y) not in reserved for node in plan.cover_nodes)
        assert len(plan.hazards) == 3
        assert all(not zone.contains(position) for zone in plan.hazards for position in reserved)


def test_objective_beats_relocate_out_of_disconnected_art_regions():
    terrain = TerrainProfile(
        "test", 256, 256, 32,
        frozenset({(32, 32), (64, 32), (96, 32), (96, 64), (224, 224)}), 0,
    )
    positions = reachable_objective_positions(((224, 224), (96, 32)), (32, 32), terrain)
    assert positions == ((96, 64), (96, 32))
    assert len(set(positions)) == 2


def test_inferred_access_lanes_preserve_objective_distance_and_authored_masks():
    terrain = TerrainProfile("test", 320, 320, 32, frozenset({(32, 32), (224, 224)}), 80)
    anchors = ((32, 32), (224, 224))
    connected, added = connect_inferred_terrain(terrain, anchors)
    assert added
    assert reachable_objective_positions((anchors[1],), anchors[0], connected) == (anchors[1],)
    authored = TerrainProfile("test", 320, 320, 32, terrain.walkable_cells, 255)
    assert connect_inferred_terrain(authored, anchors) == (authored, frozenset())


def test_enemy_burning_ticks_after_leaving_hazard_and_dead_allies_are_not_targets():
    ally, enemy = operative((32, 32)), operative((256, 256))
    enemy.apply_status("burning")
    state = CombatState(None, [ally], [enemy])
    before = enemy.health
    CombatEngine(state, can_enter=lambda x, y: False).start_enemy_turn()
    assert enemy.health == before - 2
    ally.health = 0
    assert _pick_target(enemy, [ally]) is None


def test_cover_follows_background_obstacle_boundaries_instead_of_random_open_tiles():
    open_cells = frozenset((x, y) for x in range(0, 641, 32) for y in range(0, 481, 32) if x != 320)
    terrain = TerrainProfile("map-mask", 640, 480, 32, open_cells, 255)
    plan = build_battlefield_plan(map_index=5, width=640, height=480, reserved_positions=(), terrain_profile=terrain)
    assert plan.cover_nodes
    assert all(node.world_x == 320 for node in plan.cover_nodes)
    assert not trace_sight_line((224, 224), (416, 224), list(plan.cover_nodes)).clear
