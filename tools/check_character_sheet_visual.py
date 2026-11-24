"""Real Arcade dossier captures and progression/treatment interaction regression."""

import argparse
from copy import deepcopy
import json
from math import ceil
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import arcade
from game.character import Character
from game.agent_specializations import talent_nodes_for_role
from game.management.downtime import DOWNTIME_ACTIVITIES
from game.persistence import SaveSystem
from game.progression import ALLOWED_SKILL_KEYS
from game.ui.theme.typography import set_text_size
from tools.check_squad_command_visual import fixture


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="work/character-sheet-visual")
    args = parser.parse_args()
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    window = arcade.Window(
        1672,
        941,
        "CyberCity 2085 · Operative dossier",
        visible=False,
        antialiasing=False,
    )
    gs, view = fixture()
    window.show_view(view)
    set_text_size("medium")
    view._open_hub_room("squad")
    view._open_agent_sheet(1)
    char = gs.characters[1]
    before = deepcopy(char.to_dict())
    checks = []

    def draw():
        window.switch_to()
        window.default_camera.use()
        view.on_update(1 / 60)
        view.on_draw()
        window.ctx.finish()

    def click(action, data=None):
        hit = next(
            hit
            for hit in reversed(view._modal_hits)
            if hit.action == action and (data is None or hit.data == data)
        )
        x, y = (hit.left + hit.right) / 2, (hit.bottom + hit.top) / 2
        view.on_mouse_motion(x, y, 0, 0)
        view.on_mouse_press(x, y, arcade.MOUSE_BUTTON_LEFT, 0)

    def resize(w, h):
        window.set_size(w, h)
        window.dispatch_events()
        window.flip()

    try:
        for w, h in [(1280, 720), (1672, 941), (1920, 1080), (2560, 1440)]:
            resize(w, h)
            view.dossier_page = "overview"
            draw()
            arcade.get_image(0, 0, w, h).save(output / f"dossier-overview-{w}x{h}.png")
            view.dossier_page = "skills"
            draw()
            renderer = view._character_sheet_renderer
            renderer.first_rows = {"skills": 0, "talents": 0}
            view.on_mouse_motion(0, 0, 0, 0)
            draw()
            arcade.get_image(0, 0, w, h).save(output / f"dossier-{w}x{h}.png")
            assert all(
                0 <= hit.left < hit.right <= w and 0 <= hit.bottom < hit.top <= h
                for hit in view._modal_hits
            ), (w, h)
            skills = set()
            talents = set()
            for section, seen, expected in [
                ("skills", skills, set(ALLOWED_SKILL_KEYS)),
                (
                    "talents",
                    talents,
                    {node.id for node in talent_nodes_for_role(char.role)},
                ),
            ]:
                for _ in range(12):
                    draw()
                    seen.update(
                        renderer.visible_skills
                        if section == "skills"
                        else renderer.visible_talents
                    )
                    view.on_mouse_scroll(*renderer.regions[section].center, 0, -1)
                assert seen == expected, (w, h, section, seen, expected)
            checks.append(
                {
                    "size": [w, h],
                    "skills_reached": len(skills),
                    "talents_reached": len(talents),
                }
            )
        assert (
            char.to_dict() == before
        ), "Rendering/paging must never mutate progression"
        # Disabled attributes and ranks cannot spend points.
        renderer = view._character_sheet_renderer
        renderer.first_rows = {"skills": 0, "talents": 0}
        resize(1672, 941)
        draw()
        assert not any(hit.action == "sheet_spend_stat" for hit in view._modal_hits)
        click("sheet_info", ("attribute", "agi"))
        assert char.pending_points == 0
        # Real existing mutation handlers update computed stats and rank totals.
        char.pending_points = 2
        draw()
        old_agi = char.stats.agi
        old_aim = renderer.data.derived["aim"]
        click("sheet_spend_stat", (1, "agi"))
        draw()
        assert (
            char.pending_points == 1
            and char.stats.agi == old_agi + 1
            and renderer.data.derived["aim"] == old_aim + 1
        )
        click("sheet_spend_skill_rank", (1, "firearms"))
        draw()
        assert char.pending_points == 0 and char.skills["firearms"] == 1
        assert (
            next(row for row in renderer.data.skills if row.key == "firearms").total
            == char.stats.agi + 1
        )
        char.pending_points = 1
        char.skills["firearms"] = 10
        draw()
        assert not any(
            hit.action == "sheet_spend_skill_rank" and hit.data == (1, "firearms")
            for hit in view._modal_hits
        )
        click("sheet_info", ("skill", "firearms"))
        assert char.pending_points == 1 and char.skills["firearms"] == 10
        # Tier 2 needs the game's prerequisite, not an invented level gate.
        nodes = talent_nodes_for_role(char.role)
        char.talent_points = 0
        draw()
        assert not any(hit.action == "unlock_talent" for hit in view._modal_hits)
        char.talent_points = 2
        draw()
        assert (
            next(t for t in renderer.data.talents if t.node.id == nodes[2].id).state
            == "LOCKED"
        )
        click("unlock_talent", (1, nodes[0].id))
        draw()
        assert char.talent_points == 1 and nodes[0].id in char.specializations
        assert (
            next(t for t in renderer.data.talents if t.node.id == nodes[2].id).state
            == "AVAILABLE"
        )
        click("unlock_talent", (1, nodes[2].id))
        draw()
        assert char.talent_points == 0 and nodes[2].id in char.specializations
        click("sheet_info", ("talent", nodes[0].id))
        assert char.talent_points == 0
        arcade.get_image().save(output / "dossier-upgraded.png")
        # Large text at 720p still exposes every row by keyboard and wheel.
        resize(1280, 720)
        set_text_size("large")
        draw()
        renderer.first_rows = {"skills": 0, "talents": 0}
        draw()
        arcade.get_image().save(output / "dossier-large-text.png")
        for section, expected in [("skills", 12), ("talents", len(nodes))]:
            renderer.first_rows[section] = 0
            draw()
            seen = set()
            renderer.scroll_target = section
            for _ in range(12):
                draw()
                seen.update(
                    renderer.visible_skills
                    if section == "skills"
                    else renderer.visible_talents
                )
                view.on_key_press(arcade.key.PAGEDOWN, 0)
            assert len(seen) == expected
        set_text_size("medium")
        # Different roles use their own trees; robots/power armor invent no talents.
        gs.characters.extend(
            [
                Character("Unit Rho", role="robot"),
                Character("Unit Aegis", role="power_armor"),
            ]
        )
        resize(1672, 941)
        for index in [0, 2, len(gs.characters) - 2, len(gs.characters) - 1]:
            view._open_agent_sheet(index)
            draw()
            role = gs.characters[index].role
            assert len(renderer.data.skills) == 12 and len(
                renderer.data.talents
            ) == len(talent_nodes_for_role(role))
            arcade.get_image().save(output / f"dossier-{role}.png")
        # English chrome switches without leaving French cache labels visible.
        gs.ui_language = "en"
        view._open_agent_sheet(1)
        draw()
        labels = [label for label in renderer.paint._texts.values() if label.visible]
        assert any(label.text == "SKILLS" for label in labels)
        assert not any(label.text == "COMPÉTENCES" for label in labels)
        arcade.get_image().save(output / "dossier-english.png")
        gs.ui_language = "fr"
        click("sheet_close")
        assert view.expanded_agent_sheet_index is None
        # Treatments target the displayed injured agent, including medical recovery.
        view.deployment_cursor = 1
        patient = gs.characters[1]
        patient.stats.hp = 1
        patient.recovery_turns = 3
        gs.selected_agent_names = [gs.characters[0].name]
        gs.characters[0].stats.hp = 1
        day = gs.calendar.current_day
        credits = gs.strategic_resources["credits"]
        max_hp = patient.stats.max_hp
        view.on_key_press(arcade.key.R, 0)
        assert (
            patient.stats.hp == min(max_hp, 1 + ceil(max_hp * 0.25))
            and gs.calendar.current_day == day + 1
        )
        assert (
            gs.strategic_resources["credits"] == credits and patient.recovery_turns == 2
        )
        view.on_key_press(arcade.key.H, 0)
        assert (
            patient.stats.hp == max_hp
            and gs.strategic_resources["credits"] == credits - 8
            and patient.recovery_turns == 1
        )
        assert (
            gs.characters[0].stats.hp == 1
        ), "Treatment must not heal an unrelated squad member"
        draw()
        assert len(
            [hit for hit in view._hits if hit.action == "downtime_activity"]
        ) == len(DOWNTIME_ACTIVITIES)
        arcade.get_image().save(output / "downtime-treatments.png")
        # Progression and recovered HP survive actual JSON save/load.
        snapshot = deepcopy(patient.to_dict())
        with TemporaryDirectory() as directory:
            with patch.object(
                SaveSystem,
                "slot_path",
                side_effect=lambda slot: Path(directory) / f"{slot}.json",
            ):
                view._do_save()
                view._do_load()
        assert view.game_state.characters[1].to_dict() == snapshot
        view._open_agent_sheet(1)
        draw()
        assert renderer.character.stats.hp == renderer.character.stats.max_hp
        view.on_key_press(arcade.key.ESCAPE, 0)
        assert view.expanded_agent_sheet_index is None
        report = {
            "resolutions": checks,
            "all_twelve_skills_reachable": True,
            "all_talents_reachable": True,
            "point_spending": True,
            "talent_conditions": True,
            "large_text": True,
            "roles": ["sniper", "samurai", "psi", "robot", "power_armor"],
            "healing": True,
            "persistence": True,
            "close": True,
            "english": True,
        }
        (output / "report.json").write_text(json.dumps(report, indent=2))
        print(json.dumps(report))
    finally:
        window.close()


if __name__ == "__main__":
    main()
