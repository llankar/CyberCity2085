"""Render a numbered wall survey as a diagnostic overlay (no desktop window)."""

import argparse
from pathlib import Path
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from game.map_geometry import load_map_geometry


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("map", type=Path)
    parser.add_argument("--output", type=Path, default=Path("runtime/wall-review.png"))
    args = parser.parse_args()
    survey = load_map_geometry(args.map)
    if not survey:
        raise SystemExit("Missing/stale survey; no overlay rendered.")
    image = Image.open(args.map).convert("RGBA").resize((1200, 840))
    overlay = Image.new("RGBA", image.size)
    draw = ImageDraw.Draw(overlay)
    for wall in survey["walls"]:
        if not wall["cells"]:
            continue
        if wall.get("outline_uv"):
            points = [(u*image.width, v*image.height) for u, v in wall["outline_uv"]]
            fill = (30,120,255,75) if wall.get("kind") == "water" else (255,100,40,65)
            draw.polygon(points, fill=fill, outline=(255,140,60,255), width=2)
        else:
            for x, y in wall["cells"]:
                draw.rectangle((x*30,y*30,x*30+29,y*30+29), fill=(255,100,40,65), outline=(255,140,60,180))
        x, y = wall["cells"][0]
        draw.text((x*30+2, y*30+2), wall["id"], fill=(255,255,255,255), stroke_width=1, stroke_fill=(0,0,0,255))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    Image.alpha_composite(image, overlay).convert("RGB").save(args.output)
    print(args.output)


if __name__ == "__main__":
    main()
