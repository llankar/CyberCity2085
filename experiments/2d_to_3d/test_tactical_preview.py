import unittest

from game.combat import CombatEngine, CombatState
from game.stats import EnemyStats, PlayerStats
from game.unit import Unit
from tactical_preview import TacticalPreview


class TacticalPreviewTest(unittest.TestCase):
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
