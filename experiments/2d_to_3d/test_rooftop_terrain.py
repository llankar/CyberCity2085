import json

import pytest
from shapely import union_all
from shapely.geometry import LineString, Polygon

from rooftop_terrain import MAPS, ROOFTOPS, terrain


@pytest.mark.parametrize("map_name", sorted(ROOFTOPS))
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
