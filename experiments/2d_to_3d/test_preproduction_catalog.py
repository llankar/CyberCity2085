"""The experimental selector must cover the complete original map catalogue."""
import json
from pathlib import Path


def test_selector_contains_a_preview_for_each_original_tactical_map():
    experiment = Path(__file__).resolve().parent
    godot = experiment / "godot"
    maps = experiment.parents[1] / "assets/maps"
    entries = json.loads((godot / "preproduction_catalog.json").read_text())
    originals = {path.name.removesuffix(".wall-traces.json")
                 for path in maps.glob("*.wall-traces.json")
                 if (maps / path.name.replace(".wall-traces.json", ".png")).is_file()}
    assert len(entries) == len(originals) == 122
    assert {entry["map"] for entry in entries} == originals
    for entry in entries:
        assert entry["status"] == "preview", entry["map"]
        assert entry["scene"].startswith("res://"), entry["map"]
        assert (godot / entry["scene"].removeprefix("res://")).is_file(), entry["map"]
