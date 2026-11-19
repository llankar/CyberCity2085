import unittest

from game.character import Character
from game.recruitment import create_character


class TestAgentSheetSchema(unittest.TestCase):
    def test_new_recruit_gets_schema_defaults(self):
        recruit = create_character("Agent 1", "sniper")

        self.assertIn("str", recruit.attributes)
        self.assertIn("firearms", recruit.skills)
        self.assertIn("resolve", recruit.derived_stats)
        self.assertEqual(recruit.attributes["agi"], recruit.stats.agi)

    def test_old_save_payload_is_backfilled_and_skill_ranks_are_bounded(self):
        legacy_payload = {
            "name": "Legacy",
            "role": "psi",
            "stats": {"level": 2, "psi": 9, "str": 2, "agi": 3, "con": 2, "cha": 4, "defense": 1},
            "skills": {"telepathy": 99, "firearms": -5},
        }

        restored = Character.from_dict(legacy_payload)

        self.assertIn("attributes", restored.to_dict())
        self.assertIn("derived_stats", restored.to_dict())
        self.assertEqual(restored.sex, "")
        self.assertEqual(restored.skills["telepathy"], 10)
        self.assertEqual(restored.skills["firearms"], 0)

    def test_sex_field_persists_through_character_serialization(self):
        character = Character("Vega", role="sniper", sex="female", nickname="Breaker")

        restored = Character.from_dict(character.to_dict())

        self.assertEqual(restored.sex, "female")
        self.assertEqual(restored.nickname, "Breaker")


if __name__ == "__main__":
    unittest.main()
