import pytest

from game.agents.cyberware import (
    CATALOGUE,
    BY_ID,
    MAX_HUMANITY,
    combat_bonuses,
    humanity_remaining,
    purchase_or_remove,
    toggle_cyberware,
)
from game.character import Character
from game.combat.godot_bridge import _agent_payload
from game.combat.attack_resolution import build_attack_context
from game.combat_system import create_player_units
from game.stats import EnemyStats
from game.unit import Unit
from game.ui.components.combat.initiative_timeline import _initiative_value


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
    assert chrome_payload["humanity"] == 1
    assert combat_bonuses(chrome.installed_cyberware)["crit"] == 1


def test_removing_implant_restores_capacity():
    installed, _ = toggle_cyberware(["subdermal_mesh"], "subdermal_mesh")
    assert installed == []
    assert humanity_remaining(installed) == 5


def test_catalogue_is_grouped_by_body_zone_and_prices_scale_with_power():
    assert {item.zone for item in CATALOGUE} == {
        "HEAD", "EYES", "ARMS", "TORSO", "CIRCULATORY", "NERVOUS SYSTEM", "LEGS"
    }
    by_tier = {}
    for item in CATALOGUE:
        by_tier.setdefault(item.power_tier, []).append(item)
    assert set(by_tier) == {1, 2, 3}
    for lower, upper in ((1, 2), (2, 3)):
        assert max(item.credit_cost for item in by_tier[lower]) < min(
            item.credit_cost for item in by_tier[upper]
        )
        assert max(item.humanity_cost for item in by_tier[lower]) < min(
            item.humanity_cost for item in by_tier[upper]
        )


def test_cyberware_purchase_charges_credits_and_rejects_unaffordable_surgery():
    cost = BY_ID["smart_eye"].credit_cost
    installed, funds, changed, reason = purchase_or_remove([], "smart_eye", cost)
    assert (installed, funds, changed, reason) == (["smart_eye"], 0, True, "installed")
    unchanged, funds, changed, reason = purchase_or_remove(installed, "tactical_coprocessor", 50)
    assert unchanged == installed and funds == 50 and not changed and reason == "funds"
    removed, funds, changed, reason = purchase_or_remove(installed, "smart_eye", 50)
    assert (removed, funds, changed, reason) == ([], 50, True, "removed")


def test_expensive_cyberware_also_consumes_more_humanity():
    cost = BY_ID["tactical_coprocessor"].credit_cost
    installed, funds, changed, reason = purchase_or_remove([], "tactical_coprocessor", cost)
    assert changed and reason == "installed" and funds == 0
    assert humanity_remaining(installed) == 2
    unchanged, funds, changed, reason = purchase_or_remove(installed, "subdermal_mesh", funds)
    assert unchanged == installed and funds == 0 and not changed and reason == "funds"


def test_each_body_zone_offers_a_choice_and_accepts_only_one_implant():
    from game.agents.cyberware import ZONE_ORDER, catalogue_for_zone, normalize_installed

    assert all(len(catalogue_for_zone(zone)) >= 10 for zone in ZONE_ORDER)
    starting = 20_000
    installed, funds, changed, reason = purchase_or_remove([], "smart_eye", starting)
    assert changed and reason == "installed"
    installed, funds, changed, reason = purchase_or_remove(installed, "predator_optics", funds)
    assert changed and reason == "replaced"
    assert "smart_eye" not in installed and installed == ["predator_optics"]
    assert funds == starting - BY_ID["smart_eye"].credit_cost - BY_ID["predator_optics"].credit_cost
    assert normalize_installed(["smart_eye", "predator_optics"]) == ["smart_eye"]


def test_legs_are_a_real_single_slot_with_tactical_bonuses():
    starting = 20_000
    installed, funds, changed, reason = purchase_or_remove([], "stride_servos", starting)
    assert changed and reason == "installed" and funds == starting - BY_ID["stride_servos"].credit_cost
    installed, funds, changed, reason = purchase_or_remove(installed, "sprinter_myomers", funds)
    assert changed and reason == "replaced"
    assert installed == ["sprinter_myomers"]
    assert combat_bonuses(installed) == {"initiative": 3, "defense": 1}


def test_arcade_unit_keeps_ap_and_combat_bonuses_across_turns():
    chrome = Character(
        "Chrome",
        role="samurai",
        installed_cyberware=["smart_eye", "titan_arm", "tactical_coprocessor"],
    )
    unit = create_player_units([chrome])[0]
    assert unit.action_points == unit.base_action_points == 3
    assert unit.tactical_aim_bonus == 2
    assert unit.tactical_melee_bonus == 4
    unit.action_points = 0
    unit.reset_actions()
    assert unit.action_points == 3

    target = Unit(position=(32, 0), stats=EnemyStats(defense=2), health=10, unit_type="enemy")
    plain = create_player_units([Character("Plain", role="samurai")])[0]
    plain.position = unit.position
    melee = build_attack_context(unit, target, "melee")
    plain_melee = build_attack_context(plain, target, "melee")
    assert melee.attack_value == plain_melee.attack_value + 4
    ranged = build_attack_context(unit, target, "ranged")
    plain_ranged = build_attack_context(plain, target, "ranged")
    assert ranged.attack_value == plain_ranged.attack_value + 2
    assert ranged.crit_chance == pytest.approx(0.17)
    assert _initiative_value(unit) == unit.stats.agi + 1


def test_arcade_subdermal_implant_applies_hp_and_defense():
    plain = create_player_units([Character("Plain", role="sniper")])[0]
    armored = create_player_units([
        Character("Armored", role="sniper", installed_cyberware=["subdermal_mesh"])
    ])[0]
    assert armored.stats.max_hp == plain.stats.max_hp + 4
    assert armored.stats.defense == plain.stats.defense + 2


def test_cybereyes_tiers_extend_tactical_vision_by_one_two_and_three_cells():
    assert BY_ID["smart_eye"].name == "Cybereyes Mk I"
    assert BY_ID["smart_eye"].combat_bonuses["vision_range"] == 1
    assert BY_ID["predator_optics"].name == "Cybereyes Mk II"
    assert BY_ID["predator_optics"].combat_bonuses["vision_range"] == 2
    assert BY_ID["omniscient_optics"].name == "Cybereyes Mk III"
    assert BY_ID["omniscient_optics"].combat_bonuses["vision_range"] == 3
