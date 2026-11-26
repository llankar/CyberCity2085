"""Replace interpolated prop footprints with a sharp tiled laboratory substrate."""
import json
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageOps

ROOT = Path(__file__).resolve().parents[2]
LAB = Path("E:/CyberCity2085-3d-lab")
phase = LAB / "generated/phase2"
base = Image.open(phase / "lab248/floor.png").convert("RGB")
survey = json.loads((ROOT / "assets/maps/city_interior_research_lab.wall-traces.json").read_text())
cw, ch = survey["canvas_size"]
w, h = base.size
mask = Image.new("L", base.size)
draw = ImageDraw.Draw(mask)
additions = json.loads(Path(__file__).with_name("lab_fixtures290.json").read_text())
assert additions["canvas_size"] == survey["canvas_size"]
rectangles = survey["walls"] + [item for item in additions["fixtures"] if item["action"] == "candidate_new"]
for item in rectangles:
    if "rect" not in item or item["id"] in {"west_wall", "east_wall"}:
        continue
    x1, y1, x2, y2 = item["rect"]
    draw.rectangle((round(x1*w/cw), round(y1*h/ch), round(x2*w/cw)-1, round(y2*h/ch)-1), fill=255)

size = max(10, round(w/40))
sample = Image.open(LAB / "sources/environment169/concrete_wall_001/diff.jpg")
tile = ImageOps.colorize(ImageOps.grayscale(sample).resize((size, size)), "#2f3a48", "#758ca4")
ImageDraw.Draw(tile).line([(0, size-1), (size-1, size-1), (size-1, 0)], fill="#25313e", width=max(1, size//24))
fill = Image.new("RGB", base.size)
for y in range(0, h, size):
    for x in range(0, w, size):
        fill.paste(tile, (x, y))
result = Image.composite(fill, base, mask)
assert Image.composite(ImageChops.difference(base, result), Image.new("RGB", base.size), ImageOps.invert(mask)).getbbox() is None
output = phase / "lab290"
output.mkdir(exist_ok=True)
result.save(output / "floor.png")
print("LAB285_FLOOR_READY")
