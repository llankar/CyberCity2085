from game.ui.components.combat.action_aftermath import build_action_aftermath_line


def test_action_aftermath_line_includes_damage_status_and_suppression() -> None:
    line = build_action_aftermath_line(
        action_label="SHOOT",
        damage=4,
        status_applied="touché",
        suppression_created=True,
    )
    assert "SHOOT" in line
    assert "DMG 4" in line
    assert "STATUT touché" in line
    assert "SUPPRESSION créée" in line


def test_action_aftermath_line_keeps_fixed_tokens_for_move() -> None:
    line = build_action_aftermath_line(action_label="MOVE")
    assert line == "MOVE | DMG 0"


def test_action_aftermath_line_appends_skill_check_outcome() -> None:
    line = build_action_aftermath_line(
        action_label="HACK",
        damage=0,
        skill_check_outcome="Tech Check: roll 4 -> total 7 (target 6) [SUCCESS]",
    )
    assert "HACK | DMG 0" in line
    assert "Tech Check: roll 4 -> total 7 (target 6) [SUCCESS]" in line
