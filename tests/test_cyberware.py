from game.agents.cyberware import (
    MAX_HUMANITY,
    combat_bonuses,
    humanity_remaining,
    toggle_cyberware,
)
from game.character import Character
from game.combat.godot_bridge import _agent_payload


def test_humanity_starts_at_five_and_never_drops_below_zero():
    assert humanity_remaining([]) == MAX_HUMANITY == 5
    installed, changed = toggle_cyberware([], "kerenzikov_reflex")
    assert changed and humanity_remaining(installed) == 3
    installed, changed = toggle_cyberware(installed, "subdermal_mesh")
    assert changed and humanity_remaining(installed) == 1
    unchanged, changed = toggle_cyberware(installed, "titan_arm")
    assert not changed and unchanged == installed
    assert humanity_remaining(unchanged) == 1


def test_character_cyberware_round_trips_through_save_data():
    agent = Character("Chrome", role="samurai", installed_cyberware=["smart_eye", "titan_arm"])
    loaded = Character.from_dict(agent.to_dict())
    assert loaded.installed_cyberware == ["smart_eye", "titan_arm"]
    assert loaded.humanity == 2


def test_combat_payload_applies_cyberware_bonuses():
    plain = Character("Plain", role="sniper")
    chrome = Character("Chrome", role="sniper", installed_cyberware=["smart_eye", "tactical_coprocessor"])
    plain_payload = _agent_payload(plain)
    chrome_payload = _agent_payload(chrome)
    assert chrome_payload["aim"] == plain_payload["aim"] + 2
    assert chrome_payload["initiative"] == plain_payload["initiative"] + 1
    assert chrome_payload["action_points"] == 5
    assert chrome_payload["humanity"] == 3
    assert combat_bonuses(chrome.installed_cyberware)["crit"] == 1


def test_removing_implant_restores_capacity():
    installed, _ = toggle_cyberware(["subdermal_mesh"], "subdermal_mesh")
    assert installed == []
    assert humanity_remaining(installed) == 5
