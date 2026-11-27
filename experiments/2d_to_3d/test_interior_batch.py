from interior_batch import INTERIORS, fixtures


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
    assert vault["vault_core"] == "pod"
    _, tunnel = fixtures("city_industrial_service_tunnel")
    assert tunnel["ne_room_pipe_elbow"] == "pipe"
    assert "nw_room_floor_grate" not in tunnel
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
    assert len(pads) == 6

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
        nodes = json.loads(model.read(size))["nodes"]
    groups = {node["name"]: node for node in nodes if node.get("children")}
    for identifier in ("west_console", "east_console", "mid_console", "north_left_shelf", "north_right_shelf"):
        group = groups[f"Occludable_{identifier}"]
        assert any("mesh" in nodes[index] for index in group["children"])

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
                if row.get("kind") != "water" and row.get("collision") is not False}
    exported = {node["name"] for node in nodes if node["name"].startswith("Occludable_") and node.get("children")}
    assert exported == expected
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
        "city_interior_penthouse_atrium": {
            "bath_sw": "Tub basin inset", "bath_se": "Tub basin inset", "south_lounge": "south_lounge cushions",
        },
        "cybercity_inner_10_penthouse_atrium": {"sw_plant": "sw_plant foliage"},
        "cybercity_inner_12_maintenance_tunnel": {
            "se_fans": "Vent fan deck", "south_inner_storage": "Warehouse pallet rack",
        },
        "cybercity_inner_14_detention_block": {
            "east_weapons": "Warehouse pallet rack", "east_tools": "Workbench steel top",
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
        path = OUTPUT / name / "environment.glb"
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
            ("abandoned_safehouse", ("01", "06"), 3),
        ) for index in variants},
    }
    for name, expected in maps.items():
        path = OUTPUT / name / "environment.glb"
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
