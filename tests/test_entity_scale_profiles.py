import hashlib
import json
from pathlib import Path

from tools.apply_entity_scale_profiles import RATIOS, apply_profiles


ROOT = Path(__file__).resolve().parents[1]


def test_reviewed_profiles_cover_every_map_without_tactical_changes(tmp_path):
    source = ROOT / "godot/combat_missions_ui/art/environment/map_presentation.json"
    target = tmp_path / "map_presentation.json"
    target.write_bytes(source.read_bytes())
    wall_hashes = {
        p.name: hashlib.sha256(p.read_bytes()).hexdigest()
        for p in (ROOT / "assets/maps").glob("*.walls.json")
    }
    report = apply_profiles(target, write=True)
    assert report["maps"] == 122 and not report["unknown_profiles"]
    data = json.loads(target.read_text(encoding="utf-8"))
    assert "One global entity-scale ratio per map" in data["notes"]
    assert {row["human_height_ratio"] for row in data["maps"].values()} == set(RATIOS.values())
    assert all(row["human_height_ratio"] == RATIOS[row["profile"]] for row in data["maps"].values())
    assert wall_hashes == {
        p.name: hashlib.sha256(p.read_bytes()).hexdigest()
        for p in (ROOT / "assets/maps").glob("*.walls.json")
    }
