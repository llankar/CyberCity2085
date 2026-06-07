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
    write_godot_combat_handoff,
)
from game.gamestate import GameState
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
        godot_executable = Path(r"E:\Godot\Godot_v4.6.3\Godot_v4.6.3-stable_win64.exe")
        if not godot_executable.exists():
            self.skipTest("Godot executable not available for headless load check")

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


if __name__ == "__main__":
    unittest.main()
