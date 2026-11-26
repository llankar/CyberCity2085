"""Run the experimental warehouse scene against the Python combat engine."""
import argparse
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from game.combat import CombatEngine, CombatState
from game.combat.movement import CELL_SIZE
from game.character import Character
from game.cover_system import CoverNode
from game.management.equipment import equip_starter_loadout
from game.map_geometry import load_map_geometry
from game.map_terrain import build_terrain_profile
from game.stats import EnemyStats, PlayerStats
from game.unit import Unit
from tactical_mailbox import TacticalMailbox
from tactical_preview import TacticalPreview

LAB = Path("E:/CyberCity2085-3d-lab")


def warehouse_preview() -> TacticalPreview:
    background = ROOT / "assets/maps/city_industrial_warehouse_floor.png"
    width, height = load_map_geometry(background)["grid"]
    terrain = build_terrain_profile(str(background), width * CELL_SIZE, height * CELL_SIZE)
    if terrain.source != "manual_wall_traces_v1":
        raise RuntimeError("Warehouse tactical geometry is unavailable")

    def spawn(cell, stats, team):
        position = tuple(axis * CELL_SIZE for axis in cell)
        if position not in terrain.walkable_cells:
            raise ValueError(f"Blocked warehouse spawn: {cell}")
        return Unit(position=position, stats=stats, health=10, action_points=3, unit_type=team)

    ally = spawn((19, 14), PlayerStats(), "player")
    ally.character = Character("Longshot", role="sniper", stats=ally.stats)
    equip_starter_loadout(ally.character.loadout, ally.character.role)
    ally.attack_range = ally.character.loadout.primary_weapon.range_cells
    enemy = spawn((29, 14), EnemyStats(level=1), "enemy")
    enemy.health = enemy.stats.hp = 50
    cover = [
        CoverNode(x // CELL_SIZE, y // CELL_SIZE, "high", passable=False)
        for x, y in sorted(terrain.sight_blocked_cells)
    ]
    return TacticalPreview(CombatEngine(CombatState(None, [ally], [enemy]),
                                        terrain_profile=terrain, cover_nodes=cover))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    temp_root = LAB / "tmp"
    temp_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="tactical-", dir=temp_root) as temp:
        mailbox = TacticalMailbox(Path(temp), warehouse_preview())
        env = dict(os.environ, CYBERCITY_TACTICAL_SESSION=temp,
                   CYBERCITY_TACTICAL_SMOKE="1" if args.smoke else "0")
        command = ["powershell.exe", "-NoProfile", "-File", str(Path(__file__).with_name("run_godot.ps1")),
                   "-Scene", "res://tactical_warehouse.tscn", "-RenderingMethod", "gl_compatibility"]
        if args.smoke:
            command.extend(["-QuitAfter", "1500"])
        with subprocess.Popen(command, env=env) as godot:
            while godot.poll() is None:
                mailbox.poll()
                time.sleep(.03)
        if args.smoke and (mailbox.sequence != 3 or mailbox.reply["state"]["round"] != 2):
            raise RuntimeError(f"Unexpected Godot exchange: {mailbox.reply}")
        return godot.returncode


if __name__ == "__main__":
    raise SystemExit(main())
