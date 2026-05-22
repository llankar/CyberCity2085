from __future__ import annotations

from dataclasses import dataclass

from ..facility import build_facility_rooms


@dataclass(frozen=True)
class FocusItem:
    key: str
    kind: str


VIEW_ROOM_ORDER: dict[str, list[str]] = {
    "command_center": ["executive", "hangar", "research", "security", "media", "black_ops", "logistics", "server"],
    "facility": ["executive", "hangar", "research", "security", "media", "black_ops", "logistics", "server"],
    "command_deck": ["briefing", "armory", "ops", "intel", "dossier", "medbay", "barracks", "insertion"],
    "mission_board": ["ops", "intel", "briefing", "insertion", "armory", "medbay", "barracks", "dossier"],
}


@dataclass
class ViewFocusModel:
    view_key: str
    room_keys: list[str]
    action_keys: list[str]
    mission_count: int = 0
    agent_count: int = 0
    current_index: int = 0

    def _items(self) -> list[FocusItem]:
        items = [FocusItem(room, "room") for room in self.room_keys]
        items.extend(FocusItem(action, "action") for action in self.action_keys)
        items.extend(FocusItem(f"mission_{index}", "mission") for index in range(self.mission_count))
        items.extend(FocusItem(f"agent_{index}", "agent") for index in range(self.agent_count))
        return items

    def active(self) -> FocusItem | None:
        items = self._items()
        if not items:
            return None
        self.current_index %= len(items)
        return items[self.current_index]

    def move(self, step: int) -> FocusItem | None:
        items = self._items()
        if not items:
            return None
        self.current_index = (self.current_index + step) % len(items)
        return self.active()

    def set_actions(self, action_keys: list[str]) -> None:
        self.action_keys = action_keys
        self._normalize_index()

    def set_list_counts(self, mission_count: int, agent_count: int) -> None:
        self.mission_count = max(0, mission_count)
        self.agent_count = max(0, agent_count)
        self._normalize_index()

    def _normalize_index(self) -> None:
        items = self._items()
        self.current_index = self.current_index % len(items) if items else 0


def _normalize_view_key(view_key: str) -> str:
    aliases = {"corp": "command_center", "city": "command_center", "squad": "command_deck", "battle": "mission_board"}
    return aliases.get(view_key, view_key)


def build_view_focus_model(view_key: str, width: int, height: int) -> ViewFocusModel:
    normalized_key = _normalize_view_key(view_key)
    rooms = build_facility_rooms(width, height, "squad" if normalized_key in {"command_deck", "mission_board"} else "corp")
    discovered_keys = [room.key for room in rooms]
    preferred_order = VIEW_ROOM_ORDER.get(normalized_key, discovered_keys)
    ordered_keys = [key for key in preferred_order if key in discovered_keys]
    ordered_keys.extend(key for key in discovered_keys if key not in ordered_keys)
    return ViewFocusModel(view_key=normalized_key, room_keys=ordered_keys, action_keys=[])
