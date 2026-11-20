"""Godot combat UI handoff tests."""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from game.character import Character
from game.combat.godot_bridge import (
    GODOT_COMBAT_PROJECT_DIR,
    build_godot_combat_command,
    build_godot_combat_payload,
    find_godot_executable,
    launch_godot_combat_ui,
    validate_godot_combat_payload,
    write_godot_combat_handoff,
)
from game.gamestate import GameState
from game.management.spec_ops_assets import ArmorRating, CombatRobot, WeaponHardpoint
from game.mission_templates import MissionTemplate
from game.ui.screens import settings_screen


def _mission() -> MissionTemplate:
    return MissionTemplate(
        id="godot_test",
        title="Neon Breach",
        objective_text="Extract the witness before Corp 37 locks the block.",
        target_faction="Corp 37",
        district="Chrome Warrens",
        district_pressure={},
        starting_enemy_count=2,
        risk_level=3,
        objective_type="extract",
    )


class GodotCombatBridgeTest(unittest.TestCase):
    def test_payload_transmits_reduced_motion_preference(self) -> None:
        game_state = GameState(
            characters=[Character("Vera")], selected_agent_names=["Vera"]
        )
        for enabled in (False, True):
            with self.subTest(enabled=enabled):
                settings = settings_screen.SettingsState(reduced_motion=enabled)
                with patch.object(settings_screen, "load_settings", return_value=settings):
                    payload = build_godot_combat_payload(game_state, _mission())
                self.assertEqual(payload["accessibility"], {"reduced_motion": enabled})

    def test_payload_satisfies_versioned_handoff_contract(self) -> None:
        game_state = GameState(
            characters=[Character("Vera", role="sniper")],
            selected_agent_names=["Vera"],
        )

        payload = build_godot_combat_payload(game_state, _mission())

        self.assertEqual(validate_godot_combat_payload(payload), [])
        self.assertEqual(payload["schema_version"], 1)
        self.assertTrue({"campaign", "mission", "map", "squad", "support_assets", "combat_ui"} <= payload.keys())

    def test_contract_reports_schema_and_tactical_action_regressions(self) -> None:
        game_state = GameState(
            characters=[Character("Vera")], selected_agent_names=["Vera"]
        )
        payload = build_godot_combat_payload(game_state, _mission())
        payload["schema_version"] = 99
        payload["combat_ui"]["primary_actions"] = ["move"]

        errors = validate_godot_combat_payload(payload)

        self.assertTrue(any("schema_version" in error for error in errors))
        self.assertTrue(any("overwatch" in error for error in errors))

    def test_payload_contains_mission_map_and_selected_squad(self) -> None:
        agent = Character("Vera", role="sniper")
        game_state = GameState(characters=[agent], selected_agent_names=["Vera"])

        payload = build_godot_combat_payload(game_state, _mission())

        self.assertEqual(payload["ui_engine"], "godot")
        self.assertEqual(payload["mission"]["title"], "Neon Breach")
        self.assertEqual(payload["mission"]["objective_type"], "extract")
        self.assertEqual(payload["squad"][0]["name"], "Vera")
        self.assertEqual(payload["squad"][0]["role"], "sniper")
        self.assertIn("path", payload["map"])
        self.assertEqual(payload["combat_ui"]["movement_mode"], "tactical_grid")

    def test_payload_contains_selected_support_asset_for_godot_units(self) -> None:
        agent = Character("Vera", role="sniper")
        robot = CombatRobot(
            id="drone",
            name="Drone",
            armor=ArmorRating(plating=3, sealed_systems=1),
            hardpoints=[
                WeaponHardpoint(
                    "Rail Stubber",
                    damage_bonus=2,
                    range_cells=5,
                    action_name="Rail Burst",
                )
            ],
            missile_capacity=1,
        )
        game_state = GameState(
            characters=[agent],
            selected_agent_names=["Vera"],
            spec_ops_assets=[robot],
            selected_asset_ids=["drone"],
        )

        payload = build_godot_combat_payload(game_state, _mission())

        self.assertEqual(payload["support_assets"][0]["id"], "drone")
        self.assertEqual(payload["support_assets"][0]["asset_type"], "combat_robot")
        self.assertEqual(payload["support_assets"][0]["role"], "robot")
        self.assertGreater(payload["support_assets"][0]["hp"], 0)
        self.assertGreaterEqual(
            payload["support_assets"][0]["max_hp"],
            payload["support_assets"][0]["hp"],
        )
        self.assertIn("Rail Burst", payload["support_assets"][0]["actions"])
        self.assertIn("Missile Salvo", payload["support_assets"][0]["actions"])
        self.assertEqual(payload["support_assets"][0]["action_points"], 2)
        self.assertGreater(payload["support_assets"][0]["size_scale"], 1.0)

    def test_write_handoff_creates_godot_readable_json(self) -> None:
        agent = Character("Mako", role="samurai")
        game_state = GameState(characters=[agent], selected_agent_names=["Mako"])
        with tempfile.TemporaryDirectory() as tmp:
            handoff_path = Path(tmp) / "mission_handoff.json"

            written = write_godot_combat_handoff(
                game_state, _mission(), handoff_path=handoff_path
            )

            self.assertEqual(written, handoff_path)
            data = json.loads(handoff_path.read_text(encoding="utf-8"))
            self.assertEqual(data["source"], "CyberCity2085")
            self.assertEqual(data["squad"][0]["name"], "Mako")

    def test_command_points_godot_to_project_and_handoff(self) -> None:
        handoff = Path("runtime/godot_combat/mission_handoff.json").resolve()
        command = build_godot_combat_command(
            "runtime/godot_combat/mission_handoff.json",
            executable="godot4",
        )

        self.assertEqual(command[0], "godot4")
        self.assertIn(str(GODOT_COMBAT_PROJECT_DIR.resolve()), command)
        self.assertIn("--handoff", command)
        self.assertIn(str(handoff), command)

    def test_find_godot_prefers_saved_settings_path(self) -> None:
        previous_path = settings_screen._SETTINGS_PATH
        try:
            with tempfile.TemporaryDirectory() as tmp:
                settings_screen._SETTINGS_PATH = str(Path(tmp) / "settings.json")
                settings_screen.save_settings(
                    settings_screen.SettingsState(godot_bin_path=r"C:\Games\Godot\Godot.exe")
                )
                with patch.dict(os.environ, {"CYBERCITY_GODOT_BIN": r"C:\Ignored\godot.exe"}, clear=False):
                    self.assertEqual(
                        find_godot_executable(),
                        os.path.expandvars(os.path.expanduser(r"C:\Games\Godot\Godot.exe")),
                    )
        finally:
            settings_screen._SETTINGS_PATH = previous_path

    def test_launch_without_executable_still_writes_handoff(self) -> None:
        game_state = GameState(
            characters=[Character("Iris")], selected_agent_names=["Iris"]
        )
        with tempfile.TemporaryDirectory() as tmp:
            handoff_path = Path(tmp) / "mission_handoff.json"

            result = launch_godot_combat_ui(
                game_state,
                _mission(),
                handoff_path=handoff_path,
                executable="",
            )

            self.assertFalse(result.launched)
            self.assertFalse(result.ready_for_godot)
            self.assertTrue(handoff_path.exists())
            self.assertIn("Godot handoff created", result.message)

    def test_headless_godot_loads_the_combat_ui_script(self) -> None:
        discovered = find_godot_executable()
        if not discovered or not Path(discovered).is_file():
            self.skipTest("Godot executable not available for headless load check")
        godot_executable = Path(discovered)

        game_state = GameState(
            characters=[Character("Vera", role="sniper")],
            selected_agent_names=["Vera"],
        )
        with tempfile.TemporaryDirectory() as tmp:
            handoff_path = Path(tmp) / "mission_handoff.json"
            write_godot_combat_handoff(game_state, _mission(), handoff_path=handoff_path)

            result = subprocess.run(
                [
                    str(godot_executable),
                    "--headless",
                    "--quit-after",
                    "1",
                    "--path",
                    str(GODOT_COMBAT_PROJECT_DIR),
                    "--",
                    "--handoff",
                    str(handoff_path),
                ],
                capture_output=True,
                text=True,
                timeout=60,
                check=False,
            )

            output = f"{result.stdout}\n{result.stderr}"
            self.assertEqual(result.returncode, 0, output)
            self.assertNotIn("Parse Error", output)
            self.assertNotIn("Failed to load script", output)
            self.assertIn("TACTICAL COMBAT UI READY", output)
            self.assertIn("grid / timeline / action bar / unit panel / log", output)

    def test_portable_install_is_discovered_without_settings_or_path(self) -> None:
        from game.combat.godot_bridge import _find_portable_godot

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            version = root / "Godot_v4.6.3"
            version.mkdir()
            executable = version / "Godot_v4.6.3-stable_win64.exe"
            executable.touch()
            (version / "Godot_v4.6.3-stable_win64_console.exe").touch()
            with patch("game.combat.godot_bridge._godot_installation_roots", return_value=[root]):
                self.assertEqual(_find_portable_godot(), str(executable.resolve()))

    def test_launch_os_error_is_reported_as_not_launched(self) -> None:
        state = GameState(characters=[Character("Iris")], selected_agent_names=["Iris"])
        with tempfile.TemporaryDirectory() as tmp:
            with patch("game.combat.godot_bridge.subprocess.Popen", side_effect=OSError("not executable")):
                result = launch_godot_combat_ui(
                    state, _mission(), handoff_path=Path(tmp) / "handoff.json", executable="invalid.exe"
                )
        self.assertTrue(result.ready_for_godot)
        self.assertFalse(result.launched)
        self.assertIn("not executable", result.message)


if __name__ == "__main__":
    unittest.main()
