"""Shared equipment illustration lookup for management interfaces."""

from pathlib import Path


def equipment_art_path(item, slot: str) -> str:
    """Return the item's Inventory artwork, with the legacy slot art as fallback."""
    if item is not None:
        item_path = Path("assets/ui/inventory/items") / f"{item.id}.png"
        if item_path.is_file():
            return item_path.as_posix()
    return f"assets/ui/inventory/{slot}.png"
