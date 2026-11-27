"""Generate floors for a batch of interiors and export their shared 3D fixtures."""
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
MAPS = ROOT.parents[1] / "assets/maps"
OUTPUT = Path("E:/CyberCity2085-3d-lab/generated/phase2/interiors")
INTERIORS = (
    "city_interior_blacksite_lab",
    "city_interior_medical_clinic",
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
    "city_interior_cyber_cafe",
    "cybercity_inner_11_cyber_cafe",
    "city_interior_penthouse_atrium",
    "cybercity_inner_10_penthouse_atrium",
    "cybercity_inner_14_detention_block",
    "wasteland_inner_10_detention_block",
    "wasteland_inner_15_detention_block",
    "city_industrial_data_vault",
    "cybercity_inner_15_data_vault",
    "city_industrial_security_checkpoint",
    "city_industrial_service_tunnel",
    "city_interior_command_deck",
    "cybercity_inner_12_maintenance_tunnel",
    "wasteland_inner_05_looted_vault",
    "wasteland_inner_06_maintenance_depot",
    "wasteland_inner_07_apartment_shelter",
    "wasteland_inner_08_data_relay_room",
    "wasteland_inner_09_bunker_command_post",
    "wasteland_inner_10_looted_vault",
    "wasteland_inner_11_emergency_medbay",
    "wasteland_inner_11_maintenance_depot",
    "wasteland_inner_12_apartment_shelter",
    "wasteland_inner_13_data_relay_room",
    "city_transit_train_tunnel",
    "city_transit_metro_interchange",
    "wasteland_inner_02_collapsed_tunnel",
    "wasteland_inner_07_collapsed_tunnel",
    "wasteland_inner_09_underground_market",
    "wasteland_inner_14_underground_market",
)


def fixtures(name):
    survey = json.loads((MAPS / f"{name}.wall-traces.json").read_text())
    selected = {}
    server_interior = name in {"cybercity_inner_15_data_vault", "cybercity_inner_05_server_room"}
    safehouse_fixtures = {
        "west_gym_weight": "gym_weights", "south_tools": "workbench",
        "south_generator": "floor_generator", "bath_sinks": "bath_sink",
        "bath_showers": "bath_shower", "south_storage": "rack",
    } if name == "city_interior_safehouse" else {}
    for row in survey["walls"]:
        identifier = row["id"]
        if identifier.startswith("outside_") or row.get("collision") is False:
            continue
        if "points" in row:
            if "_pipe" in identifier:
                selected[identifier] = "pipe"
            elif row.get("blocks_sight", True):
                selected[identifier] = "partition"
            continue
        if not any(key in row for key in ("rect", "polygon")):
            continue
        if identifier in safehouse_fixtures:
            selected[identifier] = safehouse_fixtures[identifier]
        elif identifier.endswith("_tracks"):
            selected[identifier] = "track"
        elif name == "cybercity_inner_13_warehouse_floor" and identifier.startswith("bench_"):
            selected[identifier] = "workbench"
        elif name == "cybercity_inner_13_warehouse_floor" and identifier == "barrel_s":
            selected[identifier] = "drums"
        elif server_interior and identifier.endswith("_fans"):
            selected[identifier] = "vent_fan"
        elif server_interior and identifier == "east_control":
            selected[identifier] = "console"
        elif server_interior and identifier == "west_storage":
            selected[identifier] = "rack"
        elif server_interior and identifier == "nw_generator":
            selected[identifier] = "floor_generator"
        elif name == "city_industrial_service_tunnel" and identifier == "nw_room_corner_fan":
            selected[identifier] = "vent_fan"
        elif name == "city_industrial_service_tunnel" and identifier.endswith("_valve"):
            selected[identifier] = "service_valve"
        elif name == "city_industrial_service_tunnel" and identifier.endswith("_terminal"):
            selected[identifier] = "console"
        elif name == "city_industrial_service_tunnel" and "equipment" in identifier:
            selected[identifier] = "machine"
        elif "stairs" in identifier or identifier == "stair_e" and name == "cybercity_inner_13_warehouse_floor":
            selected[identifier] = "stair"
        elif identifier.startswith("column_"):
            selected[identifier] = "column"
        elif "collapsed_span" in identifier:
            selected[identifier] = "rubble"
        elif "stall" in identifier:
            selected[identifier] = "stall"
        elif "polygon" in row and ("wall" in identifier or "partition" in identifier or "return" in identifier):
            selected[identifier] = "partition"
        elif "wall" in identifier or (name.endswith("penthouse_atrium") and "_edge" in identifier):
            selected[identifier] = "wall"
        elif "bed" in identifier or identifier.endswith("operating_table"):
            selected[identifier] = "bed"
        elif "pods" in identifier or identifier.endswith("_core") or identifier.startswith("core_") or identifier in {"central_chamber", "central_cryo", "core"}:
            selected[identifier] = "pod"
        elif any(part in identifier for part in ("crate", "_cargo", "_boxes")):
            selected[identifier] = "crate"
        elif "server" in identifier or "cabinet" in identifier:
            selected[identifier] = "cabinet"
        elif any(part in identifier for part in ("console", "computer", "gaming", "_kiosk", "ticket_", "monitor")):
            selected[identifier] = "console"
        elif any(part in identifier for part in ("sofa", "chair", "booth")):
            selected[identifier] = "sofa"
        elif "planter" in identifier or identifier.startswith("reception_plant"):
            selected[identifier] = "planter"
        elif identifier.startswith(("gate_", "turnstile_", "scanner_")):
            selected[identifier] = "gate"
        elif name == "city_industrial_security_checkpoint" and (
            identifier.endswith("_bay") or identifier.startswith("guardroom_")
        ):
            selected[identifier] = "security_bay"
        elif identifier.startswith(("security_booth_", "guardroom_")):
            selected[identifier] = "cabinet"
        elif "barrier" in identifier:
            selected[identifier] = "barrier"
        elif identifier.endswith("_fountain"):
            selected[identifier] = "fountain"
        elif any(part in identifier for part in ("desk", "table", "kitchen", "bench", "coffee", "bar_", "_bar", "counter")) or identifier == "reception":
            selected[identifier] = "table"
        elif "shelf" in identifier or "rack" in identifier:
            selected[identifier] = "rack"
        elif any(part in identifier for part in ("machine", "scan", "generator", "conduit", "_pipe", "_utility", "_track_box", "_valve")):
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
                    if "points" in row else row["polygon"]
                    for row in survey["walls"] if selected.get(row["id"]) in {"partition", "rubble"}}
        (OUTPUT / name / "fixtures.json").write_text(
            json.dumps({"selected": selected, "outlines": outlines}), encoding="utf-8"
        )
    return subprocess.run([
        "powershell.exe", "-NoProfile", "-File", str(ROOT / "run_blender.ps1"),
        "-Script", "blender/build_interiors.py", *names,
    ], check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
