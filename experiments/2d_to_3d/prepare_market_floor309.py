"""Repair the market stall footprint exposed by camera cutaway."""
import json
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter

root = Path(__file__).resolve().parents[2]
lab = Path("E:/CyberCity2085-3d-lab")
name = "city_exterior_neon_market_alley"
survey = json.loads((root / f"assets/maps/{name}.wall-traces.json").read_text())
base = Image.open(lab / f"sources/tactical_map/{name}.png").convert("RGB")
cw, ch = survey["canvas_size"]
w, h = base.size
x1, y1, x2, y2 = next(r["rect"] for r in survey["walls"] if r["id"] == "market_se")
left, top, right, bottom = round(x1*w/cw), round(y1*h/ch), round(x2*w/cw), round(y2*h/ch)
sx, sy = round(424*w/cw), round(326*h/ch)
patch = base.crop((sx, sy, sx+right-left, sy+bottom-top))
alpha = Image.new("L", patch.size)
rim = max(2, round(min(patch.size)*.035))
ImageDraw.Draw(alpha).rectangle((rim, rim, patch.width-rim-1, patch.height-rim-1), fill=255)
alpha = alpha.filter(ImageFilter.GaussianBlur(rim*.5))
result = base.copy()
result.paste(patch, (left, top), alpha)
mask = Image.new("1", base.size)
ImageDraw.Draw(mask).rectangle((left, top, right-1, bottom-1), fill=1)
assert Image.composite(Image.new("RGB", base.size), ImageChops.difference(base, result), mask).getbbox() is None
result.save(lab / "generated/phase2/market308/floor.png")
