"""Native Arcade HQ screenshots and all six department input/transition checks."""

import argparse
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import arcade
from game.ui.layouts.headquarters import (
    ROOMS,
    headquarters_layout,
    headquarters_target_at,
)
from game.ui.room_interaction import close_room
from game.persistence import SaveSystem
from game.ui.theme.typography import set_text_size
from tools.check_squad_command_visual import fixture


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="work/headquarters-visual")
    args = parser.parse_args()
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    window = arcade.Window(
        1672, 941, "CyberCity 2085 · Headquarters", visible=False, antialiasing=False
    )
    gs, view = fixture()
    with patch.object(view, "on_show_view", lambda: None):
        window.show_view(view)
    set_text_size("medium")
    close_room(view.room_ui)

    def campaign_snapshot():
        path = output / "_campaign-snapshot.json"
        gs.save(str(path))
        data = json.loads(path.read_text())
        path.unlink()
        return data

    before = campaign_snapshot()

    def draw():
        window.switch_to()
        window.default_camera.use()
        view.on_update(1 / 60)
        view.on_draw()
        window.ctx.finish()

    def click(rect):
        view.on_mouse_press(*rect.center, arcade.MOUSE_BUTTON_LEFT, 0)

    sizes = []
    for w, h in [(1280, 720), (1672, 941), (1920, 1080), (2560, 1440), (1920, 1000)]:
        window.set_size(w, h)
        window.dispatch_events()
        window.flip()
        draw()
        layout = view._headquarters.layout
        assert len([hit for hit in view._hits if hit.action == "hq_room"]) == 12
        assert all(
            0 <= hit.left < hit.right <= w and 0 <= hit.bottom < hit.top <= h
            for hit in view._hits
        )
        for i, r in enumerate(layout.rooms):
            assert headquarters_target_at(w, h, *r.center) == ROOMS[i][0]
        arcade.get_image(0, 0, w, h).save(output / f"hq-{w}x{h}.png")
        sizes.append([w, h])
    after = campaign_snapshot()
    assert before == after, "Rendering must not alter campaign state"
    window.set_size(1672, 941)
    window.dispatch_events()
    window.flip()
    draw()
    gs.ui_language = "en"
    draw()
    assert any(
        text.visible and text.text == "HEADQUARTERS"
        for text in view._headquarters.paint._texts.values()
    )
    arcade.get_image().save(output / "hq-english.png")
    gs.ui_language = "fr"
    draw()
    rain = view._headquarters.ambient.rain
    background = view._headquarters.background
    with patch(
        "arcade.load_texture",
        side_effect=AssertionError("Unexpected frame texture reload"),
    ):
        for _ in range(8):
            draw()
    assert (
        view._headquarters.ambient.rain is rain
        and view._headquarters.background is background
    )
    # Real hover, mouse entry, opening transition, department controls, Escape return.
    departments = []
    for i, (key, title, _) in enumerate(ROOMS):
        r = view._headquarters.layout.rooms[i]
        view.on_mouse_motion(*r.center, 0, 0)
        for _ in range(12):
            draw()
        assert (
            view._headquarters.hover_key == key
            and view._headquarters.amounts[key] > 0.8
        )
        if key == "research":
            arcade.get_image().save(output / "hq-hover-research.png")
        click(r)
        assert view.room_ui.active_room_key == key
        assert view.room_ui.source_rect.left == round(r.left)
        if key != "squad":
            assert view.room_ui.texture_override is not None
            draw()
            arcade.get_image().save(output / f"transition-{key}.png")
        for _ in range(20):
            view.on_update(1 / 60)
        draw()
        assert view.room_ui.expansion == 1
        assert view._hits or view.room_ui.action_buttons, key
        arcade.get_image().save(output / f"department-{key}.png")
        view.on_key_press(arcade.key.ESCAPE, 0)
        assert not view.room_ui.is_open
        draw()
        # Footer reaches the same department as the room and keyboard shortcut.
        click(view._headquarters.layout.navigation[i])
        assert view.room_ui.active_room_key == key
        view.on_key_press(arcade.key.ESCAPE, 0)
        view.on_key_press(getattr(arcade.key, f"F{i+1}"), 0)
        assert view.room_ui.active_room_key == key
        view.on_key_press(arcade.key.ESCAPE, 0)
        draw()
        departments.append(key)
    # Existing room-strip save/load actions still round-trip the real campaign.
    with TemporaryDirectory() as directory, patch.object(
        SaveSystem,
        "slot_path",
        side_effect=lambda i: Path(directory) / f"slot_{i}.json",
    ):
        view.on_key_press(arcade.key.F1, 0)
        for _ in range(20):
            view.on_update(1 / 60)
        draw()
        for action_key in ("save", "load"):
            hit = next(h for h in view._hits if h.action == action_key)
            view.on_mouse_press(
                (hit.left + hit.right) / 2,
                (hit.bottom + hit.top) / 2,
                arcade.MOUSE_BUTTON_LEFT,
                0,
            )
        assert SaveSystem.slot_path(1).is_file()
        gs = view.game_state
        view.on_key_press(arcade.key.ESCAPE, 0)
        draw()
    # Counters must refresh from live campaign data without spending anything.
    gs.strategic_resources["credits"] = 9876
    draw()
    assert any(
        label.visible and label.text == "9,876"
        for label in view._headquarters.paint._texts.values()
    )
    # Large accessibility text at minimum resolution.
    window.set_size(1280, 720)
    window.dispatch_events()
    window.flip()
    set_text_size("large")
    draw()
    visible_text = {
        text.text for text in view._headquarters.paint._texts.values() if text.visible
    }
    assert {"FONDS", "CRÉDITS", "INTEL", "MATÉRIAUX", "INFLUENCE", "ESC"}.issubset(
        visible_text
    )
    assert not any(text.endswith("…") for text in visible_text)
    # The top edge of expanded large-text navigation remains clickable, too.
    nav = view._headquarters.layout.navigation[4]
    view.on_mouse_press(nav.center[0], nav.top - 1, arcade.MOUSE_BUTTON_LEFT, 0)
    assert view.room_ui.active_room_key == "research"
    view.on_key_press(arcade.key.ESCAPE, 0)
    draw()
    arcade.get_image().save(output / "hq-large-text.png")
    # Reduced motion keeps the live menu fully navigable and selects immediate transitions.
    view._hq_reduced_motion = True
    view._headquarters.hover_key = "intel"
    view.on_update(0.1)
    draw()
    assert view._headquarters.amounts["intel"] == 1
    view.on_key_press(arcade.key.F6, 0)
    assert view.room_ui.expansion == 1
    view.on_key_press(arcade.key.ESCAPE, 0)
    draw()
    # Missing new art uses its own calibrated legacy hit regions.
    from game.ui.components.headquarters import HeadquartersRenderer
    from game.ui.components import headquarters

    real_load = headquarters._load_texture_once
    with patch.object(
        headquarters,
        "_load_texture_once",
        side_effect=lambda path: (
            None if path.endswith("tower_visual_2.png") else real_load(path)
        ),
    ):
        view._headquarters = HeadquartersRenderer()
        draw()
    assert view._headquarters.legacy
    arcade.get_image().save(output / "hq-original-fallback.png")
    for i, r in enumerate(view._headquarters.layout.rooms):
        click(r)
        assert view.room_ui.active_room_key == ROOMS[i][0]
        view.on_key_press(arcade.key.ESCAPE, 0)
        draw()
    # Footer escape and actual Esc both retain return-to-title behavior.
    with patch(
        "game.ui.screens.title_screen.TitleView", return_value=arcade.View()
    ) as title:
        click(view._headquarters.layout.navigation[6])
        title.assert_called_once()
    with patch.object(view, "on_show_view", lambda: None):
        window.show_view(view)
    with patch(
        "game.ui.screens.title_screen.TitleView", return_value=arcade.View()
    ) as title:
        view.on_key_press(arcade.key.ESCAPE, 0)
        title.assert_called_once()
    report = {
        "resolutions": sizes,
        "departments": departments,
        "mouse_footer_keyboard": True,
        "hover_transition": True,
        "live_resources": True,
        "read_only_rendering": True,
        "large_text": True,
        "reduced_motion": True,
        "legacy_fallback": True,
        "return_to_title": True,
        "save_load": True,
        "language": True,
        "cached_frames": True,
    }
    (output / "report.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report))
    window.close()


if __name__ == "__main__":
    main()
