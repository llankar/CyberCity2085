"""Render the real management screen and exercise its actual squad hit regions."""

import argparse
import json
import time
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import arcade
from game.gamestate import GameState
from game.recruitment import create_character
from game.management.equipment import EQUIPMENT_SLOTS
from game.management.downtime import DOWNTIME_ACTIVITIES
from game.ui.screens.management_screen import ManagementView
from game.ui.theme.typography import set_text_size


def fixture():
    chars = [
        create_character(n, r)
        for n, r in [
            ("Rook", "samurai"),
            ("Longshot", "sniper"),
            ("Oracle", "psi"),
            ("Katana", "samurai"),
            ("Null", "psi"),
        ]
    ]
    gs = GameState(characters=chars, selected_agent_names=[c.name for c in chars])
    gs.strategic_resources.update(credits=50, intel=50, influence=50, salvage=50)
    gs.add_funds(500, "visual_fixture", "Isolated UI test fixture")
    for i, c in enumerate(chars):
        c.stress = 15 + i * 3
    view = ManagementView(gs)
    view.setup()
    for c in chars:
        for slot in EQUIPMENT_SLOTS:
            c.loadout.equip(slot, view.equipment_catalog[slot][0])
    chars[0].pending_points = 3
    gs.selected_mission_index = next(
        (i for i, m in enumerate(gs.mission_templates) if "[STORY]" in m.title), 0
    )
    return gs, view


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="work/squad-command-visual")
    args = parser.parse_args()
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    window = arcade.Window(
        1672,
        941,
        "CyberCity 2085 · Squad Command 2.0",
        visible=False,
        antialiasing=False,
    )
    gs, view = fixture()
    window.show_view(view)
    set_text_size("medium")
    view._open_hub_room("squad")
    view.on_update(1)

    def draw():
        window.switch_to()
        window.default_camera.use()
        view.on_draw()
        window.ctx.finish()

    def click(action, data=None):
        hit = next(
            h
            for h in reversed(view._hits)
            if h.action == action and (data is None or h.data == data)
        )
        x, y = (hit.left + hit.right) / 2, (hit.bottom + hit.top) / 2
        view.on_mouse_motion(x, y, 0, 0)
        view.on_update(0.1)
        view.on_mouse_press(x, y, arcade.MOUSE_BUTTON_LEFT, 0)

    checks = []
    try:
        for w, h in [(1280, 720), (1672, 941), (1920, 1080), (2560, 1440)]:
            window.set_size(w, h)
            window.dispatch_events()
            window.flip()
            draw()
            visible_ready = [
                label
                for label in view._squad_command.paint._texts.values()
                if label.text == "PRÊT" and label.visible
            ]
            assert (
                len(visible_ready) == 5
            ), "Repeated roster labels must all remain visible in the shared text batch"
            arcade.get_image(0, 0, w, h).save(output / f"squad-{w}x{h}.png")
            assert all(
                0 <= hit.left < hit.right <= w and 0 <= hit.bottom < hit.top <= h
                for hit in view._hits
            ), (w, h)
            assert len([hit for hit in view._hits if hit.action == "equip_next"]) == 6
            assert len([hit for hit in view._hits if hit.action == "equip_prev"]) == 6
            assert len(
                [hit for hit in view._hits if hit.action == "downtime_activity"]
            ) == len(DOWNTIME_ACTIVITIES)
            before = gs.characters[0].loadout.primary_weapon
            click("equip_next", (0, "primary_weapon"))
            assert gs.characters[0].loadout.primary_weapon != before
            click("equip_prev", (0, "primary_weapon"))
            assert gs.characters[0].loadout.primary_weapon == before
            checks.append(
                {
                    "size": [w, h],
                    "hit_regions": len(view._hits),
                    "all_equipment_and_activities_visible": True,
                }
            )
        for _ in range(20):
            view.on_update(1 / 60)
            draw()
        started = time.perf_counter()
        for _ in range(20):
            view.on_update(1 / 60)
            draw()
        warm_ms = (time.perf_counter() - started) * 1000 / 20
        window.set_size(1280, 720)
        window.dispatch_events()
        window.flip()
        set_text_size("large")
        draw()
        assert len([hit for hit in view._hits if hit.action == "agent_card"]) == 4
        arcade.get_image(0, 0, 1280, 720).save(output / "squad-large-text.png")
        set_text_size("medium")
        draw()
        # Direct upgrade buttons use the original stat-point mutation.
        before = gs.characters[0].stats.str
        click("spend_stat_point", (0, "str"))
        assert gs.characters[0].stats.str == before + 1
        assert gs.characters[0].pending_points == 2
        # Existing single/double click semantics and keyboard selection.
        click("agent_card", 1)
        assert (
            view.deployment_cursor == 1
            and gs.characters[1].name not in gs.selected_agent_names
        )
        view.on_key_press(arcade.key.SPACE, 0)
        assert gs.characters[1].name in gs.selected_agent_names
        view.on_key_press(arcade.key.RIGHT, 0)
        assert view.deployment_cursor == 2
        view.on_key_press(arcade.key.LEFT, 0)
        assert view.deployment_cursor == 1
        # Both single/double click semantics use the existing card dispatcher.
        view._last_agent_click_index = None
        draw()
        click("agent_card", 1)
        click("agent_card", 1)
        assert view.expanded_agent_sheet_index == 1
        view.on_key_press(arcade.key.ESCAPE, 0)
        gs.characters[1].pending_points = 2
        # Click the large portrait to open the actual full sheet.
        draw()
        click("squad_sheet", 1)
        draw()
        assert view.expanded_agent_sheet_index == 1
        arcade.get_image(0, 0, window.width, window.height).save(
            output / "agent-sheet.png"
        )
        # Allocate an attribute, a skill rank and a talent through real modal hits.
        for action in ("sheet_spend_stat", "sheet_spend_skill_rank", "unlock_talent"):
            draw()
            hit = next(h for h in view._modal_hits if h.action == action)
            before_points = gs.characters[1].pending_points
            view.on_mouse_press(
                (hit.left + hit.right) / 2,
                (hit.bottom + hit.top) / 2,
                arcade.MOUSE_BUTTON_LEFT,
                0,
            )
            if action != "unlock_talent":
                assert gs.characters[1].pending_points == before_points - 1
        view.on_key_press(arcade.key.ESCAPE, 0)
        assert view.expanded_agent_sheet_index is None
        # Recruit through the actual chooser with its real candidate prices.
        draw()
        click("recruit_prompt")
        draw()
        assert view.recruit_window_open
        arcade.get_image(0, 0, window.width, window.height).save(
            output / "recruitment.png"
        )
        candidate = view.pending_recruit_candidates[0]
        funds = gs.available_funds
        hit = next(h for h in view._modal_hits if h.action == "recruit_candidate")
        view.on_mouse_press(
            (hit.left + hit.right) / 2,
            (hit.bottom + hit.top) / 2,
            arcade.MOUSE_BUTTON_LEFT,
            0,
        )
        assert gs.available_funds == funds - candidate.price
        assert candidate.name in [c.name for c in gs.characters]
        # Scroll newly recruited agents into view without altering squad membership.
        draw()
        selection = list(gs.selected_agent_names)
        region = view._squad_command.regions["roster"]
        view.on_mouse_scroll(*region.center, 0, -4)
        draw()
        assert any(
            h.action == "agent_card" and h.data == len(gs.characters) - 1
            for h in view._hits
        )
        assert gs.selected_agent_names == selection
        # All downtime activities and keyboard 7–9 retain real costs/effects.
        for i, code in enumerate(
            [arcade.key.KEY_7, arcade.key.KEY_8, arcade.key.KEY_9]
        ):
            day = gs.calendar.current_day
            view.on_key_press(code, 0)
            assert gs.calendar.current_day > day
        view.deployment_cursor = 0
        view._squad_command.roster_first = 0
        draw()
        slot = view.selected_save_slot
        click("squad_nav", "slot_prev")
        assert view.selected_save_slot != slot
        click("squad_nav", "slot_next")
        assert view.selected_save_slot == slot
        # Saving/loading is real, isolated in a temporary directory.
        with TemporaryDirectory() as directory:
            from game.persistence import SaveSystem

            with patch.object(
                SaveSystem,
                "slot_path",
                side_effect=lambda slot: Path(directory) / f"slot{slot}.json",
            ):
                click("squad_nav", "save")
                before_names = [c.name for c in view.game_state.characters]
                click("squad_nav", "load")
                assert [c.name for c in view.game_state.characters] == before_names
        # Navigation destinations are observed at the window boundary.
        draw()
        with patch.object(window, "show_view") as show:
            click("open_mission_map")
            assert show.call_count == 1
            show.reset_mock()
            click("squad_nav", "next_step")
            assert show.call_count == 1
            show.reset_mock()
            view.on_key_press(arcade.key.B, 0)
            assert show.call_count == 1
            show.reset_mock()
            view.on_key_press(arcade.key.ENTER, 0)
            assert show.call_count == 1
            show.reset_mock()
            click("squad_settings")
            assert show.call_count == 1
            settings = show.call_args.args[0]
            assert settings._return_view is view
            settings.window = window
            settings._back()
            assert show.call_args.args[0] is view
        # English UI uses the configured language, not French mockup strings.
        view.game_state.ui_language = "en"
        draw()
        labels = [label.text for label in view._squad_command.paint._texts.values()]
        assert any("ACTIVE MISSION" in text for text in labels)
        assert not any(
            label.text == "MISSION ACTIVE" and label.visible
            for label in view._squad_command.paint._texts.values()
        ), "Old-language labels must not remain in the batch"
        arcade.get_image(0, 0, window.width, window.height).save(
            output / "squad-english.png"
        )
        count = len(view.game_state.characters)
        removed_name = view.game_state.characters[view.deployment_cursor].name
        click("squad_nav", "remove_agent")
        assert len(view.game_state.characters) == count - 1
        assert removed_name not in view.game_state.selected_agent_names
        day = view.game_state.calendar.current_day
        view.on_key_press(arcade.key.D, 0)
        assert view.game_state.calendar.current_day == day + 1
        for code, room in [
            (arcade.key.F1, "command"),
            (arcade.key.F2, "city"),
            (arcade.key.F4, "assets"),
            (arcade.key.F5, "research"),
            (arcade.key.F6, "intel"),
            (arcade.key.F3, "squad"),
        ]:
            view.on_key_press(code, 0)
            assert view.room_ui.active_room_key == room
        draw()
        click("squad_close")
        assert not view.room_ui.is_open
        view.on_key_press(arcade.key.F3, 0)
        # Empty and overflow rosters remain usable; deletion stays on original path.
        view.game_state.characters = []
        view.game_state.selected_agent_names = []
        draw()
        assert any(h.action == "recruit_prompt" for h in view._hits)
        report = {
            "resolutions": checks,
            "equipment": True,
            "stat_upgrade": True,
            "recruitment": True,
            "roster_scroll": True,
            "downtime": True,
            "save_load": True,
            "navigation": True,
            "english": True,
            "empty_roster": True,
            "modal_allocations": True,
            "remove_agent": True,
            "keyboard_rooms": True,
            "large_text": True,
            "warm_draw_ms": warm_ms,
        }
        (output / "report.json").write_text(json.dumps(report, indent=2))
        print(json.dumps(report))
    finally:
        window.close()


if __name__ == "__main__":
    main()
