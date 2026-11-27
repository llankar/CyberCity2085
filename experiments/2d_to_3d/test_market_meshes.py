"""Check one retained mesh and material surfaces per merged market stall."""
import json
from pathlib import Path
import struct

import pytest


@pytest.mark.parametrize(("folder", "map_name", "prefix"), [
    ("", "market325", "Occludable_market_"),
    ("billboard_avenues", "cybercity_street_07_neon_market_alley", "Occludable_market_"),
    ("billboard_avenues", "wasteland_city_02_burned_market_block", "Occludable_stall_"),
    ("interiors", "wasteland_inner_09_underground_market", "Occludable_stall_"),
])
def test_exported_stalls_retain_independent_groups_and_materials(folder, map_name, prefix):
    root = Path("E:/CyberCity2085-3d-lab/generated/phase2")
    path = root / folder / map_name / "environment.glb"
    if not path.is_file():
        pytest.skip("Run the local market Blender batch first")
    with path.open("rb") as model:
        _, _, _, chunk_size, chunk_type = struct.unpack("<4sIII4s", model.read(20))
        assert chunk_type == b"JSON"
        document = json.loads(model.read(chunk_size))
    nodes = document["nodes"]
    stalls = [node for node in nodes if node["name"].startswith(prefix) and "children" in node]
    assert stalls
    for stall in stalls:
        children = [nodes[index] for index in stall["children"]]
        if map_name == "market325":
            children = [node for node in children if " rigid surfaces" in node["name"]]
        if map_name != "wasteland_city_02_burned_market_block":
            assert len(children) == 1, stall["name"]
        materials = {
            primitive["material"]
            for child in children
            for primitive in document["meshes"][child["mesh"]]["primitives"]
        }
        assert len(materials) > 1, stall["name"]


def test_tech_market_buildings_export_textured_roofs_and_facade_bays():
    path = Path("E:/CyberCity2085-3d-lab/generated/phase2/techmarket341/environment.glb")
    if not path.is_file():
        pytest.skip("Run the Tech Market Blender batch first")
    with path.open("rb") as model:
        size = struct.unpack("<4sIII4s", model.read(20))[3]
        data = json.loads(model.read(size))
    nodes = data["nodes"]
    roots = {node["name"]: node for node in nodes if node["name"].startswith("Occludable_") and node.get("children")}
    survey_path = Path(__file__).resolve().parents[2] / "assets/maps/city_district_tech_market.wall-traces.json"
    traces = json.loads(survey_path.read_text())["walls"]
    assert roots.keys() == {f"Occludable_{trace['id']}" for trace in traces}
    for trace in traces:
        identifier = trace["id"]
        if "polygon" not in trace or identifier.startswith("building_") or identifier == "north_bench":
            continue
        parts = {nodes[index]["name"] for index in roots[f"Occludable_{identifier}"]["children"]}
        assert identifier in parts
        assert any(part.startswith("Canopy post") for part in parts)
        assert any(part.startswith("Canopy edge rail") for part in parts)
    for direction in ("nw", "west", "sw", "ne", "east", "se"):
        name = f"building_{direction}"
        parts = [nodes[index] for index in roots[f"Occludable_{name}"]["children"]]
        assert len(parts) > 2
        roof = next(part for part in parts if part["name"] == name)
        materials = [data["materials"][part["material"]]
                     for part in data["meshes"][roof["mesh"]]["primitives"]]
        assert len([material for material in materials
                    if "baseColorTexture" in material["pbrMetallicRoughness"]]) == 2
        assert any(part["name"].startswith("Facade entrance light") for part in parts)


def test_neon_market_awning_is_independently_occludable():
    path = Path("E:/CyberCity2085-3d-lab/generated/phase2/market325/environment.glb")
    if not path.is_file():
        pytest.skip("Build Neon Market on E: first")
    with path.open("rb") as model:
        size = struct.unpack("<4sIII4s", model.read(20))[3]
        nodes = json.loads(model.read(size))["nodes"]
    awning = next(node for node in nodes if node["name"] == "Occludable_west_awning")
    parts = [nodes[index]["name"] for index in awning["children"]]
    assert "West awning canopy" in parts
    assert sum(name.startswith("West awning outer pole") for name in parts) == 2


def test_floor_detail_restores_texture_without_touching_original_aisles():
    import numpy as np
    from PIL import Image
    from prepare_floor248 import restore_surface_detail

    original = Image.new("RGB", (64,64), (90,80,70))
    mask = np.zeros((64,64), dtype=np.uint8)
    mask[12:52, 10:54] = 255
    sample = Image.fromarray(((np.indices((16,16)).sum(axis=0) % 2) * 255).astype(np.uint8))
    changed = np.asarray(restore_surface_detail(original, mask, sample, 16))
    assert np.array_equal(changed[mask == 0], np.asarray(original)[mask == 0])
    assert int(np.ptp(changed[23:41, 23:41, 0])) > 30


def test_donor_pavement_is_confined_to_the_traced_polygon():
    from PIL import Image
    from prepare_floor248 import restore_donor_pavement

    source = Image.new("RGB", (32,32), (100,110,120))
    base = Image.new("RGB", (32,32), (20,30,40))
    polygon = [(8,8),(24,8),(8,24)]
    survey = {"canvas_size": (32,32), "walls": [{"id": "awning", "polygon": polygon}]}
    repaired = restore_donor_pavement(base, source, survey, {"awning": (0,0,5,5)})
    assert repaired.getpixel((10,10))[0] > 70
    assert repaired.getpixel((23,23)) == base.getpixel((23,23))
    assert repaired.getpixel((7,10)) == base.getpixel((7,10))
