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
            nodes = json.loads(model.read(size))["nodes"]
        groups = {node["name"] for node in nodes
                  if node["name"].startswith("Occludable_") and node.get("children")}
        assert groups == {f"Occludable_{identifier}" for identifier in expected}
