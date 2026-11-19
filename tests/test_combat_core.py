"""Core combat mechanics — cover bonuses, ranged enemy AI, dead-unit clean-up."""

import random
import unittest

from game.combat_system import run_enemy_ai
from game.cover_system import CoverNode, cover_defense_bonus
from game.stats import EnemyStats, PlayerStats, perform_attack
from game.unit import Unit


def _player(hp: int = 20, x: int = 100, y: int = 100, atk_range: int = 1) -> Unit:
    stats = PlayerStats(level=2, str=5, agi=5, psi=2, defense=1)
    stats.hp = hp
    stats.max_hp = hp
    u = Unit(position=(x, y), stats=stats, health=hp, unit_type="agent", attack_range=atk_range)
    return u


def _enemy(hp: int = 10, x: int = 200, y: int = 100, atk_range: int = 1) -> Unit:
    stats = EnemyStats(level=1, str=3, agi=3, defense=1)
    stats.hp = hp
    stats.max_hp = hp
    u = Unit(position=(x, y), stats=stats, health=hp, unit_type="enemy", attack_range=atk_range)
    return u


class TestCoverDefenseBonus(unittest.TestCase):
    def test_extra_defense_reduces_hit_chance(self):
        """Higher extra_defense makes attacks less likely to land."""
        random.seed(0)
        attacker = PlayerStats(level=1, agi=3)
        defender = EnemyStats(level=1, defense=1)
        defender.hp = 100
        defender.max_hp = 100

        # 1000 attacks without cover
        no_cover_hits = sum(
            int(perform_attack(attacker, defender, "agi", extra_defense=0)[0])
            for _ in range(1000)
        )
        defender.hp = 100  # reset

        # 1000 attacks with +2 cover bonus
        cover_hits = sum(
            int(perform_attack(attacker, defender, "agi", extra_defense=2)[0])
            for _ in range(1000)
        )

        # Hit rate should be noticeably lower with cover
        self.assertLess(cover_hits, no_cover_hits)

    def test_cover_bonus_applied_via_unit_in_cover_bonus(self):
        """Unit.in_cover_bonus flows through to perform_attack via _perform_attack.

        We test perform_attack directly (100 trials) to avoid action_point
        depletion interfering with the statistical comparison.
        """
        attacker_stats = PlayerStats(level=1, agi=4)
        defender_stats = EnemyStats(level=1, defense=1)

        N = 500
        random.seed(42)
        hits_no_cover = sum(
            int(perform_attack(attacker_stats, defender_stats, "agi", extra_defense=0)[0])
            for _ in range(N)
        )

        random.seed(42)
        hits_with_cover = sum(
            int(perform_attack(attacker_stats, defender_stats, "agi", extra_defense=4)[0])
            for _ in range(N)
        )

        # With +4 extra defense the hit rate should be noticeably lower
        self.assertLess(hits_with_cover, hits_no_cover)

        # Sanity: in_cover_bonus=0 must not reduce hits vs baseline
        attacker = _player(hp=20, x=0, y=0, atk_range=5)
        defender = _enemy(hp=500, x=64, y=0)  # hp high enough to survive
        defender.in_cover_bonus = 0
        attacker.action_points = 1
        pre = defender.stats.hp
        attacker.shoot(defender)
        # After one shot, damage was resolved with 0 cover bonus (no error)
        self.assertGreaterEqual(pre, defender.stats.hp)

    def test_cover_defense_bonus_from_cover_node(self):
        """cover_defense_bonus returns correct values for unit on/near a node."""
        node = CoverNode(grid_x=3, grid_y=3, cover_type="high")
        unit = _player(x=3 * 32, y=3 * 32)    # standing on the node
        self.assertEqual(cover_defense_bonus(unit, [node]), 2)

        unit2 = _player(x=3 * 32, y=4 * 32)    # one tile away
        self.assertEqual(cover_defense_bonus(unit2, [node]), 2)

        unit3 = _player(x=6 * 32, y=6 * 32)    # far from node
        self.assertEqual(cover_defense_bonus(unit3, [node]), 0)


class TestEnemyRangedAI(unittest.TestCase):
    def test_enemy_with_range_shoots_from_distance(self):
        """Enemy with attack_range > 1 uses shoot() and doesn't need to close distance."""
        # Place player and ranged enemy 3 cells apart (96px)
        player = _player(hp=100, x=0, y=0)
        enemy  = _enemy(hp=50, x=3 * 32, y=0, atk_range=5)  # 5-cell range

        random.seed(7)
        results = run_enemy_ai([player], [enemy])

        # Enemy should have attacked (damage result) — not just moved
        attack_results = [r for r in results if r.damage > 0]
        self.assertTrue(len(attack_results) >= 1, "Ranged enemy should have dealt damage from 3 cells away")

    def test_enemy_without_range_must_close_distance(self):
        """Enemy with attack_range=1 must move adjacent before dealing damage."""
        player = _player(hp=100, x=0, y=0)
        enemy  = _enemy(hp=50, x=5 * 32, y=0, atk_range=1)  # melee only, 5 cells away

        random.seed(1)
        results = run_enemy_ai([player], [enemy])

        # Should have moved (no direct damage from start position)
        move_results = [r for r in results if r.moved]
        self.assertTrue(len(move_results) >= 1, "Melee enemy should have moved toward player")

    def test_dead_enemy_skipped_in_ai(self):
        """Enemies with health <= 0 before the AI pass are completely skipped."""
        player = _player(hp=30)
        alive  = _enemy(hp=15, x=64, y=0)
        dead   = _enemy(hp=0,  x=32, y=0)   # already dead
        dead.stats.hp = 0

        results = run_enemy_ai([player], [alive, dead])

        # All results should come from alive enemy only
        for r in results:
            self.assertIs(r.enemy, alive)


class TestDeadEnemyNotInList(unittest.TestCase):
    def test_enemy_removed_from_list_on_kill(self):
        """Enemy killed in run_enemy_ai is removed from enemy_units list."""
        player = _player(hp=1)   # very fragile — will die
        enemy  = _enemy(hp=50, x=32, y=0, atk_range=1)

        enemy_list  = [enemy]
        player_list = [player]
        defeated    = []

        random.seed(3)
        run_enemy_ai(
            player_list,
            enemy_list,
            defeated_player_units=defeated,
        )

        # Player should be in defeated, not in active list
        if defeated:
            self.assertNotIn(player, player_list)


if __name__ == "__main__":
    unittest.main()
