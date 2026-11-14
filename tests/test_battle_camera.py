"""Pure tactical camera behaviour tests."""

import unittest

from game.combat.camera import camera_pan_limits, camera_pan_to_focus, clamp_camera_pan


class BattleCameraTest(unittest.TestCase):
    def test_pan_limits_scale_but_remain_restrained(self):
        self.assertEqual(camera_pan_limits(1920, 1000), (192.0, 125.0))
        self.assertEqual(camera_pan_limits(800, 600), (100.0, 75.0))

    def test_pan_is_clamped_to_overscanned_map(self):
        self.assertEqual(clamp_camera_pan(999, -999, 1920, 1000), (192.0, -125.0))

    def test_focus_recentres_toward_active_unit_without_leaving_map(self):
        self.assertEqual(camera_pan_to_focus((960, 500), 1920, 1000), (0.0, 0.0))
        self.assertEqual(camera_pan_to_focus((100, 80), 1920, 1000), (-192.0, -125.0))


if __name__ == "__main__":
    unittest.main()
