"""Main-menu navigation and save safety; real visuals run in an isolated process."""

from pathlib import Path
import json
import os
import subprocess
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

fake_arcade = types.SimpleNamespace(
    View=type("View", (), {"__init__": lambda self, *a, **kw: None}),
    MOUSE_BUTTON_LEFT=1,
    key=types.SimpleNamespace(
        RETURN=13, ENTER=13, SPACE=32, ESCAPE=27, UP=38, W=87, DOWN=40, S=83, M=77
    ),
)
sys.modules["arcade"] = fake_arcade
from game.ui.screens.title_screen import TitleView
from game.ui.layouts.title_menu import title_layout
from game.ui.layouts.world_map_beacons import Rect


class TitleScreenUITest(unittest.TestCase):
    def test_supported_resolutions_keep_all_controls_and_logo_disjoint(self):
        for size in [(1280, 720), (1920, 1080), (2560, 1440)]:
            layout = title_layout(*size)
            bounds = Rect(0, 0, *size)
            regions = [
                layout.logo,
                layout.subtitle,
                *layout.buttons,
                layout.footer,
                layout.notice,
            ]
            self.assertTrue(
                all(r.inside(bounds) and r.width > 0 and r.height > 0 for r in regions)
            )
            for i, r in enumerate(regions):
                self.assertFalse(any(r.intersects(other) for other in regions[i + 1 :]))
            self.assertGreaterEqual(layout.buttons[0].width, 320)
            self.assertGreaterEqual(layout.buttons[0].height, 50)

    def test_keyboard_skips_disabled_continue_and_wraps(self):
        view = TitleView()
        view.on_key_press(fake_arcade.key.DOWN, 0)
        self.assertEqual(view._hover_index, 2)
        view.on_key_press(fake_arcade.key.UP, 0)
        self.assertEqual(view._hover_index, 0)
        view.on_key_press(fake_arcade.key.UP, 0)
        self.assertEqual(view._hover_index, 3)
        view._continue_available = True
        view._hover_index = 0
        view.on_key_press(fake_arcade.key.DOWN, 0)
        self.assertEqual(view._hover_index, 1)

    def test_missing_or_corrupt_save_never_creates_new_campaign(self):
        view = TitleView()
        with patch.object(view, "_go_management") as management:
            view._activate("continue")
            management.assert_not_called()
            view._continue_available = True
            view._continue_path = Path("invalid.json")
            with patch(
                "game.persistence.SaveSystem.load_game",
                side_effect=ValueError("bad save"),
            ):
                view._activate("continue")
                management.assert_not_called()
        self.assertFalse(view._continue_available)
        self.assertIn("SAVE UNAVAILABLE", view._message)

    def test_continue_targets_the_most_recent_real_slot(self):
        view = TitleView()
        with tempfile.TemporaryDirectory() as folder, patch(
            "game.persistence.SaveSystem.slot_path",
            side_effect=lambda i: Path(folder) / f"slot_{i}.json",
        ), patch("game.combat.checkpoints.latest_combat_checkpoint", return_value=None):
            p = Path(folder)
            (p / "slot_1.json").write_text("{}")
            (p / "slot_4.json").write_text("{}")
            os.utime(p / "slot_1.json", (1700000000, 1700000000))
            os.utime(p / "slot_4.json", (1700000010, 1700000010))
            view._refresh_continue()
            self.assertEqual(view._continue_path, p / "slot_4.json")
            marker = object()
            with patch(
                "game.persistence.SaveSystem.load_game", return_value=(marker, None)
            ) as load, patch.object(view, "_go_management") as management:
                view._activate("continue")
                load.assert_called_once_with(p / "slot_4.json")
                management.assert_called_once_with(marker)

    def test_reduced_motion_stops_time_and_immediately_updates_focus(self):
        view = TitleView()
        view._reduced_motion = True
        view._hover_index = 2
        view.on_update(0.5)
        self.assertEqual(view._elapsed, 0)
        self.assertEqual(view._focus_amounts, [0, 0, 1, 0])

    @unittest.skipUnless(os.environ.get("DISPLAY"), "Real Arcade capture requires X11")
    def test_native_visual_controls_and_persistence(self):
        with tempfile.TemporaryDirectory() as folder:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "tools.check_title_menu_visual",
                    "--output",
                    folder,
                ],
                capture_output=True,
                text=True,
                timeout=120,
                env={**os.environ, "ALSOFT_DRIVERS": "null"},
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads((Path(folder) / "report.json").read_text())
            self.assertTrue(
                all(value for key, value in report.items() if key != "resolutions")
            )
