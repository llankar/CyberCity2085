"""Strategic calendar and day-advance management flow."""

import sys
import tempfile
import types
import unittest
from pathlib import Path

from game.character import Character
from game.gamestate import GameState
from game.management.calendar import StrategicCalendar
from game.mission_system import resolve_mission_outcome
from game.mission_templates import MissionTemplate
from game.ui.command_deck import build_calendar_status_line
from game.ui.room_interaction import ROOM_ACTIONS


def _mission() -> MissionTemplate:
    return MissionTemplate(
        id="calendar_test",
        title="Calendar Test",
        objective_text="Prove time moves after the operation.",
        target_faction="Clockwork Saints",
        district="Chrome Warrens",
        district_pressure={},
        starting_enemy_count=1,
        risk_level=1,
    )


class CalendarManagementTest(unittest.TestCase):
    def test_strategic_calendar_tracks_day_week_month_and_label(self):
        calendar = StrategicCalendar()

        calendar.advance_days(7)

        self.assertEqual(calendar.current_day, 8)
        self.assertEqual(calendar.current_week, 2)
        self.assertEqual(calendar.current_month, 1)
        self.assertEqual(calendar.campaign_date_label, "2085.M01.D08")
        self.assertTrue(calendar.is_new_week)

    def test_game_state_manual_day_advance_triggers_income_events_and_recovery(self):
        agent = Character("Stitch", recovery_turns=1)
        game_state = GameState(characters=[agent])
        starting_funds = game_state.available_funds

        game_state.advance_one_day("manual command")

        self.assertEqual(game_state.calendar.current_day, 2)
        self.assertEqual(game_state.turn, 2)
        self.assertGreater(game_state.available_funds, starting_funds)
        self.assertEqual(agent.recovery_turns, 0)
        self.assertTrue(
            any("passive income" in event for event in game_state.event_log)
        )
        self.assertTrue(
            any("Pending fallout reviewed" in event for event in game_state.event_log)
        )
        self.assertTrue(
            any("Stitch is deployable after recovery" in event for event in game_state.event_log)
        )

    def test_mission_resolution_advances_calendar_on_success_and_failure(self):
        success_state = GameState()
        failure_state = GameState()

        resolve_mission_outcome(success_state, _mission(), True)
        resolve_mission_outcome(failure_state, _mission(), False)

        self.assertEqual(success_state.calendar.current_day, 2)
        self.assertEqual(failure_state.calendar.current_day, 2)
        self.assertTrue(
            any("mission success" in event for event in success_state.event_log)
        )
        self.assertTrue(
            any("mission failure" in event for event in failure_state.event_log)
        )

    def test_calendar_serializes_through_game_state_save(self):
        game_state = GameState()
        game_state.advance_days(3, "test")

        with tempfile.TemporaryDirectory() as temp_dir:
            save_path = Path(temp_dir) / "savegame.json"
            game_state.save(str(save_path))
            loaded = GameState.load(str(save_path))

        self.assertEqual(loaded.calendar.current_day, 4)
        self.assertEqual(loaded.calendar.campaign_date_label, "2085.M01.D04")
        self.assertEqual(loaded.turn, 4)

    def test_command_deck_exposes_manual_advance_day_action(self):
        corp_actions = [action.key for action in ROOM_ACTIONS["corp"]["executive"]]
        city_actions = [action.key for action in ROOM_ACTIONS["city"]["municipal"]]
        status_line = build_calendar_status_line("2085.M01.D02", 2, 1)

        self.assertIn("advance_day", corp_actions)
        self.assertIn("advance_day", city_actions)
        self.assertIn("D ADVANCE DAY", status_line)


if __name__ == "__main__":
    unittest.main()
