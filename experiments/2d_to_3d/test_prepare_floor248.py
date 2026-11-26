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
