from hashlib import sha256
import json
from pathlib import Path

import pytest

from game.map_geometry import load_map_geometry
from game.map_terrain import build_terrain_profile
from game.combat.encounter_placement import fit_encounter


CASES=(("city_interior_safehouse.png",41,5,"6676a56d4ebc636799812ba36180ba83ba4d34c9819235631979c8f229182e33"),
       ("cybercity_inner_03_research_lab.png",32,6,"808d411affa6fdc4489a3df6fd4c6887a752b14c4bec2e86c556cc93778712d0"))


@pytest.mark.parametrize("case",CASES)
@pytest.mark.parametrize("size",((1280,720),(960,640),(1920,1000)))
def test_reviewed_interior_padding_is_blocked_and_encounters_fit(case,size):
    path=Path("assets/maps")/case[0]
    terrain=build_terrain_profile(path,*size,forced_walkable=((96,0),(0,448)))
    assert all(not terrain.is_walkable(x,0) for x in range(0,size[0],32))
    assert all(not terrain.is_walkable(0,y) for y in range(0,size[1],32))
    assert terrain.survey_sha256==sha256(path.with_suffix(".walls.json").read_bytes()).hexdigest()
    for kind in ("extract","defend","containment"):
        p=fit_encounter(terrain,[(96+i*64,64) for i in range(6)],[(1152,352+i*32) for i in range(8)],
                         [(448,320)],objective_kind=kind,breach_y=192)
        cells=(*p.allies,*p.enemies,*p.objectives)
        assert len(set(cells))==len(cells)
        assert all(terrain.is_walkable(*c) and c[0]>0 and c[1]>0 for c in cells)


def test_reviewed_safehouse_and_lab_keep_every_original_obstacle():
    for name,count,bounds,digest in CASES:
        layout=load_map_geometry(Path("assets/maps")/name)
        original=[w for w in layout["walls"] if w["kind"]!="unplayable_margin"]
        assert len(original)==count
        assert sha256(json.dumps(original,sort_keys=True,separators=(",",":")).encode()).hexdigest()==digest
        margins=[w for w in layout["walls"] if w["kind"]=="unplayable_margin"]
        assert len(margins)==bounds and all(not w["blocks_sight"] for w in margins)
