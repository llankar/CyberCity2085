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

from game.gamestate import GameState
from game.recruitment import recruit_agent
from game import views


class _FakeWindow:
    def __init__(self):
        self.shown_view = None
        self.height = 720
        self.width = 1280

    def show_view(self, view):
        self.shown_view = view


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
            "Recruit at least one agent before launching an operation.",
        )

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
