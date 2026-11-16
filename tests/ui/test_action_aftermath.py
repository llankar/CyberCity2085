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


def test_movement_does_not_announce_zero_attack_damage() -> None:
    line = build_action_aftermath_line(action_label="MOVE")
    assert line == "MOVE"


def test_elimination_is_distinct_from_suppression_and_aid_is_not_an_attack():
    line=build_action_aftermath_line(action_label="FIRE",damage=4,defeated_target=True,status_applied="CRITICAL")
    assert "HOSTILE DOWN" in line and "CRITICAL" in line
    assert "SUPPRESSION" not in line
    aid=build_action_aftermath_line(action_label="FIRST AID",status_applied="Restores 2 HP")
    assert "DMG" not in aid and "Restores 2 HP" in aid


def test_action_aftermath_line_appends_skill_check_outcome() -> None:
    line = build_action_aftermath_line(
        action_label="HACK",
        damage=0,
        skill_check_outcome="Tech Check: roll 4 -> total 7 (target 6) [SUCCESS]",
    )
    assert "HACK | DMG 0" in line
    assert "Tech Check: roll 4 -> total 7 (target 6) [SUCCESS]" in line
