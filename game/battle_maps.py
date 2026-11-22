"""Battle map catalog and mission-based pool selection."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha1
import json
from pathlib import Path
from typing import Any


ASSET_DIR = Path("assets/maps")
MAP_PRESENTATION_PATH = Path("godot/combat_missions_ui/art/environment/map_presentation.json")
BATTLE_TOKEN_SCALE = 1.5 * 1.10
BATTLE_TOKEN_SCALE_NON_ROBOT = BATTLE_TOKEN_SCALE / 2
BASE_HUMAN_HEIGHT_RATIO = 0.015

_IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg"}
_WASTELAND_MISSION_KEYWORDS = (
    "badlands",
    "wasteland",
    "outskirts",
    "frontier",
    "outside",
    "ruins",
    "wreck",
    "shack",
    "starver",
    "mutant",
    "raider",
)


def _slug(text: str) -> str:
    return (
        text.strip().lower()
        .replace("/", "-")
        .replace("\\", "-")
        .replace(" ", "-")
        .replace("_", "-")
    )


def _humanize(filename: str) -> str:
    stem = Path(filename).stem.replace("_", " ").replace("-", " ")
    return " ".join(stem.split()).title() if stem else "Unknown Map"


def _hash_index(seed: str, pool_size: int) -> int:
    if pool_size <= 0:
        return 0
    digest = sha1(seed.strip().lower().encode("utf-8")).hexdigest()
    return int(digest[:8], 16) % pool_size


def _is_city_map(filename: str) -> bool:
    return filename.lower().startswith(("city_", "cybercity_"))


def _scene_for(filename: str, environment: str) -> str:
    lower = filename.lower()
    if environment == "city":
        if "subway" in lower or "underground" in lower:
            return "subway"
        if "interior" in lower or "arcology" in lower or "inner" in lower:
            return "interior"
        if "rooftop" in lower:
            return "rooftop"
        if "alley" in lower:
            return "alley"
        if "plaza" in lower:
            return "plaza"
        if "industrial" in lower:
            return "industrial"
        if "district" in lower:
            return "district"
        if "transit" in lower or "bridge" in lower or "train" in lower:
            return "transit"
        return "exterior"
    if "shack" in lower:
        return "interior"
    if "road" in lower:
        return "exterior"
    if "wreck" in lower or "cemetary" in lower or "ambush" in lower or "wood" in lower:
        return "ruins"
    return "waste"


def _label_for(filename: str, environment: str, scene: str) -> str:
    return f"{environment.title()} {scene.title()}: {_humanize(filename)}"


@dataclass(frozen=True)
class BattleMapEntry:
    key: str
    filename: str
    label: str
    environment: str
    scene: str

    @property
    def path(self) -> str:
        return str(ASSET_DIR / self.filename)


def _build_base_catalog() -> list[BattleMapEntry]:
    entries: list[BattleMapEntry] = []
    if not ASSET_DIR.exists():
        return entries
    for path in sorted(ASSET_DIR.iterdir(), key=lambda item: item.name.lower()):
        if not path.is_file() or path.suffix.lower() not in _IMAGE_SUFFIXES:
            continue
        filename = path.name
        if "walkable" in filename.lower() or filename.lower().startswith("preview_"):
            continue
        environment = "city" if _is_city_map(filename) else "wasteland"
        scene = _scene_for(filename, environment)
        entries.append(
            BattleMapEntry(
                key=_slug(f"{environment}-{scene}-{path.stem}"),
                filename=filename,
                label=_label_for(filename, environment, scene),
                environment=environment,
                scene=scene,
            )
        )
    return entries


def build_battle_map_catalog() -> list[BattleMapEntry]:
    """Build the battle map catalog from the current art files."""
    return _build_base_catalog()


BATTLE_MAP_CATALOG: tuple[BattleMapEntry, ...] = tuple(build_battle_map_catalog())
CITY_BATTLE_MAPS: tuple[BattleMapEntry, ...] = tuple(
    entry for entry in BATTLE_MAP_CATALOG if entry.environment == "city"
)
WASTELAND_BATTLE_MAPS: tuple[BattleMapEntry, ...] = tuple(
    entry for entry in BATTLE_MAP_CATALOG if entry.environment == "wasteland"
)


def infer_battle_environment(mission: Any) -> str:
    """Return the mission's map environment: city or wasteland."""
    if mission is None:
        return "city"

    explicit = str(getattr(mission, "battle_environment", "") or "").strip().lower()
    if explicit in {"city", "wasteland"}:
        return explicit

    text_bits = [
        str(getattr(mission, "id", "")),
        str(getattr(mission, "title", "")),
        str(getattr(mission, "target_faction", "")),
        str(getattr(mission, "district", "")),
        str(getattr(mission, "objective_text", "")),
        str(getattr(mission, "enemy_theme", "")),
    ]
    tags = getattr(mission, "tags", []) or []
    for tag in tags:
        text_bits.append(str(getattr(tag, "name", tag)))
    haystack = " ".join(text_bits).lower()

    if any(keyword in haystack for keyword in _WASTELAND_MISSION_KEYWORDS):
        return "wasteland"
    return "city"


def battle_map_pool_for_environment(environment: str) -> list[BattleMapEntry]:
    env = str(environment or "city").strip().lower()
    if env == "wasteland":
        return list(WASTELAND_BATTLE_MAPS)
    return list(CITY_BATTLE_MAPS)


def battle_map_pool_for_mission(mission: Any) -> list[BattleMapEntry]:
    return battle_map_pool_for_environment(infer_battle_environment(mission))


def _load_map_height_ratios(path: Path = MAP_PRESENTATION_PATH) -> dict[str, float]:
    """Load the shared per-map presentation ratio without changing map geometry."""
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    if int(data.get("schema_version", 0)) != 1:
        return {}
    return {
        str(filename): float(row["human_height_ratio"])
        for filename, row in data.get("maps", {}).items()
        if isinstance(row, dict) and "human_height_ratio" in row
    }


_MAP_HEIGHT_RATIOS = _load_map_height_ratios()


def battle_map_unit_scale(map_entry: BattleMapEntry | str | None) -> float:
    """Return one global visual multiplier for every unit image on a map."""
    if isinstance(map_entry, BattleMapEntry):
        filename = map_entry.filename
    elif map_entry:
        filename = Path(str(map_entry)).name
    else:
        return 1.0
    ratio = _MAP_HEIGHT_RATIOS.get(filename, BASE_HUMAN_HEIGHT_RATIO)
    return max(0.5, min(2.0, ratio / BASE_HUMAN_HEIGHT_RATIO))


def _is_robot_unit(unit: Any) -> bool:
    asset = getattr(unit, "spec_ops_asset", None)
    if asset is not None:
        asset_type = str(getattr(asset, "asset_type", "") or "").strip().lower()
        if asset_type in {"combat_robot", "support_robot", "drone"} or asset_type.endswith("_robot"):
            return True

    unit_type = str(getattr(unit, "unit_type", "") or "").strip().lower()
    if unit_type in {"combat_robot", "support_robot", "drone", "robot"} or unit_type.endswith("_robot"):
        return True

    char = getattr(unit, "character", None)
    if char is not None:
        char_role = str(getattr(char, "role", "") or "").strip().lower()
        if char_role in {"robot", "combat_robot"}:
            return True

    theme = str(getattr(unit, "enemy_theme", "") or "").strip().lower()
    if theme.endswith("_robot") or "robot" in theme:
        return True

    return False


def battle_token_scale_for_unit(
    unit: Any,
    map_entry: BattleMapEntry | str | None = None,
) -> float:
    """Apply the map's single global ratio after the unit's intrinsic size."""
    intrinsic = BATTLE_TOKEN_SCALE if _is_robot_unit(unit) else BATTLE_TOKEN_SCALE_NON_ROBOT
    return intrinsic * battle_map_unit_scale(map_entry)


def select_battle_map_entry(mission: Any) -> BattleMapEntry | None:
    pool = battle_map_pool_for_mission(mission)
    if not pool:
        return None
    seed_bits = [
        str(getattr(mission, "id", "")),
        str(getattr(mission, "title", "")),
        str(getattr(mission, "district", "")),
        str(getattr(mission, "objective_type", "")),
    ]
    index = _hash_index("::".join(seed_bits), len(pool))
    return pool[index]


__all__ = [
    "ASSET_DIR",
    "BATTLE_MAP_CATALOG",
    "BATTLE_TOKEN_SCALE",
    "BATTLE_TOKEN_SCALE_NON_ROBOT",
    "BASE_HUMAN_HEIGHT_RATIO",
    "MAP_PRESENTATION_PATH",
    "BattleMapEntry",
    "CITY_BATTLE_MAPS",
    "WASTELAND_BATTLE_MAPS",
    "battle_map_pool_for_environment",
    "battle_map_pool_for_mission",
    "battle_map_unit_scale",
    "battle_token_scale_for_unit",
    "build_battle_map_catalog",
    "infer_battle_environment",
    "select_battle_map_entry",
]
