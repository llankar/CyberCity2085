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
from game.map_terrain import TerrainProfile
from game.stats import EnemyStats, PlayerStats
from game.unit import Unit
from tactical_mailbox import TacticalMailbox
from tactical_preview import TacticalPreview

LAB = Path("E:/CyberCity2085-3d-lab")
SCENARIOS = {
    "warehouse": ("city_industrial_warehouse_floor", (19, 13), (29, 13)),
    "metro": ("city_transit_metro_interchange", (16, 13), (23, 13)),
    "downtown": ("city_exterior_downtown_intersection", (18, 9), (25, 9)),
    "rooftop": ("city_exterior_rooftop_access", (12, 11), (18, 11)),
    "skybridge": ("city_rooftop_skybridge_spine", (14, 11), (20, 11)),
    "factory": ("city_industrial_factory_floor", (15, 10), (22, 10)),
    "lab": ("city_interior_research_lab", (16, 13), (23, 13)),
    "apartments": ("city_district_apartment_block", (21, 11), (28, 11)),
    "ashfield": ("wasteland_outdoor_02_ashfield_ruins", (18, 13), (25, 13)),
    "substation": ("city_industrial_power_substation", (21, 9), (28, 9)),
}
TITLES = {
    "warehouse": "Warehouse", "metro": "Metro Interchange", "downtown": "Downtown Intersection",
    "rooftop": "Rooftop Access", "skybridge": "Skybridge Spine",
    "factory": "Factory Floor", "lab": "Research Lab", "apartments": "Apartment Block",
    "ashfield": "Ashfield Ruins", "substation": "Power Substation",
}
SUPPORT_CELLS = {
    "warehouse": (20, 14), "metro": (17, 12), "downtown": (19, 10),
    "rooftop": (13, 12), "skybridge": (15, 10),
    "factory": (16, 9), "lab": (17, 12), "apartments": (22, 12),
    "ashfield": (19, 12), "substation": (22, 8),
}
CATALOG = Path(__file__).with_name("godot") / "preproduction_catalog.json"


def catalogue_scenarios() -> dict[str, dict]:
    return {
        entry["map"]: entry
        for entry in json.loads(CATALOG.read_text(encoding="utf-8"))
        if entry["status"] == "preview"
    }


def scenario_maps() -> dict[str, str]:
    curated = {map_name for map_name, _, _ in SCENARIOS.values()}
    return TITLES | {
        name: name.replace("_", " ").title()
        for name in catalogue_scenarios()
        if name not in curated
    }


def automatic_spawns(terrain, width: int, height: int):
    cells = {(x // CELL_SIZE, y // CELL_SIZE) for x, y in terrain.walkable_cells}
    ordered = sorted(cells, key=lambda cell: (
        abs(2 * cell[0] - width) + abs(2 * cell[1] - height), cell,
    ))
    for distance in (7, 5, 3):
        for x, y in ordered:
            for dx, dy in ((1, 0), (0, 1), (-1, 0), (0, -1)):
                if not all((x + i * dx, y + i * dy) in cells for i in range(1, distance + 1)):
                    continue
                for side in (-1, 1):
                    support = (x + dx - side * dy, y + dy + side * dx)
                    if support in cells:
                        return (x, y), support, (x + distance * dx, y + distance * dy)
    raise ValueError(f"No connected deployment corridor on {terrain.image_path}")


def scenario_preview(scenario: str) -> TacticalPreview:
    map_name = SCENARIOS[scenario][0] if scenario in SCENARIOS else scenario
    background = ROOT / "assets/maps" / f"{map_name}.png"
    geometry = load_map_geometry(background)
    if not geometry or not geometry.get("reviewed") or geometry.get("method") != "manual_wall_traces_v1":
        raise RuntimeError(f"Tactical geometry is unavailable: {map_name}")
    width, height = geometry["grid"]

    def world_cell(column, row):
        # Godot draws cell centres from the source texture's top-left origin.
        return column * CELL_SIZE, (height - 1 - row) * CELL_SIZE

    walls = geometry["walls"]
    blocked = {world_cell(*cell) for wall in walls for cell in wall["cells"]}
    opaque = {world_cell(*cell) for wall in walls if wall.get("blocks_sight", True)
              for cell in wall["cells"]}
    walkable = {world_cell(column, row) for column in range(width) for row in range(height)} - blocked
    terrain = TerrainProfile(str(background), width * CELL_SIZE, height * CELL_SIZE, CELL_SIZE,
                             frozenset(walkable), 255, source=geometry["method"],
                             sight_blocked_cells=frozenset(opaque))

    if scenario in SCENARIOS:
        _, ally_cell, enemy_cell = SCENARIOS[scenario]
        support_cell = SUPPORT_CELLS[scenario]
    else:
        ally_cell, support_cell, enemy_cell = automatic_spawns(terrain, width, height)

    def spawn(cell, stats, team):
        position = tuple(axis * CELL_SIZE for axis in cell)
        if position not in terrain.walkable_cells:
            raise ValueError(f"Blocked spawn on {map_name}: {cell}")
        return Unit(position=position, stats=stats, health=stats.hp, action_points=3, unit_type=team)

    ally = spawn(ally_cell, PlayerStats(agi=7), "player")
    ally.character = Character("Longshot", role="sniper", stats=ally.stats)
    equip_starter_loadout(ally.character.loadout, ally.character.role)
    catalog = default_equipment_catalog()
    for slot, item_id in (("sidearm", "mono_knife"), ("utility_item", "trauma_patch")):
        ally.character.loadout.equip(slot, next(item for item in catalog[slot] if item.id == item_id))
    ally.attack_range = ally.character.loadout.primary_weapon.range_cells
    support = spawn(support_cell, PlayerStats(agi=3, psi=4), "player")
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
    if selected not in scenario_maps():
        raise ValueError(f"Unknown experimental map: {selected}")
    return selected


def open_mailbox(directory: Path, map_key: str, smoke: bool, *, smoke_outcome: str = "") -> TacticalMailbox:
    preview = scenario_preview(map_key)
    if smoke:
        # A ranged drill exercises playback without waiting for the enemy to approach.
        preview.units["enemy:0"].attack_range = 10
        random.seed(4)
    if smoke_outcome == "victory":
        ally, enemy = preview.units["ally:0"], preview.units["enemy:0"]
        ally.stats.agi = 100
        enemy.stats.hp = enemy.health = 1
    elif smoke_outcome == "defeat":
        preview.units["enemy:0"].stats.agi = 100
        for key in ("ally:0", "ally:1"):
            ally = preview.units[key]
            ally.stats.hp = ally.health = 1
    mailbox = TacticalMailbox(directory, preview, trace_timing=smoke)
    atomic_json(directory / "battlefield.json", battlefield_presentation(map_key))
    return mailbox


def battlefield_presentation(map_key: str) -> dict:
    map_name = SCENARIOS[map_key][0] if map_key in SCENARIOS else map_key
    entry = catalogue_scenarios()[map_name]
    return {"title": scenario_maps()[map_key], "preview_scene": entry["scene"]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--map", choices=scenario_maps(), help="Skip the map selection screen")
    checks = parser.add_mutually_exclusive_group()
    checks.add_argument("--smoke", action="store_true")
    checks.add_argument("--smoke-victory", action="store_const", dest="smoke_outcome", const="victory", default="")
    checks.add_argument("--smoke-defeat", action="store_const", dest="smoke_outcome", const="defeat")
    checks.add_argument("--benchmark", action="store_true", help="Measure uncapped overview orbit, tactical idle and tactical orbit")
    checks.add_argument("--benchmark-combat", action="store_true",
                        help="Measure uncapped active combat using the scripted skirmish, without screenshots")
    args = parser.parse_args()
    if args.benchmark_combat and not args.map:
        parser.error("--benchmark-combat requires --map")
    smoke = args.smoke or args.benchmark_combat or bool(args.smoke_outcome)
    temp_root = LAB / "tmp"
    temp_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="tactical-", dir=temp_root) as temp:
        directory = Path(temp)
        map_key = args.map or ("metro" if args.smoke_outcome == "defeat" else None)
        mailbox = open_mailbox(directory, map_key, smoke, smoke_outcome=args.smoke_outcome) if map_key else None
        if not map_key:
            atomic_json(directory / "scenarios.json", {
                "maps": [{"id": key, "title": title} for key, title in scenario_maps().items()],
            })
        scene = "tactical_battlefield" if map_key else "tactical_menu"
        env = dict(os.environ, CYBERCITY_TACTICAL_SESSION=temp,
                   CYBERCITY_TACTICAL_SMOKE="1" if smoke else "0",
                   CYBERCITY_TACTICAL_SMOKE_OUTCOME=args.smoke_outcome,
                   CYBERCITY_TACTICAL_BENCHMARK="1" if args.benchmark else "0",
                   CYBERCITY_TACTICAL_BENCHMARK_COMBAT="1" if args.benchmark_combat else "0")
        command = ["powershell.exe", "-NoProfile", "-File", str(Path(__file__).with_name("run_godot.ps1")),
                   "-Scene", f"res://{scene}.tscn", "-RenderingMethod", "gl_compatibility"]
        if smoke:
            command.extend(["-QuitAfter", "15000" if args.benchmark_combat else "1500"])
        with subprocess.Popen(command, env=env) as godot:
            while godot.poll() is None:
                if mailbox is None:
                    map_key = selected_map(directory)
                    if map_key:
                        mailbox = open_mailbox(directory, map_key, smoke, smoke_outcome=args.smoke_outcome)
                else:
                    mailbox.poll()
                time.sleep(.01 if mailbox is not None else .03)
        if godot.returncode:
            return godot.returncode
        if smoke and mailbox is None:
            raise RuntimeError("The map selector did not start a scenario")
        if args.smoke_outcome and mailbox.reply["state"]["outcome"] != args.smoke_outcome:
            raise RuntimeError(f"Unexpected Godot outcome exchange: {mailbox.reply}")
        if (args.smoke or args.benchmark_combat) and (mailbox.sequence != 6 or mailbox.reply["state"]["round"] != 2
                           or not mailbox.reply["state"]["units"][0]["defending"]):
            raise RuntimeError(f"Unexpected Godot exchange: {mailbox.reply}")
        return godot.returncode


if __name__ == "__main__":
    raise SystemExit(main())
