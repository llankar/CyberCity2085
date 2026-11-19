"""Mission selection and transition helpers for squad UI."""


def previous_mission_index(current_index: int, mission_count: int) -> int:
    if mission_count <= 0:
        return 0
    return (current_index - 1) % mission_count


def next_mission_index(current_index: int, mission_count: int) -> int:
    if mission_count <= 0:
        return 0
    return (current_index + 1) % mission_count


def mission_index_from_focus_key(focus_key: str, mission_count: int) -> int:
    if mission_count <= 0:
        return 0
    mission_idx = int(focus_key.rsplit("_", 1)[-1])
    return mission_idx % mission_count
