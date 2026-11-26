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
)


def fixtures(name):
    survey = json.loads((MAPS / f"{name}.wall-traces.json").read_text())
    selected = {}
    for row in survey["walls"]:
        identifier = row["id"]
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
        elif "shelf" in identifier or "rack" in identifier:
            selected[identifier] = "rack"
        elif "machine" in identifier or "scan" in identifier:
            selected[identifier] = "machine"
    return survey, selected


def main():
    names = sys.argv[1:] or INTERIORS
    for name in names:
        if name not in INTERIORS:
            raise ValueError(f"Unconfigured interior: {name}")
        _, selected = fixtures(name)
        subprocess.run([sys.executable, str(ROOT / "prepare_floor248.py"), "--map", name,
                        "--output", str(OUTPUT / name), "--objects", ",".join(selected),
                        "--include-side-walls"], check=True)
    return subprocess.run([
        "powershell.exe", "-NoProfile", "-File", str(ROOT / "run_blender.ps1"),
        "-Script", "blender/build_interiors.py", *names,
    ], check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
