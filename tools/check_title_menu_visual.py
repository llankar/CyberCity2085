"""Actual Arcade title captures and input/persistence checks with isolated saves."""

import argparse
import json
import time
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch, Mock
import arcade
from game.gamestate import GameState
from game.persistence import SaveSystem
from game.ui.screens.title_screen import TitleView
from game.ui.screens import settings_screen
from game.ui.theme.typography import set_text_size


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="work/title-menu-visual")
    args = parser.parse_args()
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    window = arcade.Window(
        1672, 941, "CyberCity 2085 · Main menu", visible=False, antialiasing=False
    )
    music = Mock()
    with TemporaryDirectory() as directory, patch.object(
        settings_screen, "_SETTINGS_PATH", str(Path(directory) / "settings.json")
    ), patch.object(
        SaveSystem,
        "slot_path",
        side_effect=lambda i: Path(directory) / f"slot_{i}.json",
    ), patch(
        "game.audio.SoundManager.get", return_value=music
    ):
        view = TitleView()
        window.show_view(view)
        assert not view._continue_available

        def draw():
            window.switch_to()
            window.default_camera.use()
            view.on_update(1 / 60)
            view.on_draw()
            window.ctx.finish()
            motion_labels = [
                text
                for text in view._renderer.paint._texts.values()
                if text.visible and text.text.startswith("MOTION:")
            ]
            assert len(motion_labels) == 1 and "…" not in motion_labels[0].text

        def click(index, button=arcade.MOUSE_BUTTON_LEFT):
            l, b, r, t, *_ = view._buttons[index]
            view.on_mouse_press((l + r) / 2, (b + t) / 2, button, 0)

        draw()
        arcade.get_image().save(output / "menu-no-save.png")
        with patch.object(view, "_go_management") as management:
            click(1)
            management.assert_not_called()
        view.on_key_press(arcade.key.DOWN, 0)
        assert view._hover_index == 2
        view.on_key_press(arcade.key.UP, 0)
        assert view._hover_index == 0
        state = GameState()
        state.strategic_resources["credits"] = 123
        SaveSystem.save_game(state, SaveSystem.slot_path(3))
        view._refresh_continue()
        assert view._continue_available
        view._message = ""
        view._hover_index = 1
        set_text_size("medium")
        checks = []
        for w, h in [(1280, 720), (1672, 941), (1920, 1080), (2560, 1440)]:
            window.set_size(w, h)
            window.dispatch_events()
            window.flip()
            draw()
            assert all(
                0 <= l < r <= w and 0 <= b < t <= h for l, b, r, t, *_ in view._buttons
            )
            assert len(view._buttons) == 4
            for label, key in view.menu_items:
                rendered = [
                    text
                    for text in view._renderer.paint._texts.values()
                    if text.visible and text.text == label
                ]
                assert len(rendered) == 1 and rendered[0].font_size >= 18
            assert view._renderer.wordmark is not None
            arcade.get_image(0, 0, w, h).save(output / f"menu-{w}x{h}.png")
            checks.append([w, h])
        cached_rain = view._renderer.atmosphere.rain
        cached_logo = view._renderer.wordmark
        with patch(
            "arcade.load_texture",
            side_effect=AssertionError("Uncached frame texture load"),
        ):
            started = time.perf_counter()
            for _ in range(20):
                draw()
            warm_ms = (time.perf_counter() - started) * 1000 / 20
        assert (
            view._renderer.atmosphere.rain is cached_rain
            and view._renderer.wordmark is cached_logo
        )
        with patch.object(view, "_go_management") as management:
            click(1)
            assert management.call_args.args[0].strategic_resources["credits"] == 123
        with patch.object(view, "_activate") as activate:
            for i in range(4):
                l, b, r, t, *_ = view._buttons[i]
                view.on_mouse_motion((l + r) / 2, (b + t) / 2, 0, 0)
                view.on_key_press(arcade.key.ENTER, 0)
                assert activate.call_args.args[0] == view.menu_items[i][1]
            click(0, arcade.MOUSE_BUTTON_RIGHT)
            assert activate.call_count == 4
        with patch(
            "game.ui.screens.new_game_screen.NewGameSetupView",
            return_value=arcade.View(),
        ) as new_game:
            click(0)
            new_game.assert_called_once()
        window.show_view(view)
        view._activate("settings")
        settings = window.current_view
        assert (
            isinstance(settings, settings_screen.SettingsView)
            and settings._return_view is view
        )
        settings._back()
        assert window.current_view is view
        with patch("game.ui.screens.title_screen.arcade.exit") as quit_game:
            view.on_key_press(arcade.key.ESCAPE, 0)
            quit_game.assert_called_once()
        window.set_size(1280, 720)
        window.dispatch_events()
        window.flip()
        set_text_size("large")
        draw()
        arcade.get_image().save(output / "menu-large-text.png")
        # Reduced animation is persistent and freezes atmosphere and pulse time.
        view.on_key_press(arcade.key.M, 0)
        assert settings_screen.load_settings().reduced_motion
        before = view._elapsed
        view.on_update(0.5)
        assert view._elapsed == before
        draw()
        arcade.get_image().save(output / "menu-reduced-motion.png")
        fresh = TitleView()
        window.show_view(fresh)
        assert fresh._reduced_motion
        window.show_view(view)
        motion = view._renderer.layout.motion
        view.on_mouse_press(*motion.center, arcade.MOUSE_BUTTON_LEFT, 0)
        assert not settings_screen.load_settings().reduced_motion
        # A corrupt existing save must not silently start an unrelated new campaign.
        SaveSystem.slot_path(3).write_text("{broken")
        view._refresh_continue()
        with patch.object(view, "_go_management") as management:
            view._activate("continue")
            management.assert_not_called()
        assert not view._continue_available and view._message
        # Preserve the old artwork fallback, plus a procedural last resort.
        set_text_size("medium")
        view._message = ""
        with patch(
            "game.ui.screens.title_screen._TITLE_VISUAL_ASSET",
            Path(directory) / "missing.png",
        ):
            view._background_texture = view._load_background_texture()
        assert view._background_texture is not None
        draw()
        arcade.get_image().save(output / "menu-legacy-fallback.png")
        view._background_texture = None
        draw()
        arcade.get_image().save(output / "menu-procedural-fallback.png")
        music.play_music.assert_any_call("music_title")
        report = {
            "resolutions": checks,
            "continue_actual_save": True,
            "disabled_without_save": True,
            "corrupt_save_safe": True,
            "new_game": True,
            "settings_return": True,
            "quit": True,
            "keyboard_mouse": True,
            "reduced_motion_persisted": True,
            "fallbacks": True,
            "title_music": True,
            "cached_frames": True,
            "warm_frame_ms": round(warm_ms, 2),
        }
        (output / "report.json").write_text(json.dumps(report, indent=2))
        print(json.dumps(report))
    window.close()


if __name__ == "__main__":
    main()
