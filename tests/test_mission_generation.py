"""Mission board generation keeps daily flavor while staying deterministic."""

import unittest

from game.gamestate import GameState
from game.combat.godot_bridge import build_godot_combat_payload
from game.mission_generation import _regional_missions
from game.mission_system import ensure_mission_templates, resolve_mission_outcome


class MissionGenerationTest(unittest.TestCase):
    def test_regional_outcomes_apply_contract_specific_district_effects(self):
        missions = {mission.id: mission for mission in _regional_missions("Chrome Warrens")}
        for contract, victory, field, delta in (
            ("shelter_perimeter", True, "stability", 5),
            ("clinic_breach", False, "media_heat", 5),
            ("samurai_intercept", False, "media_heat", 2),
        ):
            with self.subTest(contract=contract):
                state = GameState()
                setattr(state.district, field, 30)
                resolve_mission_outcome(state, missions[contract], victory)
                self.assertEqual(getattr(state.district, field), 30 + delta)

    def test_regional_contracts_offer_defense_containment_and_priority_targets(self):
        missions = {mission.id: mission for mission in _regional_missions("Chrome Warrens")}
        expected = {
            "shelter_perimeter": "defend",
            "clinic_breach": "containment",
            "samurai_intercept": "assassination",
        }
        state = GameState()
        for contract, objective in expected.items():
            with self.subTest(contract=contract):
                mission = missions[contract]
                payload = build_godot_combat_payload(state, mission)
                self.assertEqual(payload["mission"]["objective_type"], objective)
                self.assertTrue(payload["map"]["path"])

    def test_daily_generation_creates_day_tagged_board(self):
        game_state = GameState(mission_templates=[])

        ensure_mission_templates(game_state)

        self.assertEqual(game_state.mission_board_generated_day, game_state.calendar.current_day)
        self.assertTrue(game_state.mission_templates)
        self.assertGreaterEqual(len(game_state.mission_templates), 3)
        self.assertLessEqual(len(game_state.mission_templates), 6)
        self.assertTrue(
            any(f"Day {game_state.calendar.current_day}" in m.title for m in game_state.mission_templates)
        )
        self.assertTrue(
            all(
                f"Day {game_state.calendar.current_day}" in m.title or m.title.startswith("[STORY]")
                for m in game_state.mission_templates
            )
        )

    def test_same_day_generation_is_stable(self):
        game_state = GameState(mission_templates=[])

        ensure_mission_templates(game_state)
        first_ids = [m.id for m in game_state.mission_templates]
        ensure_mission_templates(game_state)
        second_ids = [m.id for m in game_state.mission_templates]

        self.assertEqual(first_ids, second_ids)

    def test_next_day_regenerates_board(self):
        game_state = GameState(mission_templates=[])

        ensure_mission_templates(game_state)
        day_one_ids = [m.id for m in game_state.mission_templates]

        game_state.advance_one_day("test")
        ensure_mission_templates(game_state)
        day_two_ids = [m.id for m in game_state.mission_templates]

        self.assertNotEqual(day_one_ids, day_two_ids)


if __name__ == "__main__":
    unittest.main()
