"""Layout/data contracts plus optional real Arcade rendering and interactions."""

import json
import os
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace
import pytest
from game.i18n import t
from game.ui.layouts.squad_command import squad_command_layout, visible_roster_range


def test_squad_equipment_reuses_inventory_item_art_for_every_catalog_item():
    from game.management.equipment import default_equipment_catalog
    from game.ui.components.equipment_art import equipment_art_path

    for slot, items in default_equipment_catalog().items():
        for item in items:
            path = equipment_art_path(item, slot)
            assert path == f"assets/ui/inventory/items/{item.id}.png"
            assert Path(path).is_file()


def test_squad_equipment_art_falls_back_for_an_empty_slot():
    from game.ui.components.equipment_art import equipment_art_path

    assert equipment_art_path(None, "sidearm") == "assets/ui/inventory/sidearm.png"


@pytest.mark.parametrize(
    "width,height", [(1280, 720), (1672, 941), (1920, 1080), (2560, 1440)]
)
def test_columns_are_readable_and_disjoint_at_supported_resolutions(width, height):
    layout = squad_command_layout(width, height)
    assert layout.roster.width >= 300
    assert layout.equipment.width > layout.roster.width
    assert layout.mission.width >= 400
    for rect in layout.columns:
        assert rect.bottom > layout.footer.top
        assert rect.top < layout.header.bottom
        assert 0 <= rect.left < rect.right <= width
    assert not layout.roster.intersects(layout.equipment)
    assert not layout.equipment.intersects(layout.mission)


def test_roster_pagination_keeps_all_members_accessible():
    assert list(visible_roster_range(0, 0, 0)) == []
    assert list(visible_roster_range(9, 0, 0)) == list(range(5))
    assert list(visible_roster_range(9, 8, 99)) == list(range(4, 9))


@pytest.mark.parametrize(
    "language,expected", [("fr", "ACTIVE MISSION"), ("en", "ACTIVE MISSION")]
)
def test_squad_chrome_obeys_campaign_language(language, expected):
    assert t("squad.active_mission", language) == expected
    for slot in (
        "primary_weapon",
        "sidearm",
        "armor",
        "utility_item",
        "psi_focus",
        "special_gear",
    ):
        assert not t("squad.slot." + slot, language).startswith("squad.")
    for key in ("shore_leave", "sim_drills", "group_therapy"):
        assert not t("squad.activity." + key, language).startswith("squad.")


@pytest.mark.skipif(
    sys.platform != "linux" or not os.environ.get("DISPLAY"),
    reason="Real Arcade framebuffers require X11",
)
def test_live_squad_command_capture_and_interactions(tmp_path):
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "tools.check_squad_command_visual",
            "--output",
            str(tmp_path),
        ],
        cwd=Path(__file__).resolve().parents[1],
        env={**os.environ, "ALSOFT_DRIVERS": "null"},
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    report = json.loads((tmp_path / "report.json").read_text())
    assert len(report["resolutions"]) == 4
    assert all(
        check["all_equipment_and_activities_visible"] for check in report["resolutions"]
    )
    for feature in (
        "equipment",
        "stat_upgrade",
        "recruitment",
        "roster_scroll",
        "downtime",
        "save_load",
        "navigation",
        "english",
        "empty_roster",
    ):
        assert report[feature]


def test_mission_art_uses_real_context_and_is_deterministic():
    from game.ui.components.squad_mission import mission_art_path

    city = SimpleNamespace(
        id="data_context",
        title="Data cache",
        battle_environment="city",
        district="Chrome Warrens",
    )
    assert "city_07_data_vault" in mission_art_path(city)
    wastes = SimpleNamespace(
        id="other", title="Patrol", battle_environment="wasteland", district="Badlands"
    )
    assert "/wasteland/" in mission_art_path(wastes).replace("\\", "/")
    assert mission_art_path(wastes) == mission_art_path(wastes)
    assert Path(mission_art_path(wastes)).is_file()


def test_modal_chrome_localization_preserves_identity_and_numbers():
    from game.ui.components.squad_copy import localized_squad_copy

    assert localized_squad_copy("RECRUITMENT WINDOW", "fr") == "RECRUITMENT WINDOW"
    assert localized_squad_copy("ATTRIBUTES", "en") == "ATTRIBUTES"
    assert (
        localized_squad_copy("ROOK | SAMURAI | LEVEL 12", "fr")
        == "ROOK | SAMURAI | LEVEL 12"
    )


def test_agent_card_hint_matches_double_click_squad_toggle():
    assert t("squad.double_click", "en") == "Double-click: toggle squad"


def test_feedback_keeps_result_without_technical_action_fields():
    from game.ui.components.squad_copy import notification_summary

    assert (
        notification_summary(
            "[SUCCESS] Action: stat_upgrade | Result: completed | Impact: Rook +1 STR | Next: Proceed"
        )
        == "Rook +1 STR"
    )
    assert notification_summary("[WARNING] Not enough credits") == "Not enough credits"
