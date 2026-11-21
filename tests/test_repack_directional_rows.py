import importlib.util
from pathlib import Path

import pytest
from PIL import Image, ImageDraw


MODULE_PATH = Path(__file__).parents[1] / "tools" / "art" / "repack_directional_rows.py"
SPEC = importlib.util.spec_from_file_location("repack_directional_rows", MODULE_PATH)
repack = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(repack)


def _row(count=8, bridge_alpha=0):
    image = Image.new("RGBA", (count * 50, 80))
    draw = ImageDraw.Draw(image)
    for index in range(count):
        left = index * 50 + 10
        draw.rectangle((left, 10, left + 29, 69), fill=(index * 20, 80, 120, 255))
        if bridge_alpha and index < count - 1:
            draw.line((left + 30, 40, left + 49, 40), fill=(10, 10, 10, bridge_alpha), width=1)
    return image


def test_repack_row_contains_eight_complete_centered_sprites():
    output = repack.repack_row(_row())
    assert output.width % 8 == 0
    cell_width = output.width // 8
    for index in range(8):
        cell = output.crop((index * cell_width, 0, (index + 1) * cell_width, output.height))
        assert cell.getchannel("A").getbbox()
        assert cell.getchannel("A").getbbox()[3] == output.height - 16


def test_adaptive_threshold_ignores_weak_alpha_bridges():
    runs, threshold = repack.find_eight_runs(_row(bridge_alpha=15))
    assert len(runs) == 8
    assert threshold == 16


def test_rejects_row_without_eight_substantial_silhouettes():
    with pytest.raises(ValueError, match="exactly 8"):
        repack.repack_row(_row(count=7))


def test_two_row_source_writes_distinct_phases():
    top = _row()
    bottom = _row()
    bottom.putpixel((10, 10), (255, 0, 0, 255))
    source = Image.new("RGBA", (400, 160))
    source.alpha_composite(top, (0, 0))
    source.alpha_composite(bottom, (0, 80))
    lead, follow = repack.repack_two_rows(source)
    assert lead.size == follow.size
    assert lead.tobytes() != follow.tobytes()
