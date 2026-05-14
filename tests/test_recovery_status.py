"""Agent recovery timers and deployment eligibility."""

import unittest

from game import battle_outcomes
from game.character import Character, is_deployable
from game.combat_system import create_player_units
from game.gamestate import GameState


class RecoveryStatusTest(unittest.TestCase):
    def test_character_recovery_serializes_and_blocks_deployment(self):
        agent = Character("Archive", recovery_turns=2)

        restored = Character.from_dict(agent.to_dict())

        self.assertEqual(restored.recovery_turns, 2)
        self.assertFalse(is_deployable(restored))

    def test_create_player_units_skips_unavailable_agents(self):
        ready = Character("Ready")
        recovering = Character("Recovering", recovery_turns=1)

        units = create_player_units([ready, recovering])

        self.assertEqual([unit.character for unit in units], [ready])

    def test_advance_turn_reduces_recovery_and_restores_deployment(self):
        agent = Character("Stitch", recovery_turns=1)
        game_state = GameState(characters=[agent])

        game_state.advance_turn()

        self.assertEqual(agent.recovery_turns, 0)
        self.assertTrue(is_deployable(agent))
        self.assertTrue(
            any(
                "Stitch is deployable after recovery" in event
                for event in game_state.event_log
            )
        )

    def test_critical_injury_applies_short_recovery(self):
        agent = Character("Wound")
        events = []
        original_choice = battle_outcomes.random.choice
        battle_outcomes.random.choice = lambda outcomes: "critically injured"
        try:
            outcome = battle_outcomes.resolve_defeated_agent_outcome(
                agent,
                remove_character=lambda character: None,
                record_event=events.append,
            )
        finally:
            battle_outcomes.random.choice = original_choice

        self.assertEqual(outcome, "critically injured")
        self.assertEqual(
            agent.recovery_turns, battle_outcomes.CRITICAL_INJURY_RECOVERY_TURNS
        )
        self.assertFalse(is_deployable(agent))
        self.assertIn("critical injuries", events[0])

    def test_captured_applies_larger_recovery_than_critical_injury(self):
        agent = Character("Caught")
        original_choice = battle_outcomes.random.choice
        battle_outcomes.random.choice = lambda outcomes: "captured"
        try:
            battle_outcomes.resolve_defeated_agent_outcome(
                agent,
                remove_character=lambda character: None,
                record_event=lambda event: None,
            )
        finally:
            battle_outcomes.random.choice = original_choice

        self.assertEqual(agent.recovery_turns, battle_outcomes.CAPTURED_RECOVERY_TURNS)
        self.assertGreater(
            battle_outcomes.CAPTURED_RECOVERY_TURNS,
            battle_outcomes.CRITICAL_INJURY_RECOVERY_TURNS,
        )
        self.assertFalse(is_deployable(agent))

    def test_traumatized_extracted_agents_remain_deployable(self):
        agent = Character("Shaken")
        original_choice = battle_outcomes.random.choice
        battle_outcomes.random.choice = lambda outcomes: "traumatized but extracted"
        try:
            battle_outcomes.resolve_defeated_agent_outcome(
                agent,
                remove_character=lambda character: None,
                record_event=lambda event: None,
            )
        finally:
            battle_outcomes.random.choice = original_choice

        self.assertEqual(agent.recovery_turns, 0)
        self.assertTrue(is_deployable(agent))


if __name__ == "__main__":
    unittest.main()
