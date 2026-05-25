"""Generate a batch of tactical map PNG variants from the existing set."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageEnhance, ImageFilter, ImageOps


ROOT = Path(__file__).resolve().parents[1]
MAP_DIR = ROOT / "assets" / "maps"


@dataclass(frozen=True)
class VariantRecipe:
    source: str
    output: str
    crop_scale: float
    brightness: float
    contrast: float
    color: float
    sharpness: float
    tint: tuple[int, int, int] | None = None
    scanlines: bool = False


RECIPES: tuple[VariantRecipe, ...] = (
    VariantRecipe("streets.png", "streets_neon_rain.png", 0.92, 0.98, 1.18, 1.12, 1.05, (38, 120, 180), True),
    VariantRecipe("streets.png", "streets_blackout.png", 0.88, 0.72, 1.32, 0.82, 1.08, (18, 26, 34), True),
    VariantRecipe("bridge.png", "bridge_breach.png", 0.90, 1.00, 1.22, 1.05, 1.08, (166, 118, 44), False),
    VariantRecipe("bridge.png", "bridge_fog.png", 0.86, 0.84, 1.06, 0.90, 0.95, (34, 56, 72), False),
    VariantRecipe("buildings3.jpeg", "buildings_lowlight.png", 0.90, 0.78, 1.28, 0.82, 1.05, (12, 28, 46), True),
    VariantRecipe("buildings3.jpeg", "buildings_hardlight.png", 0.94, 1.06, 1.18, 1.08, 1.05, (52, 84, 122), False),
    VariantRecipe("train bridge.png", "train_bridge_storm.png", 0.88, 0.88, 1.24, 0.86, 1.00, (28, 40, 60), True),
    VariantRecipe("train bridge.png", "train_bridge_signal.png", 0.92, 1.04, 1.10, 1.15, 1.08, (42, 112, 160), False),
    VariantRecipe("parking lot.jpeg", "parking_lot_overwatch.png", 0.91, 0.96, 1.20, 1.00, 1.02, (56, 72, 92), True),
    VariantRecipe("parking lot.jpeg", "parking_lot_grit.png", 0.87, 0.86, 1.30, 0.86, 1.06, (82, 66, 48), False),
    VariantRecipe("wreck2.jpeg", "wreck_afterstrike.png", 0.89, 0.90, 1.25, 0.88, 1.00, (110, 44, 32), True),
    VariantRecipe("wreck2.jpeg", "wreck_blueprint.png", 0.93, 1.05, 1.08, 1.18, 1.10, (34, 96, 164), False),
)


def _crop_to_ratio(img: Image.Image, scale: float) -> Image.Image:
    if not (0.50 <= scale <= 1.0):
        scale = max(0.50, min(1.0, scale))
    w, h = img.size
    crop_w = max(1, int(w * scale))
    crop_h = max(1, int(h * scale))
    left = (w - crop_w) // 2
    top = (h - crop_h) // 2
    return img.crop((left, top, left + crop_w, top + crop_h)).resize((w, h), Image.LANCZOS)


def _tint_image(img: Image.Image, tint: tuple[int, int, int] | None) -> Image.Image:
    if tint is None:
        return img
    overlay = Image.new("RGBA", img.size, (*tint, 42))
    return Image.alpha_composite(img.convert("RGBA"), overlay)


def _add_scanlines(img: Image.Image) -> Image.Image:
    scan = Image.new("RGBA", img.size, (0, 0, 0, 0))
    pixels = scan.load()
    for y in range(0, img.size[1], 4):
        for x in range(img.size[0]):
            pixels[x, y] = (0, 0, 0, 18)
    return Image.alpha_composite(img.convert("RGBA"), scan)


def _vignette(img: Image.Image) -> Image.Image:
    w, h = img.size
    overlay = Image.new("L", (w, h), 0)
    px = overlay.load()
    cx = w / 2
    cy = h / 2
    max_dist = (cx * cx + cy * cy) ** 0.5
    for y in range(h):
        for x in range(w):
            dist = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
            alpha = int(max(0, min(180, (dist / max_dist) * 180)))
            px[x, y] = alpha
    mask = overlay.filter(ImageFilter.GaussianBlur(radius=24))
    shade = Image.new("RGBA", (w, h), (0, 0, 0, 1))
    shade.putalpha(mask)
    return Image.alpha_composite(img.convert("RGBA"), shade)


def generate_variant(recipe: VariantRecipe) -> None:
    source_path = MAP_DIR / recipe.source
    output_path = MAP_DIR / recipe.output
    with Image.open(source_path) as base:
        img = base.convert("RGBA")
        img = _crop_to_ratio(img, recipe.crop_scale)
        img = ImageEnhance.Brightness(img).enhance(recipe.brightness)
        img = ImageEnhance.Contrast(img).enhance(recipe.contrast)
        img = ImageEnhance.Color(img).enhance(recipe.color)
        img = ImageEnhance.Sharpness(img).enhance(recipe.sharpness)
        img = _tint_image(img, recipe.tint)
        if recipe.scanlines:
            img = _add_scanlines(img)
        img = _vignette(img)
        img = ImageOps.autocontrast(img.convert("RGB")).convert("RGBA")
        img.save(output_path)
        print(f"saved {output_path.name}")


def main() -> None:
    MAP_DIR.mkdir(parents=True, exist_ok=True)
    for recipe in RECIPES:
        generate_variant(recipe)


if __name__ == "__main__":
    main()

