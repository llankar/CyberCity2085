"""Tests for temporary narrative scars derived from severe injuries."""

from __future__ import annotations

import unittest

from game.battle_outcomes import resolve_defeated_agent_outcome
from game.character import Character
from game.gamestate import GameState
from game.narrative.temporary_scars import apply_temporary_scar_from_injury


class TemporaryScarsTest(unittest.TestCase):
    def test_add_on_severe_injury(self):
        character = Character("Rook")

        scar = apply_temporary_scar_from_injury(character, "Critical battle trauma")

        self.assertIsNotNone(scar)
        self.assertEqual(len(character.temporary_scars), 1)
        self.assertEqual(character.temporary_scars[0]["key"], "critical_battle_trauma")

    def test_decrement_when_days_advance(self):
        character = Character("Nyx")
        game_state = GameState(characters=[character])
        apply_temporary_scar_from_injury(character, "Critical battle trauma")

        game_state.advance_one_day("test")

        self.assertEqual(character.temporary_scars[0]["days_remaining"], 3)

    def test_remove_when_expired(self):
        character = Character("Vale")
        game_state = GameState(characters=[character])
        apply_temporary_scar_from_injury(character, "Critical battle trauma")

        game_state.advance_days(4, "test")

        self.assertEqual(character.temporary_scars, [])
        self.assertTrue(
            any("leaves behind scar" in entry for entry in game_state.event_log)
        )

    def test_critical_outcome_applies_scar(self):
        character = Character("Mara")
        events: list[str] = []

        import game.battle_outcomes as outcomes

        original_choice = outcomes.random.choice
        outcomes.random.choice = lambda _: "critically injured"
        try:
            resolve_defeated_agent_outcome(
                character,
                remove_character=lambda _: None,
                record_event=events.append,
            )
        finally:
            outcomes.random.choice = original_choice

        self.assertEqual(len(character.temporary_scars), 1)
        self.assertTrue(any("temporary scar" in event for event in events))


if __name__ == "__main__":
    unittest.main()
