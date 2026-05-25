"""Combat preview math and warning checks."""

import unittest

from game.combat_preview import estimate_attack_preview, line_of_fire_warning
from game.stats import EnemyStats, PlayerStats
from game.unit import Unit


class CombatPreviewTest(unittest.TestCase):
    def test_preview_uses_existing_hit_formula_inputs(self):
        attacker = Unit(position=(0, 0), stats=PlayerStats(agi=8, str=2, psi=1, defense=1, con=1), health=10)
        defender = Unit(position=(64, 0), stats=EnemyStats(defense=2, agi=1, str=1, psi=1), health=10)
        defender.in_cover_bonus = 2

        preview = estimate_attack_preview(attacker, defender, "shoot")

        self.assertAlmostEqual(preview.hit_chance, 8 / (8 + 4), places=4)
        self.assertEqual(preview.min_damage, 8)
        self.assertEqual(preview.max_damage, 8)
        self.assertGreaterEqual(preview.crit_chance, 0.05)

    def test_warning_when_friendly_in_line_of_fire(self):
        attacker = Unit(position=(0, 0), stats=PlayerStats(), health=10)
        defender = Unit(position=(96, 0), stats=EnemyStats(), health=10)
        ally = Unit(position=(32, 0), stats=PlayerStats(), health=10)

        warning = line_of_fire_warning(attacker, defender, [attacker, ally])

        self.assertIsNotNone(warning)


if __name__ == "__main__":
    unittest.main()
