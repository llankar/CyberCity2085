"""Dossier presentation must project real progression and expose every grid item."""

from copy import deepcopy
import json
import os
from pathlib import Path
import subprocess
import sys
import pytest
from game.character import Character
from game.recruitment import create_character
from game.agent_specializations import talent_nodes_for_role, unlock_talent
from game.agents.sheet_calculations import compute_derived_stats
from game.ui.components.character_sheet_model import build_character_sheet_data
from game.ui.layouts.character_sheet import character_sheet_layout, paged_grid
from game.ui.layouts.world_map_beacons import Rect
from game.progression import ALLOWED_SKILL_KEYS


@pytest.mark.parametrize("role", ["samurai", "sniper", "psi", "robot", "power_armor"])
def test_model_is_read_only_and_role_driven(role):
    char = create_character("Operative", role)
    before = deepcopy(char.to_dict())
    data = build_character_sheet_data(char)
    assert char.to_dict() == before
    assert [row.key for row in data.skills] == list(ALLOWED_SKILL_KEYS)
    assert len(data.talents) == len(talent_nodes_for_role(role))
    assert data.derived == compute_derived_stats(
        data.attributes,
        char.skills,
        char.loadout.total_stat_bonuses(),
        data.stress_state,
    )


def test_skill_totals_rank_caps_stress_and_xp_match_actual_game():
    char = Character("Analyst", role="sniper")
    char.stats.level = 2
    char.stats.xp = 399
    char.stats.agi = 6
    char.skills["firearms"] = 3
    char.pending_points = 2
    char.stress = 88
    data = build_character_sheet_data(char)
    firearms = next(row for row in data.skills if row.key == "firearms")
    assert firearms.total == 9 and firearms.attribute_value == 6 and firearms.can_spend
    assert data.xp_target == 400 and data.stress_state == "breaking"
    char.skills["firearms"] = 10
    assert not next(
        row for row in build_character_sheet_data(char).skills if row.key == "firearms"
    ).can_spend
    char.gain_xp(1)
    assert char.stats.level == 3 and build_character_sheet_data(char).xp_target == 900


def test_talents_use_real_prerequisites_points_and_ownership():
    char = create_character("Viewer", "sniper")
    char.talent_points = 2
    nodes = talent_nodes_for_role("sniper")
    tree = {item.node.id: item for item in build_character_sheet_data(char).talents}
    assert tree[nodes[0].id].state == "AVAILABLE"
    assert tree[nodes[2].id].state == "LOCKED" and tree[nodes[2].id].missing_names
    assert unlock_talent(char, nodes[0].id)
    tree = {item.node.id: item for item in build_character_sheet_data(char).talents}
    assert tree[nodes[0].id].state == "UNLOCKED"
    assert tree[nodes[2].id].state == "AVAILABLE"  # No invented level/tier gate.
    char.talent_points = 0
    assert next(
        item
        for item in build_character_sheet_data(char).talents
        if item.node.id == nodes[2].id
    ).needs_point


@pytest.mark.parametrize("size", [(1280, 720), (1672, 941), (1920, 1080), (2560, 1440)])
def test_responsive_grids_expose_every_skill_and_talent(size):
    layout = character_sheet_layout(*size)
    assert layout.identity.width > 300 and layout.attributes.width > 300
    assert not layout.identity.intersects(layout.attributes)
    for panel, count, columns, minimum in [
        (layout.skills, 12, 2 if size[0] == 1280 else 3, 132),
        (layout.talents, 5, 2 if size[0] == 1280 else 3, 128),
    ]:
        bounds = Rect(
            panel.left + 12, panel.bottom + 12, panel.right - 12, panel.top - 60
        )
        seen = set()
        initial = paged_grid(bounds, count, columns, minimum, 9)
        for first in range(initial.max_first_row + 1):
            grid = paged_grid(bounds, count, columns, minimum, 9, first)
            seen.update(index for index, _ in grid.cards)
            assert all(rect.inside(bounds) for _, rect in grid.cards)
        assert seen == set(range(count))


@pytest.mark.skipif(
    sys.platform != "linux" or not os.environ.get("DISPLAY"),
    reason="Real Arcade capture requires X11",
)
def test_live_dossier_and_treatments(tmp_path):
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "tools.check_character_sheet_visual",
            "--output",
            str(tmp_path),
        ],
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True,
        text=True,
        timeout=120,
        env={**os.environ, "ALSOFT_DRIVERS": "null"},
    )
    assert result.returncode == 0, result.stdout + result.stderr
    report = json.loads((tmp_path / "report.json").read_text())
    assert report["all_twelve_skills_reachable"] and report["all_talents_reachable"]
    assert (
        report["point_spending"]
        and report["talent_conditions"]
        and report["healing"]
        and report["persistence"]
    )
