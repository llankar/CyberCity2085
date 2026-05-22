import unittest

from game.agent_aftermath import apply_mission_aftermath
from game.character import Character
from game.mission_templates import create_mission_templates
from game.recruitment import recruit_agent
from game.relationships.mentor_history import upsert_mentor_link


class MentorHistoryTests(unittest.TestCase):
    def test_upsert_creates_then_increments_link(self):
        links: dict[str, dict] = {}

        upsert_mentor_link(links, agent_id="Nyx", strategic_day=3, bond_delta=1)
        upsert_mentor_link(links, agent_id="Nyx", strategic_day=5, bond_delta=2)

        self.assertEqual(links["Nyx"]["agent_id"], "Nyx")
        self.assertEqual(links["Nyx"]["bond_level"], 3)
        self.assertEqual(links["Nyx"]["strategic_day"], 5)

    def test_recruitment_and_aftermath_evolve_links(self):
        roster: list[Character] = []
        alpha = recruit_agent(roster, "samurai")
        bravo = recruit_agent(roster, "sniper")

        self.assertIn(bravo.name, alpha.mentor_links)
        self.assertIn(alpha.name, bravo.mentor_links)

        mission = create_mission_templates()[0]
        apply_mission_aftermath([alpha, bravo], mission, victory=True)

        self.assertGreaterEqual(alpha.mentor_links[bravo.name]["bond_level"], 3)
        self.assertGreaterEqual(bravo.mentor_links[alpha.name]["bond_level"], 3)


if __name__ == "__main__":
    unittest.main()
