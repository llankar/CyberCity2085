import json
from pathlib import Path
import tempfile
import unittest

from game.combat import CombatEngine, CombatState
from game.combat.movement import CELL_SIZE
from game.stats import EnemyStats, PlayerStats
from game.unit import Unit
from tactical_preview import TacticalPreview
from tactical_mailbox import TacticalMailbox
from run_tactical_preview import SCENARIOS, scenario_preview


class TacticalPreviewTest(unittest.TestCase):
    def test_warehouse_fire_spends_ap_and_surveyed_cover_blocks_fire(self):
        preview = scenario_preview("warehouse")
        ally = preview.units["ally:0"]
        enemy = preview.units["enemy:0"]
        position = enemy.position
        enemy.position = (7 * CELL_SIZE, 11 * CELL_SIZE)
        rejected = preview.action("fire", "ally:0", target_id="enemy:0")
        self.assertFalse(rejected["success"])
        self.assertIn("line blocked", rejected["message"])
        self.assertEqual(ally.action_points, 3)
        enemy.position = position
        fired = preview.action("fire", "ally:0", target_id="enemy:0")
        self.assertTrue(fired["success"], fired)
        self.assertEqual(ally.action_points, 2)

    def test_scenarios_use_original_geometry_and_advance_round(self):
        for name, (map_name, (x, y), _) in SCENARIOS.items():
            with self.subTest(map=name):
                preview = scenario_preview(name)
                terrain = preview.engine.terrain_profile
                self.assertEqual(terrain.source, "manual_wall_traces_v1")
                self.assertEqual(Path(terrain.image_path).stem, map_name)
                destination = [x + 1, y]
                moved = preview.action("move", "ally:0", destination=destination)
                self.assertTrue(moved["success"], moved)
                self.assertEqual(moved["state"]["units"][0]["cell"], destination)
                result = preview.action("end_turn", "ally:0")
                self.assertTrue(result["success"], result)
                self.assertEqual(result["state"]["turn"], "player")
                self.assertEqual(result["state"]["round"], 2)

    def test_engine_updates_position_ap_and_rejects_blocked_cell(self):
        ally = Unit(position=(64, 64), stats=PlayerStats(), health=10, action_points=3)
        enemy = Unit(position=(320, 64), stats=EnemyStats(level=1), health=10, unit_type="enemy")
        engine = CombatEngine(CombatState(None, [ally], [enemy]),
                              can_enter=lambda x, y: x != 128)
        preview = TacticalPreview(engine)
        result = preview.action("move", "ally:0", destination=[3, 2])
        self.assertTrue(result["success"], result)
        self.assertEqual(result["state"]["units"][0]["cell"], [3, 2])
        self.assertLess(ally.action_points, 3)
        rejected = preview.action("move", "ally:0", destination=[4, 2])
        self.assertFalse(rejected["success"], rejected)
        self.assertEqual(rejected["state"], result["state"])


    def test_mailbox_applies_each_command_once(self):
        ally = Unit(position=(64, 64), stats=PlayerStats(), health=10, action_points=3)
        enemy = Unit(position=(320, 64), stats=EnemyStats(level=1), health=10, unit_type="enemy")
        engine = CombatEngine(CombatState(None, [ally], [enemy]))
        lab_tmp = Path("E:/CyberCity2085-3d-lab/tmp")
        with tempfile.TemporaryDirectory(dir=lab_tmp if lab_tmp.is_dir() else None) as temp:
            directory = Path(temp)
            mailbox = TacticalMailbox(directory, TacticalPreview(engine))
            command = directory / "command-1.json"
            command.write_text('{"action":', encoding="utf-8")
            self.assertFalse(mailbox.poll())
            command.write_text(json.dumps({"action":"move","actor":"ally:0","destination":[3,2]}),
                               encoding="utf-8")
            self.assertTrue(mailbox.poll())
            response = json.loads((directory / "reply.json").read_text(encoding="utf-8"))
            self.assertEqual(response["sequence"], 1)
            self.assertTrue(response["success"])
            self.assertFalse(mailbox.poll())
            self.assertEqual(ally.position, (96,64))
