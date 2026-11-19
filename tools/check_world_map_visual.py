"""Render the actual Arcade World Map and exercise its live hit regions.

Run with a real X11/desktop display; writes local review artifacts under work/.
No campaign save, repository publication or fake UI renderer is used.
"""

import argparse
import json
from pathlib import Path
import time
import arcade
from game.gamestate import GameState
from game.character import Character
from game.management.equipment import Weapon
from game.ui.layouts.world_map_beacons import artwork_obstacles
from unittest.mock import patch
from game.missions.flow import ensure_mission_templates
from game.ui.screens.world_map_view import MissionWorldMapView


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="work/world-map-visual")
    args = parser.parse_args()
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    state = GameState(
        characters=[Character("Rook"), Character("Vera")],
        selected_agent_names=["Rook", "Vera"],
    )
    for i, agent in enumerate(state.characters):
        agent.loadout.primary_weapon = Weapon(
            str(i),
            ["Pulse Rifle", "Plasma Carbine"][i],
            "primary_weapon",
            range_cells=8,
            attack_stat="agi",
        )
    ensure_mission_templates(state)
    state.selected_mission_index = next(
        (i for i, m in enumerate(state.mission_templates) if "[STORY]" in m.title), 0
    )
    # Controlled dynamic urgent scenario, using the real mission model and view.
    state.mission_templates[0].is_urgent = True
    window = arcade.Window(
        1672, 941, "CyberCity 2085 · World Map 2.0", visible=False, antialiasing=False
    )
    view = MissionWorldMapView(state)
    window.show_view(view)
    checks = []
    try:
        for w, h in [(1672, 941), (1280, 720), (1920, 1080)]:
            window.set_size(w, h)
            window.dispatch_events()
            window.flip()  # Realize the resized Mesa back buffer before readback.
            window.switch_to()
            window.default_camera.use()
            view._handle_action(
                "select_mission",
                (
                    state.selected_mission_index
                    if w == 1672
                    else next(
                        i
                        for i, m in enumerate(state.mission_templates)
                        if "[STORY]" in m.title
                    )
                ),
            )
            view.on_update(0.25)
            view.on_draw()
            window.ctx.finish()
            arcade.get_image(0, 0, w, h).save(output / f"world-map-{w}x{h}.png")
            keys = [p.beacon.key for p in view._placements]
            for key in keys:
                p = next(p for p in view._placements if p.beacon.key == key)
                x, y = p.label.center
                view.on_mouse_motion(x, y, 0, 0)
                view.on_update(0.1)
                assert view._hover_key == key
                view.on_mouse_press(x, y, arcade.MOUSE_BUTTON_LEFT, 0)
                view.on_draw()
                assert (
                    next(p.beacon.key for p in view._placements if p.beacon.selected)
                    == key
                )
                occupied = list(artwork_obstacles(view._image_bounds))
                for placed in view._placements:
                    for rect in [placed.marker, placed.label]:
                        assert rect.inside(view._image_bounds), (w, h, key, rect)
                        assert not any(rect.intersects(o) for o in occupied), (
                            w,
                            h,
                            key,
                            rect,
                        )
                        occupied.append(rect)
                assert view._selected_link, (w, h, key, "missing selected link")
            checks.append(
                {
                    "size": [w, h],
                    "beacons": len(view._placements),
                    "selections_checked": len(keys),
                }
            )
        # Exercise actual marker and label hit regions, hover animation and scroll.
        for kind in ["combat", "text"]:
            placement = next(
                p
                for p in view._placements
                if p.beacon.kind == kind and not p.beacon.selected
            )
            x, y = placement.label.center
            view.on_mouse_motion(x, y, 0, 0)
            view.on_update(0.1)
            assert view._hover_key == placement.beacon.key
            assert view._hover_amounts[placement.beacon.key] > 0
            view.on_mouse_press(x, y, arcade.MOUSE_BUTTON_LEFT, 0)
            assert view._selection_type == kind
            view.on_draw()
        arcade.get_image(0, 0, window.width, window.height).save(
            output / "world-map-narrative.png"
        )
        narrative_index = view._selected_text_index
        story_index = next(
            i for i, m in enumerate(state.mission_templates) if "[STORY]" in m.title
        )
        view._handle_action("select_mission", story_index)
        view.on_draw()
        bounds = view._briefing_bounds
        assert view._briefing_content_height > view._briefing_body_height
        view.on_mouse_scroll(*bounds.center, 0, -4)
        assert view._briefing_scroll > 0
        view.on_mouse_scroll(*bounds.center, 0, -1000)
        assert (
            view._briefing_scroll
            == view._briefing_content_height - view._briefing_body_height
        )
        view.on_mouse_scroll(0, 0, 0, 1000)
        assert (
            view._briefing_scroll > 0
        )  # Scrolling the map must not scroll the briefing.
        view._handle_action("select_text_mission", narrative_index)
        view.on_draw()
        assert view._briefing_scroll == 0

        # Actual navigation handlers; isolate only destination construction and
        # campaign launch, so this review cannot modify a real save or open battle.
        def click(action):
            hit = next(h for h in view._hits if h.action == action)
            view.on_mouse_press(
                (hit.left + hit.right) / 2,
                (hit.bottom + hit.top) / 2,
                arcade.MOUSE_BUTTON_LEFT,
                0,
            )

        with patch.object(window, "show_view") as show:
            with patch(
                "game.ui.screens.management_screen.ManagementView"
            ) as destination:
                click("confirm_mission")
                destination.return_value.setup.assert_called_once()
                assert destination.return_value.active_tab == "squad"
                click("back")
                view.on_key_press(arcade.key.ESCAPE, 0)
                assert show.call_count == 3
            show.reset_mock()
            with patch(
                "game.ui.screens.text_mission_view.TextMissionView"
            ) as destination:
                click("launch_mission")
                destination.assert_called_once_with(
                    state, view._text_missions[view._selected_text_index]
                )
                show.assert_called_once()
            view._handle_action("select_mission", 0)
            with patch(
                "game.ui.screens.world_map_view._launch_mission", return_value=object()
            ) as launch, patch(
                "game.ui.screens.mission_briefing_view.MissionBriefingView"
            ) as destination:
                view.on_key_press(arcade.key.ENTER, 0)
                launch.assert_called_once_with(state)
                destination.assert_called_once()
        view.on_draw()
        assert all(
            t._label.document.get_font().name == "Rajdhani"
            for t in view._renderer._texts.values()
        )
        arcade.get_image(0, 0, window.width, window.height).save(
            output / "world-map-urgent.png"
        )
        for _ in range(30):
            view.on_update(1 / 60)
            view.on_draw()
        window.ctx.finish()
        # Timing after warm caches, without screenshot readback.
        start = time.perf_counter()
        for _ in range(20):
            view.on_update(1 / 60)
            view.on_draw()
        window.ctx.finish()
        elapsed = time.perf_counter() - start
        report = {
            "checks": checks,
            "hover_and_selection": True,
            "narrative_and_combat": True,
            "navigation_and_launch": True,
            "bundled_font_verified": True,
            "warm_draw_ms": elapsed * 1000 / 20,
        }
        (output / "report.json").write_text(json.dumps(report, indent=2))
        print(json.dumps(report))
    finally:
        window.close()


if __name__ == "__main__":
    main()
