"""Recovery room support dialogue generation tests."""

import unittest

from game.character import Character
from game.narrative.recovery_dialogues import (
    apply_recovery_dialogue_effects,
    generate_recovery_dialogues,
)


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

    def test_wounded_traumatized_or_bonded_agents_can_trigger_dialogue(self):
        wounded = Character("Vera", role="sniper", stress=20, recovery_turns=2)
        traumatized = Character("Mako", role="medic", stress=25)
        traumatized.trauma.append("Haunted by Relay Trace")
        wounded.mentor_links[traumatized.name] = {
            "agent_id": traumatized.name,
            "bond_level": 3,
            "strategic_day": 4,
        }

        dialogues = generate_recovery_dialogues(
            [wounded, traumatized],
            {"day": 12, "memory": {}},
        )

        self.assertEqual(len(dialogues), 1)
        self.assertEqual(dialogues[0]["pair"], ["Vera", "Mako"])
        self.assertEqual(dialogues[0]["affinity_reason"], "mentor_link")

    def test_recovery_dialogue_effect_applies_small_stress_relief(self):
        first = Character("Nyx", stress=70)
        second = Character("Patch", stress=68)
        dialogues = [
            {
                "pair": ["Nyx", "Patch"],
                "line": "Nyx stays with Patch.",
                "affinity_reason": "relationship",
            }
        ]

        lines = apply_recovery_dialogue_effects([first, second], dialogues)

        self.assertEqual(first.stress, 69)
        self.assertEqual(second.stress, 67)
        self.assertTrue(any("Recovery bond" in line for line in lines))


if __name__ == "__main__":
    unittest.main()
