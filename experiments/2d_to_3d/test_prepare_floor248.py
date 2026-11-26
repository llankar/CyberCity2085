from PIL import Image

from prepare_floor248 import prepare


def test_open_guardrail_mask_preserves_road_between_segments():
    original = Image.new("RGB", (100, 100), "white")
    survey = {
        "canvas_size": [50, 50],
        "walls": [{"id": "ramp_guardrail", "points": [[5, 5], [5, 30], [40, 30]], "width": 3}],
    }
    _, mask = prepare(original, survey)

    assert mask[35, 10] == 255
    assert mask[60, 40] == 255
    assert mask[35, 40] == 0
    assert mask[15, 75] == 0


def test_water_polygon_is_preserved_as_ground_art():
    original = Image.new("RGB", (100, 100), "blue")
    survey = {
        "canvas_size": [100, 100],
        "walls": [
            {"id": "basin", "kind": "water", "polygon": [[0, 0], [42, 0], [42, 62], [0, 62]]},
            {"id": "container", "rect": [58, 20, 78, 36]},
        ],
    }
    repaired, mask = prepare(original, survey)

    assert not mask[:, :43].any()
    assert mask[28, 68] == 255
    assert repaired.crop((0, 0, 43, 100)).tobytes() == original.crop((0, 0, 43, 100)).tobytes()


def test_side_wall_mask_requires_explicit_replacement():
    original = Image.new("RGB", (40, 40), "white")
    survey = {
        "canvas_size": [40, 40],
        "walls": [{"id": "west_wall", "rect": [0, 5, 4, 35]}],
    }
    _, retained = prepare(original, survey)
    _, replaced = prepare(original, survey, include_side_walls=True)

    assert not retained.any()
    assert replaced[15, 2] == 255
    assert replaced[15, 5] == 0
