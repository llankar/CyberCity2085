"""Prepare rooftop deck, street and canyon boundary geometry from original surveys."""
import argparse
import json
import math
from pathlib import Path

from shapely import constrained_delaunay_triangles, union_all
from shapely.geometry import Point, Polygon, box

MAPS = Path(__file__).resolve().parents[2] / "assets/maps"
OUTPUT = Path("E:/CyberCity2085-3d-lab/generated/phase2/billboard_avenues")
ROOFTOPS = {"city_exterior_rooftop_access", "city_rooftop_skybridge_spine"}
WATERFRONTS = {"city_exterior_waterfront_docks", "cybercity_street_04_waterfront_docks",
               "cybercity_street_09_waterfront_docks"}
FLOODED_AVENUE = "cybercity_street_13_flood_prone_avenue"
# Art-only water footprint. The original roads remain walkable in combat.
AVENUE_FLOOD_OUTLINE = [(424,0),(539,0),(542,138),(570,172),(960,184),
                        (960,284),(570,290),(550,319),(539,540),(419,540),
                        (418,327),(391,300),(0,293),(0,185),(390,177),(421,147)]


def terrain(survey):
    width, height = survey["canvas_size"]
    canvas = box(0, 0, width, height)
    streets = union_all([Polygon(row["polygon"]) for row in survey["walls"]
                         if row.get("kind") == "water"]).intersection(canvas)
    deck = canvas.difference(streets)

    def triangles(region):
        return [list(triangle.exterior.coords)[:3]
                for triangle in constrained_delaunay_triangles(region).geoms]

    seam = deck.boundary.intersection(streets.boundary)
    lines = seam.geoms if hasattr(seam, "geoms") else [seam]
    edges = []
    for line in lines:
        if line.geom_type != "LineString":
            continue
        for a,b in zip(line.coords, list(line.coords)[1:]):
            dx,dy = b[0]-a[0], b[1]-a[1]
            length = math.hypot(dx,dy)
            midpoint = ((a[0]+b[0])/2, (a[1]+b[1])/2)
            left = Point(midpoint[0]-.001*dy/length, midpoint[1]+.001*dx/length)
            # Canvas Y points down. The canyon side becomes the right-hand
            # facade normal once mapped into Blender coordinates.
            edges.append([a,b] if streets.covers(left) else [b,a])
    return {"deck": triangles(deck), "street": triangles(streets), "edges": edges}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("map", choices=sorted(ROOFTOPS | WATERFRONTS | {FLOODED_AVENUE}))
    args = parser.parse_args()
    survey = json.loads((MAPS / f"{args.map}.wall-traces.json").read_text())
    if args.map == FLOODED_AVENUE:
        survey["walls"].append({"kind": "water", "polygon": AVENUE_FLOOD_OUTLINE})
    (OUTPUT / args.map / "rooftop_terrain.json").write_text(json.dumps(terrain(survey)))


if __name__ == "__main__":
    main()
