"""Resolve the environment configured by an experimental catalogue scene."""
import json
from pathlib import Path
import re


GODOT = Path(__file__).resolve().parent / "godot"


def catalogue_environment(map_name):
    entries = json.loads((GODOT / "preproduction_catalog.json").read_text())
    scene = next(entry["scene"] for entry in entries if entry["map"] == map_name)
    body = (GODOT / scene.removeprefix("res://")).read_text()
    folder = re.search(r'^review_folder = "([^"]+)"$', body, re.MULTILINE)
    if folder is None:
        raise ValueError(f"No review folder configured in {scene}")
    model = re.search(r'^review_model_name = "([^"]+)"$', body, re.MULTILINE)
    return Path(folder[1]) / (model[1] if model else "environment.glb")
