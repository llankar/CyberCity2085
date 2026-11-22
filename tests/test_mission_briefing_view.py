"""Regression checks for mission briefing launch behavior."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import unittest

from game.character import Character
from game.gamestate import GameState
from game.management.spec_ops_assets import ArmorRating, CombatRobot, WeaponHardpoint
from game.mission_templates import MissionComplication, MissionTemplate
from game.ui.screens.mission_briefing_view import (
    MissionBriefingView,
    build_mission_briefing_facts,
    mission_tag_label,
    pressure_label,
)


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
        fund_reward=90,
        objective_type="sabotage",
        possible_complications=[
            MissionComplication(
                key="relay_trace",
                name="Relay Trace",
                trigger_text="A countertrace exposes the squad route.",
                risk_threshold=2,
            )
        ],
        emotional_impact_hint={
            "level": "high",
            "text": "A failed strike leaves the district exposed to reprisals.",
        },
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
    def test_failed_process_start_does_not_open_an_endless_loading_screen(self, launch_mock):
        state = GameState()
        state.combat_mission_ui_engine = "godot"
        view = MissionBriefingView.__new__(MissionBriefingView)
        view.game_state = state
        view.mission = _mission()
        view.window = _FakeWindow()
        launch_mock.return_value = SimpleNamespace(
            command=["invalid-godot.exe"], ready_for_godot=True,
            launched=False, message="Godot launch failed: not executable",
        )

        view._launch_battle()

        self.assertTrue(view.window.shown_view._launch_failed)
        self.assertIn("Tactical deployment unavailable.", state.event_log)
        self.assertNotIn("Godot launch failed: not executable", state.event_log)

    def test_mission_tags_hide_internal_payloads_from_the_briefing(self) -> None:
        rich_tag = SimpleNamespace(name="neon_blackout", description="Internal detail", intensity=2)

        self.assertEqual(mission_tag_label(rich_tag), "Neon Blackout")
        self.assertEqual(mission_tag_label({"name": "media_heat", "intensity": 2}), "Media Heat")
        self.assertEqual(mission_tag_label("civilian_rescue"), "Civilian Rescue")

    def test_pressure_effects_are_presented_as_readable_consequences(self) -> None:
        self.assertEqual(
            pressure_label({"unrest": 3, "media_heat": 2}),
            "UNREST +3 | MEDIA HEAT +2",
        )
        self.assertEqual(pressure_label({}), "STABLE")

    def test_briefing_facts_cover_wave6_required_fields(self) -> None:
        robot = CombatRobot(
            id="drone",
            name="Kestrel Drone",
            armor=ArmorRating(plating=2),
            hardpoints=[WeaponHardpoint("Shock Carbine", range_cells=5)],
            deploy_cost=15,
        )
        game_state = GameState(
            characters=[
                Character("Vera", role="sniper", stress=20),
                Character("Mako", role="medic", stress=50),
            ],
            selected_agent_names=["Vera", "Mako"],
            spec_ops_assets=[robot],
            selected_asset_ids=["drone"],
        )
        game_state.characters[0].temporary_scars = [
            {
                "title": "Nights of Sirens",
                "days_remaining": 3,
                "tone": "vigilant",
                "tags": ["injury"],
            }
        ]
        game_state.characters[0].history = [
            "Jackal Relay: stayed in the fight after taking 18 damage."
        ]
        game_state.characters[1].history = ["Joined the squad on day 2."]

        facts = build_mission_briefing_facts(game_state, _mission())

        self.assertEqual(facts["title"], "Sabotage: Jackal Relay")
        self.assertEqual(facts["objective"], "Disrupt the relay before the district locks down.")
        self.assertEqual(facts["target_faction"], "Jackal Cartel")
        self.assertEqual(facts["district"], "Chrome Warrens")
        self.assertEqual(facts["risk_level"], 3)
        self.assertIn("30-60 projected stress", facts["expected_stress_band"])
        self.assertIn("district exposed", facts["emotional_impact"])
        self.assertEqual(facts["complications"], ["A countertrace exposes the squad route."])
        self.assertIn("maps", facts["map_thumbnail"])
        self.assertEqual(facts["squad_roster"], ["Vera", "Mako"])
        self.assertEqual(
            facts["recent_tactical_memories"],
            ["Vera: Jackal Relay: stayed in the fight after taking 18 damage."],
        )
        self.assertTrue(
            any("Vera: Nights of Sirens" in line for line in facts["temporary_scar_summary"])
        )
        self.assertEqual(facts["selected_support_assets"], ["Kestrel Drone"])
        self.assertEqual(facts["reward_preview"], "Funds +90; assets -15; net 75")
        self.assertEqual(facts["actions"], ["DEPLOY", "ABORT"])

    @patch("game.views.BattleView", new=_FakeBattleView)
    @patch("game.combat.godot_bridge.launch_godot_combat_ui")
    def test_missing_godot_does_not_offer_legacy_arcade_shortcut(self, launch_mock) -> None:
        game_state = GameState()
        game_state.combat_mission_ui_engine = "godot"
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

        bridge = view.window.shown_view
        self.assertTrue(bridge._launch_failed)
        self.assertIs(bridge.game_state, game_state)
        self.assertIs(bridge.mission, mission)
        from game.ui.screens.godot_combat_handoff_view import arcade
        with patch.object(arcade, "key", SimpleNamespace(R=82,G=71,S=83,F=70,ESCAPE=27)):
            bridge.on_key_press(70, 0)
        self.assertIs(view.window.shown_view, bridge)
        self.assertTrue(bridge._launch_failed)


if __name__ == "__main__":
    unittest.main()
