"""Pure room-action transitions for RPG/Squad UI."""

from dataclasses import dataclass


@dataclass(frozen=True)
class RoomActionResult:
    cursor_index: int
    selected_agent_names: list[str]
    selected_asset_ids: list[str]
    pending_breakdown_confirmation: bool
    pending_breakdown_mission_id: str | None


def select_roster_card(
    card_index: int,
    character_count: int,
    selected_agent_names: list[str],
    selected_asset_ids: list[str],
) -> RoomActionResult | None:
    if not 0 <= card_index < character_count:
        return None
    return RoomActionResult(
        cursor_index=card_index,
        selected_agent_names=list(selected_agent_names),
        selected_asset_ids=list(selected_asset_ids),
        pending_breakdown_confirmation=False,
        pending_breakdown_mission_id=None,
    )


def apply_agent_toggle(
    selected_agent_names: list[str],
    updated_selected_agent_names: list[str],
    selected_asset_ids: list[str],
) -> RoomActionResult:
    return RoomActionResult(
        cursor_index=0,
        selected_agent_names=list(updated_selected_agent_names),
        selected_asset_ids=list(selected_asset_ids),
        pending_breakdown_confirmation=False,
        pending_breakdown_mission_id=None,
    )


def apply_asset_toggle(
    cursor_index: int,
    selected_agent_names: list[str],
    updated_selected_asset_ids: list[str],
) -> RoomActionResult:
    return RoomActionResult(
        cursor_index=cursor_index,
        selected_agent_names=list(selected_agent_names),
        selected_asset_ids=list(updated_selected_asset_ids),
        pending_breakdown_confirmation=False,
        pending_breakdown_mission_id=None,
    )
