"""RPG view mission launch guards."""

import sys
import types
import unittest


class _FakeView:
    def __init__(self, *args, **kwargs):
        self.window = None

    def clear(self):
        pass


fake_arcade = types.SimpleNamespace(
    View=_FakeView,
    key=types.SimpleNamespace(
        B=66,
        N=78,
        KEY_1=49,
        KEY_2=50,
        KEY_3=51,
        KEY_4=52,
        KEY_5=53,
        KEY_7=55,
        KEY_8=56,
        KEY_9=57,
        C=67,
        R=82,
        S=83,
        L=76,
        UP=1000,
        DOWN=1001,
        LEFT=1002,
        RIGHT=1003,
        A=65,
        D=68,
        E=69,
        F=70,
        P=80,
        V=86,
        SPACE=32,
        ENTER=13,
        RETURN=13,
        ESCAPE=27,
    ),
    color=types.SimpleNamespace(
        WHITE=(255, 255, 255),
        AQUA=(0, 255, 255),
        LIGHT_GRAY=(200, 200, 200),
        YELLOW=(255, 255, 0),
        DARK_RED=(100, 0, 0),
        GREEN=(0, 255, 0),
        RED=(255, 0, 0),
    ),
    draw_text=lambda *args, **kwargs: None,
    draw_lrbt_rectangle_filled=lambda *args, **kwargs: None,
    draw_rect_outline=lambda *args, **kwargs: None,
    draw_line=lambda *args, **kwargs: None,
    draw_texture_rect=lambda *args, **kwargs: None,
    Camera2D=lambda *args, **kwargs: None,
    SpriteList=list,
    Sprite=lambda *args, **kwargs: types.SimpleNamespace(kill=lambda: None),
    LBWH=lambda *args, **kwargs: None,
    load_texture=lambda *args, **kwargs: None,
)
sys.modules.setdefault("arcade", fake_arcade)

from game.character import Character
from game.gamestate import GameState
from game.mission_templates import MissionTemplate
from game.recruitment import recruit_agent
from game import views


class _FakeWindow:
    def __init__(self):
        self.shown_view = None
        self.height = 720
        self.width = 1280

    def show_view(self, view):
        self.shown_view = view


def _mission(mission_id="stress_gate", title="Relay Burn", risk_level=3):
    return MissionTemplate(
        id=mission_id,
        title=title,
        objective_text="Burn the relay before the city notices.",
        target_faction="Test Faction",
        district="Test District",
        district_pressure={},
        starting_enemy_count=1,
        risk_level=risk_level,
    )


class _FakeBattleView:
    def __init__(self, game_state):
        self.game_state = game_state
        self.mission = None
        self.setup_called = False

    def setup(self, mission):
        self.mission = mission
        self.setup_called = True


class RPGViewMissionLaunchTest(unittest.TestCase):
    def test_launch_without_agents_sets_message_and_keeps_rpg_view(self):
        game_state = GameState()
        view = views.RPGView(game_state)
        view.window = _FakeWindow()
        view.setup()

        view.on_key_press(views.arcade.key.B, None)

        self.assertIsNone(view.window.shown_view)
        self.assertIsNone(game_state.active_mission)
        self.assertEqual(
            view.message,
            "Recruit at least one deployable agent before launching an operation.",
        )

    def test_launch_with_only_recovering_agent_sets_message(self):
        game_state = GameState(characters=[Character("Wounded", recovery_turns=2)])
        view = views.RPGView(game_state)
        view.window = _FakeWindow()
        view.setup()

        view.on_key_press(views.arcade.key.B, None)

        self.assertIsNone(view.window.shown_view)
        self.assertIsNone(game_state.active_mission)
        self.assertEqual(
            view.message,
            "Recruit at least one deployable agent before launching an operation.",
        )

    def test_rpg_view_shows_recovery_timer_for_unavailable_agent(self):
        drawn_text = []
        original_draw_text = views.arcade.draw_text
        views.arcade.draw_text = lambda text, *args, **kwargs: drawn_text.append(text)
        game_state = GameState(characters=[Character("Wounded", recovery_turns=3)])
        view = views.RPGView(game_state)
        view.window = _FakeWindow()
        view.setup()
        try:
            view.on_draw()
        finally:
            views.arcade.draw_text = original_draw_text

        self.assertTrue(
            any(
                "Wounded" in text and "Recovery: 3 turns" in text for text in drawn_text
            )
        )

    def test_stable_agent_launches_without_breakdown_confirmation(self):
        game_state = GameState(
            characters=[Character("Calm", stress=40)],
            mission_templates=[_mission()],
        )
        view = views.RPGView(game_state)
        view.window = _FakeWindow()
        view.setup()
        original_battle_view = views.BattleView
        views.BattleView = _FakeBattleView
        try:
            view.on_key_press(views.arcade.key.B, None)
        finally:
            views.BattleView = original_battle_view

        self.assertIsInstance(view.window.shown_view, _FakeBattleView)
        self.assertFalse(view.pending_breakdown_confirmation)
        self.assertFalse(
            any("Command forced" in event for event in game_state.event_log)
        )

    def test_breaking_risk_blocks_first_launch_attempt_with_warning(self):
        game_state = GameState(
            characters=[Character("Ghost", stress=80)],
            mission_templates=[_mission()],
        )
        view = views.RPGView(game_state)
        view.window = _FakeWindow()
        view.setup()

        view.on_key_press(views.arcade.key.B, None)

        self.assertIsNone(view.window.shown_view)
        self.assertIsNone(game_state.active_mission)
        self.assertTrue(view.pending_breakdown_confirmation)
        self.assertEqual(view.pending_breakdown_mission_id, "stress_gate")
        self.assertEqual(
            view.message,
            "Ghost is at breakdown risk. Press B again to force deployment.",
        )

    def test_second_breaking_risk_launch_attempt_proceeds_and_logs_event(self):
        game_state = GameState(
            characters=[Character("Ghost", stress=80)],
            mission_templates=[_mission()],
        )
        view = views.RPGView(game_state)
        view.window = _FakeWindow()
        view.setup()
        original_battle_view = views.BattleView
        views.BattleView = _FakeBattleView
        try:
            view.on_key_press(views.arcade.key.B, None)
            view.on_key_press(views.arcade.key.B, None)
        finally:
            views.BattleView = original_battle_view

        self.assertIsInstance(view.window.shown_view, _FakeBattleView)
        self.assertIs(view.window.shown_view.mission, game_state.active_mission)
        self.assertFalse(view.pending_breakdown_confirmation)
        self.assertTrue(
            any(
                "Command forced Ghost into Relay Burn despite breakdown risk." in event
                for event in game_state.event_log
            )
        )

    def test_breaking_confirmation_only_applies_to_same_selected_mission(self):
        game_state = GameState(
            characters=[Character("Ghost", stress=80)],
            mission_templates=[
                _mission("relay_burn", "Relay Burn"),
                _mission("black_ice", "Black Ice Sweep"),
            ],
        )
        view = views.RPGView(game_state)
        view.window = _FakeWindow()
        view.setup()

        view.on_key_press(views.arcade.key.B, None)
        view.on_key_press(views.arcade.key.KEY_2, None)
        view.on_key_press(views.arcade.key.B, None)

        self.assertIsNone(view.window.shown_view)
        self.assertIsNone(game_state.active_mission)
        self.assertTrue(view.pending_breakdown_confirmation)
        self.assertEqual(view.pending_breakdown_mission_id, "black_ice")

    def test_recruit_then_launches_selected_mission(self):
        game_state = GameState()
        recruit_agent(game_state.characters, "samurai")
        view = views.RPGView(game_state)
        view.window = _FakeWindow()
        view.setup()
        original_battle_view = views.BattleView
        views.BattleView = _FakeBattleView
        try:
            view.on_key_press(views.arcade.key.B, None)
        finally:
            views.BattleView = original_battle_view

        self.assertIsInstance(view.window.shown_view, _FakeBattleView)
        self.assertTrue(view.window.shown_view.setup_called)
        self.assertIs(view.window.shown_view.mission, game_state.active_mission)


if __name__ == "__main__":
    unittest.main()
