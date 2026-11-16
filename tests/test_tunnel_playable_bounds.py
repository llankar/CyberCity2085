from hashlib import sha256
import json
from pathlib import Path

import pytest

from game.map_geometry import load_map_geometry
from game.map_terrain import build_terrain_profile
from game.combat.encounter_placement import fit_encounter


NAMES=("wasteland_inner_02_collapsed_tunnel.png","wasteland_inner_07_collapsed_tunnel.png")


@pytest.mark.parametrize("name",NAMES)
@pytest.mark.parametrize("size",((1280,720),(960,640),(1920,1000)))
def test_tunnel_padding_blocks_forced_anchors_and_encounters_fit(name,size):
    path=Path("assets/maps")/name
    terrain=build_terrain_profile(path,*size,forced_walkable=((1088,0),(0,0)))
    assert all(not terrain.is_walkable(x,0) for x in range(0,size[0],32))
    assert all(not terrain.is_walkable(0,y) for y in range(0,size[1],32))
    assert terrain.survey_sha256==sha256(path.with_suffix(".walls.json").read_bytes()).hexdigest()
    for kind in ("extract","defend","containment"):
        placed=fit_encounter(terrain,[(96+i*64,64) for i in range(6)],[(1152,352+i*32) for i in range(8)],
                             [(448,320)],objective_kind=kind,breach_y=192)
        cells=(*placed.allies,*placed.enemies,*placed.objectives)
        assert len(set(cells))==len(cells)
        assert all(terrain.is_walkable(*c) and c[0]>0 and c[1]>0 for c in cells)


def test_tunnel_original_objects_unchanged_and_exact_duplicates_preserved():
    layouts=[load_map_geometry(Path("assets/maps")/name) for name in NAMES]
    assert layouts[0]["walls"]==layouts[1]["walls"]
    for layout in layouts:
        original=[w for w in layout["walls"] if w["kind"]!="unplayable_margin"]
        assert len(original)==23
        assert sha256(json.dumps(original,sort_keys=True,separators=(",",":")).encode()).hexdigest()=="d170d5ec24df186ec4ded53438ab4b0f9d21ac4cfc17c1f4cc2a994f7cd7959c"
        margins=[w for w in layout["walls"] if w["kind"]=="unplayable_margin"]
        assert len(margins)==6 and all(not w["blocks_sight"] for w in margins)
