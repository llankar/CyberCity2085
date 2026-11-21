import importlib.util
from pathlib import Path
import sys

import pytest
from PIL import Image, ImageDraw


MODULE_PATH = Path(__file__).parents[1] / "tools" / "art" / "repack_directional_rows.py"
sys.path.insert(0, str(MODULE_PATH.parent))
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


def test_odd_height_is_supported_when_middle_separator_is_clear():
    source = Image.new("RGBA", (400, 161))
    source.alpha_composite(_row(), (0, 0))
    source.alpha_composite(_row(), (0, 81))
    lead, follow = repack.repack_two_rows(source)
    assert lead.size == follow.size


def test_rejects_opaque_middle_separator():
    source = Image.new("RGBA", (400, 160))
    source.alpha_composite(_row(), (0, 0))
    source.alpha_composite(_row(), (0, 80))
    ImageDraw.Draw(source).rectangle((0, 79, 399, 81), fill=(255, 0, 0, 255))
    with pytest.raises(ValueError, match="middle separator"):
        repack.repack_two_rows(source)


def test_reviewed_small_component_cleanup_removes_detached_speck():
    row = _row()
    row.putpixel((45, 5), (255, 0, 0, 255))
    output = repack.repack_row(row, clean_small_components=True)
    baseline = repack.repack_row(_row(), clean_small_components=True)
    assert output.tobytes() == baseline.tobytes()


def test_2d_component_fallback_handles_overlapping_x_projections():
    row = Image.new("RGBA", (400, 100))
    draw = ImageDraw.Draw(row)
    for index in range(8):
        left = index * 50 + 5
        draw.rectangle((left, 10, left + 39, 39), fill=(80, 90, 100, 255))
        draw.rectangle((left + 10, 60, left + 49, 89), fill=(80, 90, 100, 255))
        draw.rectangle((left + 20, 35, left + 29, 64), fill=(80, 90, 100, 255))
    output = repack.repack_row(row)
    assert output.width % 8 == 0
    assert all(
        output.crop((index * output.width // 8, 0, (index + 1) * output.width // 8, output.height))
        .getchannel("A")
        .getbbox()
        for index in range(8)
    )
