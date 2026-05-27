"""
CyberCity 2085 -- AI Sprite & Portrait Generator
Uses stabilityai/sdxl-turbo (auto-downloaded on first run, ~7 GB).
Background removal via rembg (u2net).

Generates:
  assets/units/<name>.png         -- 64x64 combat sprites (transparent background)
  assets/units/<name>_512.png     -- 512x512 full-res reference
  assets/ui/portraits/<name>.png  -- 248x248 UI portraits (matching agent_01..24 style)

Run:
    python tools/gen_sprites.py
    python tools/gen_sprites.py --only-sprites
    python tools/gen_sprites.py --only-portraits
    python tools/gen_sprites.py --steps 8     # more steps = better quality
"""

from __future__ import annotations

import argparse
import os
import pathlib
import sys
import warnings

# Force UTF-8 output on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Suppress noisy xformers / HF symlink warnings before heavy imports
warnings.filterwarnings("ignore")
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import torch
from diffusers import StableDiffusionXLPipeline
from PIL import Image, ImageEnhance, ImageFilter
import rembg

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

ROOT     = pathlib.Path(__file__).parent.parent
UNIT_DIR = ROOT / "assets" / "units"
PORT_DIR = ROOT / "assets" / "ui" / "portraits"
UNIT_DIR.mkdir(parents=True, exist_ok=True)
PORT_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

MODEL_ID = "stabilityai/sdxl-turbo"

def load_pipeline() -> StableDiffusionXLPipeline:
    print(f"Loading {MODEL_ID}  (downloads ~7 GB on first run) ...")
    pipe = StableDiffusionXLPipeline.from_pretrained(
        MODEL_ID,
        torch_dtype=torch.float16,
        variant="fp16",
    )
    pipe = pipe.to("cuda")
    pipe.set_progress_bar_config(disable=True)
    return pipe


def generate(
    pipe: StableDiffusionXLPipeline,
    prompt: str,
    negative: str = "",
    w: int = 512,
    h: int = 512,
    steps: int = 4,
    seed: int | None = None,
) -> Image.Image:
    generator = torch.Generator("cuda").manual_seed(seed) if seed is not None else None
    result = pipe(
        prompt=prompt,
        negative_prompt=negative or None,
        width=w,
        height=h,
        num_inference_steps=steps,
        guidance_scale=0.0,   # turbo uses 0 guidance
        generator=generator,
    )
    return result.images[0]


# ---------------------------------------------------------------------------
# Style constants
# ---------------------------------------------------------------------------

# Portrait: match existing agent_01..24 (photorealistic, dark moody, dramatic lighting)
_PORT_STYLE = (
    "ultra-detailed photorealistic digital painting, "
    "dark neon-lit cyberpunk background, dramatic rim lighting, "
    "cinematic close-up portrait, sharp focus, 8k, "
    "moody atmosphere, professional concept art"
)
_PORT_NEG = (
    "blurry, low quality, watermark, text, signature, logo, "
    "deformed, extra limbs, anime, flat colors, bad anatomy, "
    "white background, bright background, multiple people"
)

# Sprite: single centered full-body character, dark background for clean rembg removal
_SPR_STYLE = (
    "single character standing, centered, full body front view, "
    "dark grey background, cyberpunk sci-fi, "
    "detailed concept art illustration, dramatic lighting"
)
_SPR_NEG = (
    "multiple characters, multiple views, reference sheet, turnaround sheet, "
    "sprite sheet, white background, bright background, watermark, text, "
    "blurry, deformed, cropped, partial body, cut off head, cut off legs, "
    "low quality, extra limbs, duplicate"
)

# ---------------------------------------------------------------------------
# Portrait definitions  (filename_stem, prompt, seed)
# ---------------------------------------------------------------------------

PORTRAITS: list[tuple[str, str, int]] = [
    (
        "robot_combat",
        "menacing K-9 combat robot face close-up, scarred battle-worn dark metal plating, "
        "glowing red optic sensors, exposed wiring at jaw, titanium skull design, "
        "military AI, " + _PORT_STYLE,
        101,
    ),
    (
        "robot_support",
        "sleek support drone close-up, large luminous cyan optical array eye, "
        "smooth polished white-and-silver chassis, friendly mechanical expression, "
        "holographic blue interface glow, " + _PORT_STYLE,
        102,
    ),
    (
        "power_armor_pilot",
        "female soldier inside Mantis power armor, visor raised, intense blue eyes, "
        "cybernetic cheek implant, battle scar on cheek, cyan HUD reflections, "
        "military veteran, determined expression, " + _PORT_STYLE,
        103,
    ),
    (
        "power_armor_heavy_pilot",
        "heavily built male soldier, Titan heavy armor collar framing his face, "
        "orange visor glow reflecting on skin, shaved head, burn scar on neck, "
        "resolute expression, " + _PORT_STYLE,
        104,
    ),
    (
        "enemy_grunt",
        "corporate security trooper, blue visored helmet with expressionless faceplate, "
        "corp logo stamped on forehead plate, mass-produced soldier, "
        "cold surveillance optics, " + _PORT_STYLE,
        201,
    ),
    (
        "enemy_heavy",
        "massive corporate heavy trooper, reinforced skull helmet, red glowing optics, "
        "scarred neck brace, battle-worn intimidating face, huge frame, "
        "minigun operator, " + _PORT_STYLE,
        202,
    ),
    (
        "enemy_elite",
        "corporate elite officer, sleek black helmet with narrow gold visor slit, "
        "sharp calculating eyes barely visible, angular aggressive face, "
        "command rank insignia on collar, cold authority, " + _PORT_STYLE,
        203,
    ),
    (
        "enemy_commander",
        "mega-corp supreme commander close-up, horned black battle helmet, "
        "glowing crimson eyes, ancient war veteran, "
        "deep scars beneath the faceplate, emperor of destruction, " + _PORT_STYLE,
        204,
    ),
]


def _build_portrait_specs(
    prefix: str,
    seed_base: int,
    tone_words: list[str],
    hair_words: list[str],
    clothing_words: list[str],
    cyberware_words: list[str],
    color_words: list[str],
    backdrop_words: list[str],
) -> list[tuple[str, str, int]]:
    specs: list[tuple[str, str, int]] = []
    for idx in range(1, 51):
        tone = tone_words[(idx - 1) % len(tone_words)]
        hair = hair_words[(idx * 2) % len(hair_words)]
        clothing = clothing_words[(idx * 3) % len(clothing_words)]
        cyberware = cyberware_words[(idx * 5) % len(cyberware_words)]
        color = color_words[(idx * 7) % len(color_words)]
        backdrop = backdrop_words[(idx * 11) % len(backdrop_words)]
        prompt = (
            f"{tone} cyberpunk operative portrait, {hair}, {clothing}, {cyberware}, "
            f"{color} neon accents, {backdrop}, " + _PORT_STYLE
        )
        specs.append((f"{prefix}_{idx:02d}", prompt, seed_base + idx))
    return specs


def _build_robot_portrait_specs(seed_base: int) -> list[tuple[str, str, int]]:
    chassis_words = [
        "sleek sentinel chassis",
        "heavy breacher chassis",
        "compact scout chassis",
        "angular hunter chassis",
        "industrial service chassis",
        "armored enforcement chassis",
        "lanky recon chassis",
        "bulky siege chassis",
        "polished ceremonial chassis",
        "scarred salvage-built chassis",
    ]
    optic_words = [
        "single red optic",
        "paired cyan optics",
        "tri-lens amber optics",
        "narrow green sensor slit",
        "glowing violet visor array",
        "stacked white observation lenses",
        "infrared targeting cluster",
        "cold blue tactical eye",
        "gold status optic",
        "hexagonal crimson sensor",
    ]
    wear_words = [
        "battle scratches across the faceplate",
        "oily scorch marks on the cheek plating",
        "fresh weld seams along the jaw",
        "exposed cabling at the neck ring",
        "polished armor with clean corporate decals",
        "dust-caked vents and dented plating",
        "warning stripes chipped at the edges",
        "reinforced cheek guards and bolted seams",
        "smoke residue around the optics",
        "maintenance panel scars and rivets",
    ]
    detail_words = [
        "hydraulic jawline",
        "antenna cluster crown",
        "sensor whiskers",
        "vented throat guard",
        "shoulder-mounted comms mast",
        "mechanical spine fins",
        "compact threat halo",
        "grappler collar assembly",
        "servo-packed neck brace",
        "industrial warning sigils",
    ]
    glow_words = [
        "red threat glow",
        "cyan diagnostics glow",
        "amber alert glow",
        "green standby glow",
        "violet command glow",
        "white scan glow",
        "blue target glow",
        "orange reactor glow",
        "magenta pulse glow",
        "gold status glow",
    ]
    backdrop_words = [
        "wet neon alley reflections",
        "holographic industrial haze",
        "smoky warehouse lighting",
        "rain-streaked night skyline",
        "security bunker shadows",
        "maintenance bay sparks",
        "cold factory catwalks",
        "amber emergency lighting",
        "city surveillance grid glow",
        "steel corridor gloom",
    ]
    specs: list[tuple[str, str, int]] = []
    for idx in range(1, 51):
        prompt = (
            f"robot portrait close-up, {chassis_words[(idx - 1) % len(chassis_words)]}, "
            f"{optic_words[(idx * 2) % len(optic_words)]}, {wear_words[(idx * 3) % len(wear_words)]}, "
            f"{detail_words[(idx * 5) % len(detail_words)]}, {glow_words[(idx * 7) % len(glow_words)]}, "
            f"{backdrop_words[(idx * 11) % len(backdrop_words)]}, " + _PORT_STYLE
        )
        specs.append((f"robot_{idx:02d}", prompt, seed_base + idx))
    return specs


PORTRAITS.extend(
    _build_portrait_specs(
        "agent_female",
        3000,
        [
            "female cyberpunk field agent",
            "female covert courier",
            "female corporate defector",
            "female night-market fixer",
            "female street medic",
            "female infiltration specialist",
            "female intel runner",
            "female neon detective",
            "female ex-augmented enforcer",
            "female ghost operator",
        ],
        [
            "short asymmetrical hair",
            "shoulder-length black hair",
            "platinum undercut",
            "braided cyber ponytail",
            "shaved sides and long top",
            "silver bob cut",
            "tied-back crimson hair",
            "messy salt-and-pepper hair",
            "twin braids with neon threads",
            "slick wet-look hair",
        ],
        [
            "sleek tactical coat with plated shoulders",
            "combat bodysuit under a hooded jacket",
            "armored collar and lightweight chest rig",
            "streetwear layered over stealth armor",
            "field vest with luminous seam piping",
            "reinforced blazer with hidden holsters",
            "soft scarf over a tactical undersuit",
            "magnetic utility harness and gloves",
            "urban stealth jacket with matte plates",
            "pilot jacket with embedded status LEDs",
        ],
        [
            "subdermal cheek implant",
            "optic monocle upgrade",
            "jawline data port",
            "ear-mounted comms stack",
            "temple circuit tattoo",
            "collarbone neural jack",
            "iris HUD overlay",
            "wrist projector implant",
            "neckline carbon fibers",
            "faint scar and synthetic tear duct",
        ],
        [
            "cyan",
            "magenta",
            "amber",
            "violet",
            "teal",
            "red",
            "white",
            "gold",
            "green",
            "blue",
        ],
        [
            "rainy neon street",
            "corporate atrium glow",
            "subway platform shadows",
            "smoke-filled safehouse",
            "high-rise window reflections",
            "black-market clinic lighting",
            "warehouse catwalk depth",
            "rain-slick rooftop edge",
            "underground arcade haze",
            "data-vault darkness",
        ],
    )
)

PORTRAITS.extend(
    _build_portrait_specs(
        "agent_male",
        4000,
        [
            "male cyberpunk field agent",
            "male covert courier",
            "male corporate defector",
            "male night-market fixer",
            "male street medic",
            "male infiltration specialist",
            "male intel runner",
            "male neon detective",
            "male ex-augmented enforcer",
            "male ghost operator",
        ],
        [
            "close-cropped black hair",
            "shaved head with stubble",
            "messy dark hair",
            "slicked-back silver hair",
            "undercut with shaved line art",
            "wind-tossed brown hair",
            "salt-and-pepper crew cut",
            "topknot with loose strands",
            "cropped red hair",
            "thick coarse hair and temple fade",
        ],
        [
            "armored trench coat with high collar",
            "stealth jacket over a tactical vest",
            "corporate escapee suit with hidden plates",
            "heavy-duty street armor and gloves",
            "light combat harness with ammo loops",
            "neon-lit bomber jacket and chest rig",
            "black shell coat with magnetic clasps",
            "mercenary vest with reinforced padding",
            "field jacket with layered plates",
            "covert ops coat with segmented armor",
        ],
        [
            "brow implant",
            "cybernetic jaw hinge",
            "throat port",
            "temple scanner strip",
            "data-spike behind the ear",
            "cheekline scar and optic implant",
            "neck brace with glowing nodes",
            "metallic iris lens",
            "shoulder jack cluster",
            "augmented knuckle rig",
        ],
        [
            "cyan",
            "magenta",
            "amber",
            "violet",
            "teal",
            "red",
            "white",
            "gold",
            "green",
            "blue",
        ],
        [
            "rainy neon street",
            "corporate atrium glow",
            "subway platform shadows",
            "smoke-filled safehouse",
            "high-rise window reflections",
            "black-market clinic lighting",
            "warehouse catwalk depth",
            "rain-slick rooftop edge",
            "underground arcade haze",
            "data-vault darkness",
        ],
    )
)

PORTRAITS.extend(_build_robot_portrait_specs(5000))

# ---------------------------------------------------------------------------
# Sprite definitions  (filename_stem, prompt, seed)
# ---------------------------------------------------------------------------

SPRITES: list[tuple[str, str, int]] = [
    (
        "robot_combat",
        "K-9 Breacher combat robot, squat heavily armored body, wide mechanical stance, "
        "red glowing eye visor, shoulder-mounted cannon, thick dark metal plating, "
        + _SPR_STYLE,
        1001,
    ),
    (
        "robot_support",
        "sleek support drone hovering, large cyan sensor eye, "
        "smooth white-and-silver chassis, multiple thin manipulator arms, "
        "thruster pods underneath, " + _SPR_STYLE,
        1002,
    ),
    (
        "power_armor",
        "Mantis power armor exosuit, tall angular frame, narrow cyan visor slit, "
        "shoulder pauldrons, assault rifle, dark blue-grey plating, "
        + _SPR_STYLE,
        1003,
    ),
    (
        "power_armor_heavy",
        "Titan heavy power armor, massive bulk, large shoulder-mounted autocannon, "
        "orange glowing visor, thick reinforced orange-and-black plating, "
        + _SPR_STYLE,
        1004,
    ),
    (
        "agent_samurai",
        "cyberpunk blade specialist, sleek black infiltration suit, "
        "katana raised in combat pose, red energy glow on blade, "
        "face mask with red eye slit, " + _SPR_STYLE,
        1005,
    ),
    (
        "agent_sniper",
        "cyberpunk sniper, dark tactical vest with pouches, "
        "long scoped anti-materiel rifle, blue night-vision monocle over one eye, "
        "kneeling ready stance, " + _SPR_STYLE,
        1006,
    ),
    (
        "agent_psi",
        "cyberpunk psionics operative, dark tech-circuitry robes, "
        "glowing purple energy orb levitating in raised hand, "
        "violet glowing eyes, psi-amplifier crown headpiece, " + _SPR_STYLE,
        1007,
    ),
    (
        "enemy_grunt",
        "corporate security trooper, blue tactical armor, full blue visor helmet, "
        "assault rifle at ready, standard military stance, " + _SPR_STYLE,
        2001,
    ),
    (
        "enemy_heavy",
        "corporate heavy gunner, massive reinforced plate armor, "
        "triple-barrel minigun raised, enormous muscular build, slow menacing stance, "
        + _SPR_STYLE,
        2002,
    ),
    (
        "enemy_elite",
        "corporate elite officer, sleek black-and-gold trim armor, "
        "elegant combat stance, energy pistol drawn, dark cape edge, "
        + _SPR_STYLE,
        2003,
    ),
    (
        "enemy_commander",
        "mega-corp supreme commander, imposing black spiked plate armor, "
        "horned helmet, glowing red chest power core, massive energy axe weapon, "
        + _SPR_STYLE,
        2004,
    ),
]

# ---------------------------------------------------------------------------
# Post-processing
# ---------------------------------------------------------------------------

_rembg_session = None

def _get_rembg_session():
    global _rembg_session
    if _rembg_session is None:
        _rembg_session = rembg.new_session("u2net")
    return _rembg_session


def remove_background(img: Image.Image) -> Image.Image:
    """Remove background with rembg u2net, return RGBA."""
    return rembg.remove(img, session=_get_rembg_session())


def post_portrait(img: Image.Image, size: int = 248) -> Image.Image:
    """Crop to square, resize, slight contrast/saturation lift to match existing portraits."""
    w, h = img.size
    m = min(w, h)
    img = img.crop(((w - m) // 2, (h - m) // 2, (w + m) // 2, (h + m) // 2))
    img = img.resize((size, size), Image.LANCZOS)
    img = ImageEnhance.Contrast(img).enhance(1.08)
    img = ImageEnhance.Color(img).enhance(1.12)
    return img.convert("RGBA")


def post_sprite(img: Image.Image, size: int = 64) -> Image.Image:
    """Remove background, resize to sprite size with sharpening."""
    img = remove_background(img)          # -> RGBA transparent background
    img = img.resize((size, size), Image.LANCZOS)
    img = img.filter(ImageFilter.UnsharpMask(radius=1, percent=130, threshold=2))
    return img.convert("RGBA")


# ---------------------------------------------------------------------------
# Generation runners
# ---------------------------------------------------------------------------

def run_portraits(pipe: StableDiffusionXLPipeline, steps: int) -> None:
    print("\n-- Generating portraits ------------------------------------------")
    for stem, prompt, seed in PORTRAITS:
        out_path = PORT_DIR / f"{stem}.png"
        if out_path.exists():
            print(f"  {stem} ... exists")
            continue
        print(f"  {stem} ...", end=" ", flush=True)
        img = generate(pipe, prompt, _PORT_NEG, w=512, h=512, steps=steps, seed=seed)
        img = post_portrait(img)
        img.save(out_path)
        print("saved")
    print(f"  Portraits written to {PORT_DIR.relative_to(ROOT)}")


def run_sprites(pipe: StableDiffusionXLPipeline, steps: int) -> None:
    print("\n-- Generating combat sprites --------------------------------------")
    # Warm up rembg on first sprite so subsequent ones are fast
    print("  (loading rembg u2net background-removal model ...)", flush=True)
    _get_rembg_session()
    for stem, prompt, seed in SPRITES:
        out_path  = UNIT_DIR / f"{stem}.png"
        full_path = UNIT_DIR / f"{stem}_512.png"
        print(f"  {stem} ...", end=" ", flush=True)
        full = generate(pipe, prompt, _SPR_NEG, w=512, h=512, steps=steps, seed=seed)
        full.save(full_path)
        small = post_sprite(full, size=64)
        small.save(out_path)
        print("saved")
    print(f"  Sprites written to {UNIT_DIR.relative_to(ROOT)}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Generate AI sprites and portraits")
    parser.add_argument("--only-sprites",   action="store_true")
    parser.add_argument("--only-portraits", action="store_true")
    parser.add_argument("--steps", type=int, default=4,
                        help="Inference steps per image (default 4 for turbo speed)")
    args = parser.parse_args()

    if not torch.cuda.is_available():
        print("ERROR: CUDA GPU required.")
        sys.exit(1)

    pipe = load_pipeline()

    if not args.only_sprites:
        run_portraits(pipe, args.steps)
    if not args.only_portraits:
        run_sprites(pipe, args.steps)

    print("\nAll images generated successfully.")


if __name__ == "__main__":
    main()
