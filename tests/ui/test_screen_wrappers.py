"""Regression tests for incremental UI screen-module migration."""

from game.ui.command_center import build_command_center_layout
from game.ui.dashboard import build_resource_summary_line
from game.ui.facility import build_facility_rooms
from game.ui.mission_board import risk_label
from game.ui.research_lab import build_research_lab_lines
from game.ui.screens.command_center import build_action_strip


def test_compat_wrappers_still_expose_public_helpers() -> None:
    panels = build_command_center_layout(1280, 720, "corp")
    assert panels and panels[0].key == "primary"
    assert build_resource_summary_line({"credits": 10}).startswith("Credits")
    assert build_facility_rooms(1400, 850)
    assert risk_label(4) == "severe"
    assert build_action_strip(["A", "B"]) == "A  >  B"


class _DummyState:
    strategic_resources = {"intel": 2}
    available_funds = 30
    active_research = []
    completed_research = []
    research_unlock_flags = []


def test_research_wrapper_uses_screen_module() -> None:
    lines = build_research_lab_lines(_DummyState())
    assert any("Funds" in line for line in lines)
