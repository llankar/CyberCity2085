"""Generate floors for a batch of interiors and export their shared 3D fixtures."""
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
MAPS = ROOT.parents[1] / "assets/maps"
OUTPUT = Path("E:/CyberCity2085-3d-lab/generated/phase2/interiors")
INTERIORS = (
    "cybercity_inner_03_research_lab",
    "cybercity_inner_04_medical_clinic",
    "cybercity_inner_06_blacksite_lab",
    "cybercity_inner_13_warehouse_floor",
    "wasteland_inner_03_ruined_clinic",
    "wasteland_inner_08_ruined_clinic",
    "cybercity_inner_09_apartment_block",
    "city_interior_server_room",
    "cybercity_inner_05_server_room",
    "city_interior_control_center",
    "cybercity_inner_01_control_center",
    "wasteland_inner_04_bunker_command_post",
    "city_interior_safehouse",
    "cybercity_inner_02_safehouse",
    "wasteland_inner_01_abandoned_safehouse",
    "wasteland_inner_06_abandoned_safehouse",
    "city_interior_corporate_lobby",
    "cybercity_inner_07_corporate_lobby",
    "city_interior_police_records",
    "cybercity_inner_08_police_records",
)


def fixtures(name):
    survey = json.loads((MAPS / f"{name}.wall-traces.json").read_text())
    selected = {}
    for row in survey["walls"]:
        identifier = row["id"]
        if "points" in row and row.get("blocks_sight", True):
            selected[identifier] = "partition"
            continue
        if "rect" not in row:
            continue
        if "wall" in identifier:
            selected[identifier] = "wall"
        elif "bed" in identifier or identifier == "operating_table":
            selected[identifier] = "bed"
        elif "pods" in identifier or identifier in {"central_chamber", "central_cryo"}:
            selected[identifier] = "pod"
        elif "crate" in identifier:
            selected[identifier] = "crate"
        elif "server" in identifier or "cabinet" in identifier:
            selected[identifier] = "cabinet"
        elif "console" in identifier or "computer" in identifier:
            selected[identifier] = "console"
        elif "sofa" in identifier or identifier.startswith("chair"):
            selected[identifier] = "sofa"
        elif "planter" in identifier or identifier.startswith("reception_plant"):
            selected[identifier] = "planter"
        elif identifier.startswith(("gate_", "turnstile_")):
            selected[identifier] = "gate"
        elif any(part in identifier for part in ("desk", "table", "kitchen", "bench", "coffee")) or identifier == "reception":
            selected[identifier] = "table"
        elif "shelf" in identifier or "rack" in identifier:
            selected[identifier] = "rack"
        elif "machine" in identifier or "scan" in identifier:
            selected[identifier] = "machine"
    return survey, selected


def main():
    sys.path.insert(0, str(MAPS.parents[1]))
    from game.map_geometry import stroke_outline

    names = sys.argv[1:] or INTERIORS
    for name in names:
        if name not in INTERIORS:
            raise ValueError(f"Unconfigured interior: {name}")
        survey, selected = fixtures(name)
        subprocess.run([sys.executable, str(ROOT / "prepare_floor248.py"), "--map", name,
                        "--output", str(OUTPUT / name), "--objects", ",".join(selected),
                        "--include-side-walls"], check=True)
        outlines = {row["id"]: stroke_outline(row["points"], row["width"])
                    for row in survey["walls"] if selected.get(row["id"]) == "partition"}
        (OUTPUT / name / "fixtures.json").write_text(
            json.dumps({"selected": selected, "outlines": outlines}), encoding="utf-8"
        )
    return subprocess.run([
        "powershell.exe", "-NoProfile", "-File", str(ROOT / "run_blender.ps1"),
        "-Script", "blender/build_interiors.py", *names,
    ], check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
