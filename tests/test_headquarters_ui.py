"""Shared HQ geometry and presentation-only transition invariants."""

from dataclasses import fields
import json
import os
from pathlib import Path
import subprocess
import sys
import pytest
from game.ui.layouts.headquarters import (
    headquarters_layout,
    headquarters_target_at,
    ROOMS,
    HQ_ART,
)
from game.ui.layouts.world_map_beacons import Rect
from game.ui.room_interaction import (
    RoomUIState,
    UIRect,
    open_room,
    close_room,
    active_room_rect,
    step_room_ui,
)


@pytest.mark.parametrize(
    "size", [(1280, 720), (1920, 1080), (2560, 1440), (1920, 1000)]
)
@pytest.mark.parametrize("legacy", [False, True])
@pytest.mark.parametrize("text_scale", [1.0, 1.3])
def test_room_edges_labels_and_footer_share_click_geometry(size, legacy, text_scale):
    w, h = size
    layout = headquarters_layout(w, h, legacy, text_scale)
    bounds = Rect(0, 0, w, h)
    assert layout.art.inside(bounds)
    assert len(layout.rooms) == len(ROOMS) == 6
    assert not any(
        layout.rooms[i].intersects(other)
        for i in range(6)
        for other in layout.rooms[i + 1 :]
    )
    for i, (room, label) in enumerate(zip(layout.rooms, layout.labels)):
        assert room.inside(layout.art) and label.inside(room)
        assert not room.intersects(layout.header) and not room.intersects(layout.footer)
        for point in [
            room.center,
            label.center,
            (room.left + 0.5, room.bottom + 0.5),
            (room.right - 0.5, room.top - 0.5),
        ]:
            assert (
                headquarters_target_at(w, h, *point, legacy, text_scale) == ROOMS[i][0]
            )
        assert (
            headquarters_target_at(
                w, h, *layout.navigation[i].center, legacy, text_scale
            )
            == ROOMS[i][0]
        )
    assert (
        headquarters_target_at(w, h, *layout.navigation[6].center, legacy, text_scale)
        == "close"
    )
    # Elevator shaft and hangar are scenery, not overlapping hidden room buttons.
    assert (
        headquarters_target_at(
            w,
            h,
            layout.art.left + layout.art.width * 0.49,
            layout.art.bottom + layout.art.height * 0.55,
            legacy,
        )
        is None
    )


def test_room_transition_uses_visual_origin_then_resets_without_campaign_state():
    state = RoomUIState("hub")
    open_room(state, 1280, 720, "research")
    room = headquarters_layout(1280, 720).rooms[4]
    state.source_rect = UIRect(
        round(room.left), round(room.bottom), round(room.width), round(room.height)
    )
    state.texture_override = object()
    assert active_room_rect(state, 1280, 720)[1] == state.source_rect
    step_room_ui(state, 0.28)
    assert (
        state.expansion == 1
        and active_room_rect(state, 1280, 720)[1].width > room.width
    )
    close_room(state)
    assert state.source_rect is None and state.texture_override is None
    open_room(state, 1280, 720, "command")
    assert state.source_rect is None and state.texture_override is None


def test_hq_assets_preserve_original_resource():
    from game.ui.facility import BASE_BACKDROP_ASSET

    assert Path(HQ_ART).is_file() and Path(BASE_BACKDROP_ASSET).is_file()
    assert HQ_ART != BASE_BACKDROP_ASSET


@pytest.mark.skipif(not os.environ.get("DISPLAY"), reason="Native capture requires X11")
def test_actual_headquarters_controls_and_immutable_rendering(tmp_path):
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "tools.check_headquarters_visual",
            "--output",
            str(tmp_path),
        ],
        capture_output=True,
        text=True,
        timeout=150,
        env={**os.environ, "ALSOFT_DRIVERS": "null"},
    )
    assert result.returncode == 0, result.stdout + result.stderr
    report = json.loads((tmp_path / "report.json").read_text())
    assert len(report["departments"]) == 6 and report["read_only_rendering"]
    assert (
        report["mouse_footer_keyboard"]
        and report["live_resources"]
        and report["hover_transition"]
    )
    assert (
        report["legacy_fallback"]
        and report["reduced_motion"]
        and report["return_to_title"]
    )
