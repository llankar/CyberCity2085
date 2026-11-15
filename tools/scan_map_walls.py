"""Create missing per-map wall surveys; never overwrite corrected surveys."""

import json
import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from game.battle_maps import build_battle_map_catalog
from game.map_geometry import geometry_path, scan_map_walls


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refresh-unreviewed", action="store_true")
    parser.add_argument("--compile-traces", action="store_true", help="Explicitly rebuild maps with authored wall traces")
    args = parser.parse_args()
    generated = 0
    for entry in build_battle_map_catalog():
        target = geometry_path(entry.path)
        if target.exists():
            old = json.loads(target.read_text(encoding="utf-8"))
            compile_authored = args.compile_traces and Path(entry.path).with_suffix(".wall-traces.json").is_file()
            if not compile_authored and (not args.refresh_unreviewed or old.get("reviewed") or any(wall.get("reviewed") for wall in old.get("walls", []))):
                continue
        data = scan_map_walls(entry.path)
        target.write_text(json.dumps(data, separators=(",", ":")) + "\n", encoding="utf-8")
        generated += 1
        print(f"{entry.filename}: {len(data['walls'])} numbered obstacle regions")
    print(f"Stored {generated} surveys; existing surveys preserved.")


if __name__ == "__main__":
    main()
