"""Check the local batch exports against the original obstacle surveys."""
import json
import math
from pathlib import Path
import struct

import pytest


from catalogue_test_assets import catalogue_environment


def assert_road_cap_above_backing(data, fragment):
    materials = data["materials"]
    primitives = data["meshes"][fragment["mesh"]]["primitives"]
    by_material = {materials[part["material"]]["name"]: part for part in primitives}
    cap = by_material["Original rooftop artwork"]["attributes"]
    backing = by_material["Road fracture backing"]["attributes"]
    accessors = data["accessors"]
    assert "TEXCOORD_0" in cap
    assert accessors[cap["POSITION"]]["min"][1] > accessors[backing["POSITION"]]["max"][1]


def test_ashfield_exposed_wall_uprights_have_grounded_plates():
    model = catalogue_environment("wasteland_outdoor_02_ashfield_ruins")
    if not model.is_file():
        pytest.skip("Build Ashfield Ruins on E: first")
    with model.open("rb") as stream:
        size = struct.unpack("<4sIII4s", stream.read(20))[3]
        nodes = json.loads(stream.read(size))["nodes"]
    supports = 0
    for group in nodes:
        parts = [nodes[index] for index in group.get("children", [])]
        uprights = [part for part in parts if part["name"].startswith("Ruined wall steel upright")]
        plates = [part for part in parts if part["name"].startswith("Ruined wall upright base plate")]
        assert len(plates) == len(uprights)
        supports += len(plates)
    assert supports > 0


@pytest.mark.parametrize("name", [
    "cybercity_street_12_industrial_district",
    "cybercity_street_13_industrial_district",
])
def test_industrial_cargo_roof_details_share_the_container_mesh(name):
    path = catalogue_environment(name)
    if not path.is_file():
        pytest.skip("Build the experimental industrial district on E: first")
    with path.open("rb") as model:
        _, _, _, size, _ = struct.unpack("<4sIII4s", model.read(20))
        gltf = json.loads(model.read(size))
    nodes = gltf["nodes"]
    containers = [node for node in nodes if node["name"].startswith("Warehouse shipping container")]
    assert containers
    for container in containers:
        primitives = gltf["meshes"][container["mesh"]]["primitives"]
        assert len(primitives) == 3
        roof_height = max(gltf["accessors"][part["attributes"]["POSITION"]]["max"][1]
                          for part in primitives)
        assert roof_height > .90
    assert not any(node["name"].startswith(("Container roof stiffener", "Container upper corner casting"))
                   for node in nodes)


@pytest.mark.parametrize(("map_name", "expected_cranes"), [
    ("city_exterior_waterfront_docks", 1),
    ("cybercity_street_04_waterfront_docks", 2),
    ("cybercity_street_09_waterfront_docks", 4),
    ("cybercity_street_10_waterfront_docks", 4),
])
def test_waterfront_quays_export_lattice_cranes(map_name, expected_cranes):
    path = catalogue_environment(map_name)
    if not path.is_file():
        pytest.skip("Build the experimental Waterfront Docks on E: first")
    with path.open("rb") as model:
        _, _, _, size, _ = struct.unpack("<4sIII4s", model.read(20))
        gltf = json.loads(model.read(size))
    concrete = next(material for material in gltf["materials"]
                    if material["name"] == "Industrial weathered concrete")
    assert "baseColorTexture" in concrete["pbrMetallicRoughness"]
    assert "normalTexture" in concrete
    cranes = [node for node in gltf["nodes"] if node["name"].startswith("Dockside loading crane")]
    assert len(cranes) == expected_cranes
    shutters = [node for node in gltf["nodes"] if " quay service shutter" in node["name"]]
    lamps = [node for node in gltf["nodes"] if " quay service lamp" in node["name"]]
    assert shutters and len(shutters) == len(lamps)
    assert all("mesh" in node for node in shutters + lamps)
    for crane in cranes:
        primitives = gltf["meshes"][crane["mesh"]]["primitives"]
        assert sum(gltf["accessors"][part["indices"]]["count"] for part in primitives) >= 540
    # glTF +Z is south on these maps. Inspect the exported envelope in world space.
    dockside_reaches = {
        "crane_nw": (2, "min", -13.0),
        "crane_ne": (2, "min", -13.0),
        "south_crane": (2, "max", 12.0),
        "east_crane": (0, "max", 20.0),
    }
    for group in gltf["nodes"]:
        reach = dockside_reaches.get(group["name"].removeprefix("Occludable_"))
        if not reach:
            continue
        axis, bound, threshold = reach
        crane = gltf["nodes"][group["children"][0]]
        primitives = gltf["meshes"][crane["mesh"]]["primitives"]
        positions = [gltf["accessors"][part["attributes"]["POSITION"]] for part in primitives]
        offset = crane.get("translation", [0, 0, 0])[axis]
        if bound == "min":
            assert min(position[bound][axis] for position in positions) + offset < threshold
        else:
            assert max(position[bound][axis] for position in positions) + offset > threshold


def test_freight_yard_has_four_complete_rail_profiles():
    path = catalogue_environment("city_transit_freight_yard")
    if not path.is_file():
        pytest.skip("Build the experimental Freight Yard on E: first")
    with path.open("rb") as model:
        _, _, _, size, _ = struct.unpack("<4sIII4s", model.read(20))
        gltf = json.loads(model.read(size))
    concrete = next(material for material in gltf["materials"]
                    if material["name"] == "Industrial weathered concrete")
    assert "baseColorTexture" in concrete["pbrMetallicRoughness"]
    assert "normalTexture" in concrete
    nodes = gltf["nodes"]
    cladding = [node for node in nodes if " freight cladding inset" in node["name"]]
    trays = [node for node in nodes if " freight cable tray" in node["name"]
             and " clamp" not in node["name"]]
    assert trays and len(cladding) == 2 * len(trays)
    assert all("mesh" in node for node in cladding + trays)
    stacks = [node for node in nodes if node["name"].startswith("Occludable_container_")]
    assert stacks
    for stack in stacks:
        for index in stack["children"]:
            container = nodes[index]
            primitives = gltf["meshes"][container["mesh"]]["primitives"]
            assert any(
                gltf["materials"][part["material"]]["name"] == "Original rooftop artwork"
                and "TEXCOORD_0" in part["attributes"] for part in primitives
            )
    cranes = [node for node in nodes if node["name"].startswith("Dockside loading crane")]
    assert len(cranes) == 3
    for crane in cranes:
        primitives = gltf["meshes"][crane["mesh"]]["primitives"]
        triangle_indices = sum(gltf["accessors"][part["indices"]]["count"] for part in primitives)
        # Guard against exporting the simpler solid-jib portal in the freight yard.
        assert triangle_indices >= 864
    for component in ("running rail", "rail web", "rail foot"):
        rails = [node for node in nodes if node["name"].startswith(f"Freight yard {component}")]
        assert len(rails) == 4
        assert all("mesh" in rail for rail in rails)
    assert not any(node["name"].startswith("Freight yard rail splice plate") for node in nodes)
    webs = [node for node in nodes if node["name"].startswith("Freight yard rail web")]
    for web in webs:
        primitives = gltf["meshes"][web["mesh"]]["primitives"]
        assert len(primitives) == 1
        assert gltf["accessors"][primitives[0]["attributes"]["POSITION"]]["count"] > 100
    wagons = [node for node in nodes if node["name"].startswith("South siding cargo wagon")]
    assert len(wagons) == 3
    for wagon in wagons:
        parts = [nodes[index]["name"] for index in wagon["children"]]
        assert sum(part.startswith("Freight wagon bogie") for part in parts) == 2
        assert sum(part.startswith("Freight wagon steel wheel") for part in parts) == 8
        load = next(nodes[index] for index in wagon["children"]
                    if nodes[index]["name"].startswith("Warehouse shipping container"))
        primitives = gltf["meshes"][load["mesh"]]["primitives"]
        assert any(gltf["materials"][part["material"]]["name"] == "Original rooftop artwork"
                   for part in primitives)


@pytest.mark.parametrize(("family", "first_map"), [
    ("outdoor", "wasteland_outdoor_01_dust_road_ambush"),
    ("city", "wasteland_city_01_ruined_downtown"),
])
def test_generated_models_include_every_surveyed_group(family, first_map):
    if not catalogue_environment(first_map).is_file():
        pytest.skip("Run this Wasteland Blender batch on E: first")
    maps = Path(__file__).resolve().parents[2] / "assets/maps"
    surveys = sorted(maps.glob(f"wasteland_{family}_*.wall-traces.json"))
    for survey_path in surveys:
        name = survey_path.name.split(".")[0]
        if name == "wasteland_outdoor_02_ashfield_ruins":
            continue
        with catalogue_environment(name).open("rb") as model:
            magic, _, _, size, chunk = struct.unpack("<4sIII4s", model.read(20))
            assert (magic, chunk) == (b"glTF", b"JSON")
            data = json.loads(model.read(size))
            nodes = data["nodes"]
        names = {node["name"] for node in nodes if node.get("children")}
        surveyed = json.loads(survey_path.read_text())["walls"]
        assert {f"Occludable_{row['id']}" for row in surveyed if row.get("kind") != "water"} <= names, name
        assert not {f"Occludable_{row['id']}" for row in surveyed if row.get("kind") == "water"} & names, name
        open_buses = {
            "ruined_downtown": ("bus_sw", "wreck_mid_e"),
            "flooded_civic_square": ("bus_west",),
        }
        for suffix, identifiers in open_buses.items():
            if name.endswith(suffix):
                for identifier in identifiers:
                    bus = next(node for node in nodes if node["name"] == f"Occludable_{identifier}")
                    parts = [nodes[index]["name"] for index in bus["children"]]
                    assert sum(part.startswith("Bus wreck grounded tire") for part in parts) == 4
                    assert sum(part.startswith("Bus wreck hub") for part in parts) == 4
        if name.endswith("_ruined_downtown"):
            for identifier in ("wreck_nw", "wreck_mid_w"):
                wreck = next(node for node in nodes if node["name"] == f"Occludable_{identifier}")
                assert any(nodes[i]["name"].startswith("Stripped car exposed floor")
                           for i in wreck["children"]), identifier
            prefixes = {"wall": "Downtown fractured road barrier",
                        "barrier": "Downtown fractured road barrier",
                        "rubble": "Downtown fallen masonry"}
            groups = {node["name"]: node.get("children", []) for node in nodes}
            for row in surveyed:
                identifier = row["id"]
                prefix = prefixes.get(identifier.split("_", 1)[0])
                if prefix:
                    parts = [nodes[index]["name"] for index in groups[f"Occludable_{identifier}"]]
                    assert sum(part.startswith(prefix) for part in parts) == 3, identifier
                    if identifier.startswith("rubble_"):
                        assert sum(part.startswith("Downtown loose masonry fragment")
                                   for part in parts) == 4, identifier
        if name.endswith("_dust_road_ambush"):
            for row in surveyed:
                if "points" in row or "sandbag" in row["id"]:
                    cover = next(node for node in nodes if node["name"] == f"Occludable_{row['id']}")
                    parts = [nodes[i]["name"] for i in cover["children"]]
                    label, count = (("Dust road wall brace", 2*(len(row["points"])-1))
                                    if "points" in row else ("Dust road staggered sandbag", 7))
                    assert sum(part.startswith(label) for part in parts) == count
            for identifier, component in (("wreck_se", "Convoy tanker vessel"),
                                          ("wreck_south", "Wreck flatbed side rail"),
                                          ("truck_e", "Wreck flatbed side rail")):
                wreck = next(node for node in nodes if node["name"] == f"Occludable_{identifier}")
                assert any(nodes[i]["name"].startswith(component) for i in wreck["children"])
        if name.endswith("_convoy_crossing"):
            for identifier in ("wreck_w", "wreck_ne", "wreck_se", "wreck_southwest"):
                wreck = next(node for node in nodes if node["name"] == f"Occludable_{identifier}")
                assert sum(nodes[i]["name"].startswith("Wreck flatbed crossmember")
                           for i in wreck["children"]) == 7
        if name.endswith("_salt_flat_ambush"):
            poles = [node for node in nodes if node["name"].startswith("Salt flat abandoned utility pole")]
            assert len(poles) == 4
            assert all("mesh" in pole and len(pole["children"]) == 1 for pole in poles)
            for row in surveyed:
                if "points" not in row:
                    continue
                fence = next(node for node in nodes if node["name"] == f"Occludable_{row['id']}")
                parts = [nodes[i]["name"] for i in fence["children"]]
                assert sum(part.startswith("Salt flat fence post") for part in parts) == len(row["points"])
                wires = [nodes[i] for i in fence["children"]
                         if nodes[i]["name"].startswith("Salt flat fence rail")]
                assert len(wires) == 2*(len(row["points"])-1)
                for wire in wires:
                    primitive, = data["meshes"][wire["mesh"]]["primitives"]
                    bounds = data["accessors"][primitive["attributes"]["POSITION"]]
                    assert bounds["max"][1] - bounds["min"][1] > .032
            for identifier, part in (("wreck_mid_e", "Wreck flatbed crossmember"),
                                     ("wreck_south", "Convoy tanker vessel"),
                                     ("wreck_sw", "Stripped car exposed floor"),
                                     ("wreck_e", "Stripped car exposed floor"),
                                     ("wreck_southwest", "Stripped car exposed floor")):
                wreck = next(node for node in nodes if node["name"] == f"Occludable_{identifier}")
                assert "rotation" in wreck
                assert any(nodes[i]["name"].startswith(part) for i in wreck["children"])
        if name.endswith("_irradiated_basin"):
            for identifier in ("west_ruin", "east_ruin"):
                bank = next(node for node in nodes if node["name"] == f"Occludable_{identifier}")
                assert sum(nodes[i]["name"].startswith("Basin displaced bank coping")
                           for i in bank["children"]) == 3
            pools = [node for node in nodes if node["name"].startswith("Irradiated basin pool ")]
            assert len(pools) == 4
            assert all("mesh" in pool for pool in pools)
            tank = next(node for node in nodes if node["name"] == "Occludable_sw_tank")
            shell = nodes[tank["children"][0]]
            assert shell["name"] == "Open corroded basin tank"
            tank_parts = [nodes[i]["name"] for i in shell["children"]]
            assert sum(part.startswith("Corroded tank reinforcing band") for part in tank_parts) == 3
            assert sum(part.startswith("Torn tank mounting flange") for part in tank_parts) == 2
            for identifier in ("west_pipe", "east_pipe", "east_pipe2", "south_pipe"):
                group = next(node for node in nodes if node["name"] == f"Occludable_{identifier}")
                drain = next(nodes[i] for i in group["children"]
                             if nodes[i]["name"].startswith("Hollow basin drain"))
                assert len(drain["children"]) == 2
                assert all(nodes[i]["name"].startswith("Basin drain socket collar")
                           for i in drain["children"])
        if name.endswith("_cratered_waterfront"):
            crates = next(node for node in nodes if node["name"] == "Occludable_cargo_e")
            parts = [nodes[i]["name"] for i in crates["children"]]
            assert sum(part.startswith("Quay crate fitted lid") for part in parts) == 3
            assert sum(part.startswith("Quay crate lid batten") for part in parts) == 6
            cargo = next(node for node in nodes if node["name"] == "Occludable_cargo_e2")
            parts = [nodes[i]["name"] for i in cargo["children"]]
            assert sum(part.startswith("Quay tarp lashing drop") for part in parts) == 4
            assert sum(part.startswith("Quay tarp lashing buckle") for part in parts) == 4
            for identifier in ("nw_ruin", "north_ruin", "ne_ruin"):
                ruin = next(node for node in nodes if node["name"] == f"Occludable_{identifier}")
                parts = [nodes[i]["name"] for i in ruin["children"]]
                assert sum(part.startswith("Waterfront warehouse exposed joist") for part in parts) == 3
                assert any(part.startswith("Waterfront warehouse fallen deck") for part in parts)
            for identifier in ("West basin wreck", "East basin wreck", "West edge cargo wreck"):
                wreck = next(node for node in nodes if node["name"] == identifier)
                assert "mesh" in wreck
                parts = [nodes[index]["name"] for index in wreck["children"]]
                assert sum(part.startswith("Exposed shipwreck deck frame") for part in parts) == 3
                if identifier == "West edge cargo wreck":
                    assert sum(part.startswith("Cargo hatch longitudinal coaming") for part in parts) == 6
                    assert sum(part.startswith("Cargo hatch end coaming") for part in parts) == 6
                    assert sum(part.startswith("Exposed cargo hold floor") for part in parts) == 3
                else:
                    assert sum(part.startswith("Basin wreck inner deck stringer") for part in parts) == 2
                    assert sum(part.startswith("Basin wreck buckled deck plate") for part in parts) == 2
            surfaces = {node["name"]: node for node in nodes if node["name"].startswith("Water surface ")}
            assert surfaces.keys() == {"Water surface "+row["id"] for row in surveyed if row.get("kind") == "water"}
            assert all("mesh" in node for node in surfaces.values())
            for identifier, part, multiplier in (
                ("quay_west", "Intact quay coping", 1),
                ("quay_east", "Intact quay coping", 1),
                ("quay_crater_w", "Slumped crater quay block", 3),
            ):
                row = next(row for row in surveyed if row["id"] == identifier)
                quay = next(node for node in nodes if node["name"] == f"Occludable_{identifier}")
                expected = (len(row["points"])-1)*multiplier
                if identifier != "quay_crater_w":
                    cw, ch = json.loads(survey_path.read_text())["canvas_size"]
                    gw, gh = json.loads(survey_path.with_name(f"{name}.walls.json").read_text())["grid"]
                    expected = sum(
                        max(1, round(math.hypot((bx-ax)*gw/cw, (by-ay)*gh/ch)/1.25))
                        for (ax, ay), (bx, by) in zip(row["points"], row["points"][1:])
                    )
                assert sum(nodes[i]["name"].startswith(part) for i in quay["children"]) == expected
                if identifier != "quay_crater_w":
                    bollards = sum(
                        math.hypot((bx-ax)*gw/cw, (by-ay)*gh/ch) >= .85
                        for (ax, ay), (bx, by) in zip(row["points"], row["points"][1:])
                    )
                    assert sum(nodes[i]["name"].startswith("Quay bollard crown")
                               for i in quay["children"]) == bollards
        if name.endswith("_ruined_transit_plaza"):
            rails = [node for node in nodes if node["name"].startswith("South transit running rail")]
            assert len(rails) == 2
            assert all("mesh" in node for node in rails)
            for identifier in ("top_ruin", "west_top_ruin"):
                ruin = next(node for node in nodes if node["name"] == f"Occludable_{identifier}")
                assert sum(nodes[i]["name"].startswith("Station ruin fractured pier")
                           for i in ruin["children"]) == 2
            for identifier, prefix, count in (
                ("center_planter", "Station planter rim", 6),
                ("bench_n", "Station bench slat", 3),
                ("bench_s", "Station bench slat", 3),
                ("bench_n", "Station bench backrest", 1),
                ("bench_s", "Station bench backrest", 1),
            ):
                fixture = next(node for node in nodes if node["name"] == f"Occludable_{identifier}")
                assert sum(nodes[i]["name"].startswith(prefix) for i in fixture["children"]) == count
            for row in surveyed:
                if "points" not in row:
                    continue
                boundary = next(node for node in nodes if node["name"] == f"Occludable_{row['id']}")
                parts = [nodes[i]["name"] for i in boundary["children"]]
                trim = ("Station stair guard rail" if row["id"].endswith("_stairs_guard")
                        else "Station perimeter coping")
                assert sum(part.startswith(trim) for part in parts) == len(row["points"])-1
            for direction in ("nw", "ne", "sw", "se"):
                column = next(node for node in nodes if node["name"] == f"Occludable_column_{direction}")
                assert sum(nodes[i]["name"].startswith("Station column blue panel")
                           for i in column["children"]) == 3
            south = next(node for node in nodes if node["name"] == "South transit carriage")
            parts = [nodes[i]["name"] for i in south["children"]]
            rail_centers = sorted(rail["translation"][2] for rail in rails)
            wheels = [nodes[i] for i in south["children"]
                      if nodes[i]["name"].startswith("Transit carriage wheel")]
            assert len(wheels) == 8
            wheel_centers = sorted(south["translation"][2] + wheel["translation"][2] for wheel in wheels)
            assert wheel_centers == pytest.approx([center for center in rail_centers for _ in range(4)])
            assert all(wheel["translation"][1] - .16 == pytest.approx(.054) for wheel in wheels)
            assert sum(part.startswith("Transit carriage recessed coupler") for part in parts) == 2
            assert sum(part.startswith("Transit carriage dead lamp") for part in parts) == 4
            assert sum(part.startswith("Exposed transit roof rib") for part in parts) == 3
            assert not any(part.startswith("Transit carriage roof") for part in parts)
            train = next(node for node in nodes if node["name"] == "Occludable_west_train")
            parts = [nodes[i]["name"] for i in train["children"]]
            assert sum(part.startswith("Transit carriage window mullion") for part in parts) == 14
            assert sum(part.startswith("Transit roof vent") for part in parts) == 3
            for identifier in ("west_platform", "east_platform"):
                platform = next(node for node in nodes if node["name"] == f"Occludable_{identifier}")
                assert sum(nodes[i]["name"].startswith("Blue station cladding panel")
                           for i in platform["children"]) == 5
                assert sum(nodes[i]["name"].startswith("Station tactile strip rib")
                           for i in platform["children"]) == 15
        if name.endswith("_scavenger_plaza"):
            for row in surveyed:
                if row["id"].endswith("_ruin"):
                    ruin = next(node for node in nodes if node["name"] == f"Occludable_{row['id']}")
                    parts = [nodes[i]["name"] for i in ruin["children"]]
                    assert sum(part.startswith("Scavenger broken perimeter pier") for part in parts) == 3
                    assert sum(part.startswith("Scavenger fallen floor panel") for part in parts) == 2
            wreck = next(node for node in nodes if node["name"] == "Occludable_wreck_se")
            assert "rotation" in wreck
            assert sum(nodes[i]["name"].startswith("Wreck flatbed crossmember")
                       for i in wreck["children"]) == 7
            for identifier, fabrics in (("market_n", {"sand", "olive"}),
                                        ("market_center", set()), ("table_w", set())):
                stall = next(node for node in nodes if node["name"] == f"Occludable_{identifier}")
                parts = [nodes[i]["name"] for i in stall["children"]]
                assert sum(part.startswith("Scavenger parts bin") for part in parts) == 3
                stock = ("Scavenger reclaimed bearing" if identifier == "market_n"
                         else "Scavenger used motor housing")
                assert sum(part.startswith(stock) for part in parts) == 1
                assert {part.split()[2].split(".")[0] for part in parts
                        if part.startswith("Salvaged canopy ")
                        and not part.startswith(("Salvaged canopy post", "Salvaged canopy bound hem"))} == fabrics
                for index in stall["children"]:
                    cloth = nodes[index]
                    if cloth["name"].split()[:2] == ["Salvaged", "canopy"] and not cloth["name"].startswith("Salvaged canopy post"):
                        shell, patch = data["meshes"][cloth["mesh"]]["primitives"]
                        assert data["accessors"][shell["indices"]]["count"] == 39
                        assert data["accessors"][patch["indices"]]["count"] == 3
            for row in surveyed:
                if row["id"] not in {"northeast_barricade", "southwest_barricade"}:
                    continue
                barricade = next(node for node in nodes if node["name"] == f"Occludable_{row['id']}")
                parts = [nodes[i]["name"] for i in barricade["children"]]
                segments = len(row["points"])-1
                assert sum(part.startswith("Scavenger scrap barricade") for part in parts) == segments
                assert sum(part.startswith("Scavenger barricade brace") for part in parts) == segments*3
                assert sum(part.startswith("Scavenger overlapping scrap plate") for part in parts) == segments*3
        if name.endswith("_flooded_civic_square"):
            concrete = next(material for material in data["materials"]
                            if material["name"] == "Exposed concrete aggregate")
            assert "normalTexture" in concrete
            by_name = {node["name"]: node for node in nodes}
            assert "mesh" in by_name["Flooded civic square water surface"]
            bus = by_name["Occludable_bus_west"]
            assert "rotation" in bus
            assert sum(nodes[i]["name"].startswith("Exposed bus window pillar")
                       for i in bus["children"]) == 8
            monument = by_name["Occludable_monument"]
            assert sum(nodes[i]["name"].startswith("Flooded monument") for i in monument["children"]) == 4
            for row in surveyed:
                if "ruin" in row["id"] or row["id"] == "ne_corner":
                    ruin = by_name[f"Occludable_{row['id']}"]
                    parts = [nodes[i]["name"] for i in ruin["children"]]
                    assert sum(part.startswith("Flooded ruin blue plinth panel") for part in parts) == 3
                    assert any(part.startswith("Flooded ruin fallen upper floor") for part in parts)
                    assert sum(part.startswith("Flooded ruin fallen column") for part in parts) == 1
                    assert sum(part.startswith("Flooded ruin interior rubble") for part in parts) == 3
                if row["id"].startswith("planter_"):
                    planter = by_name[f"Occludable_{row['id']}"]
                    bed = next(nodes[i] for i in planter["children"] if nodes[i]["name"] == row["id"])
                    materials = {data["materials"][part["material"]]["name"]
                                 for part in data["meshes"][bed["mesh"]]["primitives"]}
                    assert "Flooded planter wet silt" in materials
                    edges = [nodes[i] for i in planter["children"]
                             if nodes[i]["name"].startswith("Flooded planter coping")]
                    assert any(nodes[i]["name"].startswith("Flooded planter broken masonry")
                               for i in planter["children"])
                    assert len(edges) == len(row["polygon"])
        if name.endswith("_burned_market_block"):
            for row in surveyed:
                if row["id"].endswith("_ruin") or row["id"] == "ne_corner":
                    ruin = next(node for node in nodes if node["name"] == f"Occludable_{row['id']}")
                    parts = [nodes[index]["name"] for index in ruin["children"]]
                    canopy, = [nodes[index] for index in ruin["children"]
                               if nodes[index]["name"].startswith("Charred market roof remnant")]
                    assert len(canopy["children"]) == 4
                    assert sum(part.startswith("Exposed market roof joist") for part in parts) == 2
                    assert sum(part.startswith("Fallen market floor fragment") for part in parts) == 3
            for identifier, has_canvas in (("stall_w", False), ("stall_middle", True)):
                stall = next(node for node in nodes if node["name"] == f"Occludable_{identifier}")
                parts = [nodes[index]["name"] for index in stall["children"]]
                assert sum(part.startswith("Charred stall upright") for part in parts) == 4
                assert any(part.startswith("Torn market canvas") for part in parts) == has_canvas
                if identifier == "stall_w":
                    tray, = [nodes[i] for i in stall["children"]
                             if nodes[i]["name"].startswith("Burned stall fallen stock tray")]
                    assert len(tray["children"]) == 2
            steel = next(node for node in nodes if node["name"] == "Occludable_stall_se")
            parts = [nodes[index]["name"] for index in steel["children"]]
            assert sum(part.startswith("Corrugated cover rib") for part in parts) == 9
            assert not any(part.startswith("Torn market canvas") for part in parts)
        if name.endswith("_ruined_downtown"):
            concrete = next(material for material in data["materials"]
                            if material["name"] == "Exposed concrete aggregate")
            assert "normalTexture" in concrete
            for identifier in ("bus_sw", "wreck_mid_e"):
                bus = next(node for node in nodes if node["name"] == f"Occludable_{identifier}")
                parts = [nodes[index]["name"] for index in bus["children"]]
                assert sum(part.startswith("Exposed bus window pillar") for part in parts) == 8
                assert "rotation" in bus
            for node in nodes:
                label = node["name"]
                if label.startswith("Occludable_") and ("ruin" in label or label.endswith("ne_corner")):
                    parts = [nodes[index]["name"] for index in node["children"]]
                    assert sum(part.startswith("Exposed corner column") for part in parts) == 2
                    assert any(part.startswith("Broken upper floor remnant") for part in parts)
                    assert sum(part.startswith("Surviving blue facade panel") for part in parts) == 4
                    assert sum(part.startswith("Downtown collapsed floor fragment") for part in parts) == 3

@pytest.mark.parametrize("variant", ("03", "08"))
def test_collapsed_span_export_includes_textured_fracture_faces(variant):
    path = catalogue_environment(f"wasteland_city_{variant}_collapsed_overpass")
    if not path.is_file():
        pytest.skip("Run the local Overpass Blender batch first")
    with path.open("rb") as model:
        _, _, _, size, _ = struct.unpack("<4sIII4s", model.read(20))
        data = json.loads(model.read(size))
    aggregate = next(i for i, material in enumerate(data["materials"])
                     if material["name"] == "Exposed concrete aggregate")
    assert "baseColorTexture" in data["materials"][aggregate]["pbrMetallicRoughness"]
    assert any(primitive.get("material") == aggregate and "TEXCOORD_0" in primitive["attributes"]
               for mesh in data["meshes"] for primitive in mesh["primitives"])
    nodes = data["nodes"]
    root_nodes = {nodes[index]["name"]: nodes[index]
                  for index in data["scenes"][data["scene"]]["nodes"]}
    for number in range(1, 5):
        ramp = root_nodes[f"Collapsed overpass ramp {number}"]
        primitives = data["meshes"][ramp["mesh"]]["primitives"]
        assert len(primitives) == 2
        assert all("TEXCOORD_0" in part["attributes"] for part in primitives)
        surface = data["accessors"][primitives[0]["attributes"]["POSITION"]]
        assert surface["min"][1] == pytest.approx(.008)
        assert surface["max"][1] == pytest.approx(.20)
        # Each deck section has two side quads and one underside quad.
        deck_indices = data["accessors"][primitives[0]["indices"]]["count"]
        shell_indices = data["accessors"][primitives[1]["indices"]]["count"]
        assert shell_indices == 3*deck_indices + 12  # two end caps
    for obstacle in ("collapsed_center_span", "collapsed_north_span"):
        assert f"Occludable_{obstacle}" in root_nodes
        fragment = next(nodes[index] for index in root_nodes[f"Occludable_{obstacle}"]["children"]
                        if nodes[index]["name"] == obstacle)
        assert_road_cap_above_backing(data, fragment)
        roadbed = root_nodes[f"{obstacle} retained roadbed"]
        materials = {primitive["material"] for primitive in data["meshes"][roadbed["mesh"]]["primitives"]}
        assert aggregate in materials
        assert len(materials) == 2
    guardrail_groups = [node for node in nodes if node["name"].startswith("Occludable_overpass_")
                        and "_rail" in node["name"]]
    assert len(guardrail_groups) == 4
    for group in guardrail_groups:
        assert all(" sloped guardrail" in nodes[index]["name"] for index in group["children"])
    for quadrant in ("nw", "ne", "sw", "se"):
        for suffix, part in (("inner_ruin", "Fallen retaining slab"),
                             ("ruin", "Surviving corner pier")):
            ruin = root_nodes[f"Occludable_{quadrant}_{suffix}"]
            names = [nodes[index]["name"] for index in ruin["children"]]
            assert any(name.startswith(part) for name in names)
            assert sum(name.startswith("Scattered concrete fragment") for name in names) == 4


def test_convoy_crossing_has_distinct_cargo_trucks():
    path = Path("E:/CyberCity2085-3d-lab/generated/phase2/billboard_avenues/"
                "wasteland_outdoor_11_convoy_crossing/environment.glb")
    if not path.is_file():
        pytest.skip("Build Convoy Crossing on E: first")
    with path.open("rb") as model:
        size = struct.unpack("<4sIII4s", model.read(20))[3]
        data = json.loads(model.read(size))
    nodes = data["nodes"]
    groups = {node["name"]: node["children"] for node in nodes if node.get("children")}
    flatbeds = [[nodes[index]["name"] for index in children] for name, children in groups.items()
                if name.startswith("Occludable_wreck_")
                and any(nodes[index]["name"].startswith("Wreck flatbed crossmember")
                        for index in children)]
    assert flatbeds
    for parts in flatbeds:
        assert sum(part.startswith("Wreck exposed frame rail") for part in parts) == 2
        assert not any(part.startswith("Convoy cargo bed") for part in parts)
    for identifier, load in {
        "convoy_w": "Convoy tarpaulin load", "convoy_mw": "Convoy tanker vessel",
        "convoy_me": "Convoy strapped crate", "convoy_e": "Convoy tarpaulin load",
        "convoy_far_e": "Convoy tarpaulin load",
    }.items():
        parts = [nodes[index]["name"] for index in groups[f"Occludable_{identifier}"]]
        assert any(part.startswith(load) for part in parts), identifier
        for index in groups[f"Occludable_{identifier}"]:
            node = nodes[index]
            if node["name"].split(".")[0] not in {
                "Convoy cab", "Convoy tarpaulin load", "Convoy tanker vessel", "Convoy strapped crate",
            }:
                continue
            surfaces = data["meshes"][node["mesh"]]["primitives"]
            materials = {data["materials"][part["material"]]["name"] for part in surfaces}
            assert "Original rooftop artwork" in materials and len(materials) == 2
            if node["name"].split(".")[0] in {"Convoy cab", "Convoy tanker vessel"}:
                assert "Convoy worn body steel" in materials
                steel = next(material for material in data["materials"]
                             if material["name"] == "Convoy worn body steel")
                assert "normalTexture" in steel
                assert "metallicRoughnessTexture" in steel["pbrMetallicRoughness"]
        assert sum(part.startswith("Convoy grille louver") for part in parts) == 3
        assert sum(part.startswith("Convoy headlamp lens") for part in parts) == 2
        assert sum(part.startswith("Convoy wheel") for part in parts) == 6
        assert sum(part.startswith("Convoy axle hub") for part in parts) == 6
        assert sum(part.startswith("Convoy door glazing") for part in parts) == 2
        assert sum(part.startswith("Convoy front mudguard") for part in parts) == 2
        for index in groups[f"Occludable_{identifier}"]:
            wheel = nodes[index]
            if wheel["name"].startswith("Convoy wheel"):
                primitive = data["meshes"][wheel["mesh"]]["primitives"][0]
                positions = data["accessors"][primitive["attributes"]["POSITION"]]
                assert wheel["translation"][1] == pytest.approx(positions["max"][0], abs=1e-5)
        if identifier == "convoy_mw":
            assert sum(part.startswith("Convoy tanker dished end") for part in parts) == 2
            assert any(part.startswith("Convoy tanker inspection hatch") for part in parts)
            assert sum(part.startswith("Convoy tanker saddle bracket") for part in parts) == 4
        if identifier == "convoy_me":
            assert sum(part.startswith("Convoy crate lid batten") for part in parts) == 12


@pytest.mark.parametrize("variant", ("03", "08"))
def test_wrecked_highway_heavy_wrecks_have_exposed_flatbeds(variant):
    path = catalogue_environment(f"wasteland_outdoor_{variant}_wrecked_highway")
    if not path.is_file():
        pytest.skip("Build Wrecked Highway on E: first")
    with path.open("rb") as model:
        size = struct.unpack("<4sIII4s", model.read(20))[3]
        data = json.loads(model.read(size))
        nodes = data["nodes"]
    groups = {node["name"]: node["children"] for node in nodes if node.get("children")}
    for identifier in ("wreck_mid_w", "wreck_mid_e", "wreck_e", "wreck_far_e", "wreck_middle5"):
        parts = [nodes[index]["name"] for index in groups[f"Occludable_{identifier}"]]
        assert sum(part.startswith("Wreck flatbed crossmember") for part in parts) == 7
        assert sum(part.startswith("Convoy wheel") for part in parts) == 6
    assert not any(nodes[index]["name"].startswith("Wreck flatbed")
                   for index in groups["Occludable_wreck_sw"])
    for identifier in ("north_collapsed_span", "south_collapsed_ramp"):
        assert any(nodes[index]["name"].startswith("Highway exposed edge reinforcement")
                   and "mesh" in nodes[index] for index in groups[f"Occludable_{identifier}"])
        deck = next(nodes[index] for index in groups[f"Occludable_{identifier}"]
                    if nodes[index]["name"] == identifier)
        materials = {data["materials"][primitive["material"]]["name"]
                     for primitive in data["meshes"][deck["mesh"]]["primitives"]}
        assert {"Original rooftop artwork", "Exposed concrete aggregate"} <= materials
        assert_road_cap_above_backing(data, deck)


@pytest.mark.parametrize("variant", ("04", "09"))
def test_trainyard_wagon_geometry_varies_by_reference_type(variant):
    path = catalogue_environment(f"wasteland_outdoor_{variant}_rusted_trainyard")
    if not path.is_file():
        pytest.skip("Build Rusted Trainyard on E: first")
    with path.open("rb") as model:
        size = struct.unpack("<4sIII4s", model.read(20))[3]
        nodes = json.loads(model.read(size))["nodes"]
    groups = {node["name"]: node["children"] for node in nodes if node.get("children")}
    for identifier, component in {
        "wagon_n1": "Covered wagon roof", "wagon_n3": "Open wagon recessed floor",
        "wagon_mid": "Open wagon recessed floor", "wagon_s": "Rail tanker cylinder",
        "north_tank": "Rail tanker cylinder",
    }.items():
        parts = [nodes[index]["name"] for index in groups[f"Occludable_{identifier}"]]
        assert any(part.startswith(component) for part in parts), identifier
        assert sum(part.startswith("Wagon bogie") for part in parts) == 2
        if identifier == "wagon_n1":
            assert sum(part.startswith("Wagon sliding door runner") for part in parts) == 4
            assert sum(part.startswith("Wagon sliding door pull") for part in parts) == 2
    bridge = next(node for node in nodes if node["name"] == "Trainyard turntable bridge")
    wagon = next(node for node in nodes if node["name"] == "Occludable_wagon_turntable")
    assert bridge["rotation"] == wagon["rotation"]
    parts = [nodes[index]["name"] for index in bridge["children"]]
    assert any(part.startswith("Turntable circular rim") for part in parts)
    assert sum(part.startswith("Turntable bridge rail") for part in parts) == 2
    assert sum(part.startswith("Turntable bridge deck") for part in parts) == 1
    assert sum(part.startswith("Turntable bridge edge beam") for part in parts) == 2
    assert sum(part.startswith("Turntable sleeper") for part in parts) == 15
    for identifier, fragments in (("northwest_ruin", 3), ("northeast_ruin", 2)):
        parts = [nodes[index]["name"] for index in groups[f"Occludable_{identifier}"]]
        assert sum(part.startswith("Workshop broken rear wall crest") for part in parts) == 1
        assert sum(part.startswith("Broken workshop frontage") for part in parts) == fragments
        assert any(part.startswith("Workshop rear wall") for part in parts)
        assert any(part.startswith("Workshop service cabinet") for part in parts)
        if identifier == "northwest_ruin":
            assert any(part.startswith("Workshop parts crate") for part in parts)
            assert any(part.startswith("Workshop fan assembly") for part in parts)


def test_turntable_ballast_stays_inside_the_wagon_footprint():
    from PIL import Image
    from prepare_floor248 import restore_donor_pavement

    floor = Image.new("RGB", (24, 24))
    source = Image.new("RGB", floor.size, (180, 140, 90))
    survey = {"canvas_size": floor.size, "walls": [
        {"id": "wagon_turntable", "rect": [4, 5, 18, 20]},
    ]}
    result = restore_donor_pavement(floor, source, survey, {"wagon_turntable": (0, 0, 4, 4)})
    assert result.getbbox() == (5, 6, 17, 19)
    assert result.getpixel((11, 12))[0] > result.getpixel((5, 6))[0] > 0
