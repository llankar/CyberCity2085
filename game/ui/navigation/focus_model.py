from __future__ import annotations

from dataclasses import dataclass

from ..facility import build_facility_rooms


@dataclass(frozen=True)
class FocusItem:
    key: str
    kind: str


@dataclass
class ViewFocusModel:
    view_key: str
    room_keys: list[str]
    action_keys: list[str]
    mission_count: int = 0
    current_index: int = 0

    def _items(self) -> list[FocusItem]:
        items = [FocusItem(room, "room") for room in self.room_keys]
        items.extend(FocusItem(action, "action") for action in self.action_keys)
        items.extend(
            FocusItem(f"mission_{index}", "mission") for index in range(self.mission_count)
        )
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
        if self._items():
            self.current_index %= len(self._items())
        else:
            self.current_index = 0


def build_view_focus_model(view_key: str, width: int, height: int) -> ViewFocusModel:
    room_keys = [room.key for room in build_facility_rooms(width, height, view_key)]
    return ViewFocusModel(view_key=view_key, room_keys=room_keys, action_keys=[])
