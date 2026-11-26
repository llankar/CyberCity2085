"""Repair the market stall footprint exposed by camera cutaway."""
import json
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageOps

root = Path(__file__).resolve().parents[2]
lab = Path("E:/CyberCity2085-3d-lab")
name = "city_exterior_neon_market_alley"
survey = json.loads((root / f"assets/maps/{name}.wall-traces.json").read_text())
base = Image.open(lab / f"sources/tactical_map/{name}.png").convert("RGB")
cw, ch = survey["canvas_size"]
w, h = base.size
def pixels(rect):
    a, b, c, d = rect
    return round(a*w/cw), round(b*h/ch), round(c*w/cw), round(d*h/ch)


# Use pavement from the closest aisle with similar lighting to each stall.
donor_rects = {
    "market_nw": (311, 264, 381, 320),
    "market_nmid": (342, 265, 416, 319),
    "market_ne": (541, 263, 620, 308),
    "market_sw": (155, 293, 193, 375),
    "market_smid": (425, 326, 501, 403),
    "market_se": (424, 326, 498, 403),
    "market_east": (750, 290, 782, 407),
}

result = base.copy()
mask = Image.new("1", base.size)
mask_draw = ImageDraw.Draw(mask)
processed = set()
for item in survey["walls"]:
    identifier = item["id"]
    if identifier not in donor_rects:
        continue
    left, top, right, bottom = pixels(item["rect"])
    donor = base.crop(pixels(donor_rects[identifier]))
    patch = Image.new("RGB", (right-left, bottom-top))
    mirrored = ImageOps.mirror(donor)
    for row, y in enumerate(range(0, patch.height, donor.height)):
        for column, x in enumerate(range(0, patch.width, donor.width)):
            tile = mirrored if column % 2 else donor
            patch.paste(ImageOps.flip(tile) if row % 2 else tile, (x,y))
    alpha = Image.new("L", patch.size)
    rim = max(2, round(min(patch.size)*.035))
    ImageDraw.Draw(alpha).rectangle((rim, rim, patch.width-rim-1, patch.height-rim-1), fill=255)
    alpha = alpha.filter(ImageFilter.GaussianBlur(rim*.5))
    result.paste(patch, (left, top), alpha)
    mask_draw.rectangle((left, top, right-1, bottom-1), fill=1)
    processed.add(identifier)
assert processed == donor_rects.keys()
assert Image.composite(Image.new("RGB", base.size), ImageChops.difference(base, result), mask).getbbox() is None
result.save(lab / "generated/phase2/market308/floor.png")
print("MARKET_FLOOR_PATCHED", len(processed))
