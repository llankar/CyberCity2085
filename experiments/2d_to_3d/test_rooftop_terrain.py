import json
import math
import struct

import pytest
from shapely import union_all
from shapely.geometry import LineString, Point, Polygon

from rooftop_terrain import FLOODED_AVENUE, MAPS, OUTPUT, ROOFTOPS, WATERFRONTS, terrain


@pytest.mark.parametrize("map_name", sorted(ROOFTOPS | WATERFRONTS))
def test_rooftop_deck_has_no_faces_across_surveyed_voids(map_name):
    survey = json.loads((MAPS / f"{map_name}.wall-traces.json").read_text())
    geometry = terrain(survey)
    deck = union_all([Polygon(triangle) for triangle in geometry["deck"]])
    street = union_all([Polygon(triangle) for triangle in geometry["street"]])
    expected = union_all([Polygon(row["polygon"]) for row in survey["walls"]
                          if row.get("kind") == "water"])
    assert street.symmetric_difference(expected).area < 1e-7
    assert deck.intersection(street).area < 1e-7
    width, height = survey["canvas_size"]
    assert deck.area + street.area == pytest.approx(width * height)
    walls = union_all([LineString(edge) for edge in geometry["edges"]])
    assert walls.length == pytest.approx(deck.boundary.intersection(street.boundary).length)
    for (ax, ay), (bx, by) in geometry["edges"]:
        dx, dy = bx-ax, by-ay
        length = math.hypot(dx, dy)
        assert street.contains(Point((ax+bx)/2-.001*dy/length, (ay+by)/2+.001*dx/length))


@pytest.mark.parametrize("map_name", sorted(ROOFTOPS | WATERFRONTS | {FLOODED_AVENUE}))
def test_native_export_preserves_terrain_levels(map_name):
    path = OUTPUT / map_name / "environment.glb"
    if not path.is_file():
        pytest.skip("Build the rooftop environments on E: first")
    with path.open("rb") as glb:
        size = struct.unpack("<4sIII4s", glb.read(20))[3]
        data = json.loads(glb.read(size))
    nodes = {node["name"]: node for node in data["nodes"]}
    if map_name in WATERFRONTS:
        deck, lower, boundary = "Waterfront quay deck", "Waterfront basin surface", "Waterfront quay retaining walls"
        depth = -1.35
        assert any(name.startswith("Quay rubber fender") for name in nodes)
        assert any(name.startswith("Quay steel coping") for name in nodes)
    elif map_name == FLOODED_AVENUE:
        deck, lower, boundary = "Flooded avenue sidewalk", "Flooded avenue water surface", "Flooded avenue curb edges"
        depth = -.075
        assert not any(name.startswith("Quay rubber fender") for name in nodes)
        assert not any(name.startswith("Quay steel coping") for name in nodes)
    else:
        deck, lower, boundary = "Rooftop deck", "Rooftop street", "Rooftop canyon retaining walls"
        depth = -3.6
    for name, low, high in ((deck,-.025,-.025), (lower,depth,depth), (boundary,depth,-.025)):
        primitives = data["meshes"][nodes[name]["mesh"]]["primitives"]
        positions = [data["accessors"][part["attributes"]["POSITION"]] for part in primitives]
        assert min(accessor["min"][1] for accessor in positions) == pytest.approx(low)
        assert max(accessor["max"][1] for accessor in positions) == pytest.approx(high)
    survey = json.loads((MAPS / f"{map_name}.wall-traces.json").read_text())
    for trace in survey["walls"]:
        identifier = trace["id"]
        if "points" in trace and map_name in ROOFTOPS:
            parts = [data["nodes"][index]["name"] for index in nodes[f"Occludable_{identifier}"]["children"]]
            assert sum("parapet body" in name for name in parts) == len(trace["points"])-1
            assert sum("coping" in name for name in parts) == len(trace["points"])-1
        if trace.get("kind") == "water":
            assert f"Occludable_{identifier}" not in nodes
