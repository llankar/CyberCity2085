"""Responsive briefing geometry, lossless content and real Arcade interactions."""

from dataclasses import fields
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace
import json
import os
import subprocess
import sys
import pytest
from game.character import Character
from game.gamestate import GameState
from game.consequences import Consequence
from game.management.spec_ops_assets import CombatRobot, PowerArmorSuit
from game.ui.layouts.mission_briefing import briefing_layout
from game.ui.layouts.world_map_beacons import Rect
from game.ui.screens.mission_briefing_view import build_mission_briefing_facts


@pytest.mark.parametrize("size", [(1280, 720), (1920, 1080), (2560, 1440)])
def test_all_sections_are_disjoint_and_inside_the_window(size):
    layout = briefing_layout(*size)
    bounds = Rect(0, 0, *size)
    rectangles = [
        getattr(layout, f.name)
        for f in fields(layout)
        if isinstance(getattr(layout, f.name), Rect)
    ]
    assert all(r.width > 0 and r.height > 0 and r.inside(bounds) for r in rectangles)
    for i, r in enumerate(rectangles):
        assert not any(r.intersects(other) for other in rectangles[i + 1 :])
    # The actual tactical preview is materially larger than the former 200×112.
    assert layout.scene.width * 0.45 > 200


class MeasuredPainter:
    def fit(self, text, width, size, bold):
        return text if len(text) <= width else text[: max(0, int(width) - 1)] + "…"


def test_wrapping_never_discards_tail_complications_or_long_tokens():
    from game.ui.components.briefing_widgets import wrapped_lines

    source = [
        "Full details of the final complication.",
        "averylongidentifierwithoutspaces",
        "Success and failure remain readable.",
    ]
    lines = wrapped_lines(MeasuredPainter(), source, 9, 13)
    assert "".join("".join(lines).split()) == "".join("".join(source).split())
    assert all(len(line) <= 9 for line in lines)


def test_content_preserves_every_consequence_tag_and_temporary_scar():
    from game.ui.components.briefing_content import briefing_lines

    char = Character("Vera", stress=52)
    gs = GameState(characters=[char], selected_agent_names=["Vera"])
    mission = gs.mission_templates[0]
    mission.success_consequences = [
        Consequence(narrative_text=f"Success {i}") for i in range(20)
    ]
    mission.failure_consequences = [
        Consequence(narrative_text=f"Failure {i}") for i in range(20)
    ]
    mission.tags = ["civilian_rescue"]
    mission.emotional_impact_hint = {
        "short_text": "Summary",
        "text": "The complete emotional briefing must remain available.",
    }
    char.temporary_scars = [
        {
            "title": "Nights of Sirens",
            "days_remaining": 3,
            "tone": "vigilant",
            "tags": ["injury"],
        }
    ]
    before = deepcopy(char.to_dict())
    facts = build_mission_briefing_facts(gs, mission)
    lines = briefing_lines(gs, mission, facts)
    assert len(lines["success"]) == 20 and lines["success"][-1] == "Success 19"
    assert len(lines["failure"]) == 20 and lines["failure"][-1] == "Failure 19"
    assert any("Nights of Sirens" in line for line in lines["impact"])
    assert any("Civilian Rescue" in line for line in lines["impact"])
    assert "The complete emotional briefing must remain available." in lines["impact"]
    assert char.to_dict() == before


def test_art_varies_with_real_mission_context_and_support_type():
    from game.ui.components.briefing_content import mission_art_path, support_art

    base = dict(id="a", district="Chrome", battle_environment="city")
    paths = {
        mission_art_path(SimpleNamespace(**base, title=title))
        for title in [
            "Extract survivors",
            "Medical rescue",
            "Data theft",
            "Market siege",
        ]
    }
    assert len(paths) > 1 and all(Path(path).is_file() for path in paths)
    assert "power_armor" in support_art(PowerArmorSuit(id="mantis", name="Mantis"))
    assert "robot" in support_art(CombatRobot(id="k9", name="K9"))
    assert support_art(SimpleNamespace(asset_type="unknown", id="none")) is None


@pytest.mark.skipif(
    not os.environ.get("DISPLAY"), reason="Actual Arcade capture requires X11"
)
def test_native_briefing_controls_overflow_and_campaign_integrity(tmp_path):
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "tools.check_mission_briefing_visual",
            "--output",
            str(tmp_path),
        ],
        capture_output=True,
        text=True,
        timeout=120,
        env={**os.environ, "ALSOFT_DRIVERS": "null"},
    )
    assert result.returncode == 0, result.stdout + result.stderr
    report = json.loads((tmp_path / "report.json").read_text())
    assert all(
        report[k]
        for k in [
            "read_only",
            "controls",
            "map_inspection",
            "overflow",
            "empty",
            "language",
        ]
    )
