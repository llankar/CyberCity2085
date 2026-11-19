"""Regression checks for Godot movement highlight density."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BATTLEFIELD_SCRIPT = ROOT / "godot" / "combat_missions_ui" / "scripts" / "battlefield.gd"
COMBAT_UI_SCRIPT = ROOT / "godot" / "combat_missions_ui" / "scripts" / "combat_mission_ui.gd"


def _constant(source: str, name: str) -> float:
    match = re.search(rf"const {name} := ([0-9.]+)", source)
    assert match, f"missing {name}"
    return float(match.group(1))


def test_godot_move_highlights_keep_size_but_tighten_spacing() -> None:
    source = BATTLEFIELD_SCRIPT.read_text(encoding="utf-8")

    size_scale = _constant(source, "MOVE_RANGE_SCALE")
    step_scale = _constant(source, "MOVE_RANGE_STEP_SCALE")

    assert size_scale == 0.50
    assert size_scale < step_scale < 1.0
    assert "var corners := _iso_corners_inner(cell, MOVE_RANGE_SCALE)" in source
    assert "preview_center := anchor_center + (actual_center - anchor_center) * MOVE_RANGE_STEP_SCALE" in source
    assert "result.append(c + delta)" in source
    assert "var c := _move_highlight_corners(cell)" in source


def test_godot_move_highlights_are_anchored_to_active_unit() -> None:
    battlefield = BATTLEFIELD_SCRIPT.read_text(encoding="utf-8")
    combat_ui = COMBAT_UI_SCRIPT.read_text(encoding="utf-8")

    assert "func show_move_range(cells: Array[Vector2i], anchor_cell: Vector2i = Vector2i(-1, -1))" in battlefield
    assert "move_range_anchor  = anchor_cell" in battlefield
    assert "move_range_anchor  = Vector2i(-1, -1)" in battlefield
    assert "_battlefield.show_move_range(_battlefield.reachable_cells(origin, budget), origin)" in combat_ui
