"""Apply reviewed presentation-only human scale ratios by environment profile."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RATIOS = {
    "urban": 0.015,
    "open_wasteland": 0.015,
    "industrial": 0.020,
    "interior": 0.020,
    "small_interior": 0.020,
}


def apply_profiles(path: Path, write: bool = False) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    maps = data["maps"]
    unknown = sorted({row.get("profile", "") for row in maps.values()} - RATIOS.keys())
    if unknown:
        raise ValueError(f"unknown presentation profiles: {unknown}")
    changed = []
    for name, row in maps.items():
        ratio = RATIOS[row["profile"]]
        if float(row.get("human_height_ratio", -1)) != ratio:
            changed.append(name)
            row["human_height_ratio"] = ratio
    data["notes"] = (
        "Art-directed standing-silhouette height relative to source width; "
        "reviewed against visible cars, furniture, doors, machines and wrecks. "
        "Presentation only: no tactical scale, collision, pathfinding or source PNG changes."
    )
    if write:
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"maps": len(maps), "changed": len(changed), "ratios": RATIOS, "unknown_profiles": unknown}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    path = ROOT / "godot/combat_missions_ui/art/environment/map_presentation.json"
    print(json.dumps(apply_profiles(path, args.write), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
