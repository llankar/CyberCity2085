"""Corporate funds ledger and GameState integration tests."""

import tempfile
import unittest
from pathlib import Path

from game.gamestate import GameState
from game.management.funds import CorporateFunds


class FundsManagementTest(unittest.TestCase):
    def test_income_updates_available_funds_and_history(self):
        ledger = CorporateFunds()

        self.assertTrue(ledger.add_funds(35, "sponsor", "Board advance."))

        self.assertEqual(ledger.available_funds, 35)
        self.assertEqual(ledger.income, 35)
        self.assertEqual(len(ledger.transaction_history), 1)
        self.assertEqual(ledger.transaction_history[0].source, "sponsor")
        self.assertEqual(ledger.transaction_history[0].balance_after, 35)

    def test_spending_updates_expenses_and_balance(self):
        ledger = CorporateFunds(current_funds=50)

        self.assertTrue(ledger.spend_funds(15, "recruitment", "Found a sniper."))

        self.assertEqual(ledger.available_funds, 35)
        self.assertEqual(ledger.expenses, 15)
        self.assertEqual(ledger.transaction_history[0].kind, "expense")
        self.assertEqual(ledger.transaction_history[0].source, "recruitment")

    def test_insufficient_funds_fail_without_mutating_history(self):
        ledger = CorporateFunds(current_funds=10)

        self.assertFalse(ledger.spend_funds(25, "security", "Too expensive."))

        self.assertEqual(ledger.available_funds, 10)
        self.assertEqual(ledger.expenses, 0)
        self.assertEqual(ledger.transaction_history, [])
        self.assertFalse(ledger.can_afford(25))

    def test_game_state_owns_funds_helpers_and_save_history(self):
        game_state = GameState()
        opening_funds = game_state.available_funds

        self.assertTrue(game_state.add_funds(20, "mission_bonus", "Clean extraction."))
        self.assertTrue(game_state.spend_funds(5, "black_ops", "Quiet retainer."))
        self.assertEqual(game_state.available_funds, opening_funds + 15)
        self.assertEqual(game_state.budget_pool, game_state.available_funds)
        self.assertEqual(game_state.funds.transaction_history[-1].source, "black_ops")

        with tempfile.TemporaryDirectory() as temp_dir:
            save_path = Path(temp_dir) / "savegame.json"
            game_state.save(str(save_path))

            loaded = GameState.load(str(save_path))

        self.assertEqual(loaded.available_funds, game_state.available_funds)
        self.assertEqual(len(loaded.funds.transaction_history), 3)
        self.assertEqual(loaded.funds.transaction_history[-1].note, "Quiet retainer.")


if __name__ == "__main__":
    unittest.main()
