"""Generate floors for a batch of interiors and export their shared 3D fixtures."""
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
MAPS = ROOT.parents[1] / "assets/maps"
OUTPUT = Path("E:/CyberCity2085-3d-lab/generated/phase2/interiors")
CONCRETE_FLOOR_REPAIR_MAPS = {
    "city_industrial_service_tunnel",
    "cybercity_inner_12_maintenance_tunnel",
    "wasteland_inner_02_collapsed_tunnel",
    "wasteland_inner_07_collapsed_tunnel",
}
AGED_CONCRETE_INTERIORS = ("_bunker_command_post", "_underground_market", "_ruined_clinic",
                          "_collapsed_tunnel", "_looted_vault", "_maintenance_depot",
                          "_abandoned_safehouse", "_apartment_shelter")
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
    plumbing_interior = name in {
        "cybercity_inner_04_medical_clinic", "cybercity_inner_02_safehouse",
        "wasteland_inner_07_apartment_shelter", "wasteland_inner_12_apartment_shelter",
        "wasteland_inner_03_ruined_clinic", "wasteland_inner_08_ruined_clinic",
        "wasteland_inner_01_abandoned_safehouse", "wasteland_inner_06_abandoned_safehouse",
    }
    room_fixtures = {
        "city_interior_command_deck": {"north_display": "command_wall"},
        "city_interior_police_records": {"south_control": "command_console"},
        "city_industrial_data_vault": {"vault_core": "data_core"},
        "cybercity_inner_11_cyber_cafe": {"east_office_counter": "workbench"},
        "wasteland_inner_05_looted_vault": {"sw_utility": "cabinet", "core": "vault_core"},
        "wasteland_inner_10_looted_vault": {"sw_utility": "cabinet", "core": "vault_core"},
        "city_interior_penthouse_atrium": {
            "bath_sw": "bath_tub", "bath_se": "bath_tub", "south_lounge": "sofa",
        },
        "cybercity_inner_10_penthouse_atrium": {"sw_plant": "planter"},
        "cybercity_inner_12_maintenance_tunnel": {"se_fans": "vent_fan", "south_inner_storage": "rack"},
        "cybercity_inner_14_detention_block": {
            "east_weapons": "rack", "east_tools": "workbench",
            "north_cells_front": "cell_front", "south_cells_front": "cell_front",
        },
        "cybercity_inner_09_apartment_block": {"bath_s": "bath_tub"},
        "city_interior_control_center": {"north_display": "command_wall"},
        "cybercity_inner_01_control_center": {"north_display": "command_wall"},
        "city_interior_cyber_cafe": {
            "bath_sinks": "bath_sink", "bath_cubicles": "toilet_stalls", "west_storage": "rack",
        },
        "cybercity_inner_06_blacksite_lab": {"nw_sink": "bath_sink"},
        "cybercity_inner_04_medical_clinic": {
            "west_scan": "diagnostic_bench", "west_scan_s": "diagnostic_bench",
        },
        "city_transit_train_tunnel": {
            "north_utility_w": "rail_service_room", "south_utility_e": "rail_service_room",
        },
    }.get(name, {})
    safehouse_fixtures = {
        "west_gym_weight": "gym_weights", "south_tools": "workbench",
        "south_generator": "floor_generator", "bath_sinks": "bath_sink",
        "bath_showers": "bath_shower", "south_storage": "rack",
    } if name == "city_interior_safehouse" else {}
    for row in survey["walls"]:
        identifier = row["id"]
        if name == "city_industrial_service_tunnel" and row.get("kind") == "floor_detail":
            selected[identifier] = "floor_grate"
            continue
        if identifier.startswith("outside_") or row.get("collision") is False:
            continue
        if "points" in row:
            if room_fixtures.get(identifier) == "cell_front" or (
                name.startswith("wasteland_") and name.endswith("_detention_block")
                and identifier in {"cells_n_front", "cells_s_front"}
            ):
                selected[identifier] = "cell_front"
            elif "_pipe" in identifier:
                selected[identifier] = "pipe"
            elif row.get("blocks_sight", True):
                selected[identifier] = "partition"
            continue
        if not any(key in row for key in ("rect", "polygon")):
            continue
        if identifier in safehouse_fixtures:
            selected[identifier] = safehouse_fixtures[identifier]
        elif identifier in room_fixtures:
            selected[identifier] = room_fixtures[identifier]
        elif name == "city_transit_train_tunnel" and "_track_box" in identifier:
            selected[identifier] = "rail_signal"
        elif plumbing_interior and "sink" in identifier:
            selected[identifier] = "bath_sink"
        elif plumbing_interior and "shower" in identifier:
            selected[identifier] = "bath_shower"
        elif plumbing_interior and ("bath_tub" in identifier or identifier == "ne_bath"):
            selected[identifier] = "bath_tub"
        elif plumbing_interior and "toilet" in identifier:
            selected[identifier] = "bath_toilet"
        elif plumbing_interior and identifier.endswith("_storage"):
            selected[identifier] = "rack"
        elif plumbing_interior and identifier.endswith("_stove"):
            selected[identifier] = "stove"
        elif name.endswith("_abandoned_safehouse") and identifier == "kitchen_nw":
            selected[identifier] = "stove"
        elif name.endswith("_apartment_shelter") and identifier == "north_kitchen":
            selected[identifier] = "shelter_kitchen"
        elif name == "city_interior_corporate_lobby" and identifier.endswith("_meeting"):
            selected[identifier] = "meeting_table"
        elif name == "city_interior_corporate_lobby" and identifier.endswith("_utility"):
            selected[identifier] = "cabinet"
        elif name.endswith("_maintenance_depot") and "_pit_" in identifier:
            selected[identifier] = "inspection_pit"
        elif name.endswith("_maintenance_depot") and identifier.endswith("_tires"):
            selected[identifier] = "spare_tires"
        elif name.endswith("_bunker_command_post") and identifier == "central_table":
            selected[identifier] = "command_table"
        elif name.endswith("_looted_vault") and identifier.startswith("table_"):
            selected[identifier] = "vault_display"
        elif name.endswith("_ruined_clinic") and identifier == "reception":
            selected[identifier] = "clinic_reception"
        elif (name == "cybercity_inner_08_police_records" and identifier.startswith("desk_")) or (
            name == "city_interior_police_records" and identifier in {"sw_desk", "se_desk", "south_w_desk"}
        ):
            selected[identifier] = "records_desk"
        elif name.endswith("_bunker_command_post") and (
            identifier in {"command_console", "west_desk", "east_desk"}
            or identifier.endswith(("_map", "_control"))
        ):
            selected[identifier] = "command_console"
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
        elif (name == "city_industrial_service_tunnel" or name.endswith("_collapsed_tunnel")) and identifier.endswith("_valve"):
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
        elif identifier.endswith("operating_table"):
            selected[identifier] = "operating_table"
        elif "bed" in identifier:
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



def decorative_fixtures(name):
    if name != "city_industrial_service_tunnel":
        return []
    return [
        {"id": "decor_west_twin_vent", "rect": [260,624,367,686], "model": "low_vent"},
        {"id": "decor_south_twin_vent", "rect": [1163,957,1252,1022], "model": "low_vent"},
        {"id": "decor_relay_extractor", "rect": [1272,682,1313,727], "model": "low_vent"},
    ]


def main():
    sys.path.insert(0, str(MAPS.parents[1]))
    from game.map_geometry import stroke_outline
    from rooftop_terrain import terrain

    names = sys.argv[1:] or INTERIORS
    for name in names:
        if name not in INTERIORS:
            raise ValueError(f"Unconfigured interior: {name}")
        survey, selected = fixtures(name)
        decorative = decorative_fixtures(name)
        floor_command = [sys.executable, str(ROOT / "prepare_floor248.py"), "--map", name,
                         "--output", str(OUTPUT / name), "--objects", ",".join(selected),
                         "--include-side-walls"]
        if name in CONCRETE_FLOOR_REPAIR_MAPS:
            concrete = OUTPUT.parents[2] / "sources/environment169/concrete_wall_001/diff.jpg"
            floor_command += ["--surface-detail", str(concrete)]
        if decorative:
            floor_command += ["--decorative-rects", json.dumps(
                [{"id": row["id"], "rect": row["rect"]} for row in decorative], separators=(",", ":")
            )]
        subprocess.run(floor_command, check=True)
        if name.endswith(AGED_CONCRETE_INTERIORS):
            from PIL import Image, ImageEnhance

            concrete = OUTPUT.parents[2] / "sources/environment169/concrete_wall_001/diff.jpg"
            with Image.open(concrete) as source:
                toned = ImageEnhance.Brightness(source.convert("RGB")).enhance(.62)
                toned.save(OUTPUT / name / "aged_concrete_diffuse.jpg", quality=94)
        if name.endswith("_bunker_command_post"):
            from PIL import Image

            with Image.open(MAPS / f"{name}.png") as source:
                cw, ch = survey["canvas_size"]
                x1, y1, x2, y2 = 439, 183, 509, 261
                crop = (round(x1*source.width/cw), round(y1*source.height/ch),
                        round(x2*source.width/cw), round(y2*source.height/ch))
                source.crop(crop).convert("RGB").save(OUTPUT / name / "operations_map.png")
        if name.endswith("_underground_market"):
            from PIL import Image

            # Samples measured against the 820 × 462 overview of the original.
            with Image.open(MAPS / f"{name}.png") as source:
                sx, sy = source.width/820, source.height/462
                for color, (x1,y1,x2,y2) in {
                    "olive": (57,215,90,245), "rust": (187,273,230,307), "tan": (706,269,730,305),
                }.items():
                    crop = (round(x1*sx),round(y1*sy),round(x2*sx),round(y2*sy))
                    source.crop(crop).convert("RGB").save(OUTPUT / name / f"stall_canvas_{color}.png")
        outlines = {row["id"]: stroke_outline(row["points"], row["width"])
                    if "points" in row else row["polygon"]
                    for row in survey["walls"] if selected.get(row["id"]) in {"partition", "rubble"}}
        atrium = [row for row in survey["walls"] if row["id"] == "central_void"]
        floor_geometry = terrain({**survey, "walls": [{**row, "kind": "water"} for row in atrium]}) if atrium else None
        (OUTPUT / name / "fixtures.json").write_text(
            json.dumps({"selected": selected, "outlines": outlines, "floor_geometry": floor_geometry, "decorative": decorative}), encoding="utf-8"
        )
    return subprocess.run([
        "powershell.exe", "-NoProfile", "-File", str(ROOT / "run_blender.ps1"),
        "-Script", "blender/build_interiors.py", *names,
    ], check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
