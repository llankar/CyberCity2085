"""Weekly recurring corporate funding tied to the strategic calendar."""

import unittest

from game.gamestate import GameState
from game.management.corporation import CorporationFinance
from game.ui.command_deck import build_corporate_finance_lines


class WeeklyCorporateFundingTest(unittest.TestCase):
    def test_one_week_advance_adds_weekly_corporate_funding_once(self):
        game_state = GameState(
            corporation_finance=CorporationFinance(
                weekly_stipend=100,
                city_support_modifier=0.20,
                political_pressure_modifier=-0.10,
                debt_upkeep=15,
            )
        )
        starting_funds = game_state.available_funds

        game_state.advance_days(6, "test")

        self.assertEqual(game_state.calendar.current_day, 7)
        self.assertEqual(
            [
                transaction
                for transaction in game_state.funds.transaction_history
                if transaction.source == "weekly_corporate_funding"
            ],
            [],
        )

        game_state.advance_one_day("test")

        weekly_transactions = [
            transaction
            for transaction in game_state.funds.transaction_history
            if transaction.source == "weekly_corporate_funding"
        ]
        self.assertEqual(game_state.calendar.current_day, 8)
        self.assertEqual(game_state.calendar.current_week, 2)
        self.assertEqual(len(weekly_transactions), 1)
        self.assertEqual(weekly_transactions[0].amount, 95)
        self.assertEqual(
            game_state.available_funds,
            starting_funds + game_state.compute_budget() * 7 + 95,
        )
        self.assertTrue(
            any("corporate funding +95" in event for event in game_state.event_log)
        )

    def test_multi_week_advance_collects_each_crossed_week(self):
        game_state = GameState(
            corporation_finance=CorporationFinance(
                weekly_stipend=80,
                city_support_modifier=0.25,
                political_pressure_modifier=0.0,
                debt_upkeep=10,
            )
        )

        game_state.advance_days(14, "test")

        weekly_transactions = [
            transaction
            for transaction in game_state.funds.transaction_history
            if transaction.source == "weekly_corporate_funding"
        ]
        self.assertEqual(game_state.calendar.current_day, 15)
        self.assertEqual(game_state.calendar.current_week, 3)
        self.assertEqual(
            [transaction.amount for transaction in weekly_transactions], [90, 90]
        )
        self.assertIn("Week 2", weekly_transactions[0].note)
        self.assertIn("Week 3", weekly_transactions[1].note)

    def test_corporate_management_finance_copy_exposes_next_date_and_projection(self):
        game_state = GameState(
            corporation_finance=CorporationFinance(weekly_stipend=50, debt_upkeep=5)
        )

        lines = build_corporate_finance_lines(
            game_state.next_weekly_income_date,
            game_state.projected_weekly_income,
        )

        self.assertEqual(game_state.next_weekly_income_date, "2085.M01.D08")
        self.assertIn("Next weekly income 2085.M01.D08", lines)
        self.assertIn("Projected income +47 funds", lines)


if __name__ == "__main__":
    unittest.main()
