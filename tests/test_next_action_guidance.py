import unittest

from game.gamestate import GameState
from game.ui.guidance.next_action import compute_next_action


class NextActionGuidanceTest(unittest.TestCase):
    def test_guidance_never_empty(self):
        gs = GameState()
        for screen in ("corp", "city", "squad", "battle"):
            guidance = compute_next_action(gs, screen)
            self.assertTrue(guidance.text.strip())
            self.assertTrue(guidance.target_screen.strip())
            self.assertTrue(guidance.target_room.strip())

    def test_guidance_changes_when_state_changes(self):
        gs = GameState()
        first = compute_next_action(gs, "squad").text
        gs.research_unlock_flags.append("starter_unlock")
        gs.selected_agent_names = ["A", "B"]
        gs.strategic_resources["credits"] = 20
        gs.strategic_resources["intel"] = 3
        second = compute_next_action(gs, "squad").text
        self.assertNotEqual(first, second)

    def test_active_research_counts_as_progress_for_next_step(self):
        gs = GameState()
        available = gs.research_tree.available_projects(set(), set())
        self.assertTrue(available)
        self.assertTrue(gs.start_research(available[0].id))

        guidance = compute_next_action(gs, "corp")
        self.assertNotIn("Start a research project", guidance.text)


if __name__ == "__main__":
    unittest.main()
