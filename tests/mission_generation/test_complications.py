import unittest

from game.missions.complications import select_complications


class MissionComplicationsTest(unittest.TestCase):
    def test_selection_varies_by_pressure_bucket(self):
        low = select_complications(district_pressure=10, mission_tags=["stealth"], seed=1)
        high = select_complications(district_pressure=80, mission_tags=["stealth"], seed=1)

        self.assertEqual(1, len(low))
        self.assertEqual(2, len(high))
        self.assertTrue(all(item.risk_threshold == 1 for item in low))
        self.assertTrue(all(item.risk_threshold == 3 for item in high))

    def test_selection_is_deterministic_with_seed(self):
        first = select_complications(district_pressure=55, mission_tags=["data", "infiltration"], seed=42)
        second = select_complications(district_pressure=55, mission_tags=["data", "infiltration"], seed=42)

        self.assertEqual([c.key for c in first], [c.key for c in second])

    def test_selection_works_without_tags(self):
        selected = select_complications(district_pressure=45, mission_tags=None, seed=8)

        self.assertTrue(selected)
        self.assertLessEqual(len(selected), 2)


if __name__ == "__main__":
    unittest.main()
