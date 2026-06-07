"""Regression tests for render-independent combat events."""

from __future__ import annotations

import unittest

from game.combat import CombatEngine, CombatState
from game.mission_templates import MissionComplication, MissionTemplate


def _mission_with(*complications: MissionComplication) -> MissionTemplate:
    return MissionTemplate(
        id="event-test",
        title="Event Test",
        objective_text="Hold the line.",
        target_faction="corp",
        district="Neon Ward",
        district_pressure={},
        starting_enemy_count=0,
        possible_complications=list(complications),
    )


def _complication(key: str, name: str) -> MissionComplication:
    return MissionComplication(
        key=key,
        name=name,
        trigger_text="The city pushes back.",
        risk_threshold=1,
    )


class CombatEventsTest(unittest.TestCase):
    def test_reinforcements_trigger_on_turn_three(self) -> None:
        mission = _mission_with(_complication("rapid_response", "Rapid Response"))
        state = CombatState(mission, [], [], turn_number=3)
        engine = CombatEngine(state)

        results = engine.resolve_combat_events(battlefield_size=(1280, 720))

        self.assertEqual([result.kind for result in results].count("spawn_enemy"), 2)
        self.assertIn("sound_key", [result.kind for result in results])
        self.assertIn("screen_shake", [result.kind for result in results])
        self.assertIn("log_message", [result.kind for result in results])
        self.assertIn(
            "rapid_response", state.tactical_flags["triggered_combat_event_keys"]
        )

    def test_blackout_triggers_on_turn_two(self) -> None:
        mission = _mission_with(_complication("watcher_drone", "Watcher Drone"))
        state = CombatState(mission, [], [], turn_number=2)
        engine = CombatEngine(state)

        results = engine.resolve_combat_events()

        visibility_results = [
            result for result in results if result.kind == "visibility_changed"
        ]
        self.assertEqual(len(visibility_results), 1)
        self.assertEqual(visibility_results[0].payload["fog_radius"], 3)
        self.assertEqual(visibility_results[0].payload["duration_turns"], 2)
        self.assertEqual([result.kind for result in results].count("log_message"), 1)

    def test_already_triggered_event_does_not_fire_again(self) -> None:
        mission = _mission_with(_complication("rapid_response", "Rapid Response"))
        state = CombatState(
            mission,
            [],
            [],
            turn_number=4,
            tactical_flags={"triggered_combat_event_keys": {"rapid_response"}},
        )
        engine = CombatEngine(state)

        results = engine.resolve_combat_events()

        self.assertEqual(results, [])
        self.assertEqual(
            state.tactical_flags["triggered_combat_event_keys"], {"rapid_response"}
        )


if __name__ == "__main__":
    unittest.main()
