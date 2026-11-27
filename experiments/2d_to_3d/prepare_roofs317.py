"""Clean only the six residential roof fixtures replaced by geometry."""
import json
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw

from prepare_floor248 import prepare

here = Path(__file__).resolve().parent
survey = json.loads((here / "residential_roofs317.json").read_text())
base = Image.open(here.parents[1] / "assets/maps/city_district_apartment_block.png").convert("RGB")
w, h = base.size
cw, ch = survey["canvas"]
result = base.copy()
mask = Image.new("1", base.size)
draw = ImageDraw.Draw(mask)
for _, (x1, y1, x2, y2), (sx, sy) in survey["fans"]:
    left, right, sx = (round(x*w/cw) for x in (x1, x2, sx))
    top, bottom, sy = (round(y*h/ch) for y in (y1, y2, sy))
    result.paste(base.crop((sx, sy, sx+right-left, sy+bottom-top)), (left, top))
    draw.rectangle((left, top, right-1, bottom-1), fill=1)
assert Image.composite(Image.new("RGB", base.size), ImageChops.difference(base, result), mask).getbbox() is None
out = Path("E:/CyberCity2085-3d-lab/generated/phase2/residential317")
out.mkdir(exist_ok=True)
result.save(out / "roof.png")


# Keep the crisp building subfloor and previously repaired cargo footprints.
street_survey = json.loads((here.parents[1] / "assets/maps/city_district_apartment_block.wall-traces.json").read_text())
street_survey["walls"] = [
    row for row in street_survey["walls"]
    if any(tag in row["id"] for tag in ("planter", "_tree", "vehicle", "crate"))
    and row["id"] not in {"tower_south_crates", "west_street_crates", "northwest_crate"}
]
repaired, street_mask = prepare(base, street_survey)
previous = Image.open(out.parent / "residential284/floor.png").convert("RGB")
street_floor = Image.composite(repaired, previous, Image.fromarray(street_mask))
street_floor.save(out / "street_floor.png")
(out / "street_fixtures.json").write_text(json.dumps(street_survey), encoding="utf-8")
