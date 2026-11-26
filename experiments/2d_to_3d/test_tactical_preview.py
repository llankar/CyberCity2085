import json
from pathlib import Path
import tempfile
import unittest

from game.combat import CombatEngine, CombatState
from game.stats import EnemyStats, PlayerStats
from game.unit import Unit
from tactical_preview import TacticalPreview
from tactical_mailbox import TacticalMailbox
from run_tactical_preview import warehouse_preview


class TacticalPreviewTest(unittest.TestCase):
    def test_warehouse_uses_real_geometry_and_advances_round(self):
        preview = warehouse_preview()
        self.assertEqual(preview.engine.terrain_profile.source, "manual_wall_traces_v1")
        moved = preview.action("move", "ally:0", destination=[20, 14])
        self.assertTrue(moved["success"], moved)
        self.assertEqual(moved["state"]["units"][0]["cell"], [20, 14])
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
