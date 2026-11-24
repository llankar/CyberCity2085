"""Functional contracts introduced by Operative Dossier 2.0."""

from pathlib import Path

from game.agents.cyberware import ZONE_ORDER, catalogue_for_zone
from game.character import Character
from game.gamestate import GameState
from game.management.equipment import EQUIPMENT_SLOTS, default_equipment_catalog
from game.ui.components.character_sheet import (
    SHEET_CARD_FILL_ALPHA,
    SHEET_CONTROL_FILL_ALPHA,
    SHEET_PANEL_FILL_ALPHA,
)


def test_dossier_uses_readable_layered_glass():
    assert 160 <= SHEET_PANEL_FILL_ALPHA < SHEET_CARD_FILL_ALPHA
    assert SHEET_CARD_FILL_ALPHA < SHEET_CONTROL_FILL_ALPHA <= 225
from game.ui.components.character_sheet import DOSSIER_PAGES
from game.ui.layouts.character_sheet import character_sheet_layout


def test_dossier_has_exactly_five_shared_pages():
    assert DOSSIER_PAGES == (
        "overview", "skills", "inventory", "cyberware", "journal"
    )


def test_dossier_content_stays_inside_supported_resolutions():
    for width, height in ((1280, 720), (1920, 1080), (2560, 1440)):
        layout = character_sheet_layout(width, height)
        assert layout.content.inside(layout.content.__class__(0, 0, width, height))
        assert layout.content.left == layout.identity.left
        assert layout.content.right == layout.skills.right


def test_inventory_catalog_uses_real_slots_and_compatible_items():
    catalog = default_equipment_catalog()
    assert tuple(catalog) == EQUIPMENT_SLOTS
    for slot in EQUIPMENT_SLOTS:
        assert catalog[slot]
        assert all(item.can_equip_to(slot) for item in catalog[slot])


def test_cyberware_page_exposes_ten_real_implants_per_zone():
    assert len(ZONE_ORDER) == 7
    assert all(len(catalogue_for_zone(zone)) >= 10 for zone in ZONE_ORDER)


def test_dossier_graphic_assets_cover_inventory_and_cyberware_zones():
    catalog = default_equipment_catalog()
    for slot in EQUIPMENT_SLOTS:
        assert Path(f"assets/ui/inventory/{slot}.png").stat().st_size > 0
        assert Path(f"assets/ui/inventory/source_sheets/{slot}.png").stat().st_size > 0
        for item in catalog[slot]:
            assert Path(f"assets/ui/inventory/items/{item.id}.png").stat().st_size > 0
    assert sum(len(items) for items in catalog.values()) == 42
    assert Path("assets/ui/cyberware/cyberware_body_map_v1.png").stat().st_size > 0
    for zone in ZONE_ORDER:
        filename = zone.lower().replace(" ", "_") + ".png"
        assert Path("assets/ui/cyberware/zones", filename).stat().st_size > 0


def test_personal_notes_round_trip_and_old_saves_migrate_empty():
    operative = Character("Null", personal_notes=["Trust is earned."])
    restored = Character.from_dict(operative.to_dict())
    assert restored.name == "Null"
    assert restored.personal_notes == ["Trust is earned."]
    legacy = operative.to_dict()
    legacy.pop("personal_notes")
    assert Character.from_dict(legacy).personal_notes == []


def test_journal_sources_are_campaign_state_not_mock_data():
    state = GameState(characters=[Character("Rook")])
    assert state.event_log
    assert isinstance(state.campaign.completed_story_missions, list)
    assert state.characters[0].history == []
