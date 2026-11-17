"""Shared layout, full-content readers and controller-routing regressions."""

from types import SimpleNamespace
from unittest.mock import Mock
import pytest
from game.ui.layouts.department_deck import department_layout
from game.ui.layouts.world_map_beacons import Rect
from game.ui.components.document_kit import DocumentKit
from game.ui.components.departments.deck import DepartmentDeck
from game.ui.components.visual_kit import UIHit, VisualKit
from game.ui.components.squad_command import SquadCommandRenderer
from game.ui.components.utilities.reports import report_lines
from game.ui.theme.typography import set_text_size


@pytest.mark.parametrize("size", [(1280, 720), (1920, 1080), (2560, 1440)])
@pytest.mark.parametrize(
    "fractions", [(0.29, 0.42, 0.29), (0.30, 0.36, 0.34), (0.57, 0.43)]
)
def test_shell_never_overlaps_header_content_or_footer(size, fractions):
    layout = department_layout(*size, fractions)
    frame = Rect(0, 0, *size)
    regions = [layout.header, layout.content, layout.footer]
    assert all(r.inside(frame) for r in regions)
    assert (
        layout.footer.top
        < layout.content.bottom
        < layout.content.top
        < layout.header.bottom
    )
    assert (
        abs(
            sum(r.width for r in layout.columns)
            + 14 * layout.scale * (len(fractions) - 1)
            - layout.content.width
        )
        < 0.001
    )
    assert all(a.right < b.left for a, b in zip(layout.columns, layout.columns[1:]))


class Reader(DocumentKit):
    def __init__(self):
        super().__init__()
        self.u = 1
        self.lines = []
        self.hits = []
        self.paint.fit = lambda value, width, font, bold=False: (
            value
            if len(value) * font * 0.5 <= width
            else value[: max(1, int(width / (font * 0.5)) - 1)] + "…"
        )

    def label(self, text, *args, **kwargs):
        self.lines.append(text)

    def action(self, rect, label, action, data=None, **kwargs):
        self.hits.append((rect, action, data))


@pytest.mark.parametrize("text_size", ["medium", "large"])
def test_reader_retains_all_long_text_and_paths_across_pages(text_size):
    set_text_size(text_size)
    try:
        reader = Reader()
        rect = Rect(0, 0, 240, 180)
        text = (
            "\n".join(f"Entry-{i:03} / complete report" for i in range(75))
            + "\n"
            + ("a" * 120)
            + "\nFINAL_MARKER"
        )
        reader.document("report", text, rect)
        pages = reader.capacities["report"][0]
        assert pages > 1
        all_lines = []
        for page in range(pages):
            reader.pages["report"] = page
            reader.lines = []
            reader.document("report", text, rect)
            all_lines += reader.lines
        combined = " ".join(all_lines)
        assert all(f"Entry-{i:03}" in combined for i in range(75))
        assert "FINAL_MARKER" in combined
        assert combined.count("a") >= 120
    finally:
        set_text_size("medium")


def test_paginated_list_reaches_every_item_without_changing_logical_indices():
    reader = Reader()
    rows = list(range(31))
    rect = Rect(0, 0, 300, 510)
    first = list(reader.page("items", rows, rect, 100))
    pages, capacity, _ = reader.capacities["items"]
    indices = []
    for page in range(pages):
        reader.pages["items"] = page
        visible = list(reader.page("items", rows, rect, 100))
        indices.extend(i for i, row, card in visible)
        assert all(card.inside(rect) and i == row for i, row, card in visible)
    assert indices == rows
    selected = list(reader.page("items", rows, rect, 100, selected=30))
    assert any(i == 30 for i, _, _ in selected)


def test_department_ui_actions_reach_existing_controller_once_and_disabled_do_nothing():
    deck = DepartmentDeck()
    deck.view = SimpleNamespace(_dispatch=Mock(), _open_hub_room=Mock())
    deck.click("asset_repair", 3)
    deck.view._dispatch.assert_called_once_with("asset_repair", 3)
    deck.click("ui_disabled", None)
    deck.view._dispatch.assert_called_once()
    deck.click("department_room", "research")
    deck.view._open_hub_room.assert_called_once_with("research")
    deck.click("department_select", ("research", "smartlink"))
    assert deck.selection["research"] == "smartlink"


def test_campaign_reader_retains_nested_modules_and_real_values():
    lines = report_lines(
        {
            "hungry_tide": {"progress": 37, "clues": ["clue one", "clue two"]},
            "novatek": {"status": "unknown"},
        }
    )
    text = "\n".join(lines)
    assert all(
        value in text
        for value in ["HUNGRY TIDE", "37", "clue one", "clue two", "NOVATEK", "unknown"]
    )


def test_squad_and_departments_share_the_same_real_primitives():
    assert issubclass(SquadCommandRenderer, VisualKit)
    assert issubclass(DepartmentDeck, VisualKit)
    assert SquadCommandRenderer.button is DepartmentDeck.button
    assert UIHit(1, 2, 10, 20, "select", 4).contains(5, 6)


def test_every_hangar_catalogue_type_survives_save_load(tmp_path):
    from game.gamestate import GameState
    from game.management.spec_ops_assets import asset_catalog

    gs = GameState()
    gs.spec_ops_assets = asset_catalog()
    expected = [a.to_dict() for a in gs.spec_ops_assets]
    path = tmp_path / "hangar.json"
    gs.save(str(path))
    loaded = GameState.load(str(path))
    assert [a.to_dict() for a in loaded.spec_ops_assets] == expected


def test_hangar_paging_from_any_selected_row_reaches_next_page():
    deck = DepartmentDeck()
    deck.gs = SimpleNamespace(spec_ops_assets=list(range(7)))
    deck.view = SimpleNamespace(_asset_cursor=4)
    deck.pages["hangar"] = 0
    deck.capacities["hangar"] = (2, 5, Rect(0, 0, 300, 700))
    deck.click("department_page", ("hangar", 1))
    assert deck.view._asset_cursor == 5
    deck.pages["hangar"] = 1
    deck.click("department_page", ("hangar", -1))
    assert deck.view._asset_cursor == 0


def test_narrative_operative_pager_advances_from_last_visible_row():
    from game.ui.screens.text_mission_view import TextMissionView

    view = object.__new__(TextMissionView)
    view._state = "agent_select"
    view._selected_agent_idx = 3
    view._deployed_agents = lambda: list(range(5))
    view._visual_deck = SimpleNamespace(
        pages={"narrative_agents": 0},
        capacities={"narrative_agents": (2, 4, Rect(0, 0, 300, 650))},
    )
    view._handle("department_page", ("narrative_agents", 1))
    assert view._selected_agent_idx == 4
