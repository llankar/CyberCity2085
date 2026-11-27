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
