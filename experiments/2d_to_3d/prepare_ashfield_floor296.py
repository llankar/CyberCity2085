"""Replace the illustrated wreck footprints with nearby intact Ashfield terrain."""
import json
from pathlib import Path
import argparse

from PIL import Image, ImageChops, ImageDraw, ImageFilter

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--version", choices=("297", "301"), default="301")
args = parser.parse_args()
repo = Path(__file__).resolve().parents[2]
phase = Path("E:/CyberCity2085-3d-lab/generated/phase2")
survey = json.loads((repo / "assets/maps/wasteland_outdoor_02_ashfield_ruins.wall-traces.json").read_text())
base = Image.open(phase / "wasteland254/floor.png").convert("RGB")
cw, ch = survey["canvas_size"]
w, h = base.size
donors = {"wreck_e": (914, 236), "wreck_w": (313, 67), "wreck_ne": (698, 29)}
result = base.copy()
mask = Image.new("1", base.size)
draw = ImageDraw.Draw(mask)
for item in survey["walls"]:
    if item["id"] not in donors:
        continue
    x1, y1, x2, y2 = item["rect"]
    left, right = round(x1*w/cw), round(x2*w/cw)
    top, bottom = round(y1*h/ch), round(y2*h/ch)
    sx, sy = donors[item["id"]]
    sx, sy = round(sx*w/cw), round(sy*h/ch)
    patch = base.crop((sx, sy, sx+right-left, sy+bottom-top))
    # Fade only the inner rim so neighbouring terrain remains exact.
    alpha = Image.new("L", patch.size)
    rim = max(2, round(min(patch.size)*.045))
    ImageDraw.Draw(alpha).rectangle(
        (rim, rim, patch.width-rim-1, patch.height-rim-1), fill=255)
    alpha = alpha.filter(ImageFilter.GaussianBlur(rim*.43))
    result.paste(patch, (left, top), alpha)
    draw.rectangle((left, top, right-1, bottom-1), fill=1)
difference = ImageChops.difference(base, result)
assert Image.composite(Image.new("RGB", base.size), difference, mask).getbbox() is None
output = phase / ("wasteland" + args.version)
output.mkdir(exist_ok=True)
result.save(output / "floor.png")
