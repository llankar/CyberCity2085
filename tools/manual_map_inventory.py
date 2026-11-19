"""Audit every map and propagate manual traces only between byte-identical art."""

import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from game.battle_maps import build_battle_map_catalog
from game.map_geometry import load_map_geometry


def inventory():
    rows = []
    for entry in build_battle_map_catalog():
        path = Path(entry.path)
        geometry = load_map_geometry(path)
        source = path.with_suffix(".wall-traces.json")
        manual = bool(source.exists() and geometry.get("method") == "manual_wall_traces_v1" and geometry.get("reviewed"))
        source_data = json.loads(source.read_text(encoding="utf-8")) if source.exists() else {}
        rows.append({"image":path.name,"sha256":sha256(path.read_bytes()).hexdigest(),
                     "manual":manual,"objects":len(geometry.get("walls",[])),"path":path,
                     "origin":source_data.get("same_pixels_as", "direct visual trace")})
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--propagate-identical", action="store_true")
    args = parser.parse_args()
    rows = inventory()
    if args.propagate_identical:
        reviewed = {row["sha256"]:row for row in rows if row["manual"]}
        for row in rows:
            trace = row["path"].with_suffix(".wall-traces.json")
            if not trace.exists() and row["sha256"] in reviewed:
                origin = reviewed[row["sha256"]]
                data = json.loads(origin["path"].with_suffix(".wall-traces.json").read_text(encoding="utf-8"))
                data["same_pixels_as"] = origin["image"]
                trace.write_text(json.dumps(data,indent=2)+"\n",encoding="utf-8")
                print(f"Identical image: {row['image']} <- {origin['image']}")
    done = sum(row["manual"] for row in rows)
    text = ["# Manual wall survey inventory", "", f"{len(rows)} maps; {len({r['sha256'] for r in rows})} distinct image hashes; {done} compiled manual surveys.", "",
            "Pending rows are automatic candidates, not manually validated. Identical-image reuse requires an exact SHA-256 match.", "",
            "Excluded diagnostic image: `preview_control_center_edges.png` (edge-detection preview, not playable art).", "",
            "| Map | Manual survey | Objects | Trace origin |", "| --- | --- | ---: | --- |"]
    text.extend(f"| {r['image']} | {'DONE' if r['manual'] else 'PENDING'} | {r['objects']} | {r['origin']} |" for r in rows)
    Path("docs/manual_wall_inventory.md").write_text("\n".join(text)+"\n",encoding="utf-8")
    print(f"Manual coverage: {done}/{len(rows)}")


if __name__ == "__main__":
    main()
