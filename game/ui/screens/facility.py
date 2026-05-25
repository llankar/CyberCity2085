"""Corporate tower/base layout helpers for the command UI.

The visual target is an XCOM2-like base cross-section, but reinterpreted as a
city corporate tower: stacked departments, lit rooms, and civic operations
floors rather than a ship interior.
"""

from __future__ import annotations

from dataclasses import dataclass


BASE_BACKDROP_ASSET = "assets/ui/corporate_tower_base.png"
BASE_BACKDROP_SIZE = (1672, 941)
ROOM_IMAGE_DIR = "assets/ui/rooms"


@dataclass(frozen=True)
class FacilityRoom:
    """A deterministic room rectangle used by the shared UI backdrop."""

    key: str
    title: str
    left: int
    bottom: int
    width: int
    height: int
    accent: str = "blue"
    lit: bool = True
    image_path: str = ""


IMAGE_ROOM_ANCHORS = {
    # Rects are normalized from the generated backdrop image, bottom-left origin.
    "top_left": (0.197, 0.688, 0.254, 0.190),
    "top_right": (0.547, 0.665, 0.323, 0.175),
    "mid_left": (0.179, 0.469, 0.299, 0.197),
    "mid_right": (0.538, 0.460, 0.299, 0.200),
    "low_left": (0.179, 0.332, 0.299, 0.175),
    "low_right": (0.538, 0.326, 0.305, 0.197),
    "bottom_left": (0.182, 0.060, 0.272, 0.175),
    "bottom_right": (0.535, 0.054, 0.305, 0.170),
}


ROOM_TITLES = {
    "hub": [
        ("top_left", "command", "Command Core", "amber"),
        ("top_right", "city", "City Grid", "green"),
        ("mid_left", "squad", "Squad Ops", "blue"),
        ("mid_right", "assets", "Asset Bay", "amber"),
        ("low_left", "research", "Research Lab", "blue"),
        ("low_right", "intel", "Intel Archive", "red"),
    ],
    "corp": [
        ("top_left", "executive", "Executive War Room", "amber"),
        ("top_right", "hangar", "Rooftop VTOL Pad", "amber"),
        ("mid_left", "research", "Research Lab", "blue"),
        ("mid_right", "security", "Security Grid", "green"),
        ("low_left", "media", "Media Countermeasures", "blue"),
        ("low_right", "black_ops", "Black Ops Cell", "red"),
        ("bottom_left", "logistics", "Logistics Vault", "green"),
        ("bottom_right", "server", "Data Core", "blue"),
    ],
    "city": [
        ("top_left", "municipal", "Municipal Control", "amber"),
        ("top_right", "skybridge", "Skybridge Watch", "amber"),
        ("mid_left", "district", "District Pressure", "blue"),
        ("mid_right", "transit", "Transit Grid", "green"),
        ("low_left", "factions", "Faction Desk", "red"),
        ("low_right", "public", "Public Signal", "blue"),
        ("bottom_left", "relief", "Relief Logistics", "green"),
        ("bottom_right", "records", "Civic Records", "blue"),
    ],
    "squad": [
        ("top_left", "briefing", "Briefing Floor", "amber"),
        ("top_right", "armory", "Armory Cage", "blue"),
        ("mid_left", "ops", "Operations Table", "blue"),
        ("mid_right", "intel", "Intel Lab", "green"),
        ("low_left", "dossier", "Dossier Archive", "blue"),
        ("low_right", "medbay", "Medbay", "red"),
        ("bottom_left", "barracks", "Agent Barracks", "amber"),
        ("bottom_right", "insertion", "Insertion Lift", "amber"),
    ],
    "battle": [
        ("top_left", "drop", "Drop Control", "amber"),
        ("top_right", "garage", "Armored Garage", "amber"),
        ("mid_left", "maps", "Map Archive", "blue"),
        ("mid_right", "comms", "Tactical Comms", "blue"),
        ("low_left", "drone", "Drone Relay", "green"),
        ("low_right", "casualty", "Casualty Desk", "red"),
        ("bottom_left", "sensors", "Sensor Floor", "blue"),
        ("bottom_right", "uplink", "City Uplink", "green"),
    ],
}


def build_facility_rooms(
    width: int, height: int, mode: str = "corp"
) -> list[FacilityRoom]:
    """Build image-aligned corporate base room hit zones."""
    room_specs = ROOM_TITLES.get(mode, ROOM_TITLES["corp"])
    rooms: list[FacilityRoom] = []

    for index, (anchor_key, key, title, accent) in enumerate(room_specs):
        x, y, room_width, room_height = IMAGE_ROOM_ANCHORS[anchor_key]
        rooms.append(
            FacilityRoom(
                key=key,
                title=title,
                left=int(width * x),
                bottom=int(height * y),
                width=int(width * room_width),
                height=int(height * room_height),
                accent=accent,
                lit=(index % 3) != 1,
                image_path=room_image_path(anchor_key),
            )
        )
    return rooms


def room_image_path(anchor_key: str) -> str:
    """Return the project asset path for a cropped backdrop room."""
    return f"{ROOM_IMAGE_DIR}/{anchor_key}.png"


def facility_room_by_key(rooms: list[FacilityRoom], key: str) -> FacilityRoom:
    """Fetch a backdrop facility room by key."""
    for room in rooms:
        if room.key == key:
            return room
    raise KeyError(key)



def build_interactive_tooltips() -> dict[str, str]:
    """English tooltip copy for key interactive UI elements."""
    return {"room": "Click room to open available actions.", "close": "Close current room panel.", "action_strip": "Use icons to execute room actions."}
