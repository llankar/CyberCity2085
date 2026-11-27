"""Check the local batch exports against the original obstacle surveys."""
import json
import math
from pathlib import Path
import struct

import pytest


from catalogue_test_assets import catalogue_environment


def test_freight_yard_has_four_complete_rail_profiles():
    path = catalogue_environment("city_transit_freight_yard")
    if not path.is_file():
        pytest.skip("Build the experimental Freight Yard on E: first")
    with path.open("rb") as model:
        _, _, _, size, _ = struct.unpack("<4sIII4s", model.read(20))
        nodes = json.loads(model.read(size))["nodes"]
    for component in ("running rail", "rail web", "rail foot"):
        rails = [node for node in nodes if node["name"].startswith(f"Freight yard {component}")]
        assert len(rails) == 4
        assert all("mesh" in rail for rail in rails)
    wagons = [node for node in nodes if node["name"].startswith("South siding cargo wagon")]
    assert len(wagons) == 3
    for wagon in wagons:
        parts = [nodes[index]["name"] for index in wagon["children"]]
        assert sum(part.startswith("Freight wagon bogie") for part in parts) == 2
        assert sum(part.startswith("Freight wagon steel wheel") for part in parts) == 8
        assert any(part.startswith("Warehouse shipping container") for part in parts)


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
            for row in surveyed:
                if "points" not in row:
                    continue
                fence = next(node for node in nodes if node["name"] == f"Occludable_{row['id']}")
                parts = [nodes[i]["name"] for i in fence["children"]]
                assert sum(part.startswith("Salt flat fence post") for part in parts) == len(row["points"])
                assert sum(part.startswith("Salt flat fence rail") for part in parts) == 2*(len(row["points"])-1)
            for identifier, part in (("wreck_mid_e", "Wreck flatbed crossmember"),
                                     ("wreck_south", "Convoy tanker vessel")):
                wreck = next(node for node in nodes if node["name"] == f"Occludable_{identifier}")
                assert "rotation" in wreck
                assert any(nodes[i]["name"].startswith(part) for i in wreck["children"])
        if name.endswith("_irradiated_basin"):
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
        if name.endswith("_ruined_transit_plaza"):
            for identifier, prefix, count in (
                ("center_planter", "Station planter rim", 4),
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
            for identifier, fabrics in (("market_n", {"sand", "olive"}), ("market_center", set())):
                stall = next(node for node in nodes if node["name"] == f"Occludable_{identifier}")
                parts = [nodes[i]["name"] for i in stall["children"]]
                assert sum(part.startswith("Scavenger parts bin") for part in parts) == 3
                assert {part.split()[2].split(".")[0] for part in parts
                        if part.startswith("Salvaged canopy ")
                        and not part.startswith(("Salvaged canopy post", "Salvaged canopy bound hem"))} == fabrics
                assert sum(part.startswith("Salvaged canopy bound hem") for part in parts) == 2*len(fabrics)
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
                    assert sum(part.startswith("Flooded ruin interior rubble") for part in parts) == 3
                if row["id"].startswith("planter_"):
                    planter = by_name[f"Occludable_{row['id']}"]
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
                    assert sum(part.startswith("Exposed market roof joist") for part in parts) == 2
                    assert sum(part.startswith("Fallen market floor fragment") for part in parts) == 3
            for identifier, has_canvas in (("stall_w", False), ("stall_middle", True)):
                stall = next(node for node in nodes if node["name"] == f"Occludable_{identifier}")
                parts = [nodes[index]["name"] for index in stall["children"]]
                assert sum(part.startswith("Charred stall upright") for part in parts) == 4
                assert any(part.startswith("Torn market canvas") for part in parts) == has_canvas
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
        faces = data["meshes"][fragment["mesh"]]["primitives"]
        exposed = next(part for part in faces if part["material"] == aggregate)
        dark = next(part for part in faces
                    if data["materials"][part["material"]]["name"] == "Dark fractured concrete edge")
        assert data["accessors"][exposed["attributes"]["POSITION"]]["max"][1] > (
            data["accessors"][dark["attributes"]["POSITION"]]["max"][1]
        )
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
        nodes = json.loads(model.read(size))["nodes"]
    groups = {node["name"]: node["children"] for node in nodes if node.get("children")}
    for identifier, load in {
        "convoy_w": "Convoy tarpaulin load", "convoy_mw": "Convoy tanker vessel",
        "convoy_me": "Convoy strapped crate", "convoy_e": "Convoy tarpaulin load",
        "convoy_far_e": "Convoy tarpaulin load",
    }.items():
        parts = [nodes[index]["name"] for index in groups[f"Occludable_{identifier}"]]
        assert any(part.startswith(load) for part in parts), identifier
        assert sum(part.startswith("Convoy wheel") for part in parts) == 6
        if identifier == "convoy_mw":
            assert sum(part.startswith("Convoy tanker dished end") for part in parts) == 2
            assert any(part.startswith("Convoy tanker inspection hatch") for part in parts)
        if identifier == "convoy_me":
            assert sum(part.startswith("Convoy crate lid batten") for part in parts) == 12


@pytest.mark.parametrize("variant", ("03", "08"))
def test_wrecked_highway_heavy_wrecks_have_exposed_flatbeds(variant):
    path = catalogue_environment(f"wasteland_outdoor_{variant}_wrecked_highway")
    if not path.is_file():
        pytest.skip("Build Wrecked Highway on E: first")
    with path.open("rb") as model:
        size = struct.unpack("<4sIII4s", model.read(20))[3]
        nodes = json.loads(model.read(size))["nodes"]
    groups = {node["name"]: node["children"] for node in nodes if node.get("children")}
    for identifier in ("wreck_mid_w", "wreck_mid_e", "wreck_e", "wreck_far_e", "wreck_middle5"):
        parts = [nodes[index]["name"] for index in groups[f"Occludable_{identifier}"]]
        assert sum(part.startswith("Wreck flatbed crossmember") for part in parts) == 7
        assert sum(part.startswith("Convoy wheel") for part in parts) == 6
    assert not any(nodes[index]["name"].startswith("Wreck flatbed")
                   for index in groups["Occludable_wreck_sw"])


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
    bridge = next(node for node in nodes if node["name"] == "Trainyard turntable bridge")
    wagon = next(node for node in nodes if node["name"] == "Occludable_wagon_turntable")
    assert bridge["rotation"] == wagon["rotation"]
    parts = [nodes[index]["name"] for index in bridge["children"]]
    assert any(part.startswith("Turntable circular rim") for part in parts)
    assert sum(part.startswith("Turntable bridge rail") for part in parts) == 2
    assert sum(part.startswith("Turntable sleeper") for part in parts) == 15
    for identifier, fragments in (("northwest_ruin", 3), ("northeast_ruin", 2)):
        parts = [nodes[index]["name"] for index in groups[f"Occludable_{identifier}"]]
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
