"""Verify the urban batch exported lateral details under its occlusion roots."""
import json
from pathlib import Path
import struct

import pytest

from catalogue_test_assets import catalogue_environment


def test_parking_garage_retains_angled_vehicle_placements():
    path = catalogue_environment("city_exterior_parking_garage")
    if not path.is_file():
        pytest.skip("Build Parking Garage on E: first")
    with path.open("rb") as model:
        size = struct.unpack("<4sIII4s", model.read(20))[3]
        nodes = json.loads(model.read(size))["nodes"]
    for identifier in ("west_stair", "center_stair", "east_stair"):
        stair = next(node for node in nodes if node["name"] == f"Occludable_{identifier}")
        parts = [nodes[index]["name"] for index in stair["children"]]
        assert sum(part.startswith("Garage stair nosing") for part in parts) == 7
        assert sum(part.startswith("Garage stair cheek wall") for part in parts) == 2
    roof = next(node for node in nodes if node["name"] == "Occludable_north_roof_w")
    assert any(nodes[index]["name"] == "north_roof_w surveyed roof HVAC" for index in roof["children"])
    for identifier, angle in (("car_n4", -57), ("car_w", 19), ("car_mideast", -22)):
        import math
        car = next(node for node in nodes if node["name"] == f"Occludable_{identifier}")
        expected = abs(math.sin(math.radians(angle)/2))
        assert any(abs(nodes[index].get("rotation", [0, 0])[1]) == pytest.approx(expected)
                   for index in car["children"])


def test_downtown_garden_kiosk_exports_roof_planting():
    path = catalogue_environment("city_exterior_downtown_intersection")
    if not path.is_file():
        pytest.skip("Build Downtown Intersection on E: first")
    with path.open("rb") as model:
        size = struct.unpack("<4sIII4s", model.read(20))[3]
        nodes = json.loads(model.read(size))["nodes"]
    kiosk = next(node for node in nodes if node["name"] == "Occludable_southeast_kiosk")
    parts = [nodes[index]["name"] for index in kiosk["children"]]
    assert sum(part.startswith("Garden kiosk raised planter") for part in parts) == 2
    assert sum(part.startswith("Garden kiosk roof planting") for part in parts) == 10
    for identifier in ("northwest_roof", "northeast_roof", "southwest_annex"):
        roof = next(node for node in nodes if node["name"] == f"Occludable_{identifier}")
        assert any(nodes[index]["name"] == f"{identifier} surveyed roof HVAC"
                   for index in roof["children"])
    for identifier in ("car_north", "car_midwest", "car_southeast"):
        car = next(node for node in nodes if node["name"] == f"Occludable_{identifier}")
        components = [nodes[index] for index in car["children"]]
        assert any(.05 < abs(part.get("rotation", [0, 0])[1]) < .69 for part in components)
    for side, count in (("west", 5), ("east", 3)):
        barrier = next(node for node in nodes if node["name"] == f"Occludable_{side}_barrier")
        parts = [nodes[index]["name"] for index in barrier["children"]]
        assert sum(part.startswith("Downtown barrier steel brace") for part in parts) == count


def test_corporate_plaza_tower_entrances_face_the_square():
    path = catalogue_environment("city_exterior_corporate_plaza")
    if not path.is_file():
        pytest.skip("Build Corporate Plaza on E: first")
    with path.open("rb") as model:
        size = struct.unpack("<4sIII4s", model.read(20))[3]
        nodes = json.loads(model.read(size))["nodes"]
    monument = next(node for node in nodes if node["name"] == "Occludable_monument")
    parts = [nodes[index]["name"] for index in monument["children"]]
    assert sum(part.startswith("Corporate monument diamond tier") for part in parts) == 3
    assert "Corporate monument luminous crest" in parts
    for side, inward in (("west", 1), ("east", -1)):
        for position in ("north", "middle", "south"):
            label = f"{side}_tower_{position}"
            root = next(node for node in nodes if node["name"] == f"Occludable_{label}")
            parts = {nodes[index]["name"]: nodes[index] for index in root["children"]}
            surround = parts[f"{label} plaza entrance surround"]
            light = parts[f"{label} plaza entrance light"]
            assert (light["translation"][0] - surround["translation"][0])*inward > 0
            if position == "middle":
                assert sum(part.startswith(f"{label} rooftop duct section") for part in parts) == 3


@pytest.mark.parametrize("name", [
    "city_exterior_billboard_avenue",
    "cybercity_street_15_billboard_avenue",
    "cybercity_street_16_billboard_avenue",
    "cybercity_street_02_neon_market_alley",
    "cybercity_street_07_neon_market_alley",
    "cybercity_street_08_neon_market_alley",
])
def test_lateral_facade_bands_keep_building_occlusion(name):
    path = catalogue_environment(name)
    if not path.is_file():
        pytest.skip("Run the urban Blender batch on E: first")
    with path.open("rb") as glb:
        _, _, _, size, _ = struct.unpack("<4sIII4s", glb.read(20))
        nodes = json.loads(glb.read(size))["nodes"]
    bands = {index for index, node in enumerate(nodes) if " side facade band" in node["name"]}
    assert bands
    grouped = {index for node in nodes if node["name"].startswith("Occludable_")
               for index in node.get("children", [])}
    assert bands <= grouped
    rear_doors = {index for index, node in enumerate(nodes) if " rear service door" in node["name"]}
    assert rear_doors and rear_doors <= grouped
    parapets = {index for index, node in enumerate(nodes) if " roof parapet" in node["name"]}
    assert parapets and parapets <= grouped
    assert len(parapets) % 4 == 0
    fans = {index for index, node in enumerate(nodes) if " surveyed roof HVAC" in node["name"]}
    curbs = {index for index, node in enumerate(nodes) if " roof HVAC mounting curb" in node["name"]}
    expected = 2 if name == "cybercity_street_02_neon_market_alley" else 3
    assert len(fans) == len(curbs) == expected
    assert (fans | curbs) <= grouped

def test_billboard_benches_export_as_grouped_panels():
    path = Path("E:/CyberCity2085-3d-lab/generated/phase2/billboard_avenues/"
                "city_exterior_billboard_avenue/environment.glb")
    if not path.is_file():
        pytest.skip("Run the urban Blender batch on E: first")
    with path.open("rb") as glb:
        _, _, _, size, _ = struct.unpack("<4sIII4s", glb.read(20))
        nodes = json.loads(glb.read(size))["nodes"]
    benches = [node for node in nodes if node["name"].startswith("Occludable_")
               and any(" seat panel" in nodes[index]["name"] for index in node.get("children", []))]
    assert len(benches) == 6
    for bench in benches:
        parts = [nodes[index]["name"] for index in bench["children"]]
        assert sum(" seat panel" in part for part in parts) in (2, 3)
        assert sum(" seat panel" in part for part in parts) == sum(" back panel" in part for part in parts)

def test_billboard_planters_export_one_two_tone_foliage_mesh_per_group():
    path = Path("E:/CyberCity2085-3d-lab/generated/phase2/billboard_avenues/"
                "city_exterior_billboard_avenue/environment.glb")
    if not path.is_file():
        pytest.skip("Run the urban Blender batch on E: first")
    with path.open("rb") as glb:
        _, _, _, size, _ = struct.unpack("<4sIII4s", glb.read(20))
        data = json.loads(glb.read(size))
    nodes = data["nodes"]
    plants = [node for node in nodes if node["name"].endswith(" shrub foliage")]
    assert plants
    grouped = {child for node in nodes if node["name"].startswith("Occludable_")
               for child in node.get("children", [])}
    for plant in plants:
        assert nodes.index(plant) in grouped
        primitives = data["meshes"][plant["mesh"]]["primitives"]
        assert len({primitive["material"] for primitive in primitives}) == 2

def test_civic_kiosk_exports_controls_under_the_occlusion_group():
    path = Path("E:/CyberCity2085-3d-lab/generated/phase2/billboard_avenues/"
                "city_district_civic_center/environment.glb")
    if not path.is_file():
        pytest.skip("Run the civic Blender batch on E: first")
    with path.open("rb") as glb:
        _, _, _, size, _ = struct.unpack("<4sIII4s", glb.read(20))
        nodes = json.loads(glb.read(size))["nodes"]
    kiosk = next(node for node in nodes if node["name"] == "Occludable_northwest_kiosk")
    parts = {nodes[index]["name"] for index in kiosk["children"]}
    assert {f"northwest_kiosk {part}" for part in ("screen", "screen bezel", "hood", "control shelf")} <= parts
    assert sum(" service vent" in part for part in parts) == 3
    survey = Path(__file__).resolve().parents[2] / "assets/maps/city_district_civic_center.wall-traces.json"
    expected = {f"Occludable_{row['id']}" for row in json.loads(survey.read_text())["walls"]}
    roots = {node["name"]: node for node in nodes if node["name"].startswith("Occludable_") and node.get("children")}
    assert roots.keys() == expected
    landmark = [nodes[index]["name"] for index in roots["Occludable_monument_planter"]["children"]]
    assert "Civic monument beacon" in landmark
    assert any(" foliage" in part for part in landmark)


def test_holo_square_exports_occludable_obstacles_and_landmark():
    path = Path("E:/CyberCity2085-3d-lab/generated/phase2/billboard_avenues/"
                "city_district_holo_square/environment.glb")
    if not path.is_file():
        pytest.skip("Run the Holo Square Blender batch on E: first")
    with path.open("rb") as glb:
        _, _, _, size, _ = struct.unpack("<4sIII4s", glb.read(20))
        nodes = json.loads(glb.read(size))["nodes"]
    roots = {node["name"]: node["children"] for node in nodes
             if node["name"].startswith("Occludable_")}
    assert len(roots) == 39
    for building in ("building_east", "building_se"):
        assert any(nodes[index]["name"] == f"{building} surveyed roof HVAC"
                   for index in roots[f"Occludable_{building}"])
    benches = [children for name, children in roots.items() if name.startswith("Occludable_bench_")]
    assert len(benches) == 14
    assert all(any(" seat panel" in nodes[index]["name"] for index in children) for children in benches)
    platform = nodes[roots["Occludable_holo_platform"][0]]
    parts = {nodes[index]["name"] for index in platform["children"]}
    assert {"Holo Square emitter", "Holo Square projection core",
            "Holo Square lower plinth", "Holo Square upper plinth"} <= parts
    assert sum(part.startswith("Holo Square projection ring ") for part in parts) == 4
    for corner in ("nw", "ne", "sw", "se"):
        label = f"sign_{corner}_base"
        island = nodes[roots[f"Occludable_{label}"][0]]
        parts = [nodes[index]["name"] for index in island["children"]]
        assert f"{label} display bezel" in parts
        assert sum(part.startswith(f"{label} display") and "bezel" not in part for part in parts) == 2


@pytest.mark.parametrize(("variant", "count"), [("05", 10), ("10", 8), ("11", 8)])
def test_civic_plaza_polygon_planters_export_foliage(variant, count):
    name = f"cybercity_street_{variant}_civic_plaza"
    path = catalogue_environment(name)
    if not path.is_file():
        pytest.skip("Run the Civic Plaza Blender batch on E: first")
    with path.open("rb") as glb:
        size = struct.unpack("<4sIII4s", glb.read(20))[3]
        nodes = json.loads(glb.read(size))["nodes"]
    roots = {node["name"]: node for node in nodes if node.get("children")}
    trace_path = Path(__file__).resolve().parents[2] / "assets/maps" / f"{name}.wall-traces.json"
    traces = json.loads(trace_path.read_text())["walls"]
    assert {f"Occludable_{trace['id']}" for trace in traces} <= roots.keys()
    monuments = {"west_monument", "east_monument"} if variant == "05" else {"center_monument"}
    for identifier in monuments:
        parts = [nodes[index]["name"] for index in roots[f"Occludable_{identifier}"]["children"]]
        for label in ("outer octagon", "raised dais", "luminous core", "top cap"):
            assert f"{identifier} {label}" in parts
    polygons = [trace["id"] for trace in traces if "polygon" in trace]
    assert len(polygons) == count
    for identifier in polygons:
        parts = [nodes[index]["name"] for index in roots[f"Occludable_{identifier}"]["children"]]
        assert any(" foliage" in part for part in parts), identifier


@pytest.mark.parametrize(("name", "folder", "fixture", "part"), [
    ("city_district_riot_square", "billboard_avenues", "bench_nw", "bench_nw seat support"),
    ("city_interior_safehouse", "interiors", "bath_showers", "Shower head"),
])
def test_riot_square_and_safehouse_export_surveyed_fixtures(name, folder, fixture, part):
    path = Path("E:/CyberCity2085-3d-lab/generated/phase2") / folder / name / "environment.glb"
    if not path.is_file():
        pytest.skip(f"Build {name} on E: first")
    with path.open("rb") as glb:
        size = struct.unpack("<4sIII4s", glb.read(20))[3]
        nodes = json.loads(glb.read(size))["nodes"]
    groups = {node["name"]: node["children"] for node in nodes if node.get("children")}
    trace_path = Path(__file__).resolve().parents[2] / "assets/maps" / f"{name}.wall-traces.json"
    traces = json.loads(trace_path.read_text())["walls"]
    expected = {f"Occludable_{row['id']}" for row in traces if not row["id"].startswith("outside_")}
    assert expected <= groups.keys()
    assert any(nodes[index]["name"].startswith(part) for index in groups[f"Occludable_{fixture}"])


@pytest.mark.parametrize("variant", ["08", "09"])
def test_freeway_rails_follow_survey_segments(variant):
    name = f"cybercity_street_{variant}_elevated_freeway"
    path = catalogue_environment(name)
    if not path.is_file():
        pytest.skip("Build the freeway on E: first")
    with path.open("rb") as glb:
        size = struct.unpack("<4sIII4s", glb.read(20))[3]
        data = json.loads(glb.read(size))
    nodes = data["nodes"]
    roots = {node["name"]: node["children"] for node in nodes if node.get("children")}
    maps = Path(__file__).resolve().parents[2] / "assets/maps"
    survey = json.loads((maps / f"{name}.wall-traces.json").read_text())
    gw, gh = json.loads((maps / f"{name}.walls.json").read_text())["grid"]
    cw, ch = survey["canvas_size"]
    for trace in survey["walls"]:
        if "points" not in trace:
            continue
        identifier = trace["id"]
        parts = [nodes[index] for index in roots[f"Occludable_{identifier}"]]
        beams = [node for node in parts if " steel beam" in node["name"]]
        points = trace["points"]
        assert len(beams) == len(points)-1
        assert sum(" post" in node["name"] for node in parts) >= len(points)
        for beam, ((ax,ay),(bx,by)) in zip(beams, zip(points,points[1:])):
            assert beam["translation"] == pytest.approx((
                (ax+bx)*gw/(2*cw)-gw/2, .54, (ay+by)*gh/(2*ch)-gh/2,
            ), abs=.0001)


    for label, elevation in (("Freeway main deck", -.025),
                             ("North under-deck strip", -1.78), ("South under-deck strip", -1.78)):
        node = next(node for node in nodes if node["name"] == label)
        position = data["meshes"][node["mesh"]]["primitives"][0]["attributes"]["POSITION"]
        bounds = data["accessors"][position]
        assert (bounds["min"][1], bounds["max"][1]) == pytest.approx((elevation, elevation))
        if "under-deck" in label:
            tactical = json.loads((maps / f"{name}.walls.json").read_text())
            rail_ids = {"highway_north_rail", "highway_south_rail"}
            blocked = {tuple(cell) for wall in tactical["walls"] if wall["id"] in rail_ids
                       for cell in wall["cells"]}
            for row in range(gh):
                if bounds["min"][2] < row+.5-gh/2 < bounds["max"][2]:
                    assert all((column,row) in blocked for column in range(gw))
    assert sum(node["name"].startswith("Freeway pier shaft") for node in nodes) == 16
    assert sum(node["name"].startswith("Freeway transverse pier cap") for node in nodes) == 8
    rail_rows = {trace["id"]: trace["points"][0][1] for trace in survey["walls"] if "points" in trace}
    for side, rail, bound in (("West", "highway_south_rail", "min"),
                              ("East", "highway_north_rail", "max")):
        node = next(node for node in nodes if node["name"] == f"{side} feeder ramp deck")
        primitives = data["meshes"][node["mesh"]]["primitives"]
        assert len(primitives) == 2
        positions = [data["accessors"][part["attributes"]["POSITION"]] for part in primitives]
        assert min(pos["min"][1] for pos in positions) == pytest.approx(-.42)
        assert max(pos["max"][1] for pos in positions) == pytest.approx(-.012)
        for pos in positions:
            assert pos[bound][2] == pytest.approx(rail_rows[rail]*gh/ch-gh/2)


@pytest.mark.parametrize(("name", "identifier"), [
    ("city_district_riot_square", "west_north_building"),
    ("city_district_civic_center", "west_outside_building"),
    ("cybercity_street_05_civic_plaza", "northwest_building"),
    ("cybercity_street_10_civic_plaza", "nw_block"),
    ("cybercity_street_11_civic_plaza", "nw_block"),
])
def test_civic_facades_export_textured_walls_and_roofs(name, identifier):
    path = catalogue_environment(name)
    if not path.is_file():
        pytest.skip("Build the civic map on E: first")
    with path.open("rb") as model:
        size = struct.unpack("<4sIII4s", model.read(20))[3]
        data = json.loads(model.read(size))
    nodes = data["nodes"]
    root = next(node for node in nodes if node["name"] == f"Occludable_{identifier}")
    parts = [nodes[index] for index in root["children"]]
    shell = next(node for node in parts if node["name"] == identifier)
    primitives = data["meshes"][shell["mesh"]]["primitives"]
    textured = {data["materials"][part["material"]]["name"] for part in primitives
                if "TEXCOORD_0" in part["attributes"]
                and "baseColorTexture" in data["materials"][part["material"]]["pbrMetallicRoughness"]}
    assert {"Civic weathered concrete", "Original rooftop artwork"} <= textured
    concrete = next(material for material in data["materials"]
                    if material["name"] == "Civic weathered concrete")
    assert "normalTexture" in concrete
    assert sum(" civic roof coping" in part["name"] for part in parts) >= 3
    if name == "city_district_riot_square":
        assert any(" civic facade band" in part["name"] for part in parts)
        assert any(" plaza-facing facade light" in part["name"] for part in parts)
        for side in ("west", "east"):
            barrier = next(node for node in nodes if node["name"] == f"Occludable_barricade_{side}")
            parts = [nodes[index]["name"] for index in barrier["children"]]
            assert sum(part.startswith("Riot barricade upright") for part in parts) == 5
        southeast = next(node for node in nodes if node["name"] == "Occludable_east_south_building")
        assert any(nodes[index]["name"] == "east_south_building surveyed roof HVAC"
                   for index in southeast["children"])
        monument = next(node for node in nodes if node["name"] == "Occludable_statue_planter")
        monument_parts = {nodes[index]["name"] for index in monument["children"]}
        assert {"Monument lower octagon", "Monument upper plinth",
                "Monument tapered bronze sculpture", "Monument bronze crest"} <= monument_parts
def test_industrial_side_pilasters_follow_independent_building_cutaways():
    path = catalogue_environment("cybercity_street_12_industrial_district")
    if not path.is_file():
        pytest.skip("Build the industrial district on E: first")
    with path.open("rb") as model:
        size = struct.unpack("<4sIII4s", model.read(20))[3]
        nodes = json.loads(model.read(size))["nodes"]
    for side in ("w", "e"):
        label = f"central_{side}_machine"
        root = next(node for node in nodes if node["name"] == f"Occludable_{label}")
        parts = [nodes[index] for index in root["children"]]
        names = {part["name"] for part in parts}
        assert {f"{label} skid", f"{label} service panel", f"{label} service indicator"} <= names
        assert sum(name.startswith(f"{label} skid edge") for name in names) == 2
        if side == "e":
            assert "East cooling manifold" in names
        assert sum("mesh" in part for part in parts) >= 3
    clad = 0
    for node in nodes:
        parts = [nodes[index]["name"] for index in node.get("children", [])]
        if any(" industrial side pilaster" in part for part in parts):
            assert node["name"].startswith("Occludable_")
            assert sum(" industrial side pilaster" in part for part in parts) == 6
            assert sum(" industrial rear door panel" in part for part in parts) == 1
            clad += 1
    assert clad >= 2


@pytest.mark.parametrize(("factory", "count"), [("nw_factory", 3), ("sw_factory", 2)])
def test_industrial_surveyed_hvac_stays_with_its_building(factory, count):
    path = catalogue_environment("cybercity_street_12_industrial_district")
    if not path.is_file():
        pytest.skip("Build the industrial district on E: first")
    with path.open("rb") as model:
        size = struct.unpack("<4sIII4s", model.read(20))[3]
        nodes = json.loads(model.read(size))["nodes"]
    building = next(node for node in nodes if node["name"] == f"Occludable_{factory}")
    parts = [nodes[index]["name"] for index in building["children"]]
    assert sum(part.startswith(f"{factory} surveyed roof HVAC") for part in parts) == count
    assert sum(part.startswith(f"{factory} roof HVAC mounting curb") for part in parts) == count
