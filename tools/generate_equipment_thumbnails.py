"""Crop the approved generated contact sheets into per-item inventory art.

Sheet order follows ``default_equipment_catalog`` exactly, so the gameplay
catalogue remains authoritative and rebuilding the 42 thumbnails is repeatable.
"""

from __future__ import annotations

from pathlib import Path
import sys

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from game.management.equipment import default_equipment_catalog


SOURCE = ROOT / "assets" / "ui" / "inventory"
OUTPUT = SOURCE / "items"
SIZE = 384
SHEETS = SOURCE / "source_sheets"
GRIDS = {
    "primary_weapon": (3, 3),
    "sidearm": (3, 2),
    "armor": (4, 2),
    "utility_item": (4, 2),
    "psi_focus": (3, 2),
    "special_gear": (4, 2),
}
def build() -> int:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    count = 0
    for slot, items in default_equipment_catalog().items():
        columns, rows = GRIDS[slot]
        sheet = Image.open(SHEETS / f"{slot}.png").convert("RGB")
        cell_w, cell_h = sheet.width / columns, sheet.height / rows
        for index, item in enumerate(items):
            column, row = index % columns, index // columns
            box = (
                round(column * cell_w), round(row * cell_h),
                round((column + 1) * cell_w), round((row + 1) * cell_h),
            )
            canvas = sheet.crop(box).resize((SIZE, SIZE), Image.Resampling.LANCZOS)
            canvas.save(OUTPUT / f"{item.id}.png", optimize=True)
            count += 1
    return count


if __name__ == "__main__":
    print(f"generated={build()}")
