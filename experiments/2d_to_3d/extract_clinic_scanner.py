"""Isolate the scanner from the original clinic illustration for local reconstruction."""
import json
from pathlib import Path

from PIL import Image, ImageDraw


def main():
    root = Path(__file__).resolve().parents[2]
    source = root / "assets/maps/city_interior_medical_clinic"
    survey = json.loads(source.with_suffix(".wall-traces.json").read_text())
    scanner = next(row for row in survey["walls"] if row["id"] == "northeast_scanner")
    canvas_width, canvas_height = survey["canvas_size"]
    with Image.open(source.with_suffix(".png")) as original:
        sx = original.width / canvas_width
        sy = original.height / canvas_height
        x1, y1, x2, y2 = scanner["rect"]
        crop = original.crop((round(x1*sx), round(y1*sy), round(x2*sx), round(y2*sy))).convert("RGBA")
    mask = Image.new("L", crop.size)
    # Hand-traced contour on the 408 × 984 crop. Leave the floor and wall out.
    contour = (
        (98,324), (105,163), (122,109), (183,78), (254,70), (345,92), (393,132),
        (407,216), (407,436), (387,526), (378,729), (390,876), (371,949),
        (302,980), (196,973), (153,935), (139,850), (134,540), (106,512), (93,446),
    )
    ImageDraw.Draw(mask).polygon([(x*crop.width/408, y*crop.height/984) for x, y in contour],
                                 fill=255)
    crop.putalpha(mask)
    sources = Path("E:/CyberCity2085-3d-lab/sources")
    crop.crop(mask.getbbox()).save(sources / "clinic-scanner-isolated.png")


if __name__ == "__main__":
    main()
