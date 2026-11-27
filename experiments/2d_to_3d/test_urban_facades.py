"""Verify the urban batch exported lateral details under its occlusion roots."""
import json
from pathlib import Path
import struct

import pytest


@pytest.mark.parametrize("name", [
    "city_exterior_billboard_avenue",
    "cybercity_street_15_billboard_avenue",
    "cybercity_street_16_billboard_avenue",
    "cybercity_street_02_neon_market_alley",
    "cybercity_street_07_neon_market_alley",
    "cybercity_street_08_neon_market_alley",
])
def test_lateral_facade_bands_keep_building_occlusion(name):
    folder = Path("E:/CyberCity2085-3d-lab/generated/phase2/billboard_avenues")
    path = folder / name / "environment.glb"
    if not path.is_file():
        pytest.skip("Run the urban Blender batch on E: first")
    with path.open("rb") as glb:
        _, _, _, size, _ = struct.unpack("<4sIII4s", glb.read(20))
        nodes = json.loads(glb.read(size))["nodes"]
    bands = {index for index, node in enumerate(nodes) if " side facade band" in node["name"]}
    assert bands
    grouped = {index for node in nodes if node["name"].startswith("Occludable_")
               for index in node.get("children", [])}
    assert bands <= grouped
    rear_doors = {index for index, node in enumerate(nodes) if " rear service door" in node["name"]}
    assert rear_doors and rear_doors <= grouped
    parapets = {index for index, node in enumerate(nodes) if " roof parapet" in node["name"]}
    assert parapets and parapets <= grouped
    assert len(parapets) % 4 == 0
    fans = {index for index, node in enumerate(nodes) if " surveyed roof HVAC" in node["name"]}
    curbs = {index for index, node in enumerate(nodes) if " roof HVAC mounting curb" in node["name"]}
    expected = 2 if name == "cybercity_street_02_neon_market_alley" else 3
    assert len(fans) == len(curbs) == expected
    assert (fans | curbs) <= grouped

def test_billboard_benches_export_as_grouped_panels():
    path = Path("E:/CyberCity2085-3d-lab/generated/phase2/billboard_avenues/"
                "city_exterior_billboard_avenue/environment.glb")
    if not path.is_file():
        pytest.skip("Run the urban Blender batch on E: first")
    with path.open("rb") as glb:
        _, _, _, size, _ = struct.unpack("<4sIII4s", glb.read(20))
        nodes = json.loads(glb.read(size))["nodes"]
    benches = [node for node in nodes if node["name"].startswith("Occludable_")
               and any(" seat panel" in nodes[index]["name"] for index in node.get("children", []))]
    assert len(benches) == 6
    for bench in benches:
        parts = [nodes[index]["name"] for index in bench["children"]]
        assert sum(" seat panel" in part for part in parts) in (2, 3)
        assert sum(" seat panel" in part for part in parts) == sum(" back panel" in part for part in parts)

def test_billboard_planters_export_one_two_tone_foliage_mesh_per_group():
    path = Path("E:/CyberCity2085-3d-lab/generated/phase2/billboard_avenues/"
                "city_exterior_billboard_avenue/environment.glb")
    if not path.is_file():
        pytest.skip("Run the urban Blender batch on E: first")
    with path.open("rb") as glb:
        _, _, _, size, _ = struct.unpack("<4sIII4s", glb.read(20))
        data = json.loads(glb.read(size))
    nodes = data["nodes"]
    plants = [node for node in nodes if node["name"].endswith(" shrub foliage")]
    assert plants
    grouped = {child for node in nodes if node["name"].startswith("Occludable_")
               for child in node.get("children", [])}
    for plant in plants:
        assert nodes.index(plant) in grouped
        primitives = data["meshes"][plant["mesh"]]["primitives"]
        assert len({primitive["material"] for primitive in primitives}) == 2

def test_civic_kiosk_exports_controls_under_the_occlusion_group():
    path = Path("E:/CyberCity2085-3d-lab/generated/phase2/billboard_avenues/"
                "city_district_civic_center/environment.glb")
    if not path.is_file():
        pytest.skip("Run the civic Blender batch on E: first")
    with path.open("rb") as glb:
        _, _, _, size, _ = struct.unpack("<4sIII4s", glb.read(20))
        nodes = json.loads(glb.read(size))["nodes"]
    kiosk = next(node for node in nodes if node["name"] == "Occludable_northwest_kiosk")
    parts = {nodes[index]["name"] for index in kiosk["children"]}
    assert {f"northwest_kiosk {part}" for part in ("screen", "screen bezel", "hood", "control shelf")} <= parts
    assert sum(" service vent" in part for part in parts) == 3
    survey = Path(__file__).resolve().parents[2] / "assets/maps/city_district_civic_center.wall-traces.json"
    expected = {f"Occludable_{row['id']}" for row in json.loads(survey.read_text())["walls"]}
    roots = {node["name"]: node for node in nodes if node["name"].startswith("Occludable_") and node.get("children")}
    assert roots.keys() == expected
    landmark = [nodes[index]["name"] for index in roots["Occludable_monument_planter"]["children"]]
    assert "Civic monument beacon" in landmark
    assert any(" foliage" in part for part in landmark)


def test_holo_square_exports_occludable_obstacles_and_landmark():
    path = Path("E:/CyberCity2085-3d-lab/generated/phase2/billboard_avenues/"
                "city_district_holo_square/environment.glb")
    if not path.is_file():
        pytest.skip("Run the Holo Square Blender batch on E: first")
    with path.open("rb") as glb:
        _, _, _, size, _ = struct.unpack("<4sIII4s", glb.read(20))
        nodes = json.loads(glb.read(size))["nodes"]
    roots = {node["name"]: node["children"] for node in nodes
             if node["name"].startswith("Occludable_")}
    assert len(roots) == 39
    benches = [children for name, children in roots.items() if name.startswith("Occludable_bench_")]
    assert len(benches) == 14
    assert all(any(" seat panel" in nodes[index]["name"] for index in children) for children in benches)
    platform = nodes[roots["Occludable_holo_platform"][0]]
    parts = {nodes[index]["name"] for index in platform["children"]}
    assert {"Holo Square emitter", "Holo Square projection core"} <= parts
    assert sum(part.startswith("Holo Square projection ring ") for part in parts) == 4
