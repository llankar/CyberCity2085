"""Generate explicit walkability mask sidecars for tactical maps."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from game.map_terrain import export_walkable_mask


MAP_DIR = ROOT / "assets" / "maps"


def _iter_maps() -> list[Path]:
    return [
        path
        for path in sorted(MAP_DIR.iterdir())
        if path.suffix.lower() in {".png", ".jpg", ".jpeg"} and not path.name.endswith(".walkable.png")
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate .walkable.png sidecars for battle maps")
    parser.add_argument("--overwrite", action="store_true", help="Regenerate masks even if they already exist")
    args = parser.parse_args()

    for map_path in _iter_maps():
        mask_path = map_path.with_suffix(".walkable.png")
        if mask_path.exists() and not args.overwrite:
            print(f"skip {mask_path.name}")
            continue
        export_walkable_mask(str(map_path), str(mask_path))
        print(f"saved {mask_path.name}")


if __name__ == "__main__":
    main()
