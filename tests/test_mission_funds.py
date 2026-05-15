"""Mission cash reward and post-mission distribution rules."""

import unittest

from game.gamestate import GameState
from game.management.funds import (
    calculate_mission_fund_reward,
    default_mission_fund_distribution,
)
from game.mission_system import resolve_mission_outcome
from game.mission_templates import MissionTemplate


def _mission(fund_reward=80) -> MissionTemplate:
    return MissionTemplate(
        id="fund_test",
        title="Fund Test",
        objective_text="Recover a city contract cache.",
        target_faction="Ledger Saints",
        district="Chrome Warrens",
        district_pressure={},
        starting_enemy_count=1,
        risk_level=2,
        fund_reward=fund_reward,
    )


class MissionFundsTest(unittest.TestCase):
    def test_reward_calculation_requires_victory_and_positive_reward(self):
        mission = _mission(fund_reward=80)

        self.assertEqual(calculate_mission_fund_reward(mission, True), 80)
        self.assertEqual(calculate_mission_fund_reward(mission, False), 0)
        self.assertEqual(
            calculate_mission_fund_reward(_mission(fund_reward=-5), True), 0
        )

    def test_default_distribution_keeps_every_reward_dollar_allocated(self):
        distribution = default_mission_fund_distribution(80)

        self.assertEqual(sum(distribution.values()), 80)
        self.assertEqual(distribution["agent_pay_morale"], 20)
        self.assertEqual(distribution["research"], 20)
        self.assertEqual(distribution["equipment"], 16)
        self.assertEqual(distribution["robot_power_armor_maintenance"], 12)
        self.assertEqual(distribution["corporate_reserves"], 12)

    def test_successful_resolution_awards_and_distributes_through_ledger(self):
        game_state = GameState()
        starting_funds = game_state.available_funds

        resolve_mission_outcome(game_state, _mission(fund_reward=80), True)

        self.assertEqual(game_state.mission_fund_allocations["agent_pay_morale"], 20)
        self.assertEqual(game_state.mission_fund_allocations["research"], 20)
        self.assertEqual(game_state.mission_fund_allocations["equipment"], 16)
        self.assertEqual(
            game_state.mission_fund_allocations["robot_power_armor_maintenance"],
            12,
        )
        self.assertEqual(game_state.mission_fund_allocations["corporate_reserves"], 12)
        self.assertGreater(game_state.available_funds, starting_funds)
        self.assertTrue(
            any(
                transaction.source == "mission_reward"
                for transaction in game_state.funds.transaction_history
            )
        )
        self.assertTrue(
            any("Mission funds secured" in event for event in game_state.event_log)
        )

    def test_failed_resolution_does_not_pay_mission_reward(self):
        game_state = GameState()
        starting_income = game_state.funds.income

        resolve_mission_outcome(game_state, _mission(fund_reward=80), False)

        self.assertEqual(
            game_state.mission_fund_allocations,
            {
                "agent_pay_morale": 0,
                "research": 0,
                "equipment": 0,
                "robot_power_armor_maintenance": 0,
                "corporate_reserves": 0,
            },
        )
        self.assertEqual(
            game_state.funds.income,
            starting_income + game_state.compute_budget(),
        )


if __name__ == "__main__":
    unittest.main()
