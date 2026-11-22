import json

import pytest
from PIL import Image

from tools.art.build_map_art_review_sheets import build


@pytest.mark.parametrize("resolution", [(1280, 720), (1920, 1080), (2560, 1440)])
def test_review_sheet_preserves_bottom_of_each_capture(tmp_path, resolution):
    captures = tmp_path / "captures"
    captures.mkdir()
    source = captures / "source.png"
    Image.new("RGB", resolution, (255, 0, 255)).save(source)
    rows = [{"map": f"map-{index:03d}.png"} for index in range(122)]
    width, height = resolution
    for row in rows:
        (captures / row["map"].replace(".png", f"-{width}x{height}.png")).hardlink_to(source)
    (captures / "native-report.json").write_text(json.dumps(rows), encoding="utf-8")

    output = tmp_path / "sheets"
    manifest = build(captures, output)

    assert len(manifest["pages"]) == 21
    with Image.open(output / "art-review-01.jpg") as sheet:
        for y in (560, 1128, 1696):
            for x in (480, 1440):
                red, green, blue = sheet.getpixel((x, y))
                assert red > 240 and green < 15 and blue > 240
