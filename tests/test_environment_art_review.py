import json
from pathlib import Path

from tools.record_environment_art_review import record


ROOT = Path(__file__).resolve().parents[1]


def test_completed_review_covers_every_map_and_records_fallback_reasons(tmp_path):
    manifest = ROOT / "docs/images/environment-art-review-windows/manifest.json"
    source = ROOT / "godot/combat_missions_ui/art/environment/environment_art.json"
    target = tmp_path / "environment_art.json"
    target.write_bytes(source.read_bytes())
    result = record(manifest, target, write=True)
    assert result["maps_reviewed"] == 122 and result["pages_inspected"] == 21
    assert result["disabled_overlays"] >= 5
    maps = json.loads(target.read_text(encoding="utf-8"))["maps"]
    assert len(maps) == 122
    assert all(row["validation"]["artistically_complete"] for row in maps.values())
    assert all(row["validation"]["interactions"] == "passed" for row in maps.values())
    assert all(
        prop.get("enabled", True) or prop.get("disabled_reason")
        for row in maps.values() for prop in row.get("props", [])
    )
