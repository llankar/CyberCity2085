"""The experimental selector must cover the complete original map catalogue."""
import json
from pathlib import Path
import re

import pytest

from catalogue_test_assets import catalogue_environment


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


def test_identical_map_variants_share_visual_assets():
    experiment = Path(__file__).resolve().parent
    godot = experiment / "godot"
    maps = experiment.parents[1] / "assets/maps"
    catalogue = {entry["map"]: entry["scene"].removeprefix("res://")
                 for entry in json.loads((godot / "preproduction_catalog.json").read_text())}
    canonical_by_folder = {}
    for name, scene in catalogue.items():
        survey = json.loads((maps / f"{name}.wall-traces.json").read_text())
        folder = re.search(r'^review_folder = "([^"]+)"$', (godot / scene).read_text(), re.MULTILINE)
        if folder:
            canonical = Path(survey.get("same_pixels_as", name)).stem
            assert canonical_by_folder.setdefault(folder[1], canonical) == canonical, name
    for survey_path in maps.glob("*.wall-traces.json"):
        survey = json.loads(survey_path.read_text())
        if "same_pixels_as" not in survey:
            continue
        variant = survey_path.name.removesuffix(".wall-traces.json")
        original = Path(survey["same_pixels_as"]).stem
        base_survey = json.loads((maps / f"{original}.wall-traces.json").read_text())
        assert survey["walls"] == base_survey["walls"], variant
        assert survey["canvas_size"] == base_survey["canvas_size"], variant
        assert (maps / f"{variant}.png").read_bytes() == (maps / f"{original}.png").read_bytes(), variant
        assert catalogue[variant] != catalogue[original], variant
        folders = [re.search(r'^review_folder = "([^"]+)"$', (godot / catalogue[name]).read_text(),
                             re.MULTILINE).group(1) for name in (variant, original)]
        assert folders[0] == folders[1], variant


def test_local_catalogue_exports_exist():
    godot = Path(__file__).resolve().parent / "godot"
    entries = json.loads((godot / "preproduction_catalog.json").read_text())
    if not Path("E:/CyberCity2085-3d-lab/generated/phase2").is_dir():
        pytest.skip("Local experimental exports are unavailable")
    missing = [entry["map"] for entry in entries
               if not catalogue_environment(entry["map"]).is_file()]
    assert not missing, missing
