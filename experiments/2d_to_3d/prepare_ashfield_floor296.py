"""Replace the blurred wreck footprint with nearby intact Ashfield terrain."""
import json
from pathlib import Path

from PIL import Image

repo = Path(__file__).resolve().parents[2]
phase = Path("E:/CyberCity2085-3d-lab/generated/phase2")
survey = json.loads((repo / "assets/maps/wasteland_outdoor_02_ashfield_ruins.wall-traces.json").read_text())
base = Image.open(phase / "wasteland254/floor.png").convert("RGB")
cw, ch = survey["canvas_size"]
w, h = base.size
x1, y1, x2, y2 = next(row["rect"] for row in survey["walls"] if row["id"] == "wreck_e")
left, right = round(x1*w/cw), round(x2*w/cw)
top, bottom = round(y1*h/ch), round(y2*h/ch)
shift = round(47*h/ch)
patch = base.crop((left, top+shift, right, bottom+shift))
result = base.copy()
result.paste(patch, (left, top))
for rect in ((0,0,w,top),(0,bottom,w,h),(0,top,left,bottom),(right,top,w,bottom)):
    assert result.crop(rect).tobytes() == base.crop(rect).tobytes()
output = phase / "wasteland296"
output.mkdir(exist_ok=True)
result.save(output / "floor.png")
