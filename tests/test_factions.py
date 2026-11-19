"""Faction content coverage."""

from game.factions import create_core_campaign_factions, create_vertical_slice_factions


def test_vertical_slice_factions_remain_compatible() -> None:
    factions = create_vertical_slice_factions()
    names = [faction.name for faction in factions]

    assert names[:3] == ["Aegis Dynamics", "Warrens Free Clinic", "Chrome Jackals"]
    assert all(faction.revealed for faction in factions)


def test_core_campaign_factions_cover_wave6_identity_set() -> None:
    factions = create_core_campaign_factions()
    by_name = {faction.name: faction for faction in factions}

    required = {
        "Starvers",
        "Three Sevens",
        "Pharmacorp",
        "Novatek",
        "Raiders",
        "Mutants",
        "Corporate Security",
        "Preservationist AIs",
        "Exterminator AIs",
        "New York Civic Grid",
    }
    assert required.issubset(by_name)
    assert by_name["Starvers"].category == "starver"
    assert by_name["Three Sevens"].category == "corporate_antagonist"
    assert by_name["Pharmacorp"].category == "corporate"
    assert by_name["Novatek"].category == "corporate"
    assert by_name["Corporate Security"].category == "security"
    assert by_name["Preservationist AIs"].category == "hidden_ai"
    assert not by_name["Preservationist AIs"].revealed
    assert not by_name["Exterminator AIs"].revealed


def test_core_campaign_factions_can_omit_hidden_ai_for_early_campaign_lists() -> None:
    factions = create_core_campaign_factions(include_hidden=False)
    names = {faction.name for faction in factions}

    assert "Preservationist AIs" not in names
    assert "Exterminator AIs" not in names
    assert "Three Sevens" in names
