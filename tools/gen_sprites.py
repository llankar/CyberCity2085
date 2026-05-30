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


def _build_enemy_portrait_specs(
    prefix: str,
    seed_base: int,
    count: int,
    roles: list[str],
    wardrobe: list[str],
    cyberware: list[str],
    color_words: list[str],
    backdrop_words: list[str],
    label: str,
) -> list[tuple[str, str, int]]:
    specs: list[tuple[str, str, int]] = []
    for idx in range(1, count + 1):
        role = roles[(idx - 1) % len(roles)]
        outfit = wardrobe[(idx * 2) % len(wardrobe)]
        implant = cyberware[(idx * 3) % len(cyberware)]
        color = color_words[(idx * 5) % len(color_words)]
        backdrop = backdrop_words[(idx * 7) % len(backdrop_words)]
        prompt = (
            f"{role}, {outfit}, {implant}, {color} accents, {backdrop}, "
            f"{label}, " + _PORT_STYLE
        )
        specs.append((f"{prefix}_{idx:02d}", prompt, seed_base + idx))
    return specs


def _build_enemy_machine_portrait_specs(
    prefix: str,
    seed_base: int,
    count: int,
    chassis_words: list[str],
    optic_words: list[str],
    wear_words: list[str],
    detail_words: list[str],
    glow_words: list[str],
    backdrop_words: list[str],
    label: str,
) -> list[tuple[str, str, int]]:
    specs: list[tuple[str, str, int]] = []
    for idx in range(1, count + 1):
        prompt = (
            f"robot portrait close-up, {chassis_words[(idx - 1) % len(chassis_words)]}, "
            f"{optic_words[(idx * 2) % len(optic_words)]}, {wear_words[(idx * 3) % len(wear_words)]}, "
            f"{detail_words[(idx * 5) % len(detail_words)]}, {glow_words[(idx * 7) % len(glow_words)]}, "
            f"{backdrop_words[(idx * 11) % len(backdrop_words)]}, {label}, " + _PORT_STYLE
        )
        specs.append((f"{prefix}_{idx:02d}", prompt, seed_base + idx))
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

PORTRAITS.extend(
    _build_enemy_portrait_specs(
        "enemy_starver",
        6000,
        10,
        [
            "gaunt infected scavenger",
            "feral tunnel survivor",
            "desperate quarantine drifter",
            "hollow-eyed pack hunter",
            "rag-wrapped wasteland walker",
        ],
        [
            "torn coat and stitched respirator",
            "ragged hoodie with blood-stained sleeves",
            "patched riot jacket with cracked mask",
            "threadbare tactical vest and chain scarf",
            "scrap metal pauldrons over filthy cloth",
        ],
        [
            "surgical staples and pale cheek tubing",
            "makeshift mouth filter and ocular scar",
            "exposed neck implants and vaccine port",
            "shaking hand with bone-white knuckles",
            "wired collar and crude tracking chip",
        ],
        ["ash", "bone", "rust", "sickly green", "cold blue"],
        [
            "abandoned subway tunnel",
            "quarantine fence at night",
            "collapsed overpass in rain",
            "dim sewer access corridor",
            "burned-out supply depot",
        ],
        "infected, dangerous, feral",
    )
)

PORTRAITS.extend(
    _build_enemy_portrait_specs(
        "enemy_mutant",
        6100,
        20,
        [
            "mutated human survivor",
            "irradiated street brute",
            "overgrown biohazard stalker",
            "scarred zone mutant",
            "unstable flesh-warper victim",
        ],
        [
            "hazmat tatters and swollen armor plates",
            "fused denim and scrap plating",
            "radiation suit remnants and leather straps",
            "bulky scavenged harness and torn sleeves",
            "stapled tarp cloak and bone charms",
        ],
        [
            "luminous vein lines and cyber patches",
            "extra optic implant and jaw brace",
            "subdermal toxin ports and spinal fins",
            "hastily sewn med implants and scars",
            "glowing tumor nodes and tracking jack",
        ],
        ["acid green", "warning amber", "violet", "pale cyan", "muted red"],
        [
            "irradiated service tunnel",
            "toxic floodplain at dusk",
            "mangled laboratory corridor",
            "ruined apartment stairwell",
            "contaminated rail platform",
        ],
        "unstable, mutated, relentless",
    )
)

PORTRAITS.extend(
    _build_enemy_portrait_specs(
        "enemy_raider",
        6200,
        20,
        [
            "mad-max raider warlord",
            "scrapland marauder",
            "dust-road ambusher",
            "rusted helmet predator",
            "vehicle gang enforcer",
        ],
        [
            "spiked leather coat and ammo webbing",
            "patched armor with scavenged plates",
            "chain harness and dust cloak",
            "battered biker vest and armored collar",
            "raided riot armor and frayed scarf",
        ],
        [
            "visor goggles with cracked lenses",
            "jaw tattoo and metal tooth grill",
            "ear jack, nose ring, and cheek scars",
            "stolen ocular implant with burn marks",
            "helmet radio and crude sensor crown",
        ],
        ["rust", "sand", "black", "copper", "oil-stain orange"],
        [
            "dust storm roadside camp",
            "abandoned highway checkpoint",
            "scrap yard bonfire glow",
            "cinder-lit wasteland ridge",
            "broken convoy yard",
        ],
        "aggressive, scavenging, ruthless",
    )
)

PORTRAITS.extend(
    _build_enemy_portrait_specs(
        "enemy_corp_samurai",
        6300,
        20,
        [
            "cyber samurai operative",
            "corporate ninja assassin",
            "steel-masked blade specialist",
            "silent katana infiltrator",
            "high-rank stealth duelist",
        ],
        [
            "black infiltration armor with plated sash",
            "ceremonial combat coat and mesh sleeves",
            "matte tactical bodysuit with blade clips",
            "hooded armor with segmented shoulder guards",
            "night-black uniform with luminous seam lines",
        ],
        [
            "visor mask and throat data port",
            "forearm blade sheath and cheek implant",
            "spine-mounted holster and retinal HUD",
            "elegant mask with red eye slit",
            "sleeve jack and silent comm node",
        ],
        ["crimson", "indigo", "silver", "teal", "white"],
        [
            "rain-soaked neon alley",
            "high-rise rooftop shadow",
            "glass atrium with blade reflections",
            "moonlit courtyard of steel",
            "dark training hall with paper-light glow",
        ],
        "disciplined, lethal, silent",
    )
)

PORTRAITS.extend(
    _build_enemy_machine_portrait_specs(
        "enemy_corp_samurai_robot",
        6400,
        20,
        [
            "sleek samurai automaton chassis",
            "blade-bearing sentinel frame",
            "ceremonial combat android shell",
            "stealth hunter robot chassis",
            "armored duelist machine body",
        ],
        [
            "single crimson optic",
            "paired white optics",
            "narrow cyan visor strip",
            "tri-lens amber sensor",
            "masked sensor lattice",
        ],
        [
            "polished armor with minor scratches",
            "battle-scuffed plating and bolt seams",
            "matte black body panels",
            "ornate lacquered shoulder caps",
            "wire ports and vent scars",
        ],
        [
            "katana sheath mount",
            "ceremonial crest fin",
            "wrist blade housing",
            "throat vent assembly",
            "retractable sensor antenna",
        ],
        [
            "red command glow",
            "white scan glow",
            "cyan alert glow",
            "amber threat glow",
            "violet tactical glow",
        ],
        [
            "neon rain corridor",
            "steel cathedral shadows",
            "corporate dojo interior",
            "low-lit rooftop gantry",
            "security vault haze",
        ],
        "samurai-themed combat robot",
    )
)

PORTRAITS.extend(
    _build_enemy_machine_portrait_specs(
        "enemy_corp_samurai_power_armor",
        6500,
        20,
        [
            "samurai power armor helm",
            "blade guard exosuit headplate",
            "honor guard armor shell",
            "siege duelist armor chassis",
            "corporate ronin war frame",
        ],
        [
            "single gold visor",
            "red tactical optics",
            "narrow white visor slit",
            "cyan command optics",
            "black faceplate with crest",
        ],
        [
            "scarred shoulder plates and dented chest rig",
            "ornate armor with chipped lacquer",
            "heavy plated collar and bolt seams",
            "reinforced gauntlets with blade mounts",
            "battle marks around the visor",
        ],
        [
            "katana gauntlet mount",
            "crest ridge and antenna",
            "shoulder shield plates",
            "servos in the throat ring",
            "retractable mono-blade housing",
        ],
        [
            "red power core glow",
            "white HUD glow",
            "amber reactor glow",
            "blue status glow",
            "gold honor glow",
        ],
        [
            "storm-lit tower corridor",
            "smoky command bunker",
            "rain-slick fortress balcony",
            "neon-lit armor bay",
            "ceremonial war chamber",
        ],
        "samurai-themed power armor",
    )
)

PORTRAITS.extend(
    _build_enemy_portrait_specs(
        "enemy_corp_37",
        6600,
        20,
        [
            "retro-authoritarian corporate officer",
            "wartime-industrial security commander",
            "iron-gray field marshal",
            "cold doctrine strategist",
            "retro-fascist logistics chief",
        ],
        [
            "iron-gray greatcoat with rigid collar",
            "dark parade jacket and medal straps",
            "angular armored tunic and black gloves",
            "scarlet-lined trench coat",
            "uniform coat with clipped insignia",
        ],
        [
            "geometric insignia collar tab",
            "hard visor and jawline implant",
            "signal jack behind the ear",
            "stern cheek scar and throat port",
            "comm bead and optics insert",
        ],
        ["iron", "red", "black", "silver", "smoke-gray"],
        [
            "bombed-out command room",
            "steel hallway under floodlights",
            "citadel office in cold rain",
            "archive bunker with red lamps",
            "war-room balcony above fog",
        ],
        "authoritarian, disciplined, relentless",
    )
)

PORTRAITS.extend(
    _build_enemy_machine_portrait_specs(
        "enemy_corp_37_robot",
        6700,
        20,
        [
            "wartime security automaton",
            "industrial command robot",
            "retro-guardian machine chassis",
            "iron doctrine android shell",
            "storm-trooper robot frame",
        ],
        [
            "single red command eye",
            "paired white optics",
            "angular black visor strip",
            "tri-lens amber sensor",
            "cold blue threat array",
        ],
        [
            "battle-dented armor plates",
            "matte iron chassis scars",
            "riveted plating and vent seams",
            "stamped insignia panels",
            "heavy shoulder housings",
        ],
        [
            "radio mast crown",
            "ceremonial chest plate",
            "armored neck brace",
            "industrial sensor spine",
            "reinforced knee pistons",
        ],
        [
            "red threat glow",
            "amber alert glow",
            "white scan glow",
            "blue tactical glow",
            "gold status glow",
        ],
        [
            "factory bunker shadows",
            "war room haze",
            "steel corridor glare",
            "rain on blast doors",
            "archive vault gloom",
        ],
        "authoritarian security robot",
    )
)

PORTRAITS.extend(
    _build_enemy_machine_portrait_specs(
        "enemy_corp_37_power_armor",
        6800,
        20,
        [
            "retro-command power armor helm",
            "iron doctrine assault shell",
            "wartime heavy exosuit head",
            "field marshal armor mask",
            "armored security war frame",
        ],
        [
            "black visor slit",
            "red command optics",
            "smoky gold visor",
            "white tactical lens",
            "cold blue sensor eye",
        ],
        [
            "heavy plated shoulders and chest",
            "rivet-fastened armor panels",
            "battle-worn command plating",
            "stern collar and reinforced gauntlets",
            "angular armor with chipped insignia",
        ],
        [
            "thick chest reactor housing",
            "side-mounted servo stack",
            "armored neck ring",
            "reinforced thigh pistons",
            "shoulder flare housing",
        ],
        [
            "red reactor glow",
            "amber warning glow",
            "white scan glow",
            "blue control glow",
            "gold command glow",
        ],
        [
            "smoke-filled command bunker",
            "war-torn archive hall",
            "storm-lit fortress bridge",
            "steel blast-door chamber",
            "black site armory",
        ],
        "authoritarian power armor",
    )
)

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


def _build_enemy_human_sprite_specs(
    prefix: str,
    seed_base: int,
    theme_phrase: str,
    armor_words: list[str],
    weapon_words: list[str],
    stance_words: list[str],
    color_words: list[str],
    backdrop_words: list[str],
) -> list[tuple[str, str, int]]:
    specs: list[tuple[str, str, int]] = []
    subtypes = ("grunt", "heavy", "elite", "commander")
    for idx, subtype in enumerate(subtypes, start=1):
        prompt = (
            f"{theme_phrase}, {armor_words[(idx - 1) % len(armor_words)]}, "
            f"{weapon_words[(idx * 2) % len(weapon_words)]}, "
            f"{stance_words[(idx * 3) % len(stance_words)]}, "
            f"{color_words[(idx * 5) % len(color_words)]} accents, "
            f"{backdrop_words[(idx * 7) % len(backdrop_words)]}, " + _SPR_STYLE
        )
        specs.append((f"{prefix}_{subtype}", prompt, seed_base + idx))
    return specs


def _build_enemy_machine_sprite_specs(
    prefix: str,
    seed_base: int,
    theme_phrase: str,
    chassis_words: list[str],
    weapon_words: list[str],
    armor_words: list[str],
    stance_words: list[str],
    glow_words: list[str],
    backdrop_words: list[str],
) -> list[tuple[str, str, int]]:
    specs: list[tuple[str, str, int]] = []
    subtypes = ("grunt", "heavy", "elite", "commander")
    for idx, subtype in enumerate(subtypes, start=1):
        prompt = (
            f"{theme_phrase}, {chassis_words[(idx - 1) % len(chassis_words)]}, "
            f"{weapon_words[(idx * 2) % len(weapon_words)]}, "
            f"{armor_words[(idx * 3) % len(armor_words)]}, "
            f"{stance_words[(idx * 5) % len(stance_words)]}, "
            f"{glow_words[(idx * 7) % len(glow_words)]} accents, "
            f"{backdrop_words[(idx * 11) % len(backdrop_words)]}, " + _SPR_STYLE
        )
        specs.append((f"{prefix}_{subtype}", prompt, seed_base + idx))
    return specs


SPRITES.extend(
    _build_enemy_human_sprite_specs(
        "enemy_starver",
        3000,
        "gaunt infected scavenger, feral out-of-city enemy",
        [
            "torn coat, filthy layers, and ragged belt",
            "stained hoodie and broken armor scraps",
            "patched survival gear and cracked mask",
            "quarantine vest and chain scarf",
            "scrap shoulder pads and torn sleeves",
        ],
        [
            "rusted pipe blade",
            "short shotgun",
            "improvised machete",
            "rebar spear",
            "stolen carbine",
        ],
        [
            "crouched and predatory",
            "leaning forward with jittery hunger",
            "low sprint stance",
            "one knee bent, ready to lunge",
            "shoulders hunched and tense",
        ],
        ["ash", "bone", "rust", "green", "blue"],
        [
            "abandoned subway tunnel",
            "quarantine fence at night",
            "collapsed overpass in rain",
            "dim sewer access corridor",
            "burned-out supply depot",
        ],
    )
)

SPRITES.extend(
    _build_enemy_human_sprite_specs(
        "enemy_mutant",
        3100,
        "mutated human survivor, irradiated hazard enemy",
        [
            "hazmat tatters and swollen armor plates",
            "fused denim and scrap plating",
            "radiation suit remnants and leather straps",
            "bulky scavenged harness and torn sleeves",
            "stapled tarp cloak and bone charms",
        ],
        [
            "heavy hammer arm",
            "crudely sharpened cleaver",
            "spiked pipe staff",
            "stolen assault rifle",
            "bone hook blade",
        ],
        [
            "stooped and unstable",
            "wide-stance brute posture",
            "twisted torso combat lean",
            "lunging with one shoulder high",
            "lurching but aggressive",
        ],
        ["acid green", "warning amber", "violet", "cyan", "muted red"],
        [
            "irradiated service tunnel",
            "toxic floodplain at dusk",
            "mangled laboratory corridor",
            "ruined apartment stairwell",
            "contaminated rail platform",
        ],
    )
)

SPRITES.extend(
    _build_enemy_human_sprite_specs(
        "enemy_raider",
        3200,
        "mad-max raider, scavenger warband enemy",
        [
            "spiked leather coat and ammo webbing",
            "patched armor with scavenged plates",
            "chain harness and dust cloak",
            "biker vest and armored collar",
            "raided riot armor and frayed scarf",
        ],
        [
            "scrap rifle",
            "shotgun with pipe stock",
            "combat machete",
            "revolver and knife combo",
            "brass knuckle baton",
        ],
        [
            "aggressive forward drive",
            "one-foot-forward brawler stance",
            "weapon raised over the shoulder",
            "wide stance, ready to charge",
            "knees bent for a sprint",
        ],
        ["rust", "sand", "black", "copper", "orange"],
        [
            "dust storm roadside camp",
            "abandoned highway checkpoint",
            "scrap yard bonfire glow",
            "cinder-lit wasteland ridge",
            "broken convoy yard",
        ],
    )
)

SPRITES.extend(
    _build_enemy_human_sprite_specs(
        "enemy_corp_samurai",
        3300,
        "cyber samurai ninja, corporate blade assassin",
        [
            "black infiltration armor with plated sash",
            "ceremonial combat coat and mesh sleeves",
            "matte tactical bodysuit with blade clips",
            "hooded armor with segmented shoulder guards",
            "night-black uniform with luminous seam lines",
        ],
        [
            "katana in a low guard",
            "dual blades drawn",
            "monoblade extended",
            "short rifle held one-handed",
            "throwing knife fan",
        ],
        [
            "silent ready stance",
            "low duelist pose",
            "blade angled across the body",
            "mid-step infiltration posture",
            "knife hand extended, katana back",
        ],
        ["crimson", "indigo", "silver", "teal", "white"],
        [
            "rain-soaked neon alley",
            "high-rise rooftop shadow",
            "glass atrium with blade reflections",
            "moonlit courtyard of steel",
            "dark training hall with paper-light glow",
        ],
    )
)

SPRITES.extend(
    _build_enemy_machine_sprite_specs(
        "enemy_corp_samurai_robot",
        3400,
        "samurai-themed combat robot, corporate blade machine",
        [
            "sleek samurai automaton chassis",
            "blade-bearing sentinel frame",
            "ceremonial combat android shell",
            "stealth hunter robot chassis",
            "armored duelist machine body",
        ],
        [
            "katana armature",
            "monoblade emitter",
            "wrist blade module",
            "shock baton and shield edge",
            "compact rifle mount",
        ],
        [
            "polished armor with minor scratches",
            "battle-scuffed plating and bolt seams",
            "matte black body panels",
            "ornate lacquered shoulder caps",
            "wire ports and vent scars",
        ],
        [
            "forward lean slash pose",
            "balanced duelist stance",
            "guarded step with blade ready",
            "low stealth crouch",
            "mid-strike rotation",
        ],
        [
            "red command glow",
            "white scan glow",
            "cyan alert glow",
            "amber threat glow",
            "violet tactical glow",
        ],
        [
            "neon rain corridor",
            "steel cathedral shadows",
            "corporate dojo interior",
            "low-lit rooftop gantry",
            "security vault haze",
        ],
    )
)

SPRITES.extend(
    _build_enemy_machine_sprite_specs(
        "enemy_corp_samurai_power_armor",
        3500,
        "samurai-themed power armor, corporate heavy assault suit",
        [
            "samurai power armor shell",
            "blade guard exosuit frame",
            "honor guard armor chassis",
            "siege duelist armor",
            "corporate ronin war frame",
        ],
        [
            "assault rifle braced in both hands",
            "heavy beam cannon",
            "katana mounted to the forearm",
            "compact grenade launcher",
            "tactical shield and sidearm",
        ],
        [
            "scarred shoulder plates and dented chest rig",
            "ornate armor with chipped lacquer",
            "heavy plated collar and bolt seams",
            "reinforced gauntlets with blade mounts",
            "battle marks around the visor",
        ],
        [
            "braced firing stance",
            "heavy step forward",
            "shielded guard pose",
            "power-armor shoulder turn",
            "siege-ready stance",
        ],
        [
            "red power core glow",
            "white HUD glow",
            "amber reactor glow",
            "blue status glow",
            "gold honor glow",
        ],
        [
            "storm-lit tower corridor",
            "smoky command bunker",
            "rain-slick fortress balcony",
            "neon-lit armor bay",
            "ceremonial war chamber",
        ],
    )
)

SPRITES.extend(
    _build_enemy_human_sprite_specs(
        "enemy_corp_37",
        3600,
        "retro-authoritarian corporate officer, brutal industrial infantry",
        [
            "iron-gray greatcoat with rigid collar",
            "dark parade jacket and medal straps",
            "angular armored tunic and black gloves",
            "scarlet-lined trench coat",
            "uniform coat with clipped insignia",
        ],
        [
            "service pistol and baton",
            "submachine gun at the ready",
            "long rifle with bayonet",
            "command pistol and signal flare",
            "heavy carbine and knife",
        ],
        [
            "upright march stance",
            "cold command pose",
            "weapon held close to the chest",
            "stiff, disciplined step",
            "shoulders squared and rigid",
        ],
        ["iron", "red", "black", "silver", "gray"],
        [
            "bombed-out command room",
            "steel hallway under floodlights",
            "citadel office in cold rain",
            "archive bunker with red lamps",
            "war-room balcony above fog",
        ],
    )
)

SPRITES.extend(
    _build_enemy_machine_sprite_specs(
        "enemy_corp_37_robot",
        3700,
        "authoritarian security robot, retro-industrial war machine",
        [
            "wartime security automaton",
            "industrial command robot",
            "retro-guardian machine chassis",
            "iron doctrine android shell",
            "storm-trooper robot frame",
        ],
        [
            "heavy rifle mount",
            "compact suppressor cannon",
            "arm-mounted shock baton",
            "short-range grenade projector",
            "dual-mount machine pistol",
        ],
        [
            "battle-dented armor plates",
            "matte iron chassis scars",
            "riveted plating and vent seams",
            "stamped insignia panels",
            "heavy shoulder housings",
        ],
        [
            "measured marching pose",
            "weapon raised in salute",
            "locked defensive stance",
            "forward patrol gait",
            "hard target acquisition stance",
        ],
        [
            "red threat glow",
            "amber alert glow",
            "white scan glow",
            "blue tactical glow",
            "gold status glow",
        ],
        [
            "factory bunker shadows",
            "war room haze",
            "steel corridor glare",
            "rain on blast doors",
            "archive vault gloom",
        ],
    )
)

SPRITES.extend(
    _build_enemy_machine_sprite_specs(
        "enemy_corp_37_power_armor",
        3800,
        "authoritarian power armor, heavy industrial assault suit",
        [
            "retro-command power armor shell",
            "iron doctrine assault chassis",
            "wartime heavy exosuit frame",
            "field marshal armor mask",
            "armored security war frame",
        ],
        [
            "heavy cannon braced at hip",
            "battle rifle with underbarrel launcher",
            "shield and sidearm",
            "long rifle and bayonet",
            "burst-fire carbine",
        ],
        [
            "heavy plated shoulders and chest",
            "rivet-fastened armor panels",
            "battle-worn command plating",
            "stern collar and reinforced gauntlets",
            "angular armor with chipped insignia",
        ],
        [
            "advancing heavy assault stance",
            "shielded march forward",
            "cannon braced to fire",
            "wide planted power pose",
            "defensive stomp posture",
        ],
        [
            "red reactor glow",
            "amber warning glow",
            "white scan glow",
            "blue control glow",
            "gold command glow",
        ],
        [
            "smoke-filled command bunker",
            "war-torn archive hall",
            "storm-lit fortress bridge",
            "steel blast-door chamber",
            "black site armory",
        ],
    )
)

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
