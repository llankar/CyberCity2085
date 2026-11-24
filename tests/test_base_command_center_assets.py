"""Acceptance checks for the six Base Command Center visual domains."""

import json
from pathlib import Path

from PIL import Image

from game.ui.components.departments.deck import ROOM_BACKGROUNDS, ROOM_GLASS, ROOMS
from game.ui.components.departments.deck import DepartmentDeck


def test_every_department_has_distinct_local_widescreen_art():
    assert set(ROOM_BACKGROUNDS) == set(ROOMS)
    hashes = set()
    for room, value in ROOM_BACKGROUNDS.items():
        path = Path(value)
        assert path.is_file(), room
        with Image.open(path) as image:
            assert image.width >= 1600
            assert image.height >= 900
            assert image.width / image.height > 1.7
        hashes.add(hash(path.read_bytes()))
    assert len(hashes) == len(ROOMS)


def test_base_art_manifest_matches_runtime_mapping():
    root = Path("assets/ui/base_command_center")
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["generator"] == "OpenAI built-in imagegen"
    assert manifest["assets"] == {
        room: Path(path).name for room, path in ROOM_BACKGROUNDS.items()
    }


def test_lab_2_uses_real_research_categories_and_no_fake_queue_actions():
    source = Path("game/ui/components/departments/lab2.py").read_text(encoding="utf-8")
    assert "tree.projects.values()" in source
    assert "project.stat_modifiers" in source
    assert "project.unlock_flags" in source
    assert "project.requires" in source
    assert "pause" not in source.lower()
    assert "cancel" not in source.lower()


def test_department_text_panels_reveal_room_backgrounds():
    deck = DepartmentDeck()
    assert 180 <= deck.panel_fill_alpha <= 215
    assert deck.panel_fill_alpha < deck.card_fill_alpha < deck.control_fill_alpha
    assert set(ROOM_GLASS) == set(ROOM_BACKGROUNDS)
    for panel, card, control, overlay in ROOM_GLASS.values():
        assert 170 <= panel <= 195
        assert panel < card < control <= 230
        assert 110 <= overlay <= 135
