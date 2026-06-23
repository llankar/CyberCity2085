import unittest

from game.character import Character
from game.combat_system import create_enemy_units
from game.enemy_themes import mission_enemy_theme, normalize_enemy_theme
from game.mission_templates import MissionTemplate


class EnemyThemeTest(unittest.TestCase):
    def test_theme_aliases_and_mission_detection(self):
        mission = MissionTemplate(
            id="badlands_run",
            title="Badlands Run",
            objective_text="Push beyond the city limits.",
            target_faction="Scavengers",
            district="Badlands",
            district_pressure={},
            starting_enemy_count=2,
            enemy_theme="",
            risk_level=8,
        )

        self.assertEqual(normalize_enemy_theme("Three Sevens"), "corp_37")
        self.assertEqual(normalize_enemy_theme("Cyber Samurai"), "corp_samurai")
        self.assertEqual(normalize_enemy_theme("cyborg starver"), "novatek_hybrid")
        self.assertEqual(mission_enemy_theme(mission), "raider")

    def test_novatek_hybrid_theme_detects_experiment_mission_text(self):
        mission = MissionTemplate(
            id="novatek_delta",
            title="Novatek Containment Site Delta-9",
            objective_text="Extract cyborg-Starver hybrid data before mutant escalation.",
            target_faction="Novatek",
            district="Chrome Warrens",
            district_pressure={},
            starting_enemy_count=2,
            enemy_theme="",
            risk_level=7,
        )

        self.assertEqual(mission_enemy_theme(mission), "novatek_hybrid")

    def test_enemy_theme_round_trips_through_mission_template_serialization(self):
        mission = MissionTemplate(
            id="theme_test",
            title="Theme Test",
            objective_text="Validate serialized enemy routing.",
            target_faction="Three Sevens Corp",
            district="Chrome Warrens",
            district_pressure={},
            starting_enemy_count=3,
            enemy_theme="corp_37_power_armor",
            risk_level=9,
        )

        restored = MissionTemplate.from_dict(mission.to_dict())

        self.assertEqual(restored.enemy_theme, "corp_37_power_armor")

    def test_enemy_units_inherit_the_theme_from_mission(self):
        mission = MissionTemplate(
            id="battle_theme",
            title="Battle Theme",
            objective_text="Check battle spawning.",
            target_faction="Three Sevens Corp",
            district="Chrome Warrens",
            district_pressure={},
            starting_enemy_count=3,
            enemy_theme="corp_37_power_armor",
            risk_level=8,
        )

        enemy_units, count = create_enemy_units(mission, [Character("Alpha")])

        self.assertEqual(count, 3)
        self.assertTrue(enemy_units)
        self.assertTrue(all(unit.enemy_theme == "corp_37_power_armor" for unit in enemy_units))
        self.assertTrue(all(unit.attack_range >= 3 for unit in enemy_units))


if __name__ == "__main__":
    unittest.main()
