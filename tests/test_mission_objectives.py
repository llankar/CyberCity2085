"""Battlefield objective creation and completion rules."""

import unittest

from game.mission_objectives import (
    BattleObjective,
    create_battle_objective,
    interact_with_objective,
    is_in_interaction_range,
)
from game.mission_templates import MissionTemplate, create_mission_templates


def _mission(objective_type="extract"):
    return MissionTemplate(
        id="objective_test",
        title="Objective Test",
        objective_text="Secure the prototype objective.",
        target_faction="Test Faction",
        district="Test District",
        district_pressure={},
        starting_enemy_count=1,
        objective_type=objective_type,
    )


class MissionObjectivesTest(unittest.TestCase):
    def test_mission_templates_assign_distinct_objective_types(self):
        templates = {mission.id: mission for mission in create_mission_templates()}

        self.assertEqual(templates["extraction"].objective_type, "safe_extraction")
        self.assertEqual(templates["sabotage"].objective_type, "sabotage_window")
        self.assertEqual(templates["data_theft"].objective_type, "data_with_detour")

    def test_objective_creation_uses_readable_label_for_type(self):
        objective = create_battle_objective(_mission("data_theft"))

        self.assertIsNotNone(objective)
        self.assertEqual(objective.kind, "data_theft")
        self.assertEqual(objective.label, "CACHE")
        self.assertFalse(objective.completed)
        self.assertIn("CACHE", objective.status_text)
        self.assertIn("Press E near CACHE", objective.interaction_prompt)
        self.assertIn("0/2", objective.progress_text)

    def test_legacy_objective_branch_aliases_create_tactical_objectives(self):
        extraction = create_battle_objective(_mission("safe_extraction"))
        sabotage = create_battle_objective(_mission("sabotage_window"))
        data = create_battle_objective(_mission("data_with_detour"))

        self.assertEqual(extraction.kind, "extract")
        self.assertEqual(sabotage.kind, "sabotage")
        self.assertEqual(data.kind, "data_theft")

    def test_interaction_range_allows_one_grid_cell(self):
        objective = BattleObjective(kind="extract", position=(448, 320), label="WITNESS")

        self.assertTrue(is_in_interaction_range((416, 320), objective))
        self.assertTrue(is_in_interaction_range((448, 320), objective))
        self.assertFalse(is_in_interaction_range((384, 320), objective))

    def test_interaction_completes_objective_in_range(self):
        objective = BattleObjective(kind="sabotage", position=(448, 320), label="RELAY")

        completed, message = interact_with_objective((448, 288), objective)

        self.assertTrue(completed)
        self.assertTrue(objective.completed)
        self.assertEqual(objective.progress, 1)
        self.assertIn("complete", message.lower())

    def test_data_theft_requires_two_interaction_turns(self):
        objective = create_battle_objective(_mission("data_theft"))

        first_completed, first_message = interact_with_objective((448, 320), objective)
        second_completed, second_message = interact_with_objective((448, 320), objective)

        self.assertFalse(first_completed)
        self.assertIn("1/2", first_message)
        self.assertTrue(second_completed)
        self.assertTrue(objective.completed)
        self.assertIn("complete", second_message.lower())

    def test_interaction_out_of_range_keeps_objective_pending(self):
        objective = BattleObjective(kind="extract", position=(448, 320), label="WITNESS")

        completed, message = interact_with_objective((352, 320), objective)

        self.assertFalse(completed)
        self.assertFalse(objective.completed)
        self.assertIn("within one grid cell", message)

    def test_mission_template_save_load_preserves_objective_type(self):
        mission = _mission("sabotage")

        loaded = MissionTemplate.from_dict(mission.to_dict())

        self.assertEqual(loaded.objective_type, "sabotage")

    def test_mission_template_load_translates_legacy_french_briefing_text(self):
        payload = _mission("extract").to_dict()
        payload["emotional_impact_hint"] = {
            "level": "critical",
            "text": "Risque de s\u00e9quelles \u00e9motionnelles durables pour l'escouade.",
            "short_text": "Risque de s\u00e9quelles \u00e9motionnelles durables pour l'escouade (s\u00e9quelles \u00e9motionnelles probables).",
            "emotional_impact_summary": "Risque de s\u00e9quelles \u00e9motionnelles durables pour l'escouade (s\u00e9quelles \u00e9motionnelles probables).",
        }

        loaded = MissionTemplate.from_dict(payload)

        self.assertTrue(loaded.emotional_impact_hint["text"].startswith("Risk of lasting emotional scars"))
        self.assertIn("likely emotional scars", loaded.emotional_impact_hint["short_text"])
        self.assertIn("likely emotional scars", loaded.emotional_impact_hint["emotional_impact_summary"])

    def test_mission_template_load_defaults_missing_or_unknown_type_to_eliminate(self):
        legacy_payload = _mission("extract").to_dict()
        legacy_payload.pop("objective_type")
        unknown_payload = {**legacy_payload, "objective_type": "escort"}

        self.assertEqual(MissionTemplate.from_dict(legacy_payload).objective_type, "eliminate")
        self.assertEqual(MissionTemplate.from_dict(unknown_payload).objective_type, "eliminate")
        self.assertIsNone(create_battle_objective(MissionTemplate.from_dict(legacy_payload)))


if __name__ == "__main__":
    unittest.main()
