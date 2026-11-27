import json
import math

import pytest
from shapely import union_all
from shapely.geometry import LineString, Point, Polygon

from rooftop_terrain import MAPS, ROOFTOPS, WATERFRONTS, terrain


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


@pytest.mark.parametrize("map_name", sorted(ROOFTOPS))
def test_rooftop_native_export_preserves_deck_and_canyon_levels(map_name):
    import struct

    from rooftop_terrain import OUTPUT

    path = OUTPUT / map_name / "environment.glb"
    if not path.is_file():
        pytest.skip("Build the rooftop environments on E: first")
    with path.open("rb") as glb:
        size = struct.unpack("<4sIII4s", glb.read(20))[3]
        data = json.loads(glb.read(size))
    nodes = {node["name"]: node for node in data["nodes"]}
    for name, low, high in (
        ("Rooftop deck", -.025, -.025),
        ("Rooftop street", -3.6, -3.6),
        ("Rooftop canyon retaining walls", -3.6, -.025),
    ):
        primitives = data["meshes"][nodes[name]["mesh"]]["primitives"]
        positions = [data["accessors"][part["attributes"]["POSITION"]] for part in primitives]
        assert min(accessor["min"][1] for accessor in positions) == pytest.approx(low)
        assert max(accessor["max"][1] for accessor in positions) == pytest.approx(high)
    survey = json.loads((MAPS / f"{map_name}.wall-traces.json").read_text())
    for trace in survey["walls"]:
        identifier = trace["id"]
        if "points" in trace:
            parts = [data["nodes"][index]["name"] for index in nodes[f"Occludable_{identifier}"]["children"]]
            assert sum("parapet body" in name for name in parts) == len(trace["points"])-1
            assert sum("coping" in name for name in parts) == len(trace["points"])-1
        if trace.get("kind") == "water":
            assert f"Occludable_{identifier}" not in nodes
