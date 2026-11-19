"""World map mission selection helpers."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from hashlib import sha1
from math import cos, pi, sin
from pathlib import Path
from typing import Any

import arcade

from ...mission_templates import MissionTemplate


WORLD_MAP_PATH = Path("assets/worldmap/Player_World_Map_1778155726161.png")

# Normalized positions on the world map image. These are approximate anchors
# for the visible city labels and the badlands panel.
WORLD_MAP_SITES: dict[str, tuple[float, float]] = {
    "new_york": (0.08, 0.64),
    "los_angeles": (0.07, 0.52),
    "oklahoma_city": (0.10, 0.37),
    "warsaw": (0.52, 0.77),
    "berlin": (0.41, 0.79),
    "geneva": (0.36, 0.61),
    "moscow": (0.61, 0.69),
    "libreville": (0.40, 0.42),
    "cairo": (0.50, 0.37),
    "dubai": (0.61, 0.49),
    "new_delhi": (0.80, 0.36),
    "beijing": (0.83, 0.56),
    "tokyo": (0.93, 0.49),
    "badlands": (0.50, 0.42),
}

_DEFAULT_SITES = (
    "new_york",
    "los_angeles",
    "warsaw",
    "geneva",
    "cairo",
    "dubai",
    "new_delhi",
    "tokyo",
    "beijing",
    "oklahoma_city",
)

_SITE_ALIASES = {
    "nyc": "new_york",
    "new york": "new_york",
    "los angeles": "los_angeles",
    "oklahoma": "oklahoma_city",
    "new delhi": "new_delhi",
    "new-delhi": "new_delhi",
}

_SITE_KEYWORDS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("badlands", ("badlands", "wasteland", "outskirts", "frontier", "outside")),
    ("new_york", ("new york", "nyc", "manhattan", "brooklyn")),
    ("los_angeles", ("los angeles", "la ", " hollywood", "hollywood")),
    ("warsaw", ("warsaw", "three sevens", "37")),
    ("geneva", ("geneva", "corporate council", "council")),
    ("cairo", ("cairo", "africa", "nile")),
    ("dubai", ("dubai", "gulf", "arabia")),
    ("new_delhi", ("new delhi", "delhi", "india")),
    ("tokyo", ("tokyo", "japan")),
    ("beijing", ("beijing", "china")),
    ("moscow", ("moscow", "russia")),
    ("libreville", ("libreville", "gabon")),
    ("berlin", ("berlin", "germany")),
)


@dataclass(frozen=True)
class WorldMapMissionNode:
    mission_index: int
    mission: MissionTemplate
    site_key: str
    pin_x: int
    pin_y: int
    label_left: int
    label_bottom: int
    label_right: int
    label_top: int
    hit_left: int
    hit_bottom: int
    hit_right: int
    hit_top: int


def _slug(text: str) -> str:
    return (
        text.strip().lower()
        .replace("/", "_")
        .replace("\\", "_")
        .replace(" ", "_")
        .replace("-", "_")
    )


def _hash_choice(seed: str, options: tuple[str, ...]) -> str:
    if not options:
        return "new_york"
    digest = sha1(seed.strip().lower().encode("utf-8")).hexdigest()
    index = int(digest[:8], 16) % len(options)
    return options[index]


def _mission_text(mission: Any) -> str:
    bits = [
        str(getattr(mission, "id", "")),
        str(getattr(mission, "title", "")),
        str(getattr(mission, "target_faction", "")),
        str(getattr(mission, "district", "")),
        str(getattr(mission, "objective_text", "")),
        str(getattr(mission, "enemy_theme", "")),
    ]
    hint = getattr(mission, "emotional_impact_hint", None) or {}
    if isinstance(hint, dict):
        bits.extend(
            [
                str(hint.get("text", "")),
                str(hint.get("short_text", "")),
                str(hint.get("emotional_impact_summary", "")),
            ]
        )
        bits.extend(str(tag) for tag in hint.get("normalized_tags", []) or [])
    tags = getattr(mission, "tags", []) or []
    for tag in tags:
        bits.append(str(getattr(tag, "name", tag)))
    return " ".join(bits).lower()


def infer_world_map_site(mission: Any) -> str:
    explicit = _slug(str(getattr(mission, "world_map_site", "") or ""))
    if explicit in WORLD_MAP_SITES:
        return explicit
    if explicit in _SITE_ALIASES:
        return _SITE_ALIASES[explicit]

    haystack = _mission_text(mission)
    for site_key, needles in _SITE_KEYWORDS:
        if any(needle in haystack for needle in needles):
            return site_key

    if any(keyword in haystack for keyword in ("corp", "corporate", "company", "security")):
        return _hash_choice(haystack, ("geneva", "warsaw", "new_york", "dubai"))
    if any(keyword in haystack for keyword in ("city", "urban", "district", "street", "plaza")):
        return _hash_choice(haystack, ("new_york", "los_angeles", "tokyo", "beijing"))

    return _hash_choice(haystack, _DEFAULT_SITES)


def _site_point(site_key: str) -> tuple[float, float]:
    return WORLD_MAP_SITES.get(site_key, WORLD_MAP_SITES["new_york"])


@lru_cache(maxsize=1)
def load_world_map_texture() -> arcade.Texture | None:
    if not WORLD_MAP_PATH.exists():
        return None
    try:
        return arcade.load_texture(str(WORLD_MAP_PATH))
    except Exception:
        return None


@dataclass(frozen=True)
class WorldMapTextureRect:
    x: float
    y: float
    width: float
    height: float


def texture_rect(left: float, bottom: float, right: float, top: float) -> Any:
    rect_cls = getattr(arcade, "Rect", None)
    if rect_cls is not None and hasattr(rect_cls, "from_kwargs"):
        try:
            return rect_cls.from_kwargs(left=left, right=right, bottom=bottom, top=top)
        except Exception:
            pass
    return WorldMapTextureRect(
        x=(left + right) / 2,
        y=(bottom + top) / 2,
        width=max(1.0, right - left),
        height=max(1.0, top - bottom),
    )


def build_world_map_mission_nodes(
    missions: list[MissionTemplate],
    selected_index: int,
    left: int,
    bottom: int,
    right: int,
    top: int,
) -> list[WorldMapMissionNode]:
    if not missions:
        return []

    width = max(1, right - left)
    height = max(1, top - bottom)
    selected_index %= len(missions)
    site_usage: dict[str, int] = {}
    nodes: list[WorldMapMissionNode] = []

    for index, mission in enumerate(missions):
        site_key = infer_world_map_site(mission)
        duplicate_index = site_usage.get(site_key, 0)
        site_usage[site_key] = duplicate_index + 1

        fx, fy = _site_point(site_key)
        if duplicate_index:
            angle = (duplicate_index * 2 * pi) / 6
            fx += cos(angle) * 0.03
            fy += sin(angle) * 0.03
        fx = max(0.05, min(0.95, fx))
        fy = max(0.36, min(0.90, fy))  # 0.36 floor keeps pins above the map image's info panel area

        pin_x = int(left + fx * width)
        pin_y = int(bottom + fy * height)

        label_w = min(240, max(160, int(width * 0.20)))
        label_h = 44
        label_top = min(top - 8, max(bottom + label_h + 8, pin_y + 22))
        label_bottom = label_top - label_h

        if pin_x < left + width * 0.55:
            label_left = min(right - label_w - 8, pin_x + 18)
            label_right = label_left + label_w
        else:
            label_right = max(left + label_w + 8, pin_x - 18)
            label_left = label_right - label_w

        label_left = max(left + 8, min(label_left, right - label_w - 8))
        label_right = label_left + label_w
        if label_right > right - 8:
            label_right = right - 8
            label_left = label_right - label_w

        hit_left = min(pin_x - 18, label_left)
        hit_bottom = min(pin_y - 18, label_bottom)
        hit_right = max(pin_x + 18, label_right)
        hit_top = max(pin_y + 18, label_top)

        nodes.append(
            WorldMapMissionNode(
                mission_index=index,
                mission=mission,
                site_key=site_key,
                pin_x=pin_x,
                pin_y=pin_y,
                label_left=label_left,
                label_bottom=label_bottom,
                label_right=label_right,
                label_top=label_top,
                hit_left=hit_left,
                hit_bottom=hit_bottom,
                hit_right=hit_right,
                hit_top=hit_top,
            )
        )

    return nodes


def mission_label_text(mission: MissionTemplate) -> str:
    return getattr(mission, "title", "UNKNOWN MISSION")[:34].upper()


def mission_site_name(site_key: str) -> str:
    return site_key.replace("_", " ").upper()


__all__ = [
    "WORLD_MAP_PATH",
    "WORLD_MAP_SITES",
    "WorldMapMissionNode",
    "build_world_map_mission_nodes",
    "infer_world_map_site",
    "load_world_map_texture",
    "mission_label_text",
    "mission_site_name",
    "texture_rect",
]
