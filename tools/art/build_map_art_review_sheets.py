"""Build readable six-map sheets for manual environment-art review."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from PIL import Image, ImageDraw


def _capture_path(captures: Path, name: str) -> Path:
    pattern = re.compile(rf"^{re.escape(name)}-\d+x\d+\.png$")
    matches = sorted(path for path in captures.glob(f"{name}-*.png") if pattern.match(path.name))
    if len(matches) != 1:
        raise ValueError(
            f"expected exactly one primary resolution capture for {name}, found {len(matches)}"
        )
    return matches[0]


def build(captures: Path, output: Path) -> dict:
    rows = json.loads((captures / "native-report.json").read_text(encoding="utf-8"))
    if len(rows) != 122:
        raise ValueError("expected 122 native map rows")
    output.mkdir(parents=True, exist_ok=True)
    pages = []
    for page_index, start in enumerate(range(0, len(rows), 6), 1):
        sheet = Image.new("RGB", (1920, 1704), (10, 18, 25))
        draw = ImageDraw.Draw(sheet)
        names = []
        for cell, row in enumerate(rows[start:start + 6]):
            name = Path(row["map"]).stem
            source = Image.open(_capture_path(captures, name)).convert("RGB")
            source.thumbnail((960, 540))
            x, y = cell % 2 * 960, cell // 2 * 568
            sheet.paste(source, (x, y + 28))
            draw.rectangle((x, y, x + 960, y + 28), fill=(8, 22, 30))
            draw.text((x + 8, y + 7), name, fill=(126, 245, 238))
            names.append(row["map"])
        filename = f"art-review-{page_index:02d}.jpg"
        sheet.save(output / filename, quality=92, subsampling=0)
        pages.append({"file": filename, "maps": names})
    manifest = {"maps": len(rows), "pages": pages, "review_status": "NOT REVIEWED"}
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--captures", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = build(args.captures, args.output)
    print(json.dumps({"maps": result["maps"], "pages": len(result["pages"])}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
