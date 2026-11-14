"""Enemy AI upgrade regressions for Wave 6 combat feel."""

import unittest

from game.character import Character
from game.combat_system import _target_score, run_enemy_ai
from game.cover_system import CoverNode
from game.mission_objectives import create_battle_objective
from game.mission_templates import MissionTemplate
from game.stats import EnemyStats, PlayerStats
from game.unit import Unit


def _player(
    name: str = "Agent",
    *,
    role: str = "samurai",
    hp: int = 20,
    max_hp: int = 20,
    x: int = 0,
    y: int = 0,
    defense: int = 3,
) -> Unit:
    stats = PlayerStats(level=2, str=5, agi=5, psi=2, defense=defense)
    stats.hp = hp
    stats.max_hp = max_hp
    return Unit(
        position=(x, y),
        stats=stats,
        health=hp,
        character=Character(name, role=role),
        unit_type="agent",
    )


def _enemy(
    *,
    subtype: str = "grunt",
    hp: int = 20,
    x: int = 160,
    y: int = 0,
    attack_range: int = 1,
    agi: int = 3,
    ap: int = 2,
) -> Unit:
    stats = EnemyStats(level=1, str=3, agi=agi, defense=1)
    stats.hp = hp
    stats.max_hp = hp
    return Unit(
        position=(x, y),
        stats=stats,
        health=hp,
        unit_type="enemy",
        enemy_subtype=subtype,
        attack_range=attack_range,
        action_points=ap,
    )


def _mission(objective_type: str) -> MissionTemplate:
    return MissionTemplate(
        id="ai-objective",
        title="AI Objective",
        objective_text="Pressure the objective.",
        target_faction="Test",
        district="Test",
        district_pressure={},
        starting_enemy_count=1,
        objective_type=objective_type,
    )


class EnemyAIUpgradeTest(unittest.TestCase):
    def test_target_score_prioritizes_wounded_high_threat_units(self):
        enemy = _enemy(x=160, y=0)
        wounded_sniper = _player("Vera", role="sniper", hp=5, max_hp=20, x=128, y=0)
        healthy_guard = _player("Mako", role="heavy", hp=20, max_hp=20, x=32, y=0)

        self.assertGreater(
            _target_score(enemy, wounded_sniper),
            _target_score(enemy, healthy_guard),
        )

    def test_commander_aura_is_temporary_and_never_stacks_between_turns(self):
        player = _player(hp=100, x=0, y=0)
        commander = _enemy(subtype="commander", x=192, y=0, attack_range=1)
        grunt = _enemy(subtype="grunt", x=160, y=0, attack_range=1, agi=3)

        run_enemy_ai([player], [commander, grunt])
        grunt.reset_actions()
        commander.reset_actions()
        run_enemy_ai([player], [commander, grunt])

        self.assertEqual(grunt.stats.agi, 3)

    def test_ranged_enemy_repositions_to_flank_covered_target_before_shooting(self):
        player = _player(hp=100, x=64, y=0)
        player.in_cover_bonus = 2
        enemy = _enemy(x=160, y=0, attack_range=5, ap=2)
        cover_nodes = [CoverNode(grid_x=1, grid_y=0, cover_type="high")]

        results = run_enemy_ai([player], [enemy], cover_nodes=cover_nodes)

        self.assertEqual(enemy.position, (128, 0))
        self.assertTrue(any(result.decision_reason == "flanking" for result in results))

    def test_containment_objective_pulls_enemy_toward_breach_line(self):
        player = _player(hp=100, x=0, y=0)
        enemy = _enemy(x=320, y=320, attack_range=1, ap=1)
        objective = create_battle_objective(_mission("containment"))

        results = run_enemy_ai([player], [enemy], objective=objective)

        self.assertEqual(enemy.position, (320, 288))
        self.assertTrue(
            any(result.decision_reason == "objective_pressure" for result in results)
        )


if __name__ == "__main__":
    unittest.main()
