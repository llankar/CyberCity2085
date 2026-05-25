from types import SimpleNamespace

from game.ui.components.combat.initiative_timeline import build_initiative_timeline


def _unit(name: str, agi: int, health: int = 5, enemy_subtype: str = "grunt") -> SimpleNamespace:
    return SimpleNamespace(
        character=SimpleNamespace(name=name),
        spec_ops_asset=None,
        stats=SimpleNamespace(agi=agi),
        health=health,
        enemy_subtype=enemy_subtype,
    )


def test_timeline_keeps_active_unit_first_then_orders_by_initiative() -> None:
    players = [_unit("Alpha", 3), _unit("Bravo", 7), _unit("Charlie", 5)]
    enemies = [_unit("E1", 4, enemy_subtype="grunt"), _unit("E2", 9, enemy_subtype="elite")]

    timeline = build_initiative_timeline(players, enemies, active_player_index=0, slots=8)

    assert [entry.label for entry in timeline[:5]] == ["ALPHA", "BRAVO", "CHARLIE", "E2", "E1"]
    assert timeline[0].is_active is True


def test_timeline_marks_high_impact_enemy_threat() -> None:
    players = [_unit("Alpha", 3)]
    enemies = [_unit("Sniper", 8, enemy_subtype="sniper"), _unit("Grunt", 9, enemy_subtype="grunt")]

    timeline = build_initiative_timeline(players, enemies, active_player_index=0, slots=6)

    threat_entries = {entry.label: entry.threat for entry in timeline}
    assert threat_entries["SNIPER"] == "HIGH"
    assert threat_entries["GRUNT"] is None
