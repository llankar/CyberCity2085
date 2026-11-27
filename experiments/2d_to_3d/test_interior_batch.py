from catalogue_test_assets import catalogue_environment
from interior_batch import AGED_CONCRETE_INTERIORS, INTERIORS, fixtures


def test_wasteland_concrete_exports_with_a_normal_texture():
    import json
    import struct

    import pytest

    models = {catalogue_environment(name) for name in INTERIORS if name.endswith(AGED_CONCRETE_INTERIORS)}
    if not any(model.is_file() for model in models):
        pytest.skip("Local Wasteland exports are unavailable")
    for model in models:
        with model.open("rb") as stream:
            _, _, _, length, _ = struct.unpack("<4sIII4s", stream.read(20))
            document = json.loads(stream.read(length))
        material = next(item for item in document["materials"] if item["name"] == "Wasteland aged concrete")
        assert "normalTexture" in material, model


def test_underground_market_stalls_export_as_independent_meshes():
    import json
    import struct

    import pytest

    name = "wasteland_inner_09_underground_market"
    model = catalogue_environment(name)
    if not model.is_file():
        pytest.skip("Local Underground Market export is unavailable")
    with model.open("rb") as stream:
        magic, _, _, length, chunk = struct.unpack("<4sIII4s", stream.read(20))
        assert (magic, chunk) == (b"glTF", b"JSON")
        nodes = json.loads(stream.read(length))["nodes"]
    groups = {node["name"]: node for node in nodes}
    _, selected = fixtures(name)
    stalls = [identifier for identifier, kind in selected.items() if kind == "stall"]
    assert stalls
    for identifier in stalls:
        child, = groups[f"Occludable_{identifier}"]["children"]
        assert nodes[child]["name"].startswith("Salvage market stall")
        assert "mesh" in nodes[child]


def test_interior_batch_limits_replacements_to_modelled_footprints():
    for name in INTERIORS:
        survey, selected = fixtures(name)
        assert {"wall", "partition"} & set(selected.values())
        assert set(selected) <= {row["id"] for row in survey["walls"]}
        assert not any(identifier.startswith("outside_") for identifier in selected)

    _, clinic = fixtures("cybercity_inner_04_medical_clinic")
    _, lab = fixtures("cybercity_inner_06_blacksite_lab")
    _, warehouse = fixtures("cybercity_inner_13_warehouse_floor")
    assert clinic["east_bed1"] == "bed"
    assert lab["west_pods"] == "pod"
    assert warehouse["shelf_mid"] == "rack"
    assert lab["west_partition_n"] == "partition"
    _, lobby = fixtures("cybercity_inner_07_corporate_lobby")
    assert lobby["gate_1"] == "gate"
    assert lobby["sofa_ne"] == "sofa"
    assert lobby["planter_nw"] == "planter"
    _, vault = fixtures("city_industrial_data_vault")
    assert vault["west_server_rack"] == "cabinet"
    assert vault["vault_core"] == "data_core"
    _, tunnel = fixtures("city_industrial_service_tunnel")
    assert tunnel["ne_room_pipe_elbow"] == "pipe"
    assert tunnel["nw_room_floor_grate"] == "floor_grate"
    _, metro = fixtures("city_transit_metro_interchange")
    assert metro["east_top_tracks"] == "track"
    assert metro["north_stairs_w"] == "stair"

def test_train_tunnel_exports_edge_to_edge_rails_and_two_sleeper_beds():
    import json
    from pathlib import Path
    import struct

    path = Path("E:/CyberCity2085-3d-lab/generated/phase2/interiors/"
                "city_transit_train_tunnel/environment.glb")
    if not path.is_file():
        import pytest
        pytest.skip("Build the experimental Train Tunnel on E: first")
    with path.open("rb") as model:
        _, _, _, size, _ = struct.unpack("<4sIII4s", model.read(20))
        data = json.loads(model.read(size))
    rails = [node for node in data["nodes"] if node["name"].startswith("Running rail ")]
    beds = [node for node in data["nodes"] if node["name"].endswith(" sleeper bed")]
    assert len(rails) == 4
    assert len(beds) == 2
    signals = [node for node in data["nodes"] if node["name"].startswith("Trackside signal cabinet")]
    assert len(signals) == 5
    assert all("mesh" in signal for signal in signals)
    nodes = data["nodes"]
    for identifier in ("north_utility_w", "south_utility_e"):
        group = next(node for node in nodes if node["name"] == f"Occludable_{identifier}")
        assert any(nodes[index]["name"].startswith("Open rail service room")
                   for index in group["children"])
    decks = [node for node in data["nodes"] if node["name"].startswith("Maintenance crossing ")
             and node["name"].endswith(" deck")]
    assert len(decks) == 2
    for deck in decks:
        mesh = data["meshes"][deck["mesh"]]
        assert min(data["accessors"][p["attributes"]["POSITION"]]["max"][1]
                   + deck["translation"][1] for p in mesh["primitives"]) > .107
    for rail in rails:
        mesh = data["meshes"][rail["mesh"]]
        positions = [data["accessors"][p["attributes"]["POSITION"]] for p in mesh["primitives"]]
        assert min(p["min"][0] for p in positions) <= -19.99
        assert max(p["max"][0] for p in positions) >= 19.99

def test_metro_column_and_stair_details_keep_independent_visibility():
    import json
    from pathlib import Path
    import struct

    path = Path("E:/CyberCity2085-3d-lab/generated/phase2/interiors/"
                "city_transit_metro_interchange/environment.glb")
    if not path.is_file():
        import pytest
        pytest.skip("Build the experimental Metro Interchange on E: first")
    with path.open("rb") as model:
        _, _, _, size, _ = struct.unpack("<4sIII4s", model.read(20))
        nodes = json.loads(model.read(size))["nodes"]
    columns = [node for node in nodes if node["name"].startswith("Occludable_column_")]
    assert len(columns) == 10
    for column in columns:
        parts = [nodes[index]["name"] for index in column["children"]]
        assert sum(" station marker" in name for name in parts) == 1
        assert sum(" cooling louver" in name for name in parts) == 3
    stairs = [node for node in nodes if node["name"].startswith(("Occludable_north_stairs_", "Occludable_south_stairs_"))]
    assert len(stairs) == 4
    for stair in stairs:
        parts = [nodes[index]["name"] for index in stair["children"]]
        assert sum(" tread nosing" in name for name in parts) == 8
        assert sum(" handrail" in name and " post" not in name for name in parts) == 2
    tracks = [node for node in nodes if node["name"].startswith("Occludable_")
              and node["name"].endswith("_tracks")]
    assert len(tracks) == 6
    for track in tracks:
        parts = [nodes[index]["name"] for index in track["children"]]
        assert len(parts) == 4
        assert sum(" sleeper bed" in name for name in parts) == 1
        assert sum(" rail" in name for name in parts) == 2

def test_warehouse_racks_export_stock_under_each_rack_occluder():
    import json
    from pathlib import Path
    import struct

    path = Path("E:/CyberCity2085-3d-lab/generated/phase2/warehouse333/environment.glb")
    if not path.is_file():
        import pytest
        pytest.skip("Build the experimental Warehouse on E: first")
    with path.open("rb") as model:
        _, _, _, size, _ = struct.unpack("<4sIII4s", model.read(20))
        data = json.loads(model.read(size))
        nodes = data["nodes"]
    racks = [node for node in nodes if node["name"].startswith("Occludable_row")]
    assert len(racks) == 10
    for rack in racks:
        cargo = [nodes[index] for index in rack["children"] if " shelf cargo" in nodes[index]["name"]]
        assert len(cargo) == 6
        assert len({round(item["translation"][1], 2) for item in cargo}) == 3
    forklifts = [node for node in nodes if node["name"].startswith("Occludable_forklift_")]
    assert len(forklifts) == 4
    for forklift in forklifts:
        parts = [nodes[index]["name"] for index in forklift["children"]]
        assert sum(" fork" in part for part in parts) == 2
        assert sum(" wheel" in part for part in parts) == 4
    by_name = {node["name"]: node for node in nodes}
    for room, feature in (("east_office", " worktop"), ("east_stair", " nosing"), ("east_bay", " dock lip")):
        group = by_name[f"Occludable_{room}"]
        assert any(feature in nodes[index]["name"] for index in group["children"])
    root_names = {nodes[index]["name"] for index in data["scenes"][data["scene"]]["nodes"]}
    assert "east_office service floor" in root_names

def test_substation_exports_all_surveyed_equipment_groups():
    import json
    from pathlib import Path
    import struct

    path = Path("E:/CyberCity2085-3d-lab/generated/phase2/substation334/environment.glb")
    if not path.is_file():
        import pytest
        pytest.skip("Build the experimental Power Substation on E: first")
    with path.open("rb") as model:
        _, _, _, size, _ = struct.unpack("<4sIII4s", model.read(20))
        data = json.loads(model.read(size))
        nodes = data["nodes"]
    survey_path = Path(__file__).resolve().parents[2] / "assets/maps/city_industrial_power_substation.wall-traces.json"
    surveyed = {f"Occludable_{row['id']}" for row in json.loads(survey_path.read_text())["walls"]}
    exported = {node["name"] for node in nodes if node["name"].startswith("Occludable_") and node.get("children")}
    assert surveyed == exported
    roots = [nodes[index] for index in data["scenes"][data["scene"]]["nodes"]]
    pads = [node for node in roots if node["name"].endswith(" retained service pad")]
    assert len(pads) == 8
    by_name = {node["name"]: node for node in nodes}
    for identifier in ("north_pipes", "central_trunk_n", "central_trunk_s", "south_pipes"):
        group = by_name[f"Occludable_{identifier}"]
        (bundle_index,) = group["children"]
        bundle = nodes[bundle_index]
        assert bundle["name"] == f"{identifier} conduit bundle"
        assert "mesh" in bundle
    for identifier in ("west_substation", "east_substation"):
        group = by_name[f"Occludable_{identifier}"]
        assert sum(nodes[index]["name"].startswith(f"{identifier} breaker module")
                   for index in group["children"]) == 3

def test_factory_console_and_shelf_groups_are_native_geometry():
    import json
    from pathlib import Path
    import struct

    path = Path("E:/CyberCity2085-3d-lab/generated/phase2/factory330/environment.glb")
    if not path.is_file():
        import pytest
        pytest.skip("Build the experimental Factory Floor on E: first")
    with path.open("rb") as model:
        _, _, _, size, _ = struct.unpack("<4sIII4s", model.read(20))
        data = json.loads(model.read(size))
        nodes = data["nodes"]
    groups = {node["name"]: node for node in nodes if node.get("children")}
    roots = [nodes[index] for index in data["scenes"][data["scene"]]["nodes"]]
    assert sum(" retained pipe shoe" in node["name"] for node in roots) == 8
    for identifier in ("west_console", "east_console", "mid_console", "north_left_shelf", "north_right_shelf"):
        group = groups[f"Occludable_{identifier}"]
        assert any("mesh" in nodes[index] for index in group["children"])
        if identifier.endswith("_console"):
            parts = [nodes[index]["name"] for index in group["children"]]
            assert sum(part.startswith(f"{identifier} deck crossbar") for part in parts) == 4

def test_dockside_exports_all_surveyed_obstacle_groups():
    import json
    from pathlib import Path
    import struct

    path = Path("E:/CyberCity2085-3d-lab/generated/phase2/dockside338/environment.glb")
    if not path.is_file():
        import pytest
        pytest.skip("Build the experimental Dockside Terminal on E: first")
    with path.open("rb") as model:
        _, _, _, size, _ = struct.unpack("<4sIII4s", model.read(20))
        nodes = json.loads(model.read(size))["nodes"]
    survey_path = Path(__file__).resolve().parents[2] / "assets/maps/city_industrial_dockside_terminal.wall-traces.json"
    survey = json.loads(survey_path.read_text())
    expected = {f"Occludable_{row['id']}" for row in survey["walls"]
                if row.get("kind") == "floor_detail"
                or (row.get("kind") != "water" and row.get("collision") is not False)}
    exported = {node["name"] for node in nodes if node["name"].startswith("Occludable_") and node.get("children")}
    assert exported == expected
    for label in ("North moored cargo vessel", "South moored cargo vessel"):
        vessel = next(node for node in nodes if node["name"] == label)
        assert "mesh" in vessel
        parts = [nodes[index]["name"] for index in vessel["children"]]
        assert sum(part.startswith("Warehouse shipping container") for part in parts) == 3
        for component in ("Bridge glazing", "Forward hatch", "Aft mooring winch"):
            assert any(part.startswith(component) for part in parts)
    for identifier in ("east_upper_cabin", "east_lower_cabin"):
        cabin = next(node for node in nodes if node["name"] == f"Occludable_{identifier}")
        parts = [nodes[index]["name"] for index in cabin["children"]]
        assert sum(f"{identifier} front window" in part for part in parts) == 2
        assert f"{identifier} roof vent" in parts
    grate = next(node for node in nodes if node["name"] == "Occludable_east_center_grate")
    bars = [nodes[index] for index in grate["children"]
            if nodes[index]["name"].startswith("Drain grate bar")]
    assert len(bars) == 10
    assert all(node["translation"][1] < .02 for node in bars)
    forklifts = [node for node in nodes if node["name"].startswith("Occludable_")
                 and node["name"].endswith("_forklift")]
    assert len(forklifts) == 8
    for forklift in forklifts:
        parts = [nodes[index]["name"] for index in forklift["children"]]
        assert sum(" fork" in part for part in parts) == 2
        assert sum(" wheel" in part for part in parts) == 4


def test_showcase_clinic_and_blacksite_cover_all_surveyed_fixtures():
    import json
    import struct

    import pytest
    from interior_batch import OUTPUT

    for name in ("city_interior_medical_clinic", "city_interior_blacksite_lab"):
        survey, selected = fixtures(name)
        expected = {row["id"] for row in survey["walls"]}
        assert set(selected) == expected
        path = OUTPUT / name / "environment.glb"
        if not path.is_file():
            pytest.skip(f"Build {name} on E: first")
        with path.open("rb") as model:
            _, _, _, size, _ = struct.unpack("<4sIII4s", model.read(20))
            data = json.loads(model.read(size))
        nodes = data["nodes"]
        groups = {node["name"] for node in nodes
                  if node["name"].startswith("Occludable_") and node.get("children")}
        assert groups == {f"Occludable_{identifier}" for identifier in expected}

        for node in nodes:
            if selected.get(node["name"]) != "partition":
                continue
            primitives = data["meshes"][node["mesh"]]["primitives"]
            assert any(
                "TEXCOORD_0" in part["attributes"]
                and "baseColorTexture" in data["materials"][part["material"]]["pbrMetallicRoughness"]
                for part in primitives
            ), node["name"]

        if name == "city_interior_blacksite_lab":
            identifier = "central_chamber"
            required_parts = {"Containment footprint deck", "Containment specimen tray"}
        else:
            identifier = "northeast_scanner"
            required_parts = {"Scanner gantry shell", "Scanner patient table"}
        fixture = next(node for node in nodes if node["name"] == f"Occludable_{identifier}")
        assert required_parts <= {nodes[index]["name"] for index in fixture["children"]}


def test_checkpoint_bays_export_open_rooms_under_individual_cutaways():
    import json
    import struct

    import pytest
    from interior_batch import OUTPUT

    name = "city_industrial_security_checkpoint"
    survey, selected = fixtures(name)
    expected = {row["id"] for row in survey["walls"]}
    assert set(selected) == expected
    bays = {identifier for identifier, kind in selected.items() if kind == "security_bay"}
    assert len(bays) == 10
    model = OUTPUT / name / "environment.glb"
    if not model.is_file():
        pytest.skip("Build Security Checkpoint on E: first")
    with model.open("rb") as glb:
        size = struct.unpack("<4sIII4s", glb.read(20))[3]
        nodes = json.loads(glb.read(size))["nodes"]
    roots = {node["name"]: node["children"] for node in nodes if node.get("children")}
    assert {f"Occludable_{identifier}" for identifier in expected} <= roots.keys()
    for identifier in bays:
        parts = [nodes[index]["name"] for index in roots[f"Occludable_{identifier}"]]
        for component in ("floor pan", "doorway threshold", "worktop", "monitor"):
            assert any(part.startswith(f"Security bay {component}") for part in parts)
        assert all("roof" not in part.lower() for part in parts)

    for identifier in expected:
        parts = [nodes[index]["name"] for index in roots[f"Occludable_{identifier}"]]
        if identifier.startswith("barrier_"):
            assert sum(part.startswith("Barrier anchor post") for part in parts) >= 3
        elif identifier.startswith("scanner_"):
            assert sum(part.startswith("Scanner conveyor slat") for part in parts) == 8
            assert sum(part.startswith("Scanner arch upright") for part in parts) == 2
        elif identifier.startswith("security_booth_"):
            assert any(part.startswith("Checkpoint reader display") for part in parts)


def test_interior_maps_export_remaining_fixture_groups():
    import json
    import struct

    import pytest
    from interior_batch import OUTPUT

    additions = {
        "cybercity_inner_15_data_vault": {
            "nw_fans": "Vent fan deck", "ne_fans": "Vent fan deck",
            "sw_fans": "Vent fan deck", "se_fans": "Vent fan deck",
            "east_control": "east_control display",
        },
        "cybercity_inner_05_server_room": {
            "nw_fans": "Vent fan deck", "ne_fans": "Vent fan deck",
            "south_fans": "Vent fan deck", "nw_generator": None,
            "west_storage": "Warehouse pallet rack",
        },
        "cybercity_inner_13_warehouse_floor": {
            "bench_mid": "Workbench steel top", "bench_e": "Workbench steel top",
            "bench_w": "Workbench steel top", "bench_sw": "Workbench steel top",
            "barrel_s": "Warehouse service drum", "stair_e": "stair_e tread nosing",
        },
        "city_industrial_service_tunnel": {
            "nw_room_corner_fan": "Vent fan deck",
            "central_north_equipment_alcove": None,
            "ne_room_west_terminal": "ne_room_west_terminal display",
            "east_outer_equipment": None,
            "southeast_terminal": "southeast_terminal display",
            "south_inner_room_valve": "Service valve handwheel",
        },
    }
    additions.update({
        "city_interior_medical_clinic": {"east_operating_table": "Surgery operating table"},
        "cybercity_inner_04_medical_clinic": {
            "operating_table": "Surgery operating table",
            "west_scan": "Clinic diagnostic bench", "west_scan_s": "Clinic diagnostic bench",
        },
        "city_interior_command_deck": {"north_display": "Command vertical display"},
        "city_interior_police_records": {"south_control": "Command map display"},
        "cybercity_inner_11_cyber_cafe": {"east_office_counter": "Workbench steel top"},
        "wasteland_inner_05_looted_vault": {"sw_utility": "sw_utility panel"},
        "wasteland_inner_10_looted_vault": {"sw_utility": "sw_utility panel"},
        "city_interior_penthouse_atrium": {
            "bath_sw": "Tub basin inset", "bath_se": "Tub basin inset", "south_lounge": "south_lounge cushions",
            "center_fountain": "center_fountain inset water",
        },
        "cybercity_inner_10_penthouse_atrium": {"sw_plant": "sw_plant foliage"},
        "cybercity_inner_12_maintenance_tunnel": {
            "se_fans": "Vent fan deck", "south_inner_storage": "Warehouse pallet rack",
        },
        "cybercity_inner_14_detention_block": {
            "east_weapons": "Warehouse pallet rack", "east_tools": "Workbench steel top",
            "north_cells_front": "Detention cell frontage", "south_cells_front": "Detention cell frontage",
        },
        "wasteland_inner_10_detention_block": {
            "cells_n_front": "Detention cell frontage", "cells_s_front": "Detention cell frontage",
        },
        "cybercity_inner_09_apartment_block": {
            "sofa_s3": "sofa_s3 cushions", "chair_s3": "chair_s3 back",
            "bath_s": "Tub basin inset", "south_monitor": "south_monitor display",
        },
        "city_interior_control_center": {
            "north_display": "Command vertical display", "sw_sofa": "sw_sofa cushions",
        },
        "cybercity_inner_01_control_center": {
            "north_display": "Command vertical display", "west_sofa": "west_sofa cushions",
            "west_coffee": "west_coffee worktop",
        },
        "city_interior_cyber_cafe": {
            "bath_sinks": "Washbasin bowl", "bath_cubicles": "Stall privacy divider",
            "west_storage": "Warehouse pallet rack",
        },
        "cybercity_inner_06_blacksite_lab": {
            "nw_bench": "nw_bench worktop", "nw_sink": "Washbasin bowl",
        },
    })
    additions["city_interior_corporate_lobby"] = {
        "west_meeting": "Meeting table top", "east_meeting": "Meeting table top",
        "west_south_utility": None, "east_south_utility": None,
    }
    for index in ("06", "11"):
        additions[f"wasteland_inner_{index}_maintenance_depot"] = {
            "west_pit_n": "Inspection pit access rung", "west_pit_s": "Inspection pit access rung",
            "ne_tires": "Stacked spare tire",
        }
    for index in ("04", "09"):
        additions[f"wasteland_inner_{index}_bunker_command_post"] = {
            identifier: "Command map display" for identifier in ("north_map", "west_control", "east_control")
        }
    for name, fixtures_to_check in additions.items():
        path = (catalogue_environment(name) if name.startswith("wasteland_inner_")
                else OUTPUT / name / "environment.glb")
        if not path.is_file():
            pytest.skip(f"Build {name} on E: first")
        with path.open("rb") as glb:
            size = struct.unpack("<4sIII4s", glb.read(20))[3]
            nodes = json.loads(glb.read(size))["nodes"]
        groups = {node["name"]: node["children"] for node in nodes if node.get("children")}
        for identifier, component in fixtures_to_check.items():
            parts = [nodes[index]["name"] for index in groups[f"Occludable_{identifier}"]]
            assert parts
            if component:
                assert any(part.startswith(component) for part in parts), identifier


def test_server_banks_export_as_grouped_cabinets_with_power_indicators():
    import json
    import struct

    import pytest
    from interior_batch import OUTPUT

    for map_name, expected in (
        ("cybercity_inner_05_server_room", 10),
        ("cybercity_inner_15_data_vault", 8),
        ("city_interior_server_room", 13),
    ):
        path = OUTPUT / map_name / "environment.glb"
        if not path.is_file():
            pytest.skip(f"Build {map_name} on E: first")
        with path.open("rb") as glb:
            size = struct.unpack("<4sIII4s", glb.read(20))[3]
            data = json.loads(glb.read(size))
        nodes = data["nodes"]
        banks = {index for index, node in enumerate(nodes)
                 if node["name"].startswith("Server cabinet bank")}
        assert len(banks) == expected
        assert banks <= {index for node in nodes if node["name"].startswith("Occludable_")
                         for index in node.get("children", [])}
        for index in banks:
            parts = data["meshes"][nodes[index]["mesh"]]["primitives"]
            materials = {data["materials"][part["material"]]["name"] for part in parts}
            assert {"Server bank graphite", "Terminal display"} <= materials


def test_clinic_and_shelter_plumbing_is_exported_as_geometry():
    import json
    import struct

    import pytest
    from interior_batch import OUTPUT

    parts = {
        "bath_sink": "Washbasin bowl", "bath_shower": "Shower head",
        "bath_tub": "Tub basin inset", "bath_toilet": "Toilet cistern", "stove": "Stove burner",
    }
    maps = {
        "cybercity_inner_04_medical_clinic": 2,
        "cybercity_inner_02_safehouse": 3,
        **{f"wasteland_inner_{index}_{family}": count for family, variants, count in (
            ("apartment_shelter", ("07", "12"), 3),
            ("ruined_clinic", ("03", "08"), 2),
            ("abandoned_safehouse", ("01", "06"), 4),
        ) for index in variants},
    }
    for name, expected in maps.items():
        path = (catalogue_environment(name) if name.startswith("wasteland_inner_")
                else OUTPUT / name / "environment.glb")
        if not path.is_file():
            pytest.skip(f"Build {name} on E: first")
        with path.open("rb") as glb:
            size = struct.unpack("<4sIII4s", glb.read(20))[3]
            nodes = json.loads(glb.read(size))["nodes"]
        groups = {node["name"]: node["children"] for node in nodes if node.get("children")}
        _, selected = fixtures(name)
        modeled = {identifier: parts[kind] for identifier, kind in selected.items() if kind in parts}
        assert len(modeled) == expected, name
        for identifier, part in modeled.items():
            assert any(nodes[index]["name"].startswith(part)
                       for index in groups[f"Occludable_{identifier}"])



def test_penthouse_atrium_has_physical_recess_in_export():
    import json
    import struct

    import pytest
    from interior_batch import OUTPUT

    path = OUTPUT / "cybercity_inner_10_penthouse_atrium/environment.glb"
    if not path.is_file():
        pytest.skip("Build Penthouse Atrium 10 on E: first")
    with path.open("rb") as glb:
        size = struct.unpack("<4sIII4s", glb.read(20))[3]
        data = json.loads(glb.read(size))
    nodes = {node["name"]: node for node in data["nodes"]}
    assert "Occludable_central_void" not in nodes
    for label, low, high in (
        ("Atrium upper floor", -.025, -.025),
        ("Atrium recessed level", -1.85, -1.85),
        ("Atrium shaft sides", -1.85, -.025),
    ):
        mesh = data["meshes"][nodes[label]["mesh"]]
        accessor = data["accessors"][mesh["primitives"][0]["attributes"]["POSITION"]]
        assert (accessor["min"][1], accessor["max"][1]) == pytest.approx((low,high))


def test_extended_interior_partitions_use_worn_steel():
    import json
    import struct

    import pytest
    from interior_batch import OUTPUT

    for name in (
        "city_interior_safehouse", "city_interior_cyber_cafe", "city_industrial_service_tunnel",
        "cybercity_inner_05_server_room", "cybercity_inner_10_penthouse_atrium",
        "cybercity_inner_13_warehouse_floor",
        "city_interior_server_room", "city_industrial_data_vault", "cybercity_inner_15_data_vault",
    ):
        path = OUTPUT / name / "environment.glb"
        if not path.is_file():
            pytest.skip(f"Build {name} on E: first")
        with path.open("rb") as glb:
            size = struct.unpack("<4sIII4s", glb.read(20))[3]
            data = json.loads(glb.read(size))
        nodes = {node["name"]: node for node in data["nodes"]}
        _, selected = fixtures(name)
        partitions = [identifier for identifier, kind in selected.items() if kind == "partition"]
        assert partitions, name
        for identifier in partitions:
            mesh = data["meshes"][nodes[identifier]["mesh"]]
            assert any(
                "TEXCOORD_0" in part["attributes"]
                and data["materials"][part["material"]]["name"] == "Wall269 worn steel PBR"
                for part in mesh["primitives"]
            ), (name, identifier)


def test_console_uses_separate_metal_worktop_and_recessed_display():
    import json
    import struct

    from interior_batch import OUTPUT

    path = OUTPUT / "city_industrial_service_tunnel" / "environment.glb"
    with path.open("rb") as glb:
        size = struct.unpack("<4sIII4s", glb.read(20))[3]
        data = json.loads(glb.read(size))
    nodes = {node["name"]: node for node in data["nodes"]}
    terminal = "southeast_terminal"
    root = nodes[f"Occludable_{terminal}"]
    parts = [data["nodes"][index]["name"] for index in root["children"]]
    assert f"{terminal} display bezel" in parts
    assert sum(name.startswith(f"{terminal} control key") for name in parts) == 4
    for label, expected in (
        ("worktop", "Brushed equipment worktop"), ("display", "Console low-light display"),
    ):
        mesh = data["meshes"][nodes[f"{terminal} {label}"]["mesh"]]
        material = data["materials"][mesh["primitives"][0]["material"]]
        assert material["name"] == expected
        assert max(material.get("emissiveFactor", [0])) < .25


def test_service_tunnel_decor_is_exported_without_tactical_obstacles():
    import json
    import struct

    from interior_batch import MAPS, OUTPUT, decorative_fixtures

    name = "city_industrial_service_tunnel"
    decor = {row["id"] for row in decorative_fixtures(name)}
    assert len(decor) == 3
    tactical = json.loads((MAPS / f"{name}.walls.json").read_text())
    assert decor.isdisjoint(row["id"] for row in tactical["walls"])
    with (OUTPUT / name / "environment.glb").open("rb") as model:
        size = struct.unpack("<4sIII4s", model.read(20))[3]
        nodes = json.loads(model.read(size))["nodes"]
    groups = {node["name"]: node["children"] for node in nodes if node.get("children")}
    for identifier in decor:
        children = [nodes[index] for index in groups[f"Occludable_{identifier}"]]
        assert sum("mesh" in child for child in children) == 2

    survey = json.loads((MAPS / f"{name}.wall-traces.json").read_text())
    grates = {row["id"] for row in survey["walls"]
              if row.get("kind") == "floor_detail" and row.get("collision") is False}
    assert len(grates) == 3
    floor_details = {row["id"] for row in tactical["walls"]
                     if row["kind"] == "floor_detail" and not row["blocks_sight"]}
    assert grates <= floor_details
    for identifier in grates:
        children = [nodes[index] for index in groups[f"Occludable_{identifier}"]]
        bars = [node for node in children if node["name"].startswith("Drain grate bar")]
        assert len(bars) == 10
        assert all(node["translation"][1] < .02 for node in bars)


def test_penthouse_ripple_exports_only_a_local_scale_animation():
    import json
    import struct

    from interior_batch import OUTPUT

    path = OUTPUT / "city_interior_penthouse_atrium" / "environment.glb"
    with path.open("rb") as glb:
        size = struct.unpack("<4sIII4s", glb.read(20))[3]
        data = json.loads(glb.read(size))
        binary_size, _ = struct.unpack("<I4s", glb.read(8))
        binary = glb.read(binary_size)
    animation = next(clip for clip in data["animations"] if clip["name"] == "AtriumWaterRipple")
    channel, = animation["channels"]
    target = channel["target"]
    assert target["path"] == "scale"
    assert data["nodes"][target["node"]]["name"] == "center_fountain ripple"
    sampler = animation["samplers"][channel["sampler"]]
    values = data["accessors"][sampler["output"]]
    view = data["bufferViews"][values["bufferView"]]
    offset = view.get("byteOffset", 0) + values.get("byteOffset", 0)
    scales = [struct.unpack_from("<3f", binary, offset+index*12)[0] for index in range(values["count"])]
    assert min(scales) < 1.0 < max(scales)
