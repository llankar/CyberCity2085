import sys
from pathlib import Path

import pytest


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools" / "art"))
from import_directional_clips import sheet_directions


def test_sheet_order_preserves_default_and_maps_reviewed_pairs():
    assert sheet_directions({}, 4, 4) == [4, 5, 6, 7]
    order = [2, 1, 0, 7, 6, 5, 4, 3]
    assert sheet_directions({"direction_indices": order}, 8) == order


@pytest.mark.parametrize("order", [[0, 0, 1, 2], [0, 1, 2, 8], [0, 1, 2], [0, 1, 2, True]])
def test_sheet_order_rejects_invalid_facings(order):
    with pytest.raises(ValueError, match="distinct engine facings"):
        sheet_directions({"direction_indices": order}, 4)
