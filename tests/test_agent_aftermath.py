"""Agent mission aftermath rules."""

import os
import sys
import tempfile
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
        H=72,
        M=77,
        R=82,
        S=83,
        L=76,
        TAB=9,
        X=88,
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
        MOD_SHIFT=1,
        MOD_CTRL=2,
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

from game.agent_aftermath import apply_mission_aftermath
from game.ui.dashboard import build_agent_aftermath_lines
from game.character import Character
from game.consequences import Consequence
from game.gamestate import GameState
from game.mission_templates import MissionComplication, MissionTemplate
from game.savage_fate import tag_from_library
from game.unit import Unit
from game import views


def _mission(title="Low Risk Sweep", risk_level=1):
    return MissionTemplate(
        id="test",
        title=title,
        objective_text="Test objective",
        target_faction="Test Faction",
        district="Test District",
        district_pressure={},
        starting_enemy_count=1,
        risk_level=risk_level,
    )


def _complication():
    return MissionComplication(
        key="faction_retaliation",
        name="Faction Retaliation",
        trigger_text="The target faction marks the squad.",
        risk_threshold=1,
        tags=[tag_from_library("faction_retaliation")],
        consequence=Consequence(severity=3),
    )


class _FakeWindow:
    def __init__(self):
        self.shown_view = None

    def show_view(self, view):
        self.shown_view = view


class AgentAftermathTest(unittest.TestCase):
    def test_high_risk_mission_adds_more_stress_than_low_risk(self):
        low_risk_agent = Character("Low")
        high_risk_agent = Character("High")

        apply_mission_aftermath([low_risk_agent], _mission(risk_level=1), True)
        apply_mission_aftermath([high_risk_agent], _mission(risk_level=4), True)

        self.assertGreater(high_risk_agent.stress, low_risk_agent.stress)
        self.assertIn("Low Risk Sweep", high_risk_agent.history[0])

    def test_clean_victory_adds_loyalty_and_history(self):
        agent = Character("Clean")

        lines = apply_mission_aftermath(
            [agent], _mission("Clinic Rescue", risk_level=2), True
        )

        self.assertEqual(agent.loyalty, 1)
        self.assertEqual(agent.stress, 6)
        self.assertIn("Clinic Rescue", agent.history[0])
        self.assertIn("Aftermath: Clean", lines[0])

    def test_complication_adds_visible_stress_and_tag(self):
        agent = Character("Marked")
        complication = _complication()

        lines = apply_mission_aftermath(
            [agent], _mission("Relay Burn", risk_level=4), False, complication
        )

        self.assertGreaterEqual(agent.stress, 25)
        self.assertIn("faction_retaliation", agent.savage_tags)
        self.assertIn("Faction Retaliation", lines[0])

    def test_stress_is_clamped_to_readable_range(self):
        agent = Character("Frayed", stress=98)

        apply_mission_aftermath(
            [agent], _mission(risk_level=10), False, _complication()
        )

        self.assertEqual(agent.stress, 100)

    def test_end_battle_writes_aftermath_to_event_log(self):
        game_state = GameState(characters=[Character("Survivor")])
        mission = _mission("Event Log Test", risk_level=2)
        battle_view = views.BattleView(game_state)
        battle_view.window = _FakeWindow()
        battle_view.mission = mission
        battle_view.initial_enemy_count = 1
        battle_view.triggered_complication = None
        battle_view.player_units = [
            Unit(
                position=(0, 0),
                stats=game_state.characters[0].stats,
                character=game_state.characters[0],
                health=game_state.characters[0].stats.hp,
            )
        ]
        battle_view.defeated_player_units = []

        original_resolver = views.resolve_mission_outcome_system
        views.resolve_mission_outcome_system = lambda *args: None
        try:
            battle_view.end_battle(True)
        finally:
            views.resolve_mission_outcome_system = original_resolver

        self.assertTrue(
            any(
                "Aftermath: Survivor carries Event Log Test" in event
                for event in game_state.event_log
            )
        )
        self.assertEqual(
            game_state.latest_agent_aftermath,
            [
                "Aftermath: Survivor carries Event Log Test "
                "(victory, stress 6/100, loyalty +1)."
            ],
        )
        self.assertIn("Event Log Test", game_state.characters[0].history[0])

    def test_battle_view_movement_uses_tactical_grid_occupancy(self):
        game_state = GameState(characters=[Character("Runner")])
        battle_view = views.BattleView(game_state)
        battle_view.player_units = [Unit(position=(0, 0), character=game_state.characters[0])]
        battle_view.enemy_units = [Unit(position=(32, 0), unit_type="grunt")]
        battle_view.terrain_profile = object()

        battle_view.combat_state = views.CombatState(
            None, battle_view.player_units, battle_view.enemy_units
        )

        self.assertFalse(battle_view.can_move_to(32, 0, exclude=battle_view.player_units[0]))
        self.assertTrue(battle_view.can_move_to(999, 999, exclude=None))

    def test_dashboard_report_shows_latest_compact_aftermath_first(self):
        lines = [
            "Aftermath: One carries Old Job.",
            "Aftermath: Two carries New Job.",
            "Aftermath: Three carries Final Job.",
        ]

        self.assertEqual(
            build_agent_aftermath_lines(lines, limit=2),
            ["Three carries Final Job.", "Two carries New Job."],
        )

    def test_latest_agent_aftermath_persists_through_save_load(self):
        game_state = GameState()
        game_state.latest_agent_aftermath = [
            "Aftermath: Saved Agent carries Archive Raid."
        ]

        with tempfile.NamedTemporaryFile(delete=False) as save_file:
            save_path = save_file.name
        try:
            game_state.save(save_path)
            loaded_state = GameState.load(save_path)
        finally:
            os.unlink(save_path)

        self.assertEqual(
            loaded_state.latest_agent_aftermath,
            ["Aftermath: Saved Agent carries Archive Raid."],
        )


if __name__ == "__main__":
    unittest.main()
