"""Unit coverage for the pure combat engine package."""

from __future__ import annotations

import unittest

from game.combat import CombatEngine, CombatState
from game.stats import EnemyStats, PlayerStats
from game.unit import (
    ALL_STATUS_EFFECTS,
    STATUS_BLEEDING,
    STATUS_BURNING,
    STATUS_CONTAMINATED,
    STATUS_PANICKED,
    Unit,
)


def _ally(ap: int = 0, hp: int = 11) -> Unit:
    stats = PlayerStats(con=1)
    stats.hp = hp
    return Unit(position=(0, 0), stats=stats, health=hp, action_points=ap)


def _enemy(ap: int = 0, hp: int = 10, position: tuple[int, int] = (320, 0)) -> Unit:
    stats = EnemyStats(level=1)
    stats.hp = hp
    return Unit(position=position, stats=stats, health=hp, action_points=ap, unit_type="enemy")


class CombatEngineTest(unittest.TestCase):
    def test_start_player_turn_resets_ap_ticks_status_and_logs_turn(self) -> None:
        ally = _ally(ap=0, hp=5)
        ally.apply_status(STATUS_BLEEDING)
        state = CombatState(None, [ally], [_enemy()], turn="enemy", turn_number=1)
        engine = CombatEngine(state)

        result = engine.start_player_turn()

        self.assertFalse(result.ended)
        self.assertEqual(state.turn, "player")
        self.assertEqual(state.turn_number, 2)
        self.assertEqual(state.active_index, 0)
        self.assertEqual(ally.action_points, 2)
        self.assertEqual(ally.health, 4)
        self.assertIn("── Turn 2 ──", state.logs)

    def test_status_effect_set_covers_required_wave6_statuses(self) -> None:
        self.assertEqual(
            set(ALL_STATUS_EFFECTS),
            {"suppressed", "bleeding", "stunned", "burning", "contaminated", "panicked"},
        )

    def test_burning_contaminated_and_panicked_tick_on_turn_start(self) -> None:
        ally = _ally(ap=2, hp=8)
        ally.apply_status(STATUS_BURNING)
        ally.apply_status(STATUS_CONTAMINATED)
        ally.apply_status(STATUS_PANICKED)
        state = CombatState(None, [ally], [_enemy()], turn="enemy", turn_number=1)
        engine = CombatEngine(state)

        engine.start_player_turn()

        self.assertEqual(ally.health, 5)
        self.assertEqual(ally.action_points, 0)
        self.assertTrue(ally.has_status(STATUS_BURNING))
        self.assertTrue(ally.has_status(STATUS_CONTAMINATED))
        self.assertFalse(ally.has_status(STATUS_PANICKED))
        self.assertIn("agent is burning (-2 HP)", state.logs)
        self.assertIn("agent is contaminated (-1 HP)", state.logs)

    def test_end_turn_action_consumes_remaining_ap(self) -> None:
        ally = _ally(ap=2)
        state = CombatState(None, [ally], [_enemy()], turn="player")
        engine = CombatEngine(state)

        result = engine.perform_action("end_turn")

        self.assertTrue(result.success)
        self.assertEqual(result.consumed_ap, 2)
        self.assertEqual(ally.action_points, 0)

    def test_end_battle_check_reports_victory_when_no_enemies_remain(self) -> None:
        state = CombatState(None, [_ally(ap=1)], [], turn="player")
        engine = CombatEngine(state)

        result = engine.end_battle_check()

        self.assertTrue(result.ended)
        self.assertEqual(result.outcome, "victory")
        self.assertEqual(result.reason, "all_enemies_down")

    def test_end_battle_check_reports_defeat_when_all_allies_are_down(self) -> None:
        downed = _ally(ap=0, hp=0)
        state = CombatState(None, [downed], [_enemy()], turn="player")
        engine = CombatEngine(state)

        result = engine.end_battle_check()

        self.assertTrue(result.ended)
        self.assertEqual(result.outcome, "defeat")
        self.assertEqual(result.reason, "all_allies_down")

    def test_action_with_ap_sets_defense_and_spends_one_point(self) -> None:
        ally = _ally(ap=2)
        state = CombatState(None, [ally], [_enemy()], turn="player")
        engine = CombatEngine(state)

        result = engine.perform_action("defend")

        self.assertTrue(result.success)
        self.assertEqual(result.consumed_ap, 1)
        self.assertEqual(ally.action_points, 1)
        self.assertTrue(ally.is_defending)


if __name__ == "__main__":
    unittest.main()
