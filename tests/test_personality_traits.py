"""Tests for compact agent personality traits and mission-log modulation."""

import unittest

from game.narrative.personality_traits import (
    assign_personality_traits,
    modulate_mission_log_tone,
)


class PersonalityTraitsTest(unittest.TestCase):
    def test_modulation_effective_on_text(self):
        text = "Complication triggered: blackout spread through sector 9."

        modulated = modulate_mission_log_tone(text, "steadfast", "cunning")

        self.assertIn("Steady voice:", modulated)
        self.assertIn(text, modulated)
        self.assertIn("Finds leverage in chaos.", modulated)

    def test_trait_assignment_is_deterministic_with_identical_seed(self):
        first = assign_personality_traits("Agent 3", "sniper", roster_index=3, seed=99)
        second = assign_personality_traits("Agent 3", "sniper", roster_index=3, seed=99)

        self.assertEqual(first, second)

    def test_neutral_fallback_without_traits(self):
        text = "Mission launched: Quiet Static against Chrome Jackals."

        self.assertEqual(modulate_mission_log_tone(text, None, None), text)
        self.assertEqual(modulate_mission_log_tone(text, "", ""), text)


if __name__ == "__main__":
    unittest.main()
