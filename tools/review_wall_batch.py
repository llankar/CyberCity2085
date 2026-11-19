"""Make a labelled two-column survey contact sheet without opening windows."""

import argparse
from pathlib import Path
import sys

from PIL import Image, ImageDraw

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from game.map_geometry import load_map_geometry


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("maps", nargs="+")
    parser.add_argument("--output", default="runtime/manual-wall-batch.png")
    args = parser.parse_args()
    sheet = Image.new("RGB",(1920,570*((len(args.maps)+1)//2)),(10,15,20))
    for index, name in enumerate(args.maps):
        path = Path("assets/maps")/name
        image = Image.open(path).convert("RGBA").resize((960,540))
        overlay = Image.new("RGBA",image.size)
        draw = ImageDraw.Draw(overlay)
        for wall in load_map_geometry(path).get("walls",[]):
            if not wall.get("cells") or not wall.get("outline_uv"):
                continue
            points = [(u*960,v*540) for u,v in wall["outline_uv"]]
            draw.polygon(points,fill=(255,120,20,55),outline=(255,180,50,255),width=2)
        x,y=(index%2)*960,(index//2)*570
        sheet.paste(Image.alpha_composite(image,overlay).convert("RGB"),(x,y+30))
        ImageDraw.Draw(sheet).text((x+8,y+8),path.name,fill="white")
    destination=Path(args.output)
    destination.parent.mkdir(parents=True,exist_ok=True)
    sheet.save(destination)
    print(destination)


if __name__=="__main__":
    main()
