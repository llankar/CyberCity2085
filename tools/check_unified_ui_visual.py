"""Native Arcade department capture, real controller interactions and save QA."""

import argparse
import json
import time
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import arcade
from tools.check_squad_command_visual import fixture
from game.management.spec_ops_assets import asset_catalog
from game.management.events import ActiveEvent, EventTemplate, EventChoice
from game.ui.theme.typography import set_text_size


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="work/unified-ui")
    args = parser.parse_args()
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    window = arcade.Window(
        1280, 720, "CyberCity · UI Unification", visible=False, antialiasing=False
    )
    gs, view = fixture()
    gs.spec_ops_assets = asset_catalog()
    gs.ui_language = "fr"
    gs.spec_ops_assets[0].maintenance.integrity = 75
    gs.active_events = [
        ActiveEvent(
            id="qa_crisis",
            template=EventTemplate(
                title="Grid Riots",
                category="SOCIAL_UNREST",
                description="The district is close to breaking. Respond to restore control.",
                severity=4,
                choices=[
                    EventChoice("respond", "Respond"),
                    EventChoice("ignore", "Observe"),
                ],
                expiration_days=2,
            ),
            created_day=gs.calendar.current_day,
            expires_day=gs.calendar.current_day + 2,
        )
    ]
    with patch.object(view, "on_show_view", lambda: None):
        window.show_view(view)
    set_text_size("medium")

    def snapshot():
        state = view.game_state
        return json.dumps(
            {
                "characters": [c.to_dict() for c in state.characters],
                "assets": [a.to_dict() for a in state.spec_ops_assets],
                "campaign": state.campaign.to_dict(),
                "funds": state.available_funds,
                "resources": state.strategic_resources,
                "corporate": state.corp_budget,
                "city": state.city_budget,
            },
            sort_keys=True,
        )

    def draw():
        before = snapshot()
        window.switch_to()
        window.default_camera.use()
        view.on_draw()
        window.ctx.finish()
        assert snapshot() == before, "Rendering must not mutate campaign data"

    def capture(name):
        draw()
        arcade.get_image(0, 0, window.width, window.height).save(
            output / f"{name}-{window.width}x{window.height}.png"
        )

    def click(action, data=None):
        draw()
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
    with TemporaryDirectory() as tmp:
        for width, height in [(1280, 720), (1920, 1080), (2560, 1440)]:
            window.set_size(width, height)
            window.dispatch_events()
            window.flip()
            for room in ["assets", "command", "city", "squad", "research", "intel"]:
                view._open_hub_room(room)
                if room == "assets":
                    if view._department_deck is None:
                        draw()
                    view._department_deck.selection["asset_bay_mode"] = "armory"
                view.on_update(1)
                draw()
                gs.save(f"{tmp}/before.json")
                before = json.loads(Path(f"{tmp}/before.json").read_text())
                capture(room)
                if room == "assets":
                    pages = view._department_deck.capacities["armory_catalog"][0]
                    assert pages > 1
                    click("department_page", ("armory_catalog", 1))
                    assert view._department_deck.pages["armory_catalog"] == 1
                    capture("assets-catalog-page-2")
                    view._department_deck.pages["armory_catalog"] = 0
                gs.save(f"{tmp}/after.json")
                assert before == json.loads(
                    Path(f"{tmp}/after.json").read_text()
                ), "Drawing mutated campaign data"
                assert all(
                    0 <= r.left < r.right <= width and 0 <= r.bottom < r.top <= height
                    for r in view._hits
                ), (room, width, height)
                assert view._department_deck is not None
            view._open_hub_room("assets")
            view._department_deck.selection["asset_bay_mode"] = "vehicles"
            view._asset_cursor = 3
            capture("assets-armor")
            assert len([h for h in view._hits if h.action == "assign_pilot"]) >= 4
            click("assign_pilot", (3, gs.characters[0].name))
            assert gs.spec_ops_assets[3].pilot_agent_name == gs.characters[0].name
            checks.append([width, height])
        view._open_hub_room("assets")
        view._department_deck.selection["asset_bay_mode"] = "vehicles"
        view._asset_cursor = 0
        funds = gs.available_funds
        cost = gs.spec_ops_assets[0].maintenance.repair_cost
        click("asset_repair", 0)
        assert (
            gs.spec_ops_assets[0].maintenance.integrity == 100
            and gs.available_funds == funds - cost
        )
        click("asset_deploy_toggle", 0)
        assert gs.spec_ops_assets[0].id in gs.selected_asset_ids
        click("asset_deploy_toggle", 0)
        assert gs.spec_ops_assets[0].id not in gs.selected_asset_ids
        view._asset_cursor = 3
        draw()
        click("assign_pilot", (3, gs.characters[0].name))
        assert gs.spec_ops_assets[3].pilot_agent_name == gs.characters[0].name
        capture("assets-pilot")
        view._catalog_scroll = 4
        count = len(gs.spec_ops_assets)
        click("catalog_acquire_by_id", asset_catalog()[4].id)
        assert len(gs.spec_ops_assets) == count + 1 and gs.spec_ops_assets[
            -1
        ].name.startswith(asset_catalog()[4].name)
        # Wrap catalogue/hangar and keyboard cursor without losing the actual item index.
        click("catalog_scroll", 1)
        assert view._catalog_scroll == 5
        view._asset_cursor = len(gs.spec_ops_assets) - 1
        draw()
        assert any(
            h.action == "asset_select" and h.data == view._asset_cursor
            for h in view._hits
        )
        view.on_key_press(arcade.key.LEFT, 0)
        assert view._asset_cursor == len(gs.spec_ops_assets) - 2
        view._open_hub_room("city")
        old = gs.city_budget.get("armaments", 0)
        click("city_upgrade_armaments")
        assert gs.city_budget["armaments"] == old + 10
        view._open_hub_room("research")
        draw()
        view._department_deck.selection["research"] = "weapon_corporate_rail_lattice"
        capture("research-equipment-unlocks")
        view._department_deck.selection["research"] = "weapon_smartlink_mk1"
        draw()
        action = next(
            h.action for h in view._hits if h.action.startswith("start_research_")
        )
        click(action)
        assert gs.active_research
        capture("research-progress")
        # Traverse every catalogue project page and select the real project ID.
        pages = view._department_deck.capacities["research"][0]
        seen = set()
        for _ in range(pages):
            draw()
            seen.update(
                h.data[1]
                for h in view._hits
                if h.action == "department_select" and h.data[0] == "research"
            )
            if pages > 1:
                click("department_page", ("research", 1))
        assert seen == set(gs.research_tree.projects)
        view._open_hub_room("command")
        before = gs.corp_budget.get("research", 0)
        click("corp_upgrade_research")
        assert gs.corp_budget["research"] == before + 10
        click("weekly_directive_civil_defense")
        assert gs.weekly_directive_id == "civil_defense"
        click("event_response_0_0")
        assert all(e.id != "qa_crisis" for e in gs.active_events)
        view._open_hub_room("intel")
        draw()
        hit = next(h for h in view._hits if h.action == "department_select")
        click(hit.action, hit.data)
        # The reader includes all campaign modules, not just the first legacy lines.
        draw()
        click("department_select", ("intel_mode", "campaign"))
        draw()
        assert (
            len(
                [
                    h
                    for h in view._hits
                    if h.action == "department_select" and h.data[0] == "intel_campaign"
                ]
            )
            == 5
        )
        from game.persistence import SaveSystem

        with patch.object(
            SaveSystem, "slot_path", side_effect=lambda slot: f"{tmp}/slot-{slot}.json"
        ):
            funds = gs.available_funds
            click("save")
            gs.add_funds(17, "qa", "Temporary fixture mutation")
            click("load")
            assert view.game_state.available_funds == funds
        gs = view.game_state
        gs.ui_language = "en"
        set_text_size("large")
        window.set_size(1280, 720)
        window.dispatch_events()
        window.flip()
        for room in ["assets", "command", "city", "squad", "research", "intel"]:
            view._open_hub_room(room)
            if room == "assets":
                view._department_deck.selection["asset_bay_mode"] = "armory"
            capture(room + "-large-en")
        set_text_size("medium")
        gs.ui_language = "fr"
        view._open_hub_room("assets")
        view._department_deck.selection["asset_bay_mode"] = "vehicles"
        view._asset_cursor = 0
        draw()
        disabled = next(h for h in view._hits if h.action == "ui_disabled")
        view.on_mouse_motion(
            (disabled.left + disabled.right) / 2,
            (disabled.bottom + disabled.top) / 2,
            0,
            0,
        )
        capture("assets-disabled-hover")
        view.on_key_press(arcade.key.TAB, 0)
        assert view._department_deck.hover
        view.on_key_press(arcade.key.F5, 0)
        assert view.room_ui.active_room_key == "research"
        for _ in range(5):
            draw()
        start = time.perf_counter()
        for _ in range(10):
            draw()
        warm_ms = (time.perf_counter() - start) * 100
    print(
        json.dumps(
            {
                "resolutions": checks,
                "render_is_readonly": True,
                "buy_repair_deploy_pilot": True,
                "research_all_pages": True,
                "directives_events_upgrades": True,
                "save_load": True,
                "keyboard": True,
                "large_en": True,
                "warm_draw_ms": round(warm_ms, 2),
            }
        )
    )
    window.close()


if __name__ == "__main__":
    main()
