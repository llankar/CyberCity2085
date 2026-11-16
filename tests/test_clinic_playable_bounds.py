"""Reviewed building bounds exclude exterior padding without erasing obstacles."""

from hashlib import sha256
import json
from pathlib import Path

import pytest

from game.combat.encounter_placement import fit_encounter
from game.map_geometry import load_map_geometry
from game.map_terrain import build_terrain_profile


NAMES = ("wasteland_inner_03_ruined_clinic.png", "wasteland_inner_08_ruined_clinic.png")


@pytest.mark.parametrize("name", NAMES)
@pytest.mark.parametrize("size", [(1280, 720), (960, 640), (1920, 1000)])
def test_clinic_exterior_bottom_and_west_padding_are_not_walkable(name, size):
    path = Path("assets/maps") / name
    profile = build_terrain_profile(str(path), *size, forced_walkable=((160, 0),))
    assert all(not profile.is_walkable(x, 0) for x in range(0, size[0], 32))
    assert all(not profile.is_walkable(0, y) for y in range(0, size[1], 32))
    assert profile.survey_sha256 == sha256(path.with_suffix(".walls.json").read_bytes()).hexdigest()
    for kind in ("extract", "defend", "containment"):
        placed = fit_encounter(profile, [(96+i*64, 64) for i in range(6)],
                                [(1152, 352+i*32) for i in range(8)], [(448, 320), (320, 224)],
                                objective_kind=kind, breach_y=192)
        assert all(profile.is_walkable(*point) for point in (*placed.allies, *placed.enemies, *placed.objectives))
        assert all(y > 0 and x > 0 for x, y in (*placed.allies, *placed.enemies))


def test_boundary_pass_preserves_every_preexisting_clinic_obstacle():
    # Golden scope guard: this pass may add margins, never erase the 34 reviewed objects.
    for name in NAMES:
        geometry = load_map_geometry(Path("assets/maps") / name)
        original = [wall for wall in geometry["walls"] if wall["kind"] != "unplayable_margin"]
        assert len(original) == 34
        assert sha256(json.dumps(original, sort_keys=True, separators=(",", ":")).encode()).hexdigest() == "6ec831a569da7116828784a14eba2ef87014d626e92cd47c5c1fea7e2837db2b"
        margins = [wall for wall in geometry["walls"] if wall["kind"] == "unplayable_margin"]
        assert len(margins) == 4 and all(not wall["blocks_sight"] for wall in margins)
    first, second = (load_map_geometry(Path("assets/maps") / name) for name in NAMES)
    assert first["walls"] == second["walls"]


def test_reviewed_central_floor_remains_available_and_top_padding_is_excluded():
    profile = build_terrain_profile("assets/maps/"+NAMES[0], 1280, 720)
    assert all(profile.is_walkable(*cell) for cell in ((576, 384), (640, 352), (704, 320), (544, 320)))
    assert not profile.is_walkable(640, 704)
