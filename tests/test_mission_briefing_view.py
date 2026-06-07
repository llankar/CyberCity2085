"""Regression checks for mission briefing launch behavior."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import unittest

from game.gamestate import GameState
from game.mission_templates import MissionTemplate
from game.ui.screens.mission_briefing_view import MissionBriefingView


def _mission() -> MissionTemplate:
    return MissionTemplate(
        id="briefing_test",
        title="Sabotage: Jackal Relay",
        objective_text="Disrupt the relay before the district locks down.",
        target_faction="Jackal Cartel",
        district="Chrome Warrens",
        district_pressure={},
        starting_enemy_count=3,
        risk_level=3,
        objective_type="sabotage",
    )


class _FakeWindow:
    def __init__(self) -> None:
        self.shown_view = None

    def show_view(self, view) -> None:
        self.shown_view = view


class _FakeBattleView:
    def __init__(self, game_state) -> None:
        self.game_state = game_state
        self.mission = None

    def setup(self, mission) -> None:
        self.mission = mission


class MissionBriefingLaunchTest(unittest.TestCase):
    @patch("game.views.BattleView", new=_FakeBattleView)
    @patch("game.combat.godot_bridge.launch_godot_combat_ui")
    def test_launch_falls_back_to_arcade_when_godot_is_unavailable(self, launch_mock) -> None:
        game_state = GameState()
        mission = _mission()
        view = MissionBriefingView.__new__(MissionBriefingView)
        view.game_state = game_state
        view.mission = mission
        view.window = _FakeWindow()
        launch_mock.return_value = SimpleNamespace(
            handoff_path=Path("runtime/godot_combat/mission_handoff.json"),
            command=[],
            launched=False,
            ready_for_godot=False,
            message="Godot handoff created; install Godot or set CYBERCITY_GODOT_BIN to launch the combat UI.",
        )

        view._launch_battle()

        self.assertIsInstance(view.window.shown_view, _FakeBattleView)
        self.assertIs(view.window.shown_view.game_state, game_state)
        self.assertIs(view.window.shown_view.mission, mission)
        self.assertIn("Godot unavailable; launching local Arcade battle fallback.", game_state.event_log[-1])


if __name__ == "__main__":
    unittest.main()
