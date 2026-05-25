import unittest

from game.agent_specializations import apply_talent_bonuses
from game.character import Character
from game.recruitment import ROLE_NAME_POOLS, build_recruitment_candidates, create_character, recruit_agent


class AgentProgressionTest(unittest.TestCase):
    def test_recruitment_candidates_are_named_and_role_balanced(self):
        roster = [Character("Kilo"), Character("Echo")]

        candidates = build_recruitment_candidates(roster)

        self.assertEqual(len(candidates), 6)
        self.assertTrue(all(candidate.name for candidate in candidates))
        self.assertTrue(all(candidate.role in {"samurai", "sniper", "psi"} for candidate in candidates))
        self.assertNotIn("Agent 1", {candidate.name for candidate in candidates})

    def test_recruit_agent_uses_the_requested_name(self):
        roster = []

        recruit = recruit_agent(roster, "samurai", "Sable")

        self.assertEqual(recruit.name, "Sable")
        self.assertEqual(roster[0].name, "Sable")
        self.assertEqual(recruit.talent_points, 1)

    def test_placeholder_roster_labels_are_normalized_to_codename_names(self):
        character = create_character("Agent 1", "samurai")

        self.assertNotEqual(character.name, "Agent 1")
        self.assertIn(character.name, ROLE_NAME_POOLS["samurai"])

    def test_talent_bonuses_apply_to_combat_stats(self):
        character = Character("Orchid", role="psi")
        character.specializations = ["psi_mind_focus", "psi_warding_shell"]

        stats = apply_talent_bonuses(character.stats, character.specializations)

        self.assertGreaterEqual(stats.psi, character.stats.psi + 1)
        self.assertGreaterEqual(stats.defense, character.stats.defense + 1)


if __name__ == "__main__":
    unittest.main()
