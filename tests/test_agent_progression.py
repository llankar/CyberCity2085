import unittest
import random

from game.agent_specializations import apply_talent_bonuses
from game.character import Character
from game.recruitment import ROLE_NAME_POOLS, build_recruitment_candidates, create_character, recruit_agent
from game.ui.portraits import (
    portrait_path_for_agent,
    portrait_path_for_enemy,
    portrait_path_for_power_armor,
    portrait_path_for_robot,
)


class AgentProgressionTest(unittest.TestCase):
    def test_recruitment_candidates_are_named_and_role_balanced(self):
        roster = [Character("Kilo"), Character("Echo")]

        candidates = build_recruitment_candidates(roster, count=6, rng=random.Random(1337))

        self.assertEqual(len(candidates), 6)
        self.assertTrue(all(candidate.name for candidate in candidates))
        self.assertTrue(all(candidate.role in {"samurai", "sniper", "psi"} for candidate in candidates))
        self.assertTrue(all(candidate.function for candidate in candidates))
        self.assertTrue(all(candidate.background for candidate in candidates))
        self.assertTrue(all(candidate.advantages for candidate in candidates))
        self.assertTrue(all(candidate.price > 0 for candidate in candidates))
        self.assertTrue(all(candidate.skill_line().startswith("SKILLS") for candidate in candidates))
        self.assertTrue(any(any(rank > 0 for rank in candidate.skill_ranks.values()) for candidate in candidates))
        self.assertTrue(all(candidate.portrait_path.endswith(".png") for candidate in candidates))
        self.assertTrue(all(candidate.stat_line() for candidate in candidates))
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

    def test_portrait_pools_split_human_and_robot_variants(self):
        female = portrait_path_for_agent("Vega", "sniper", "female")
        male = portrait_path_for_agent("Vega", "sniper", "male")
        robot = portrait_path_for_robot("robot_k9_01", "combat_robot")
        armor = portrait_path_for_power_armor("armor_mantis_01", "power_armor")
        raider = portrait_path_for_enemy("raider_01", "raider", "grunt")

        self.assertIn("agent_female_", female)
        self.assertIn("agent_male_", male)
        self.assertIn("robot_", robot)
        self.assertIn("power_armor_", armor)
        self.assertIn("enemy_raider_", raider)
        self.assertTrue(female.endswith(".png"))
        self.assertTrue(male.endswith(".png"))
        self.assertTrue(robot.endswith(".png"))
        self.assertTrue(armor.endswith(".png"))
        self.assertTrue(raider.endswith(".png"))

    def test_talent_bonuses_apply_to_combat_stats(self):
        character = Character("Orchid", role="psi")
        character.specializations = ["psi_mind_focus", "psi_warding_shell"]

        stats = apply_talent_bonuses(character.stats, character.specializations)

        self.assertGreaterEqual(stats.psi, character.stats.psi + 1)
        self.assertGreaterEqual(stats.defense, character.stats.defense + 1)


if __name__ == "__main__":
    unittest.main()
