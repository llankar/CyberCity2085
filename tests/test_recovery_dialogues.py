"""Recovery room support dialogue generation tests."""

import unittest

from game.character import Character
from game.narrative.recovery_dialogues import generate_recovery_dialogues


class RecoveryDialoguesTest(unittest.TestCase):
    def test_triggers_when_stress_is_high(self):
        agents = [
            Character("Nyx", role="samurai", stress=80),
            Character("Patch", role="medic", stress=72),
            Character("Calm", role="scout", stress=20),
        ]
        state = {
            "day": 7,
            "squad_by_agent": {"Nyx": "Alpha", "Patch": "Alpha", "Calm": "Beta"},
            "memory": {},
        }

        dialogues = generate_recovery_dialogues(agents, state)

        self.assertEqual(len(dialogues), 1)
        self.assertEqual(dialogues[0]["pair"], ["Nyx", "Patch"])
        self.assertEqual(dialogues[0]["affinity_reason"], "same_squad")
        self.assertIn("memory", state)

    def test_no_dialogue_when_conditions_not_met(self):
        agents = [
            Character("LowA", stress=20),
            Character("LowB", stress=30),
        ]

        dialogues = generate_recovery_dialogues(agents, {"day": 8, "memory": {}})

        self.assertEqual(dialogues, [])

    def test_avoids_repeating_pair_and_line_on_next_day(self):
        agents = [
            Character("Nyx", role="samurai", stress=82),
            Character("Patch", role="medic", stress=75),
            Character("Cipher", role="netrunner", stress=78),
        ]
        state_day_1 = {
            "day": 10,
            "squad_by_agent": {"Nyx": "Alpha", "Patch": "Alpha", "Cipher": "Beta"},
            "memory": {},
            "max_dialogues": 1,
        }
        day_1 = generate_recovery_dialogues(agents, state_day_1)

        state_day_2 = {
            "day": 11,
            "squad_by_agent": state_day_1["squad_by_agent"],
            "memory": state_day_1["memory"],
            "max_dialogues": 1,
        }
        day_2 = generate_recovery_dialogues(agents, state_day_2)

        self.assertEqual(len(day_1), 1)
        self.assertEqual(len(day_2), 1)
        self.assertNotEqual(day_1[0]["pair"], day_2[0]["pair"])
        self.assertNotEqual(day_1[0]["line"], day_2[0]["line"])


if __name__ == "__main__":
    unittest.main()
