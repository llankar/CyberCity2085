"""Focus-state transitions used by squad UI views."""


def should_open_room_for_focus(kind: str) -> bool:
    return kind == "room"


def should_trigger_action_for_focus(kind: str) -> bool:
    return kind == "action"


def should_select_mission_for_focus(kind: str, mission_count: int) -> bool:
    return kind == "mission" and mission_count > 0
