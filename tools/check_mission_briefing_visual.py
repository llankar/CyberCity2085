"""Capture actual Arcade briefing; verify scrolling, route controls and read-only rendering."""

import argparse
from copy import deepcopy
import json
from pathlib import Path
from unittest.mock import patch
import arcade
from game.management.spec_ops_assets import CombatRobot, PowerArmorSuit
from game.consequences import Consequence
from game.recruitment import create_character
from game.ui.components.briefing_content import mission_art_path
from game.mission_templates import MissionComplication
from game.ui.screens.mission_briefing_view import (
    MissionBriefingView,
    build_mission_briefing_facts,
)
from game.ui.theme.typography import set_text_size
from tools.check_squad_command_visual import fixture


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="work/briefing-visual")
    args = parser.parse_args()
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    window = arcade.Window(1672, 941, "CyberCity 2085 · Briefing", visible=False)
    gs, _ = fixture()
    gs.selected_agent_names = [a.name for a in gs.characters[:5]]
    mission = gs.mission_templates[gs.selected_mission_index]
    mission.risk_level = 8
    mission.success_consequences = [
        Consequence(
            narrative_text="Extraction succeeds: survivors spread trust through the district shelters."
        )
    ]
    mission.failure_consequences = [
        Consequence(
            narrative_text="Evacuation fails: missing agents become symbols of corporate abandonment."
        )
    ]
    mission.emotional_impact_hint = {
        "level": "high",
        "text": "Risk of lasting emotional scars for the squad.",
    }
    for i, a in enumerate(gs.characters):
        a.stress = 35 + i * 7
    gs.spec_ops_assets = [
        PowerArmorSuit(id="mantis", name="Mantis Light Armor", deploy_cost=15),
        CombatRobot(id="kestrel", name="Kestrel Drone", deploy_cost=10),
    ]
    gs.selected_asset_ids = ["mantis", "kestrel"]
    view = MissionBriefingView(gs, mission)
    # Native rendering without initializing audio devices in the capture harness.
    with patch.object(view, "on_show_view", view._load_assets):
        window.show_view(view)
    before = [deepcopy(a.to_dict()) for a in gs.characters]
    snapshot = deepcopy(mission.to_dict())
    campaign = (
        gs.calendar.current_day,
        deepcopy(gs.strategic_resources),
        deepcopy(gs.funds.__dict__),
        list(gs.selected_agent_names),
        list(gs.selected_asset_ids),
    )
    set_text_size("medium")

    def draw():
        window.switch_to()
        window.default_camera.use()
        view.on_update(1 / 60)
        view.on_draw()
        window.ctx.finish()

    def click(action, data=None):
        hit = next(
            h
            for h in view._hits
            if h.action == action and (data is None or h.data == data)
        )
        view.on_mouse_press(
            (hit.left + hit.right) / 2,
            (hit.bottom + hit.top) / 2,
            arcade.MOUSE_BUTTON_LEFT,
            0,
        )

    checks = []
    for w, h in [(1280, 720), (1672, 941), (1920, 1080), (2560, 1440)]:
        window.set_size(w, h)
        window.dispatch_events()
        window.flip()
        draw()
        assert all(
            0 <= hit.left < hit.right <= w and 0 <= hit.bottom < hit.top <= h
            for hit in view._hits
        ), (w, h)
        assert view._abort_rect and view._deploy_rect
        arcade.get_image(0, 0, w, h).save(output / f"briefing-{w}x{h}.png")
        checks.append([w, h])
    # Map is the exact mission-selected texture; full inspection is a real modal.
    click("map")
    draw()
    assert view._renderer.map_open
    arcade.get_image().save(output / "briefing-map.png")
    with patch.object(view, "_abort") as abort:
        view.on_key_press(arcade.key.ESCAPE, 0)
        assert not view._renderer.map_open
        abort.assert_not_called()
    draw()
    with patch.object(view, "_launch_battle") as launch, patch.object(
        view, "_abort"
    ) as abort:
        click("deploy")
        launch.assert_called_once()
        click("abort")
        abort.assert_called_once()
        view.on_key_press(arcade.key.ENTER, 0)
        assert launch.call_count == 2
        view.on_key_press(arcade.key.ESCAPE, 0)
        assert abort.call_count == 2
    assert (
        before == [a.to_dict() for a in gs.characters] and snapshot == mission.to_dict()
    )
    assert campaign == (
        gs.calendar.current_day,
        gs.strategic_resources,
        gs.funds.__dict__,
        gs.selected_agent_names,
        gs.selected_asset_ids,
    )
    original_view = view
    alternate = next(
        m for m in gs.mission_templates if mission_art_path(m) != view._renderer.art
    )
    view = MissionBriefingView(gs, alternate)
    with patch.object(view, "on_show_view", view._load_assets):
        window.show_view(view)
    draw()
    arcade.get_image().save(output / "briefing-alternate-mission.png")
    assert view._renderer.art != original_view._renderer.art
    view = original_view
    with patch.object(view, "on_show_view", view._load_assets):
        window.show_view(view)
    # All long lists must remain reachable, including >6 agents and >4 supports.
    gs.characters.extend(create_character(f"Reserve {i}", "sniper") for i in range(4))
    gs.selected_agent_names = [a.name for a in gs.characters]
    mission.possible_complications = [
        MissionComplication(
            key=f"c{i}",
            name=f"Complication {i}",
            trigger_text=f"Complication {i}: A rapid-response squad is rerouted toward the extraction; corporate counterintelligence flags the operation in real time.",
            risk_threshold=1,
        )
        for i in range(14)
    ]
    mission.success_consequences *= 8
    mission.failure_consequences *= 8
    gs.spec_ops_assets.extend(
        CombatRobot(id=f"unit{i}", name=f"Support unit {i}", deploy_cost=i)
        for i in range(8)
    )
    gs.selected_asset_ids = [a.id for a in gs.spec_ops_assets]
    view._facts = build_mission_briefing_facts(gs, mission)
    window.set_size(1280, 720)
    window.dispatch_events()
    window.flip()
    set_text_size("large")
    draw()
    for section in [
        "complications",
        "impact",
        "success",
        "failure",
        "squad",
        "support",
    ]:
        r, max_scroll = view._renderer.scroll_regions[section]
        view.on_mouse_scroll(*r.center, 0, -10000)
        draw()
        assert view._renderer.offsets[section] == max_scroll, (
            section,
            view._renderer.offsets[section],
            max_scroll,
        )
    assert len(view._renderer.agents) > 6 and len(view._renderer.assets) > 4
    assert any(
        h.action == "info" and h.data == gs.characters[-1].name for h in view._hits
    )
    assert not any(
        label.visible
        and (label.text.startswith("sheet.") or label.text.startswith("briefing."))
        for label in view._renderer.paint._texts.values()
    )
    arcade.get_image().save(output / "briefing-large-overflow.png")
    # Empty lists do not create bogus agents/support/consequences or disable controls.
    gs.selected_agent_names = []
    gs.selected_asset_ids = []
    view._facts = build_mission_briefing_facts(gs, mission)
    draw()
    arcade.get_image().save(output / "briefing-empty.png")
    set_text_size("medium")
    gs.ui_language = "en"
    draw()
    assert any(
        label.text == "DEPLOY  [ENTER]" and label.visible
        for label in view._renderer.paint._texts.values()
    )
    arcade.get_image().save(output / "briefing-english.png")
    report = {
        "resolutions": checks,
        "read_only": True,
        "controls": True,
        "map_inspection": True,
        "overflow": True,
        "empty": True,
        "language": True,
    }
    (output / "report.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report))
    window.close()


if __name__ == "__main__":
    main()
