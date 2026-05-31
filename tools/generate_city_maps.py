"""Generate city battle maps from the existing wasteland map set.

The output is a set of 50 distinct city-style tactical backgrounds built from
current map textures plus procedural urban overlays. The original maps remain
the wasteland pool.
"""

from __future__ import annotations

import math
import random
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter


WIDTH = 1920
HEIGHT = 1080
SOURCE_DIR = Path("assets/maps")
OUTPUT_SCENES = (
    "exterior",
    "interior",
    "alley",
    "transit",
    "industrial",
    "rooftop",
    "plaza",
    "subway",
    "arcology",
    "district",
)


def _source_maps() -> list[Path]:
    paths = [
        path
        for path in sorted(SOURCE_DIR.iterdir(), key=lambda item: item.name.lower())
        if path.is_file()
        and path.suffix.lower() in {".png", ".jpg", ".jpeg"}
        and not path.name.startswith("city_")
        and not path.name.startswith("wasteland_")
        and "walkable" not in path.name.lower()
    ]
    if not paths:
        raise RuntimeError("No source maps found in assets/maps")
    return paths


def _load_base(path: Path, rng: random.Random) -> Image.Image:
    image = Image.open(path).convert("RGBA").resize((WIDTH, HEIGHT), Image.LANCZOS)
    if rng.random() < 0.5:
        image = image.transpose(Image.FLIP_LEFT_RIGHT)
    if rng.random() < 0.2:
        image = image.transpose(Image.FLIP_TOP_BOTTOM)
    return image


def _apply_grade(image: Image.Image, scene: str, rng: random.Random) -> Image.Image:
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    tint = {
        "exterior": (18, 38, 60, 60),
        "interior": (16, 24, 40, 100),
        "alley": (24, 18, 42, 85),
        "transit": (14, 38, 54, 70),
        "industrial": (34, 28, 22, 78),
        "rooftop": (20, 42, 58, 65),
        "plaza": (16, 34, 44, 55),
        "subway": (18, 20, 32, 95),
        "arcology": (12, 30, 54, 75),
        "district": (22, 28, 38, 70),
    }[scene]
    ImageDraw.Draw(overlay).rectangle([0, 0, WIDTH, HEIGHT], fill=tint)
    if scene in {"exterior", "rooftop", "district"}:
        overlay = ImageChops.add(overlay, Image.new("RGBA", image.size, (40, 130, 180, 18)))
    if scene in {"interior", "subway", "arcology"}:
        overlay = ImageChops.add(overlay, Image.new("RGBA", image.size, (30, 80, 150, 24)))
    if scene in {"alley", "industrial"}:
        overlay = ImageChops.add(overlay, Image.new("RGBA", image.size, (60, 40, 24, 18)))

    image = Image.alpha_composite(image, overlay)
    image = ImageEnhance.Color(image).enhance(0.72 if scene in {"interior", "subway"} else 0.85)
    image = ImageEnhance.Contrast(image).enhance(1.08)
    image = ImageEnhance.Brightness(image).enhance(0.92 if scene != "plaza" else 1.0)
    if rng.random() < 0.35:
        image = image.filter(ImageFilter.GaussianBlur(radius=0.35))
    return image


def _draw_glow(draw: ImageDraw.ImageDraw, xyxy: tuple[int, int, int, int], fill: tuple[int, int, int, int], outline: tuple[int, int, int, int]) -> None:
    x1, y1, x2, y2 = xyxy
    for pad, alpha in ((10, 24), (6, 44), (2, 90)):
        draw.rounded_rectangle([x1 - pad, y1 - pad, x2 + pad, y2 + pad], radius=8 + pad, outline=(*outline[:3], alpha), width=2)
    draw.rounded_rectangle([x1, y1, x2, y2], radius=6, fill=fill, outline=outline, width=2)


def _add_windows(draw: ImageDraw.ImageDraw, rng: random.Random, *, x0: int, x1: int, y0: int, y1: int, cols: int, rows: int, color: tuple[int, int, int]) -> None:
    if cols <= 0 or rows <= 0:
        return
    cell_w = max(10, (x1 - x0) // cols)
    cell_h = max(10, (y1 - y0) // rows)
    for col in range(cols):
        for row in range(rows):
            if rng.random() < 0.36:
                px = x0 + col * cell_w + rng.randint(4, 8)
                py = y0 + row * cell_h + rng.randint(4, 8)
                draw.rectangle([px, py, px + max(3, cell_w // 3), py + max(3, cell_h // 3)], fill=(*color, rng.randint(120, 220)))


def _draw_exterior(image: Image.Image, rng: random.Random) -> Image.Image:
    draw = ImageDraw.Draw(image, "RGBA")
    # Building silhouettes.
    for side in (0, 1):
        base_x = 0 if side == 0 else WIDTH
        sign = 1 if side == 0 else -1
        x = 0 if side == 0 else WIDTH - 220
        for _ in range(4 + rng.randint(0, 3)):
            bw = rng.randint(120, 260)
            bh = rng.randint(300, 760)
            bx = x + sign * rng.randint(0, 120)
            if side == 0:
                x = min(380, bx + bw - rng.randint(20, 80))
                rect = [max(0, bx), max(0, HEIGHT - bh), min(WIDTH, bx + bw), HEIGHT]
            else:
                x = max(WIDTH - 380, bx - bw + rng.randint(20, 80))
                rect = [max(0, bx - bw), max(0, HEIGHT - bh), min(WIDTH, bx), HEIGHT]
            color = (18 + rng.randint(0, 18), 24 + rng.randint(0, 18), 34 + rng.randint(0, 24), 255)
            draw.rectangle(rect, fill=color)
            _add_windows(draw, rng, x0=rect[0] + 8, x1=rect[2] - 8, y0=rect[1] + 18, y1=rect[3] - 24, cols=6, rows=max(3, (rect[3] - rect[1]) // 70), color=(70, 220, 220))
    # Street perspective and lanes.
    center = WIDTH // 2
    vanishing_y = HEIGHT // 2 + 140
    draw.polygon([(0, HEIGHT), (center - 180, vanishing_y), (center - 80, vanishing_y), (200, HEIGHT)], fill=(52, 54, 60, 220))
    draw.polygon([(WIDTH, HEIGHT), (center + 180, vanishing_y), (center + 80, vanishing_y), (WIDTH - 200, HEIGHT)], fill=(52, 54, 60, 220))
    draw.line([(center - 120, HEIGHT), (center - 24, vanishing_y)], fill=(240, 190, 80, 140), width=4)
    draw.line([(center + 120, HEIGHT), (center + 24, vanishing_y)], fill=(240, 190, 80, 140), width=4)
    draw.line([(center, HEIGHT), (center, vanishing_y)], fill=(255, 255, 255, 120), width=4)
    for idx in range(10):
        y = HEIGHT - 80 - idx * 68
        draw.line([(center - 10, y), (center + 10, y - 14)], fill=(255, 255, 255, 80), width=4)
    # Neon signage and cables.
    for _ in range(8):
        sx = rng.randint(120, WIDTH - 220)
        sy = rng.randint(100, HEIGHT - 260)
        _draw_glow(draw, (sx, sy, sx + rng.randint(60, 160), sy + rng.randint(24, 56)), (20, 30, 40, 210), (80, 240, 210, 220))
    for _ in range(6):
        y = rng.randint(120, 420)
        draw.line([(0, y), (WIDTH, y + rng.randint(-18, 18))], fill=(80, 220, 255, 80), width=2)
    # Rain.
    for _ in range(650):
        x = rng.randint(0, WIDTH)
        y = rng.randint(0, HEIGHT)
        draw.line([(x, y), (x - 5, y + 18)], fill=(170, 210, 255, rng.randint(18, 55)), width=1)
    return image


def _draw_interior(image: Image.Image, rng: random.Random) -> Image.Image:
    draw = ImageDraw.Draw(image, "RGBA")
    # Ceilings and corridor panels.
    draw.rectangle([0, 0, WIDTH, 180], fill=(18, 24, 34, 235))
    for y in range(20, 160, 28):
        draw.rectangle([120, y, WIDTH - 120, y + 10], fill=(80, 220, 210, 80))
    # Perspective corridor.
    center = WIDTH // 2
    draw.polygon([(120, HEIGHT), (center - 260, 220), (center + 260, 220), (WIDTH - 120, HEIGHT)], fill=(28, 30, 40, 230))
    draw.polygon([(220, HEIGHT), (center - 170, 300), (center + 170, 300), (WIDTH - 220, HEIGHT)], fill=(36, 40, 52, 210))
    for side in (240, WIDTH - 240):
        for _ in range(8):
            w = rng.randint(30, 90)
            h = rng.randint(20, 70)
            x = side + rng.randint(-90, 90)
            y = rng.randint(230, HEIGHT - 220)
            draw.rectangle([x, y, x + w, y + h], fill=(rng.randint(30, 70), rng.randint(80, 130), rng.randint(120, 220), 150))
    # Screens and doors.
    for _ in range(12):
        x = rng.randint(160, WIDTH - 300)
        y = rng.randint(240, HEIGHT - 280)
        _draw_glow(draw, (x, y, x + rng.randint(80, 180), y + rng.randint(50, 120)), (12, 18, 28, 220), (90, 240, 255, 230))
    return image


def _draw_alley(image: Image.Image, rng: random.Random) -> Image.Image:
    draw = ImageDraw.Draw(image, "RGBA")
    # Tight walls.
    wall_w = rng.randint(220, 320)
    draw.rectangle([0, 0, wall_w, HEIGHT], fill=(30, 32, 40, 230))
    draw.rectangle([WIDTH - wall_w, 0, WIDTH, HEIGHT], fill=(28, 30, 38, 230))
    draw.polygon([(wall_w, 0), (WIDTH - wall_w, 0), (WIDTH // 2 + 40, 250), (WIDTH // 2 - 40, 250)], fill=(22, 24, 32, 210))
    # Fire escapes, signs, and puddles.
    for side_x in (wall_w - 70, WIDTH - wall_w + 20):
        for idx in range(6):
            y = 100 + idx * 120
            draw.line([(side_x, y), (side_x + (60 if side_x < WIDTH // 2 else -60), y)], fill=(150, 150, 170, 120), width=4)
            draw.line([(side_x, y), (side_x, y + 90)], fill=(150, 150, 170, 120), width=4)
    for _ in range(14):
        x = rng.randint(wall_w + 20, WIDTH - wall_w - 120)
        y = rng.randint(220, HEIGHT - 100)
        _draw_glow(draw, (x, y, x + rng.randint(50, 130), y + rng.randint(16, 46)), (14, 20, 30, 220), (255, 70, 170, 220))
    for _ in range(18):
        x = rng.randint(wall_w + 20, WIDTH - wall_w - 20)
        y = rng.randint(HEIGHT - 170, HEIGHT - 40)
        draw.ellipse([x, y, x + rng.randint(40, 120), y + rng.randint(12, 36)], fill=(20, 40, 56, 180))
    return image


def _draw_transit(image: Image.Image, rng: random.Random) -> Image.Image:
    draw = ImageDraw.Draw(image, "RGBA")
    # Tracks and bridge structure.
    left = WIDTH // 2 - 360
    right = WIDTH // 2 + 360
    draw.polygon([(0, HEIGHT), (left, 360), (right, 360), (WIDTH, HEIGHT)], fill=(34, 38, 46, 220))
    for offset in (-18, 18):
        draw.line([(WIDTH // 2 + offset, 360), (WIDTH // 2 + offset, HEIGHT)], fill=(180, 150, 90, 150), width=5)
    for y in range(420, HEIGHT, 70):
        draw.line([(WIDTH // 2 - 260, y), (WIDTH // 2 + 260, y)], fill=(220, 220, 220, 120), width=4)
    for x in range(0, WIDTH, 140):
        draw.line([(x, 260), (x + 60, 1080)], fill=(70, 90, 120, 110), width=3)
    for _ in range(10):
        x = rng.randint(100, WIDTH - 260)
        y = rng.randint(160, 360)
        _draw_glow(draw, (x, y, x + 120, y + 40), (10, 18, 28, 220), (80, 240, 180, 220))
    return image


def _draw_industrial(image: Image.Image, rng: random.Random) -> Image.Image:
    draw = ImageDraw.Draw(image, "RGBA")
    # Containers and pipes.
    for y in (HEIGHT - 200, HEIGHT - 360, HEIGHT - 520):
        for x in range(0, WIDTH, 260):
            draw.rectangle([x + 20, y, x + 220, y + 150], fill=(28 + rng.randint(0, 22), 30 + rng.randint(0, 18), 34 + rng.randint(0, 16), 230))
            draw.rectangle([x + 32, y + 20, x + 208, y + 36], fill=(220, 180, 80, 110))
    for _ in range(18):
        x = rng.randint(80, WIDTH - 180)
        y = rng.randint(140, HEIGHT - 260)
        draw.rectangle([x, y, x + rng.randint(80, 200), y + rng.randint(16, 44)], fill=(80, 90, 100, 170))
        draw.arc([x - 40, y - 40, x + 240, y + 100], 190, 340, fill=(120, 220, 220, 100), width=4)
    return image


def _draw_rooftop(image: Image.Image, rng: random.Random) -> Image.Image:
    draw = ImageDraw.Draw(image, "RGBA")
    # Roof parapets and skyline.
    draw.rectangle([0, HEIGHT - 260, WIDTH, HEIGHT], fill=(22, 28, 36, 220))
    for x in range(0, WIDTH, 180):
        draw.rectangle([x, HEIGHT - 300, x + 90, HEIGHT - 240], fill=(34, 40, 52, 255))
        draw.rectangle([x + 12, HEIGHT - 288, x + 78, HEIGHT - 252], fill=(70, 220, 210, 80))
    # Antennae and AC units.
    for _ in range(16):
        x = rng.randint(60, WIDTH - 120)
        y = rng.randint(HEIGHT - 280, HEIGHT - 40)
        draw.rectangle([x, y, x + rng.randint(30, 90), y + rng.randint(20, 60)], fill=(44, 54, 68, 230))
        draw.line([(x + 10, y), (x + 10, y - rng.randint(40, 160))], fill=(180, 210, 255, 140), width=3)
    return image


def _draw_plaza(image: Image.Image, rng: random.Random) -> Image.Image:
    draw = ImageDraw.Draw(image, "RGBA")
    # Open civic plaza with tiles and light poles.
    for x in range(0, WIDTH, 120):
        draw.line([(x, 0), (x, HEIGHT)], fill=(60, 68, 78, 70), width=1)
    for y in range(0, HEIGHT, 120):
        draw.line([(0, y), (WIDTH, y)], fill=(60, 68, 78, 70), width=1)
    draw.ellipse([WIDTH // 2 - 220, HEIGHT // 2 - 220, WIDTH // 2 + 220, HEIGHT // 2 + 220], outline=(70, 220, 220, 130), width=6)
    for angle in range(0, 360, 60):
        rad = math.radians(angle)
        x = WIDTH // 2 + int(math.cos(rad) * 280)
        y = HEIGHT // 2 + int(math.sin(rad) * 180)
        draw.line([(WIDTH // 2, HEIGHT // 2), (x, y)], fill=(80, 240, 180, 70), width=4)
    for _ in range(10):
        x = rng.randint(100, WIDTH - 100)
        y = rng.randint(120, HEIGHT - 120)
        draw.line([(x, y), (x, y + 140)], fill=(210, 220, 240, 120), width=4)
        draw.ellipse([x - 10, y - 10, x + 10, y + 10], fill=(255, 240, 100, 180))
    return image


def _draw_subway(image: Image.Image, rng: random.Random) -> Image.Image:
    draw = ImageDraw.Draw(image, "RGBA")
    # Tunnel arch and rails.
    draw.pieslice([120, 120, WIDTH - 120, HEIGHT + 280], 180, 360, fill=(22, 26, 34, 240), outline=(90, 100, 118, 200), width=5)
    draw.rectangle([WIDTH // 2 - 120, 320, WIDTH // 2 + 120, HEIGHT], fill=(18, 22, 30, 230))
    for y in range(360, HEIGHT, 70):
        draw.line([(WIDTH // 2 - 180, y), (WIDTH // 2 + 180, y)], fill=(180, 180, 190, 120), width=4)
    for x in range(WIDTH // 2 - 240, WIDTH // 2 + 241, 80):
        draw.line([(x, 320), (x - 50, HEIGHT)], fill=(75, 85, 100, 120), width=3)
    for _ in range(12):
        x = rng.randint(150, WIDTH - 300)
        y = rng.randint(180, 340)
        _draw_glow(draw, (x, y, x + rng.randint(80, 160), y + rng.randint(24, 48)), (16, 20, 32, 220), (255, 90, 120, 220))
    return image


SCENE_DRAWERS = {
    "exterior": _draw_exterior,
    "interior": _draw_interior,
    "alley": _draw_alley,
    "transit": _draw_transit,
    "industrial": _draw_industrial,
    "rooftop": _draw_rooftop,
    "plaza": _draw_plaza,
    "subway": _draw_subway,
    "arcology": _draw_interior,
    "district": _draw_exterior,
}


def _make_city_map(index: int, source: Path, scene: str) -> Image.Image:
    rng = random.Random(index * 137 + len(scene))
    image = _load_base(source, rng)
    image = _apply_grade(image, scene, rng)
    image = Image.alpha_composite(image, Image.new("RGBA", image.size, (0, 0, 0, 0)))
    drawer = SCENE_DRAWERS[scene]
    image = drawer(image, rng)
    # Final color punch and subtle glow.
    image = ImageEnhance.Sharpness(image).enhance(1.2)
    image = ImageEnhance.Brightness(image).enhance(0.98)
    return image


def generate_city_maps(output_dir: Path = SOURCE_DIR) -> list[Path]:
    source_maps = _source_maps()
    written: list[Path] = []
    for index in range(50):
        scene = OUTPUT_SCENES[index % len(OUTPUT_SCENES)]
        source = source_maps[index % len(source_maps)]
        image = _make_city_map(index + 1, source, scene)
        filename = output_dir / f"city_{scene}_{index + 1:02d}.png"
        image.save(filename)
        written.append(filename)
    return written


if __name__ == "__main__":
    generated = generate_city_maps()
    print(f"Generated {len(generated)} city maps.")
