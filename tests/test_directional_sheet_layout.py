import json
import sys
from pathlib import Path

import pytest
from PIL import Image


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools" / "art"))
import import_directional_clips as importer
from import_directional_clips import apply_chroma_key, sheet_directions


def test_sheet_order_preserves_default_and_maps_reviewed_pairs():
    assert sheet_directions({}, 4, 4) == [4, 5, 6, 7]
    order = [2, 1, 0, 7, 6, 5, 4, 3]
    assert sheet_directions({"direction_indices": order}, 8) == order


@pytest.mark.parametrize("order", [[0, 0, 1, 2], [0, 1, 2, 8], [0, 1, 2], [0, 1, 2, True]])
def test_sheet_order_rejects_invalid_facings(order):
    with pytest.raises(ValueError, match="distinct engine facings"):
        sheet_directions({"direction_indices": order}, 4)


def test_chroma_key_removes_flat_background_and_unmixes_edge_colour():
    image = Image.new("RGBA", (3, 1), (0, 255, 255, 255))
    image.putpixel((1, 0), (64, 191, 191, 255))
    image.putpixel((2, 0), (64, 48, 32, 255))

    keyed = apply_chroma_key(image, [0, 255, 255], inner=0, outer=255)

    assert keyed.getpixel((0, 0)) == (0, 0, 0, 0)
    edge = keyed.getpixel((1, 0))
    assert 0 < edge[3] < 255
    assert edge[1] < 32 and edge[2] < 32
    assert edge[1] <= edge[0] + 32 and edge[2] <= edge[0] + 32
    assert keyed.getpixel((2, 0))[3] > 200


@pytest.mark.parametrize("key,inner,outer", [
    ([0, 255], 8, 96), ([0, 256, 0], 8, 96), ([0, 255, 255], 96, 8),
])
def test_chroma_key_rejects_invalid_configuration(key, inner, outer):
    with pytest.raises(ValueError):
        apply_chroma_key(Image.new("RGBA", (1, 1)), key, inner, outer)


def test_walk_rows_imports_four_phases_for_eight_reviewed_directions(tmp_path, monkeypatch):
    monkeypatch.setattr(importer, "ROOT", tmp_path)
    units = tmp_path / "assets/units"
    units.mkdir(parents=True)
    Image.new("RGBA", (16, 16), (80, 40, 20, 255)).save(units / "boar_512.png")
    source = tmp_path / "walk.png"
    sheet = Image.new("RGBA", (8 * 24, 4 * 24))
    for row in range(4):
        for col in range(8):
            colour = (40 + row * 30, 30 + col * 10, 20, 255)
            Image.new("RGBA", (14, 16), colour).save(tmp_path / "cell.png")
            sheet.alpha_composite(Image.open(tmp_path / "cell.png"), (col * 24 + 5, row * 24 + 4))
    sheet.save(source)
    importer.build("boar", {
        "applicable_clips": ["move"],
        "non_applicable_clips": {},
        "clips": [{"clip": "move", "layout": "walk_rows", "path": str(source),
                   "direction_indices": [1, 2, 3, 4, 5, 6, 7, 0]}],
    })
    manifest = json.loads((tmp_path / "assets/combat_visual/animations/boar.json").read_text())
    assert [len(row) for row in manifest["animations"]["move"]["rows"]] == [4] * 8
    assert manifest["coverage"] == "complete"


def test_extract_can_preserve_reviewed_disconnected_costume_details():
    image = Image.new("RGBA", (64, 32))
    image.paste((80, 60, 40, 255), (2, 4, 9, 28))
    image.paste((80, 60, 40, 255), (13, 4, 16, 7))

    filtered = importer.extract(image, 0, 0, grid_rows=1)
    preserved = importer.extract(image, 0, 0, grid_rows=1, clean_components=False)

    assert sum(preserved.getchannel("A").getdata()) > sum(filtered.getchannel("A").getdata())


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


def test_action_columns_reject_single_row_silhouette_slicing(tmp_path, monkeypatch):
    monkeypatch.setattr(importer, "ROOT", tmp_path)
    original = tmp_path / "assets/units/broken_512.png"
    original.parent.mkdir(parents=True)
    original.write_bytes(b"identity")
    sheet = tmp_path / "single-row.png"
    image = Image.new("RGBA", (128, 32))
    for col in range(8):
        image.paste((80, 60, 40, 255), (col * 16 + 4, 2, col * 16 + 12, 30))
    image.save(sheet)

    with pytest.raises(ValueError, match="use single_row_pair"):
        importer.build("broken", {
            "applicable_clips": ["idle"],
            "clips": [{"path": sheet, "clip": "idle", "layout": "action_columns"}],
        })


def test_single_rows_pair_complete_sprites_without_vertical_slicing(tmp_path, monkeypatch):
    monkeypatch.setattr(importer, "ROOT", tmp_path)
    original = tmp_path / "assets/units/stalker_512.png"
    original.parent.mkdir(parents=True)
    original.write_bytes(b"identity")

    def sheet(path, offset):
        image = Image.new("RGB", (128, 16), (0, 255, 255))
        for col in range(8):
            image.paste((offset + col, 60, 100),
                        (col * 16 + 4, 2, col * 16 + 12, 14))
            image.putpixel((col * 16 + 14, 2), (offset + col, 60, 100))
        image.save(path)

    phases = [tmp_path / f"phase-{index}.png" for index in range(4)]
    for index, path in enumerate(phases):
        sheet(path, 20 + index * 20)
    importer.build("stalker", {
        "applicable_clips": ["idle", "move"],
        "clips": [
            {"path": phases[0], "follow_through_path": phases[1],
             "clip": "idle", "layout": "single_row_pair",
             "chroma_key": [0, 255, 255], "chroma_inner": 4, "chroma_outer": 128,
             "keep_disconnected_details": True},
            {"path": phases[0], "phase_paths": [str(path) for path in phases[1:]],
             "clip": "move", "layout": "single_row_walk",
             "chroma_key": [0, 255, 255], "chroma_inner": 4, "chroma_outer": 128,
             "keep_disconnected_details": True},
        ],
    })
    manifest = __import__("json").loads(
        (tmp_path / "assets/combat_visual/animations/stalker.json").read_text())
    with Image.open(tmp_path / "assets/combat_visual/animations/stalker.png") as atlas:
        def red(frame):
            return atlas.getpixel((frame % 8 * 256 + 128, frame // 8 * 256 + 220))[0]
        idle = [[red(frame) for frame in row]
                for row in manifest["animations"]["idle"]["rows"]]
        move = [[red(frame) for frame in row]
                for row in manifest["animations"]["move"]["rows"]]
    assert idle == [[20 + direction, 40 + direction] for direction in range(8)]
    assert move == [[20 + direction, 40 + direction, 60 + direction, 80 + direction]
                    for direction in range(8)]
    assert atlas.getchannel("A").getextrema()[0] == 0
    assert manifest["provenance"][1]["keep_disconnected_details"] is True
