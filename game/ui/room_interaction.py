"""Click-first room interaction helpers for graphical command screens."""

from __future__ import annotations

from dataclasses import dataclass, field

from .facility import FacilityRoom, build_facility_rooms, facility_room_by_key
from .theme import spacing, motion_durations
from .theme.motion import ease_smoothstep, pulse_from_elapsed


@dataclass(frozen=True)
class UIRect:
    """A lightweight rectangle for hit-testing and animation."""

    left: int
    bottom: int
    width: int
    height: int

    @property
    def right(self) -> int:
        return self.left + self.width

    @property
    def top(self) -> int:
        return self.bottom + self.height

    @property
    def center_x(self) -> int:
        return self.left + self.width // 2

    @property
    def center_y(self) -> int:
        return self.bottom + self.height // 2

    def contains(self, x: int, y: int) -> bool:
        return self.left <= x <= self.right and self.bottom <= y <= self.top


@dataclass(frozen=True)
class RoomAction:
    """A command available inside an expanded room."""

    key: str
    icon: str
    label: str = ""


@dataclass(frozen=True)
class ActionButton:
    """A clickable icon button inside an expanded room."""

    action: RoomAction
    rect: UIRect
    visual_state: str = "normal"


@dataclass
class RoomUIState:
    """Mutable state for room selection and expansion animation."""

    mode: str
    active_room_key: str | None = None
    expansion: float = 0.0
    action_buttons: list[ActionButton] = field(default_factory=list)
    pulse: float = 0.0

    @property
    def is_open(self) -> bool:
        return self.active_room_key is not None


ROOM_ACTIONS = {
    "corp": {
        "executive": [
            RoomAction("advance_day", "city", "Advance day"),
            RoomAction("politics", "influence", "Fund politics"),
            RoomAction("event_0", "shield", "Event choice A"),
            RoomAction("event_1", "radar", "Event choice B"),
        ],
        "research": [
            RoomAction("start_research_0", "research", "Start project 1"),
            RoomAction("start_research_1", "armory", "Start project 2"),
            RoomAction("research", "research", "Fund research"),
        ],
        "security": [RoomAction("security", "shield", "Fund security")],
        "black_ops": [
            RoomAction("black_ops", "black_ops", "Fund black ops"),
            RoomAction("recruit_samurai", "armory", "Recruit samurai"),
            RoomAction("recruit_sniper", "radar", "Recruit sniper"),
            RoomAction("recruit_psi", "research", "Recruit psi"),
        ],
        "media": [RoomAction("politics", "influence", "Fund politics")],
        "logistics": [RoomAction("security", "shield", "Fund security")],
        "server": [RoomAction("research", "research", "Fund research")],
        "hangar": [
            RoomAction("city", "city", "City control"),
            RoomAction("squad", "squad", "Squad tower"),
        ],
    },
    "city": {
        "municipal": [
            RoomAction("advance_day", "city", "Advance day"),
            RoomAction("garrisons", "shield", "Fund garrisons"),
        ],
        "district": [RoomAction("defense_zones", "radar", "Fund zones")],
        "transit": [RoomAction("armaments", "armory", "Fund arms")],
        "factions": [RoomAction("garrisons", "shield", "Fund garrisons")],
        "public": [RoomAction("defense_zones", "radar", "Fund zones")],
        "relief": [RoomAction("armaments", "armory", "Fund arms")],
        "records": [
            RoomAction("defense_zones", "radar", "Fund zones"),
            RoomAction("event_0", "shield", "Event choice A"),
            RoomAction("event_1", "influence", "Event choice B"),
        ],
        "skybridge": [RoomAction("squad", "squad", "Squad tower")],
    },
    "squad": {
        "barracks": [
            RoomAction("recruit_samurai", "armory", "Recruit samurai"),
            RoomAction("recruit_sniper", "radar", "Recruit sniper"),
            RoomAction("recruit_psi", "research", "Recruit psi"),
        ],
        "ops": [
            RoomAction("mission_prev", "left", "Prev mission"),
            RoomAction("mission_next", "right", "Next mission"),
            RoomAction("launch", "launch", "Launch mission"),
        ],
        "intel": [
            RoomAction("mission_prev", "left", "Prev mission"),
            RoomAction("mission_next", "right", "Next mission"),
        ],
        "medbay": [
            RoomAction("agent_prev", "left", "Prev agent"),
            RoomAction("select_agent", "select", "Toggle squad"),
            RoomAction("agent_next", "right", "Next agent"),
        ],
        "armory": [
            RoomAction("select_agent", "select", "Toggle squad"),
            RoomAction("launch", "launch", "Launch mission"),
            RoomAction("toggle_asset", "armory", "Toggle support"),
        ],
        "briefing": [
            RoomAction("agent_prev", "left", "Prev agent"),
            RoomAction("agent_next", "right", "Next agent"),
            RoomAction("launch", "launch", "Launch mission"),
        ],
        "dossier": [
            RoomAction("agent_prev", "left", "Prev agent"),
            RoomAction("agent_next", "right", "Next agent"),
        ],
        "insertion": [
            RoomAction("launch", "launch", "Launch mission"),
            RoomAction("toggle_asset", "armory", "Toggle support"),
        ],
    },
}


def clamp_progress(value: float) -> float:
    """Clamp animation progress into 0-1."""
    return max(0.0, min(1.0, value))


def room_rect(room: FacilityRoom) -> UIRect:
    """Convert a facility room into a UI rectangle."""
    return UIRect(room.left, room.bottom, room.width, room.height)


def expanded_room_rect(width: int, height: int) -> UIRect:
    """Return the full-screen room target bounds."""
    margin_x = max(spacing.xl - 6, int(width * 0.035))
    margin_bottom = max(spacing.xl + 12, int(height * 0.06))
    margin_top = max(spacing.xl, int(height * 0.045))
    return UIRect(
        margin_x,
        margin_bottom,
        width - margin_x * 2,
        height - margin_bottom - margin_top,
    )


def close_button_rect(width: int, height: int) -> UIRect:
    """Return the icon-only close button area."""
    size = max(42, min(58, int(min(width, height) * 0.065)))
    return UIRect(width - size - (spacing.xl - 6), height - size - (spacing.xl - 6), size, size)


def interpolate_rect(start: UIRect, end: UIRect, progress: float) -> UIRect:
    """Ease a room rectangle toward its expanded target."""
    t = clamp_progress(progress)
    eased = ease_smoothstep(t)
    return UIRect(
        int(start.left + (end.left - start.left) * eased),
        int(start.bottom + (end.bottom - start.bottom) * eased),
        int(start.width + (end.width - start.width) * eased),
        int(start.height + (end.height - start.height) * eased),
    )


def room_at_point(
    width: int, height: int, mode: str, x: int, y: int
) -> FacilityRoom | None:
    """Return the topmost facility room under a pointer."""
    for room in reversed(build_facility_rooms(width, height, mode)):
        if room_rect(room).contains(x, y):
            return room
    return None


def actions_for_room(mode: str, room_key: str) -> list[RoomAction]:
    """Return the icon actions available in a room."""
    base_actions = list(ROOM_ACTIONS.get(mode, {}).get(room_key, []))
    utility_actions = [
        RoomAction("save", "shield", "Save game"),
        RoomAction("load", "intel", "Load game"),
    ]
    return [RoomAction("next_step", "radar", "Next step"), *base_actions, *utility_actions]


def layout_action_buttons(
    width: int, height: int, actions: list[RoomAction]
) -> list[ActionButton]:
    """Place icon buttons in the expanded room with readable labels and safe spacing."""
    if not actions:
        return []
    button_size = max(58, min(92, int(min(width, height) * 0.11)))
    gap = max(spacing.md, button_size // 3)
    total_width = len(actions) * button_size + (len(actions) - 1) * gap
    start_x = (width - total_width) // 2
    bottom = max(spacing.xl * 3 + 10, int(height * 0.16))
    buttons = []
    for index, action in enumerate(actions):
        left = start_x + index * (button_size + gap)
        buttons.append(
            ActionButton(action, UIRect(left, bottom, button_size, button_size))
        )
    return buttons


def action_at_point(buttons: list[ActionButton], x: int, y: int) -> RoomAction | None:
    """Return the clicked icon action, if any."""
    for button in buttons:
        if button.rect.contains(x, y):
            return button.action
    return None


def layout_roster_card_rects(
    rect: UIRect, buttons: list[ActionButton], card_count: int
) -> list[UIRect]:
    """Place roster cards above the action buttons inside an expanded room."""
    if card_count <= 0:
        return []
    left = rect.left + max(spacing.lg + 6, rect.width // 24)
    right = rect.right - max(spacing.lg + 6, rect.width // 24)
    action_top = max((button.rect.top for button in buttons), default=rect.bottom + 100)
    bottom = action_top + spacing.xl + 14
    top_limit = rect.top - max(250, rect.height // 3)
    card_height = max(86, min(112, int((top_limit - bottom) * 0.9)))
    if card_height < 72:
        card_height = 72
    gap = spacing.sm
    columns = min(4, max(1, card_count))
    card_width = max(190, min(260, int((right - left - gap * (columns - 1)) / columns)))
    card_rects = []
    for index in range(min(card_count, 8)):
        row = index // columns
        col = index % columns
        card_left = left + col * (card_width + gap)
        card_bottom = bottom + row * (card_height + gap)
        if card_bottom + card_height > rect.top - 96:
            break
        card_rects.append(UIRect(card_left, card_bottom, card_width, card_height))
    return card_rects


def roster_card_at_point(
    rect: UIRect, buttons: list[ActionButton], card_count: int, x: int, y: int
) -> int | None:
    """Return the roster-card index under a pointer, if any."""
    for index, card_rect in enumerate(
        layout_roster_card_rects(rect, buttons, card_count)
    ):
        if card_rect.contains(x, y):
            return index
    return None


def open_room(
    state: RoomUIState, width: int, height: int, room_key: str
) -> list[ActionButton]:
    """Select a room and refresh its buttons."""
    state.active_room_key = room_key
    state.expansion = 0.0
    state.action_buttons = layout_action_buttons(
        width, height, actions_for_room(state.mode, room_key)
    )
    return state.action_buttons


def close_room(state: RoomUIState) -> None:
    """Close the active room immediately."""
    state.active_room_key = None
    state.expansion = 0.0
    state.action_buttons = []


ROOM_TRANSITION_SECONDS = motion_durations.room_transition_seconds


def step_room_ui(state: RoomUIState, delta_time: float) -> None:
    """Advance room expansion and ambient pulse animation."""
    state.pulse = (state.pulse + delta_time) % 10.0
    if state.active_room_key is not None:
        speed = 1.0 / max(ROOM_TRANSITION_SECONDS, 0.01)
        state.expansion = clamp_progress(state.expansion + delta_time * speed)


def active_room_rect(
    state: RoomUIState, width: int, height: int
) -> tuple[FacilityRoom, UIRect] | None:
    """Return the current animated room rectangle."""
    if state.active_room_key is None:
        return None
    rooms = build_facility_rooms(width, height, state.mode)
    room = facility_room_by_key(rooms, state.active_room_key)
    return (
        room,
        interpolate_rect(
            room_rect(room), expanded_room_rect(width, height), state.expansion
        ),
    )
