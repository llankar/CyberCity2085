"""Run an experimental 3D map against the original Python combat engine."""
import argparse
import json
import os
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from game.combat import CombatEngine, CombatState
from game.combat.movement import CELL_SIZE
from game.combat.session_protocol import atomic_json
from game.character import Character
from game.cover_system import CoverNode
from game.management.equipment import default_equipment_catalog, equip_starter_loadout
from game.map_geometry import load_map_geometry
from game.map_terrain import build_terrain_profile
from game.stats import EnemyStats, PlayerStats
from game.unit import Unit
from tactical_mailbox import TacticalMailbox
from tactical_preview import TacticalPreview

LAB = Path("E:/CyberCity2085-3d-lab")
SCENARIOS = {
    "warehouse": ("city_industrial_warehouse_floor", (19, 14), (29, 14)),
    "metro": ("city_transit_metro_interchange", (16, 14), (23, 14)),
    "downtown": ("city_exterior_downtown_intersection", (18, 10), (25, 10)),
    "rooftop": ("city_exterior_rooftop_access", (12, 12), (18, 12)),
    "skybridge": ("city_rooftop_skybridge_spine", (14, 12), (20, 12)),
    "factory": ("city_industrial_factory_floor", (15, 11), (22, 11)),
    "lab": ("city_interior_research_lab", (16, 14), (23, 14)),
    "apartments": ("city_district_apartment_block", (21, 12), (28, 12)),
    "ashfield": ("wasteland_outdoor_02_ashfield_ruins", (18, 14), (25, 14)),
    "substation": ("city_industrial_power_substation", (21, 10), (28, 10)),
}
TITLES = {
    "warehouse": "Warehouse", "metro": "Metro Interchange", "downtown": "Downtown Intersection",
    "rooftop": "Rooftop Access", "skybridge": "Skybridge Spine",
    "factory": "Factory Floor", "lab": "Research Lab", "apartments": "Apartment Block",
    "ashfield": "Ashfield Ruins", "substation": "Power Substation",
}
SUPPORT_CELLS = {
    "warehouse": (20, 15), "metro": (17, 13), "downtown": (19, 11),
    "rooftop": (13, 13), "skybridge": (15, 11),
    "factory": (16, 10), "lab": (17, 13), "apartments": (22, 13),
    "ashfield": (19, 13), "substation": (22, 9),
}
CATALOG = Path(__file__).with_name("godot") / "preproduction_catalog.json"


def scenario_preview(scenario: str) -> TacticalPreview:
    map_name, ally_cell, enemy_cell = SCENARIOS[scenario]
    background = ROOT / "assets/maps" / f"{map_name}.png"
    geometry = load_map_geometry(background)
    if not geometry:
        raise RuntimeError(f"Invalid original map geometry: {map_name}")
    width, height = geometry["grid"]
    terrain = build_terrain_profile(str(background), width * CELL_SIZE, height * CELL_SIZE)
    if terrain.source != "manual_wall_traces_v1":
        raise RuntimeError(f"Tactical geometry is unavailable: {map_name}")

    def spawn(cell, stats, team):
        position = tuple(axis * CELL_SIZE for axis in cell)
        if position not in terrain.walkable_cells:
            raise ValueError(f"Blocked spawn on {map_name}: {cell}")
        return Unit(position=position, stats=stats, health=stats.hp, action_points=3, unit_type=team)

    ally = spawn(ally_cell, PlayerStats(), "player")
    ally.character = Character("Longshot", role="sniper", stats=ally.stats)
    equip_starter_loadout(ally.character.loadout, ally.character.role)
    catalog = default_equipment_catalog()
    for slot, item_id in (("sidearm", "mono_knife"), ("utility_item", "trauma_patch")):
        ally.character.loadout.equip(slot, next(item for item in catalog[slot] if item.id == item_id))
    ally.attack_range = ally.character.loadout.primary_weapon.range_cells
    support = spawn(SUPPORT_CELLS[scenario], PlayerStats(psi=4), "player")
    support.character = Character("Oracle", role="psi", stats=support.stats)
    equip_starter_loadout(support.character.loadout, support.character.role)
    support.attack_range = support.character.loadout.primary_weapon.range_cells
    enemy = spawn(enemy_cell, EnemyStats(level=5), "enemy")
    enemy.attack_range = 3
    cover = [
        CoverNode(x // CELL_SIZE, y // CELL_SIZE, "high", passable=False)
        for x, y in sorted(terrain.sight_blocked_cells)
    ]
    return TacticalPreview(CombatEngine(CombatState(None, [ally, support], [enemy]),
                                        terrain_profile=terrain, cover_nodes=cover))


def selected_map(directory: Path) -> str | None:
    try:
        selected = (directory / "map-selection.txt").read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        return None
    if selected not in SCENARIOS:
        raise ValueError(f"Unknown experimental map: {selected}")
    return selected


def open_mailbox(directory: Path, map_key: str, smoke: bool) -> TacticalMailbox:
    preview = scenario_preview(map_key)
    if smoke:
        # A ranged drill exercises playback without waiting for the enemy to approach.
        preview.units["enemy:0"].attack_range = 10
        random.seed(4)
    mailbox = TacticalMailbox(directory, preview)
    atomic_json(directory / "battlefield.json", battlefield_presentation(map_key))
    return mailbox


def battlefield_presentation(map_key: str) -> dict:
    map_name = SCENARIOS[map_key][0]
    catalogue = json.loads(CATALOG.read_text(encoding="utf-8"))
    entry = next(row for row in catalogue if row["map"] == map_name)
    if entry["status"] != "preview":
        raise ValueError(f"No 3D environment for {map_name}")
    return {"title": TITLES[map_key], "preview_scene": entry["scene"]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--map", choices=SCENARIOS, help="Skip the map selection screen")
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    temp_root = LAB / "tmp"
    temp_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="tactical-", dir=temp_root) as temp:
        directory = Path(temp)
        map_key = args.map
        mailbox = open_mailbox(directory, map_key, args.smoke) if map_key else None
        if not map_key:
            atomic_json(directory / "scenarios.json", {
                "maps": [{"id": key, "title": TITLES[key]} for key in SCENARIOS],
            })
        scene = "tactical_battlefield" if map_key else "tactical_menu"
        env = dict(os.environ, CYBERCITY_TACTICAL_SESSION=temp,
                   CYBERCITY_TACTICAL_SMOKE="1" if args.smoke else "0")
        command = ["powershell.exe", "-NoProfile", "-File", str(Path(__file__).with_name("run_godot.ps1")),
                   "-Scene", f"res://{scene}.tscn", "-RenderingMethod", "gl_compatibility"]
        if args.smoke:
            command.extend(["-QuitAfter", "1500"])
        with subprocess.Popen(command, env=env) as godot:
            while godot.poll() is None:
                if mailbox is None:
                    map_key = selected_map(directory)
                    if map_key:
                        mailbox = open_mailbox(directory, map_key, args.smoke)
                else:
                    mailbox.poll()
                time.sleep(.03)
        if args.smoke and mailbox is None:
            raise RuntimeError("The map selector did not start a scenario")
        if args.smoke and (mailbox.sequence != 6 or mailbox.reply["state"]["round"] != 2
                           or not mailbox.reply["state"]["units"][0]["defending"]):
            raise RuntimeError(f"Unexpected Godot exchange: {mailbox.reply}")
        return godot.returncode


if __name__ == "__main__":
    raise SystemExit(main())
