"""Check the local batch exports against the original obstacle surveys."""
import json
from pathlib import Path
import struct

import pytest


def test_generated_outdoor_models_include_every_surveyed_group():
    output = Path("E:/CyberCity2085-3d-lab/generated/phase2/billboard_avenues")
    if not (output / "wasteland_outdoor_01_dust_road_ambush/environment.glb").is_file():
        pytest.skip("Run the outdoor Blender batch on E: first")
    maps = Path(__file__).resolve().parents[2] / "assets/maps"
    surveys = sorted(maps.glob("wasteland_outdoor_*.wall-traces.json"))
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
        assert {f"Occludable_{row['id']}" for row in surveyed} <= names, name
