"""Build deterministic per-item inventory art from the approved category plates.

The source catalogue remains authoritative.  This script adds a distinct color
signature, tag glyph and exact item name to the matching category illustration;
it never invents equipment or stats.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
import sys

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from game.management.equipment import default_equipment_catalog


SOURCE = ROOT / "assets" / "ui" / "inventory"
OUTPUT = SOURCE / "items"
SIZE = 384


def _font(size: int, bold: bool = False):
    candidates = [
        Path("C:/Windows/Fonts") / ("bahnschrift.ttf" if not bold else "bahnschrift.ttf"),
        Path("C:/Windows/Fonts") / ("arialbd.ttf" if bold else "arial.ttf"),
    ]
    for path in candidates:
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def _accent(item_id: str) -> tuple[int, int, int]:
    digest = hashlib.sha256(item_id.encode("utf-8")).digest()
    palette = ((0, 235, 235), (255, 177, 35), (204, 103, 255), (55, 236, 176), (255, 83, 112))
    return palette[digest[0] % len(palette)]


def _glyph(draw: ImageDraw.ImageDraw, tags: list[str], accent, box):
    left, top, right, bottom = box
    cx, cy = (left + right) // 2, (top + bottom) // 2
    width = max(3, (right-left)//18)
    tagset = set(tags)
    if tagset & {"blade", "melee"}:
        draw.line((left+12, bottom-10, right-10, top+10), fill=accent, width=width)
        draw.polygon([(right-10, top+10), (right-28, top+15), (right-15, top+28)], fill=accent)
    elif tagset & {"medical", "stimulant"}:
        draw.rounded_rectangle((cx-9, top+9, cx+9, bottom-9), 4, fill=accent)
        draw.rounded_rectangle((left+9, cy-9, right-9, cy+9), 4, fill=accent)
    elif tagset & {"stealth", "camo"}:
        draw.ellipse((left+7, cy-18, right-7, cy+18), outline=accent, width=width)
        draw.ellipse((cx-7, cy-7, cx+7, cy+7), fill=accent)
    elif tagset & {"psi", "crystal", "lens"}:
        draw.polygon([(cx, top+6), (right-8, cy), (cx, bottom-6), (left+8, cy)], outline=accent, width=width)
        draw.ellipse((cx-6, cy-6, cx+6, cy+6), fill=accent)
    elif tagset & {"tech", "cyber", "ai", "implant"}:
        draw.rounded_rectangle((left+8, top+8, right-8, bottom-8), 7, outline=accent, width=width)
        for dx, dy in ((-12,-12),(12,-12),(-12,12),(12,12)):
            draw.ellipse((cx+dx-3, cy+dy-3, cx+dx+3, cy+dy+3), fill=accent)
        draw.line((cx-12, cy-12, cx+12, cy+12), fill=accent, width=width)
    elif tagset & {"armor", "vest", "coat", "reactive", "exo", "light"}:
        draw.polygon([(cx, top+6), (right-8, top+18), (right-15, bottom-14), (cx, bottom-5), (left+15, bottom-14), (left+8, top+18)], outline=accent, width=width)
    else:
        draw.line((left+8, cy, right-8, cy), fill=accent, width=width)
        draw.line((right-23, cy-12, right-8, cy, right-23, cy+12), fill=accent, width=width)


def build() -> int:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    count = 0
    for slot, items in default_equipment_catalog().items():
        base = Image.open(SOURCE / f"{slot}.png").convert("RGB").resize((SIZE, SIZE), Image.Resampling.LANCZOS)
        base = ImageEnhance.Brightness(base.filter(ImageFilter.GaussianBlur(5))).enhance(0.28)
        for item in items:
            accent = _accent(item.id)
            canvas = base.copy()
            overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(overlay)
            draw.rectangle((0, 0, SIZE, 62), fill=(2, 10, 17, 228))
            draw.rectangle((0, SIZE-48, SIZE, SIZE), fill=(2, 10, 17, 235))
            draw.rectangle((0, 0, SIZE-1, SIZE-1), outline=(*accent, 235), width=4)
            draw.rectangle((0, 61, SIZE, 65), fill=(*accent, 210))
            _glyph(draw, item.tags, accent, (SIZE-72, 7, SIZE-12, 55))
            _glyph(draw, item.tags, (*accent, 235), (72, 96, SIZE-72, SIZE-82))
            draw.text((15, 13), item.name.upper(), font=_font(22, True), fill=(235, 246, 249, 255), stroke_width=1, stroke_fill=(0,0,0,220))
            tag_text = " // ".join(tag.upper() for tag in item.tags[:3]) or slot.replace("_", " ").upper()
            draw.text((15, SIZE-37), tag_text, font=_font(16), fill=(*accent, 255))
            canvas = Image.alpha_composite(canvas.convert("RGBA"), overlay)
            canvas.save(OUTPUT / f"{item.id}.png", optimize=True)
            count += 1
    return count


if __name__ == "__main__":
    print(f"generated={build()}")
