"""Check one retained mesh and material surfaces per merged market stall."""
import json
from pathlib import Path
import struct

import pytest


@pytest.mark.parametrize(("folder", "map_name", "prefix"), [
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
        assert len(stall["children"]) == 1, stall["name"]
        mesh = document["meshes"][nodes[stall["children"][0]]["mesh"]]
        assert len({primitive["material"] for primitive in mesh["primitives"]}) > 1
