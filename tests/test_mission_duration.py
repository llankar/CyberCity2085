"""Mission duration defaults and calendar advancement rules."""

import unittest

from game.gamestate import GameState
from game.mission_system import launch_selected_mission, resolve_mission_outcome
from game.mission_templates import MissionTemplate, create_mission_templates


def _mission(duration_days: int | None = None) -> MissionTemplate:
    kwargs = {}
    if duration_days is not None:
        kwargs["duration_days"] = duration_days
    return MissionTemplate(
        id="duration_test",
        title="Duration Test",
        objective_text="Validate calendar pacing.",
        target_faction="Clockwork Saints",
        district="Chrome Warrens",
        district_pressure={},
        starting_enemy_count=1,
        risk_level=1,
        **kwargs,
    )


class MissionDurationTest(unittest.TestCase):
    def test_generated_missions_default_to_one_day(self):
        missions = create_mission_templates("Chrome Warrens")

        self.assertTrue(missions)
        self.assertTrue(all(mission.duration_days == 1 for mission in missions))
        self.assertTrue(
            all(mission.to_dict()["duration_days"] == 1 for mission in missions)
        )

    def test_launching_and_resolving_selected_mission_advances_exactly_one_day(self):
        game_state = GameState(mission_templates=[_mission()])
        starting_day = game_state.calendar.current_day

        mission = launch_selected_mission(game_state)
        resolve_mission_outcome(game_state, mission, True)

        self.assertEqual(game_state.calendar.current_day, starting_day + 1)
        self.assertEqual(game_state.turn, starting_day + 1)

    def test_direct_resolution_advances_by_default_mission_duration(self):
        game_state = GameState()
        starting_day = game_state.calendar.current_day

        resolve_mission_outcome(game_state, _mission(duration_days=1), False)

        self.assertEqual(game_state.calendar.current_day, starting_day + 1)
        self.assertEqual(game_state.turn, starting_day + 1)

    def test_resolution_respects_explicit_duration_override(self):
        game_state = GameState()
        starting_day = game_state.calendar.current_day

        resolve_mission_outcome(game_state, _mission(duration_days=2), True)

        self.assertEqual(game_state.calendar.current_day, starting_day + 2)
        self.assertEqual(game_state.turn, starting_day + 2)

    def test_duration_serialization_defaults_old_missions_to_one_day(self):
        mission = MissionTemplate.from_dict(
            {
                "id": "legacy",
                "title": "Legacy Mission",
                "objective_text": "Restore an old save mission.",
                "target_faction": "Chrome Jackals",
                "district": "Chrome Warrens",
                "district_pressure": {},
                "starting_enemy_count": 1,
            }
        )

        self.assertEqual(mission.duration_days, 1)
        self.assertEqual(mission.to_dict()["duration_days"], 1)


if __name__ == "__main__":
    unittest.main()
