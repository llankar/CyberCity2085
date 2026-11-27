"""Check the local batch exports against the original obstacle surveys."""
import json
from pathlib import Path
import struct

import pytest


@pytest.mark.parametrize(("family", "first_map"), [
    ("outdoor", "wasteland_outdoor_01_dust_road_ambush"),
    ("city", "wasteland_city_01_ruined_downtown"),
])
def test_generated_models_include_every_surveyed_group(family, first_map):
    output = Path("E:/CyberCity2085-3d-lab/generated/phase2/billboard_avenues")
    if not (output / first_map / "environment.glb").is_file():
        pytest.skip("Run this Wasteland Blender batch on E: first")
    maps = Path(__file__).resolve().parents[2] / "assets/maps"
    surveys = sorted(maps.glob(f"wasteland_{family}_*.wall-traces.json"))
    for survey_path in surveys:
        name = survey_path.name.split(".")[0]
        if name == "wasteland_outdoor_02_ashfield_ruins":
            continue
        with (output / name / "environment.glb").open("rb") as model:
            magic, _, _, size, chunk = struct.unpack("<4sIII4s", model.read(20))
            assert (magic, chunk) == (b"glTF", b"JSON")
            nodes = json.loads(model.read(size))["nodes"]
        names = {node["name"] for node in nodes if node.get("children")}
        surveyed = json.loads(survey_path.read_text())["walls"]
        assert {f"Occludable_{row['id']}" for row in surveyed if row.get("kind") != "water"} <= names, name
        assert not {f"Occludable_{row['id']}" for row in surveyed if row.get("kind") == "water"} & names, name

def test_collapsed_span_export_includes_textured_fracture_faces():
    path = Path("E:/CyberCity2085-3d-lab/generated/phase2/billboard_avenues/"
                "wasteland_city_03_collapsed_overpass/environment.glb")
    if not path.is_file():
        pytest.skip("Run the local Overpass Blender batch first")
    with path.open("rb") as model:
        _, _, _, size, _ = struct.unpack("<4sIII4s", model.read(20))
        data = json.loads(model.read(size))
    aggregate = next(i for i, material in enumerate(data["materials"])
                     if material["name"] == "Exposed concrete aggregate")
    assert "baseColorTexture" in data["materials"][aggregate]["pbrMetallicRoughness"]
    assert any(primitive.get("material") == aggregate and "TEXCOORD_0" in primitive["attributes"]
               for mesh in data["meshes"] for primitive in mesh["primitives"])
    nodes = data["nodes"]
    root_nodes = {nodes[index]["name"]: nodes[index]
                  for index in data["scenes"][data["scene"]]["nodes"]}
    for obstacle in ("collapsed_center_span", "collapsed_north_span"):
        assert f"Occludable_{obstacle}" in root_nodes
        roadbed = root_nodes[f"{obstacle} retained roadbed"]
        materials = {primitive["material"] for primitive in data["meshes"][roadbed["mesh"]]["primitives"]}
        assert aggregate in materials
        assert len(materials) == 2
    guardrail_groups = [node for node in nodes if node["name"].startswith("Occludable_overpass_")
                        and "_rail" in node["name"]]
    assert len(guardrail_groups) == 4
    for group in guardrail_groups:
        assert all(" sloped guardrail" in nodes[index]["name"] for index in group["children"])
