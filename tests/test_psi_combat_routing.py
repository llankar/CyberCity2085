"""Psi agents retain offensive powers alongside squad stress support."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_godot_routes_mind_spike_as_a_targeted_psi_attack() -> None:
    source = (ROOT / "godot/combat_missions_ui/scripts/combat_mission_ui.gd").read_text(encoding="utf-8")
    assert '"Mind Spike":    {"type": "PSI"' in source
    assert '"Psi Focus":     {"type": "PSI_HEAL"' in source
    assert '"PSI":       return "PSI"' in source
    assert '["FIRE", "MELEE", "PSI"]' in source


def test_psi_fallback_roster_exposes_attack_and_support() -> None:
    source = (ROOT / "godot/combat_missions_ui/scripts/combat_mission_ui.gd").read_text(encoding="utf-8")
    assert '"psi":    agent_actions = ["Move", "Defend", "Mind Spike", "Psi Focus", "Pistol Shot"]' in source
    assert '"psi":               int(agent.get("psi", 5))' in source
    assert 'clean == "" or clean.to_lower() == "null"' not in source


def test_hud_distinguishes_offensive_and_support_psi_actions() -> None:
    source = (ROOT / "godot/combat_missions_ui/scripts/visual_hud.gd").read_text(encoding="utf-8")
    assert '"Mind Spike":"MIND SPIKE"' in source
    assert '"Psi Focus":"PSI FOCUS"' in source
