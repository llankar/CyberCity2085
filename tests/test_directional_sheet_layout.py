import sys
from pathlib import Path

import pytest
from PIL import Image


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools" / "art"))
import import_directional_clips as importer
from import_directional_clips import sheet_directions


def test_sheet_order_preserves_default_and_maps_reviewed_pairs():
    assert sheet_directions({}, 4, 4) == [4, 5, 6, 7]
    order = [2, 1, 0, 7, 6, 5, 4, 3]
    assert sheet_directions({"direction_indices": order}, 8) == order


@pytest.mark.parametrize("order", [[0, 0, 1, 2], [0, 1, 2, 8], [0, 1, 2], [0, 1, 2, True]])
def test_sheet_order_rejects_invalid_facings(order):
    with pytest.raises(ValueError, match="distinct engine facings"):
        sheet_directions({"direction_indices": order}, 4)


def test_action_rows_pair_poses_by_direction(tmp_path, monkeypatch):
    monkeypatch.setattr(importer, "ROOT", tmp_path)
    original = tmp_path / "assets/units/commander_512.png"
    original.parent.mkdir(parents=True)
    sheet = Image.new("RGBA", (64, 64))
    for index in range(16):
        row, col = divmod(index, 4)
        sheet.paste((20 + index, 60, 100, 255),
                    (col * 16 + 4, row * 16 + 3, col * 16 + 12, row * 16 + 13))
    sheet.save(original)
    importer.build("commander", {
        "applicable_clips": ["fire"],
        "clips": [{"path": original, "clip": "fire", "layout": "action_rows",
                   "pose_indices": poses, "direction_indices": [7 - index for index in poses]}
                  for poses in ([0, 2, 4, 6], [1, 3, 5, 7])],
    })
    with Image.open(tmp_path / "assets/combat_visual/animations/commander.png") as atlas:
        colors = [atlas.getpixel((index % 8 * 256 + 128, index // 8 * 256 + 220))[0]
                  for index in range(16)]
    assert colors == [color for index in reversed(range(8)) for color in (20 + index, 28 + index)]


def test_direction_columns_preserve_action_pairs_and_four_phase_walk(tmp_path, monkeypatch):
    monkeypatch.setattr(importer, "ROOT", tmp_path)
    original = tmp_path / "assets/units/walker_512.png"
    original.parent.mkdir(parents=True)
    original.write_bytes(b"identity")

    def sheet(path, offset):
        image = Image.new("RGBA", (128, 32))
        for row in range(2):
            for col in range(8):
                value = offset + row * 8 + col
                image.paste((value, 60, 100, 255),
                            (col * 16 + 4, row * 16 + 2, col * 16 + 12, row * 16 + 14))
        image.save(path)

    action = tmp_path / "action.png"
    walk = tmp_path / "walk.png"
    middle = tmp_path / "middle.png"
    sheet(action, 20)
    sheet(walk, 40)
    sheet(middle, 60)
    importer.build("walker", {
        "applicable_clips": ["idle", "move"],
        "clips": [
            {"path": action, "clip": "idle", "layout": "action_columns"},
            {"path": walk, "intermediate_path": middle, "clip": "move", "layout": "walk_columns"},
        ],
    })
    manifest = __import__("json").loads(
        (tmp_path / "assets/combat_visual/animations/walker.json").read_text())
    with Image.open(tmp_path / "assets/combat_visual/animations/walker.png") as atlas:
        def red(frame):
            return atlas.getpixel((frame % 8 * 256 + 128, frame // 8 * 256 + 220))[0]
        idle = [[red(frame) for frame in row] for row in manifest["animations"]["idle"]["rows"]]
        move = [[red(frame) for frame in row] for row in manifest["animations"]["move"]["rows"]]
    assert idle == [[20 + direction, 28 + direction] for direction in range(8)]
    assert move == [[40 + direction, 60 + direction, 48 + direction, 68 + direction]
                    for direction in range(8)]
