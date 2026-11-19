"""Persistent per-background obstacle surveys in Godot texture/grid coordinates.

Generated surveys are explicitly unreviewed; they can be corrected wall by wall
without changing combat code or rescanning an edited survey at launch.
"""

from collections import deque
from hashlib import sha256
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageStat

COLS, ROWS = 40, 28


def stroke_outline(points, width):
    """Turn a traced wall centreline into an exact, bounded miter footprint."""
    normals = []
    for (ax, ay), (bx, by) in zip(points, points[1:]):
        length = math.hypot(bx-ax, by-ay)
        if not length:
            raise ValueError("Repeated consecutive points in wall trace")
        normals.append((-(by-ay)/length, (bx-ax)/length))
    left, right = [], []
    for index, (x, y) in enumerate(points):
        before = normals[max(0,index-1)]
        after = normals[min(index,len(normals)-1)]
        nx, ny = before[0]+after[0], before[1]+after[1]
        length = math.hypot(nx, ny)
        nx, ny = (nx/length,ny/length) if length else after
        scale = min(width, width/2/max(0.5,nx*after[0]+ny*after[1]))
        left.append([x+nx*scale,y+ny*scale])
        right.append([x-nx*scale,y-ny*scale])
    return left + list(reversed(right))


def geometry_path(image_path):
    return Path(image_path).with_suffix(".walls.json")


def scan_map_walls(image_path):
    """Survey solid dark/textured regions, retaining discrete numbered objects."""
    image_path = Path(image_path)
    with Image.open(image_path) as source:
        image_size = list(source.size)
        image = source.convert("RGB").resize((800, 560)).filter(ImageFilter.GaussianBlur(1))
    traced = image_path.with_suffix(".wall-traces.json")
    if traced.is_file():
        authored = json.loads(traced.read_text(encoding="utf-8"))
        width, height = authored["canvas_size"]
        walls = []
        for trace in authored["walls"]:
            mask = Image.new("L", (width, height))
            draw = ImageDraw.Draw(mask)
            if "rect" in trace:
                x0,y0,x1,y1 = trace["rect"]
                outline = [[x0,y0],[x1,y0],[x1,y1],[x0,y1]]
            else:
                outline = trace["polygon"] if "polygon" in trace else stroke_outline(trace["points"],trace["width"])
            draw.polygon([tuple(p) for p in outline], fill=255)
            sampled = mask.resize((COLS, ROWS), Image.Resampling.BOX)
            cells = [[x,y] for y in range(ROWS) for x in range(COLS) if sampled.getpixel((x,y)) >= 45] if trace.get("collision", True) else []
            wall = {"id":trace["id"],"kind":trace.get("kind", "solid_obstacle"),"blocks_sight":trace.get("blocks_sight", True),"reviewed":True,"cells":cells}
            wall["outline_uv"] = [[x/width, y/height] for x, y in outline]
            walls.append(wall)
        return {"schema_version":1,"image":image_path.name,
                "image_sha256":sha256(image_path.read_bytes()).hexdigest(),
                "image_size":image_size,"grid":[COLS,ROWS],"coordinates":"texture_top_left",
                "method":"manual_wall_traces_v1","reviewed":True,"walls":walls}
    scores = {}
    for y in range(ROWS):
        for x in range(COLS):
            tile = image.crop((x*20, y*20, (x+1)*20, (y+1)*20))
            stat = ImageStat.Stat(tile)
            brightness = sum(a*b for a, b in zip(stat.mean, (0.2126, 0.7152, 0.0722)))
            scores[x, y] = brightness - sum(stat.stddev)/3 * 0.7
    ordered = sorted(scores.values())
    threshold = min(ordered[int(len(ordered) * 0.34)], sum(ordered)/len(ordered)*0.8)
    candidates = {cell for cell, score in scores.items() if score <= threshold}
    # Remove isolated texture specks. Keep compact regions and linear structures.
    blocked = {
        (x, y) for x, y in candidates
        if sum((nx, ny) in candidates for nx, ny in ((x-1,y),(x+1,y),(x,y-1),(x,y+1))) >= 2
    }
    remaining = set(blocked)
    walls = []
    while remaining:
        start = min(remaining, key=lambda cell: (cell[1], cell[0]))
        remaining.remove(start)
        queue, cells = deque([start]), [start]
        while queue:
            x, y = queue.popleft()
            for neighbor in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
                if neighbor in remaining:
                    remaining.remove(neighbor)
                    queue.append(neighbor)
                    cells.append(neighbor)
        if len(cells) < 3:
            continue
        walls.append({"id": f"wall_{len(walls)+1:03d}", "kind": "solid_obstacle",
                      "reviewed": False, "cells": [list(cell) for cell in sorted(cells, key=lambda c:(c[1],c[0]))]})
    return {"schema_version": 1, "image": image_path.name,
            "image_sha256": sha256(image_path.read_bytes()).hexdigest(),
            "image_size": image_size, "grid": [COLS, ROWS],
            "coordinates": "texture_top_left", "method": "image_region_scan_v1",
            "reviewed": False, "walls": walls}


def load_map_geometry(image_path):
    """Use stored surveys only, and reject stale or malformed coordinates."""
    image_path = Path(image_path)
    path = geometry_path(image_path)
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or data.get("image") != image_path.name or data.get("coordinates") != "texture_top_left":
            return {}
        if data.get("schema_version") != 1 or data.get("grid") != [COLS, ROWS]:
            return {}
        if data.get("image_sha256") != sha256(image_path.read_bytes()).hexdigest():
            return {}
        identifiers = set()
        for wall in data["walls"]:
            if wall["id"] in identifiers:
                return {}
            identifiers.add(wall["id"])
            for x, y in wall["cells"]:
                if type(x) is not int or type(y) is not int or not (0 <= x < COLS and 0 <= y < ROWS):
                    return {}
        return data
    except (OSError, ValueError, KeyError, TypeError):
        return {}
