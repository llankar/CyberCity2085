"""Deterministic input integration checks against an actual hidden BattleView."""

from unittest.mock import patch


def exercise_turn_controls(view):
    """End each agent through real mouse dispatch, then run the real enemy phase."""
    import arcade
    start_turn = view.turn_number
    positions = [unit.position for unit in view.player_units]
    checks = []

    def click(key):
        view.on_draw()
        _, rect = next(button for button in view.combat_action_buttons if button[0].key == key)
        view.on_mouse_press(rect.left+rect.width/2,rect.bottom+rect.height/2,arcade.MOUSE_BUTTON_LEFT,0)

    actor = view.player_units[view.active_index]
    ap = actor.action_points
    click("end_turn")
    assert view.pending_end_turn_confirmation and actor.action_points == ap
    view.on_key_press(arcade.key.ESCAPE,0)
    assert not view.pending_end_turn_confirmation and not view._paused and actor.action_points == ap
    checks.append("escape_cancels_end_confirmation_without_pausing_or_spending_ap")
    click("end_turn")
    click("move")
    assert not view.pending_end_turn_confirmation and actor.action_points == ap
    view.on_key_press(arcade.key.ESCAPE,0)
    assert not view._pointer_moving
    checks.append("choosing_another_action_clears_stale_confirmation")

    ended = []
    for _ in range(len(view.player_units)):
        actor = view.player_units[view.active_index]
        before = actor.action_points
        click("end_turn")
        assert view.pending_end_turn_confirmation and actor.action_points == before
        ended.append(actor.character.name)
        click("end_turn")
        assert not view.pending_end_turn_confirmation
    assert view.turn == "player" and view.turn_number == start_turn+1
    assert view.active_index == 0
    assert all(unit.action_points == 2 for unit in view.player_units)
    assert [unit.position for unit in view.player_units] == positions
    checks.append("second_button_click_ends_each_agent_and_runs_one_real_enemy_phase")
    checks.append("next_player_turn_restores_ap_and_active_selection")
    return {"checks":checks,"agents_ended":ended,"turn_before":start_turn,"turn_after":view.turn_number,
            "next_phase":view.turn,"allied_positions_unchanged":True}


def exercise_fire_controls(view, target, *, settle=False):
    """Exercise real handlers/engine; caller owns an explicitly hidden window."""
    import arcade
    player = view.player_units[view.active_index]
    initial_ap = player.action_points
    initial_hp = target.health
    initial_positions = [unit.position for unit in view.player_units]
    journal_preference = view._show_combat_log
    checks = []
    view.on_key_press(arcade.key.ESCAPE, 0)
    assert not view.selecting_target and player.action_points == initial_ap
    checks.append("keyboard_cancel_costs_no_ap")

    def click_fire():
        view.on_draw()
        _, rect = next(button for button in view.combat_action_buttons if button[0].key == "fire")
        view.on_mouse_press(rect.left+rect.width/2, rect.bottom+rect.height/2, arcade.MOUSE_BUTTON_LEFT, 0)
        assert view.selecting_target and player.action_points == initial_ap
        assert view.pending_attack == "shoot"

    click_fire()
    checks.append("action_bar_opens_real_fire_targeting")
    view.on_mouse_press(0, 0, arcade.MOUSE_BUTTON_RIGHT, 0)
    assert not view.selecting_target and player.action_points == initial_ap
    assert view._show_combat_log == journal_preference
    checks.append("pointer_cancel_preserves_ap_and_journal")

    click_fire()
    view.on_draw()
    dx, dy = view._pointer_camera_offset
    point = (target.position[0]-dx, target.position[1]-dy)
    view.on_mouse_press(*point, arcade.MOUSE_BUTTON_LEFT, 0)
    assert view.selecting_target and player.action_points == initial_ap and target.health == initial_hp
    checks.append("first_target_click_is_preview_only")
    with patch("game.combat.attack_resolution.random.random", return_value=0.0):
        view.on_mouse_press(*point, arcade.MOUSE_BUTTON_LEFT, 0)
    assert player.action_points == initial_ap-1
    assert 0 < target.health < initial_hp
    assert target.health == target.stats.hp
    assert not view.selecting_target and view.pending_attack is None
    assert view._show_combat_log == journal_preference
    assert [unit.position for unit in view.player_units] == initial_positions
    assert any("dmg" in line for line in view.combat_log_messages)
    assert view._flash_alpha == 0, "Outgoing attacks must use local feedback, not a screen-edge flash"
    checks.append("second_click_resolves_real_attack_once_for_one_ap")
    if settle:
        sprite_positions = [(unit.sprite.center_x,unit.sprite.center_y) for unit in view.player_units]
        for _ in range(150):
            view.on_update(1/60)
        assert view.attack_line is None and view.attack_timer == 0
        assert not any((view.damage_popups,view.particles,view._unit_flashes,
                        view._death_rings,view._muzzle_flashes,view._psi_waves))
        assert view._shake_intensity == view._flash_alpha == view._aftermath_timer == 0
        assert player.action_points == initial_ap-1
        assert sprite_positions == [(unit.sprite.center_x,unit.sprite.center_y) for unit in view.player_units]
        assert [unit.position for unit in view.player_units] == initial_positions
        assert view._perform_combat_action("fire") and view.selecting_target
        view.on_key_press(arcade.key.ESCAPE,0)
        assert not view.selecting_target and player.action_points == initial_ap-1
        checks.append("effects_finish_and_next_action_remains_available_without_spending_ap")
    return {"checks":checks,"actor_ap_before":initial_ap,"actor_ap_after":player.action_points,
            "target_hp_before":initial_hp,"target_hp_after":target.health,
            "outgoing_edge_flash_alpha":view._flash_alpha,
            "rng":"forced hit and critical; no balance claim",
            "journal_preference_preserved":True}
