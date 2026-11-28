"""Idempotent equipment custody across tactical mission resolution."""

from __future__ import annotations

from collections import Counter

from game.management.equipment import EQUIPMENT_SLOTS


def snapshot_deployed_equipment(characters, deployed_names) -> list[dict]:
    """Capture deployed loadouts before combat can remove roster entries."""
    by_name = {character.name: character for character in characters}
    rows = []
    for name in deployed_names:
        character = by_name.get(name)
        if character is None:
            continue
        items = []
        for slot in EQUIPMENT_SLOTS:
            item = character.loadout.item_for_slot(slot)
            if item is not None:
                items.append({"slot": slot, "id": item.id, "name": item.name})
        rows.append({"agent_name": name, "items": items})
    return rows


def snapshot_unit_equipment(units) -> list[dict]:
    names = []
    characters = []
    for unit in units:
        character = getattr(unit, "character", None)
        if character is not None and character.name not in names:
            names.append(character.name)
            characters.append(character)
    return snapshot_deployed_equipment(characters, names)


def resolve_equipment_custody(state, snapshot: list[dict], victory: bool) -> dict:
    """Recover casualty gear unless a failed mission permanently loses everyone.

    The operation mutates only campaign quantities and is expected to run inside
    the existing atomic mission-resolution transaction.
    """
    roster_names = {character.name for character in state.characters}
    deployed_names = {row["agent_name"] for row in snapshot}
    dead_rows = [row for row in snapshot if row["agent_name"] not in roster_names]
    total_items = Counter(
        item["id"] for row in snapshot for item in row.get("items", [])
    )
    recovered_items = Counter(
        item["id"] for row in dead_rows for item in row.get("items", [])
    )
    total_wipe = bool(deployed_names) and not (deployed_names & roster_names)
    lose_deployment = total_wipe and not victory
    lost_items = Counter()
    if lose_deployment:
        reserve_items = Counter(
            item["id"]
            for row in snapshot_deployed_equipment(state.characters, roster_names)
            for item in row["items"]
        )
        for item_id, quantity in total_items.items():
            available = max(0, int(state.owned_equipment.get(item_id, 0)))
            removed = min(max(0, available - reserve_items[item_id]), quantity)
            if removed:
                state.owned_equipment[item_id] = available - removed
                if state.owned_equipment[item_id] == 0:
                    state.owned_equipment.pop(item_id)
                lost_items[item_id] = removed
        recovered_items.clear()

    status = "lost" if lose_deployment else ("recovered" if dead_rows else "retained")
    return {
        "status": status,
        "total_wipe": total_wipe,
        "deployed_agents": len(deployed_names),
        "casualties": len(dead_rows),
        "recovered": dict(sorted(recovered_items.items())),
        "lost": dict(sorted(lost_items.items())),
    }
