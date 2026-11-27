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
    for rail in rails:
        mesh = data["meshes"][rail["mesh"]]
        positions = [data["accessors"][p["attributes"]["POSITION"]] for p in mesh["primitives"]]
        assert min(p["min"][0] for p in positions) <= -19.99
        assert max(p["max"][0] for p in positions) >= 19.99

def test_metro_column_details_keep_independent_visibility():
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
