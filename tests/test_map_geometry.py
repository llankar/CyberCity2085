import json
from pathlib import Path
import shutil
import subprocess

from PIL import Image
import pytest

from game.battle_maps import build_battle_map_catalog
from game.map_geometry import geometry_path, load_map_geometry, scan_map_walls, stroke_outline


def test_every_background_has_an_independent_valid_stored_wall_survey():
    entries = build_battle_map_catalog()
    assert entries
    for entry in entries:
        geometry = load_map_geometry(entry.path)
        assert geometry, entry.filename
        assert geometry["image"] == entry.filename
        assert geometry["coordinates"] == "texture_top_left"
        assert geometry["method"] == "manual_wall_traces_v1", entry.filename
        assert geometry["reviewed"] is True, entry.filename
        assert Path(entry.path).with_suffix(".wall-traces.json").is_file(), entry.filename
        ids = [wall["id"] for wall in geometry["walls"]]
        assert len(ids) == len(set(ids))
        assert all(wall.get("outline_uv") for wall in geometry["walls"]), entry.filename
    manual = load_map_geometry("assets/maps/city_industrial_data_vault.png")
    assert manual["reviewed"] is True
    assert manual["method"] == "manual_wall_traces_v1"
    assert len(manual["walls"]) == 23
    square = load_map_geometry("assets/maps/city_district_holo_square.png")
    assert square["reviewed"] is True
    assert len(square["walls"]) == 39
    platform = next(wall for wall in square["walls"] if wall["id"] == "holo_platform")
    assert platform["outline_uv"]
    assert [20, 14] in platform["cells"]
    assert all([20, 8] not in wall["cells"] for wall in square["walls"])


def test_all_manual_sources_reproduce_the_stored_survey_and_duplicate_art_matches():
    """Catch edits that forget to compile, omissions and unsafe reuse of variants."""
    by_hash = {}
    for entry in build_battle_map_catalog():
        stored = load_map_geometry(entry.path)
        assert scan_map_walls(entry.path) == stored, entry.filename
        source = json.loads(Path(entry.path).with_suffix(".wall-traces.json").read_text(encoding="utf-8"))
        if origin := source.get("same_pixels_as"):
            original = load_map_geometry(Path(entry.path).with_name(origin))
            assert original["image_sha256"] == stored["image_sha256"], entry.filename
        previous = by_hash.setdefault(stored["image_sha256"], stored["walls"])
        assert previous == stored["walls"], entry.filename


@pytest.mark.parametrize("filename,blocked,open_floor", [
    ("city_exterior_corporate_plaza.png", (20,14), (20,9)),
    ("cybercity_inner_02_safehouse.png", (18,16), (25,16)),
    ("cybercity_street_06_downtown_intersection.png", (11,4), (20,14)),
    ("wasteland_inner_05_looted_vault.png", (20,13), (20,18)),
    ("wasteland_outdoor_12_salt_flat_ambush.png", (18,22), (20,17)),
])
def test_manual_landmarks_block_obstacles_but_keep_visible_floor_open(filename, blocked, open_floor):
    geometry = load_map_geometry(Path("assets/maps") / filename)
    cells = {tuple(cell) for wall in geometry["walls"] for cell in wall["cells"]}
    assert blocked in cells
    assert open_floor not in cells


def test_dockside_manual_footprints_preserve_aisles_and_distinguish_water():
    dock = load_map_geometry("assets/maps/city_industrial_dockside_terminal.png")
    assert dock["reviewed"] and dock["method"] == "manual_wall_traces_v1"
    walls = {wall["id"]: wall for wall in dock["walls"]}
    assert len(walls) == 67
    assert [20, 11] in walls["central_container_red"]["cells"]
    assert all([20, 8] not in wall["cells"] for wall in walls.values())
    assert walls["harbor_water"]["blocks_sight"] is False
    assert walls["east_center_grate"]["cells"] == []
    assert all(wall.get("outline_uv") for wall in walls.values())


def test_service_tunnel_traces_keep_walkways_open_and_cover_pipes():
    geometry = load_map_geometry("assets/maps/city_industrial_service_tunnel.png")
    assert geometry["reviewed"] and geometry["method"] == "manual_wall_traces_v1"
    walls = {wall["id"]: wall for wall in geometry["walls"]}
    assert len(walls) == 74
    cells = {tuple(cell) for wall in walls.values() for cell in wall["cells"]}
    assert (17,15) not in cells
    assert (17,20) not in cells
    assert (11,6) in cells
    assert walls["west_mid_floor_grate"]["cells"] == []
    assert all(wall.get("outline_uv") for wall in walls.values())


def test_traced_wall_stroke_keeps_exact_thickness_and_does_not_snap_to_grid():
    outline = stroke_outline([[100,100],[300,100]], 20)
    assert min(point[1] for point in outline) == 90
    assert max(point[1] for point in outline) == 110
    assert min(point[0] for point in outline) == 100
    assert max(point[0] for point in outline) == 300


def test_image_scan_records_dark_wall_in_correct_texture_coordinates(tmp_path):
    path = tmp_path / "test.png"
    image = Image.new("RGB", (800, 560), "white")
    from PIL import ImageDraw
    ImageDraw.Draw(image).rectangle((300, 0, 359, 559), fill="black")
    image.save(path)
    geometry = scan_map_walls(path)
    cells = [cell for wall in geometry["walls"] for cell in wall["cells"]]
    assert cells
    assert all(15 <= x <= 17 for x, y in cells)


def test_stale_survey_and_out_of_bounds_edits_are_rejected(tmp_path):
    path = tmp_path / "test.png"
    Image.new("RGB", (80, 56), "white").save(path)
    data = scan_map_walls(path)
    data["walls"] = [{"id": "bad", "cells": [[40, 0]]}]
    geometry_path(path).write_text(json.dumps(data), encoding="utf-8")
    assert load_map_geometry(path) == {}
    data["walls"] = []
    geometry_path(path).write_text(json.dumps(data), encoding="utf-8")
    assert load_map_geometry(path)
    Image.new("RGB", (80, 56), "black").save(path)
    assert load_map_geometry(path) == {}


def test_godot_wall_layout_blocks_movement_los_and_preserves_projection(tmp_path):
    from game.combat.godot_bridge import find_godot_executable
    executable = find_godot_executable()
    if not executable:
        pytest.skip("Godot not installed")
    scripts = Path("godot/combat_missions_ui/scripts")
    for name in ("map_wall_layout.gd", "battlefield.gd", "combat_signals.gd"):
        shutil.copy2(scripts / name, tmp_path / name)
    (tmp_path / "project.godot").write_text('config_version=5\n[autoload]\nCombatSignals="*res://combat_signals.gd"\n', encoding="utf-8")
    (tmp_path / "actual.json").write_text(json.dumps(load_map_geometry("assets/maps/city_district_riot_square.png")), encoding="utf-8")
    (tmp_path / "city_district_riot_square.walls.json").write_text((tmp_path / "actual.json").read_text(encoding="utf-8"), encoding="utf-8")
    smoke = '''extends SceneTree
func _initialize():
    var layout = load("res://map_wall_layout.gd")
    var actual = JSON.parse_string(FileAccess.get_file_as_string("res://actual.json"))
    var refreshed = layout.geometry_for_map({"path":"city_district_riot_square.png", "geometry":{"grid":[0,0]}}, ProjectSettings.globalize_path("res://"))
    if layout.cover_nodes(refreshed).is_empty():
        push_error("Stale embedded survey overrode corrected map data")
        quit(7)
        return
    if layout.cover_nodes(actual).is_empty():
        push_error("Actual JSON survey produced zero obstacles")
        quit(6)
        return
    var geometry := {"grid": [40,28], "walls": [{"id":"wall_001", "cells":[[2,0],[2,1],[2,2]]}]}
    var board = load("res://battlefield.gd").new()
    root.add_child(board)
    board.configure(Vector2(1280,720), null, layout.cover_nodes(geometry), Vector2i(3,1))
    if not board.debug_walls_visible:
        quit(5)
        return
    board.debug_walls_visible = false
    if not board.is_wall(Vector2i(2,1)) or board.has_los(Vector2i(1,1), Vector2i(3,1), []):
        quit(1)
        return
    var water := {"grid":[40,28],"walls":[{"id":"water","blocks_sight":false,"cells":[[2,1]]}]}
    var water_board = load("res://battlefield.gd").new()
    root.add_child(water_board)
    water_board.configure(Vector2(1280,720),null,layout.cover_nodes(water),Vector2i(3,1))
    if not water_board.is_wall(Vector2i(2,1)) or not water_board.has_los(Vector2i(1,1),Vector2i(3,1),[]):
        quit(8)
        return
    var route = board.find_path(Vector2i(1,1), Vector2i(3,1))
    if route.size() <= 3 or Vector2i(2,1) in route:
        quit(2)
        return
    if board.world_to_cell(board.cell_to_world(Vector2i(8,6))) != Vector2i(8,6):
        quit(3)
        return
    var players: Array[Dictionary] = [{"position":Vector2i(2,1)}]
    var enemies: Array[Dictionary] = [{"position":Vector2i(2,2)}]
    var objective := {"cell":Vector2i(2,0)}
    layout.place_encounter(players,enemies,objective,board)
    if board.is_wall(players[0]["position"]) or board.is_wall(enemies[0]["position"]) or board.is_wall(objective["cell"]):
        quit(4)
        return
    print("MAP_WALLS_OK")
    quit(0)
'''
    (tmp_path / "smoke.gd").write_text(smoke, encoding="utf-8")
    result = subprocess.run([executable,"--headless","--audio-driver","Dummy","--quit-after","5","--path",str(tmp_path),"--script","res://smoke.gd"],capture_output=True,text=True,timeout=30)
    output = result.stdout + result.stderr
    assert result.returncode == 0, output
    assert "SCRIPT ERROR" not in output, output
    assert "MAP_WALLS_OK" in output, output


@pytest.mark.parametrize("filename", ["city_exterior_waterfront_docks.png", "city_industrial_dockside_terminal.png", "cybercity_street_04_waterfront_docks.png"])
def test_dock_maps_have_stored_obstructions(filename):
    geometry = load_map_geometry(Path("assets/maps") / filename)
    assert geometry, filename
    assert sum(len(wall["cells"]) for wall in geometry["walls"]) > 0
