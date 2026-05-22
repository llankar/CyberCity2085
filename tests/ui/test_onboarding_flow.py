from game.gamestate import GameState
from game.ui.onboarding.tutorial_overlay import overlay_state_for_screen


def test_tutorial_step_progression():
    gs = GameState()
    assert gs.mark_tutorial_event("entered_room") is True
    assert gs.tutorial_progress["tutorial_step_index"] == 1
    assert gs.mark_tutorial_event("formed_squad") is False
    gs.mark_tutorial_event("selected_agent")
    gs.mark_tutorial_event("formed_squad")
    gs.mark_tutorial_event("opened_mission_board")
    gs.mark_tutorial_event("launched_mission")
    gs.mark_tutorial_event("used_battle_controls")
    assert gs.tutorial_progress["tutorial_completed"] is True


def test_overlay_visibility_on_target_screens():
    gs = GameState()
    corp = overlay_state_for_screen(gs.tutorial_progress, "corp")
    squad = overlay_state_for_screen(gs.tutorial_progress, "squad")
    assert corp["visible"] is True
    assert squad["visible"] is False


def test_help_panel_content_presence_in_english():
    gs = GameState()
    panel = overlay_state_for_screen(gs.tutorial_progress, "battle")["help"]
    assert "Objective" not in panel["objective"]  # sentence content only
    assert any("Arrows move" in control for control in panel["controls"])
    assert "objective" in panel
    assert panel["next"]
