from pathlib import Path
import importlib.util


def _load_module(path: str, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_mission_selection_wraparound():
    mission = _load_module("game/ui/controllers/mission_controller.py", "mission_controller")
    assert mission.previous_mission_index(0, 3) == 2
    assert mission.next_mission_index(2, 3) == 0
    assert mission.mission_index_from_focus_key("mission_7", 3) == 1


def test_room_transition_selection_resets_pending_breakdown():
    room = _load_module("game/ui/controllers/room_actions_controller.py", "room_actions_controller")
    result = room.select_roster_card(1, 4, ["A"], ["asset-1"])
    assert result is not None
    assert result.cursor_index == 1
    assert result.pending_breakdown_confirmation is False
    assert result.pending_breakdown_mission_id is None


def test_agent_and_asset_actions_reset_breakdown_state():
    room = _load_module("game/ui/controllers/room_actions_controller.py", "room_actions_controller")
    agent_state = room.apply_agent_toggle(["A"], ["A", "B"], ["asset-1"])
    assert agent_state.selected_agent_names == ["A", "B"]
    assert agent_state.pending_breakdown_confirmation is False

    asset_state = room.apply_asset_toggle(2, ["A", "B"], ["asset-2"])
    assert asset_state.cursor_index == 2
    assert asset_state.selected_asset_ids == ["asset-2"]
    assert asset_state.pending_breakdown_mission_id is None


def test_focus_transitions():
    focus = _load_module("game/ui/controllers/focus_controller.py", "focus_controller")
    assert focus.should_open_room_for_focus("room") is True
    assert focus.should_trigger_action_for_focus("action") is True
    assert focus.should_select_mission_for_focus("mission", 2) is True
    assert focus.should_select_mission_for_focus("mission", 0) is False


def test_views_import_controller_wiring():
    source = Path("game/views.py").read_text(encoding="utf-8")
    assert "from .ui.controllers.mission_controller import" in source
    assert "from .ui.controllers.room_actions_controller import" in source
    assert "from .ui.controllers.focus_controller import" in source
