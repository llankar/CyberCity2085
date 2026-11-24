from game.character import Character
from game.gamestate import GameState
from game.management.events import ActiveEvent, EventChoice, EventTemplate
from game.management.weekly_planning import apply_weekly_directive, build_management_forecast


def _funded_state() -> GameState:
    state = GameState(characters=[Character("Mara", stress=60, recovery_turns=2)])
    state.add_funds(1_000, "test", "weekly planning test")
    return state


def test_forecast_exposes_money_pressure_readiness_and_event_urgency() -> None:
    state = _funded_state()
    state.active_events = [
        ActiveEvent(
            id="urgent",
            template=EventTemplate(
                title="Grid Riots",
                category="SOCIAL_UNREST",
                description="The district is close to breaking.",
                severity=4,
                choices=[EventChoice("respond", "Respond")],
                expiration_days=2,
            ),
            created_day=state.calendar.current_day,
            expires_day=state.calendar.current_day + 2,
        )
    ]

    forecast = build_management_forecast(state)

    assert forecast.projected_net == forecast.projected_income - forecast.asset_upkeep
    assert forecast.total_agents == 1
    assert forecast.ready_agents == 0
    assert forecast.urgent_event == "Grid Riots"
    assert forecast.urgent_event_days == 2
    assert forecast.threat_level in {"stable", "guarded", "high", "critical"}


def test_only_one_directive_can_be_applied_each_week() -> None:
    state = _funded_state()

    first_ok, _ = apply_weekly_directive(state, "crew_recovery")
    second_ok, second_message = apply_weekly_directive(state, "civil_defense")

    assert first_ok is True
    assert second_ok is False
    assert "already set" in second_message
    assert state.characters[0].stress == 45
    assert state.characters[0].recovery_turns == 1


def test_new_week_unlocks_a_new_directive_and_effects_are_visible() -> None:
    state = _funded_state()
    initial_stability = state.district.stability
    initial_unrest = state.district.unrest

    ok, _ = apply_weekly_directive(state, "civil_defense")
    state.advance_days(7, "test planning cycle")
    next_ok, _ = apply_weekly_directive(state, "black_intel")

    assert ok and next_ok
    assert state.district.stability == min(100, initial_stability + 8)
    assert state.district.unrest == max(0, initial_unrest - 6)
    assert state.strategic_resources["intel"] == 4
    assert state.strategic_resources["influence"] == 2


def test_weekly_directive_round_trips_in_save(tmp_path) -> None:
    state = _funded_state()
    apply_weekly_directive(state, "black_intel")
    path = tmp_path / "weekly-plan.json"
    state.save(str(path))

    loaded = GameState.load(str(path))

    assert loaded.weekly_directive_week == state.calendar.current_week
    assert loaded.weekly_directive_id == "black_intel"
    assert build_management_forecast(loaded).directive_locked is True


def test_old_save_without_weekly_fields_loads_unlocked(tmp_path) -> None:
    state = _funded_state()
    path = tmp_path / "legacy.json"
    state.save(str(path))
    import json

    payload = json.loads(path.read_text(encoding="utf-8"))
    payload.pop("weekly_directive_week")
    payload.pop("weekly_directive_id")
    path.write_text(json.dumps(payload), encoding="utf-8")

    loaded = GameState.load(str(path))
    assert loaded.weekly_directive_week == 0
    assert loaded.weekly_directive_id == ""


def test_command_room_exposes_each_weekly_directive_as_an_action() -> None:
    from game.ui.room_interaction import actions_for_room

    action_keys = {action.key for action in actions_for_room("hub", "command")}

    assert {
        "weekly_directive_civil_defense",
        "weekly_directive_crew_recovery",
        "weekly_directive_black_intel",
    } <= action_keys
