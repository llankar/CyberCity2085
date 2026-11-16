"""Pure tactical camera behaviour tests."""

import unittest

from game.combat.camera import camera_pan_limits, camera_pan_to_focus, clamp_camera_pan, keep_focus_visible


class BattleCameraTest(unittest.TestCase):
    def test_combat_transition_reframes_same_agent_above_larger_hud(self):
        position = (96, 64)
        deployment = keep_focus_visible(position, (0, 0), 1280, 720, hud_bottom=40)
        self.assertGreaterEqual(position[1]-deployment[1], 72)
        combat = keep_focus_visible(position, deployment, 1280, 720, hud_bottom=210)
        self.assertGreaterEqual(position[1]-combat[1], 242)
        self.assertLess(combat[1], deployment[1])

    def test_hud_clearance_reveals_low_units_without_moving_the_world_position(self):
        for width,height in ((960,640),(1280,720),(1920,1000)):
            for position in ((96,0),(96,64),(448,320)):
                pan=keep_focus_visible(position,(0,0),width,height,hud_bottom=210)
                self.assertGreaterEqual(position[1]-pan[1],242)
                self.assertEqual(clamp_camera_pan(*pan,width,height,hud_bottom=210),pan)

    def test_visible_focus_keeps_manual_pan_and_home_can_reveal_the_bottom(self):
        self.assertEqual(keep_focus_visible((640,400),(20,-40),1280,720,hud_bottom=210),(20,-40))
        pan=camera_pan_to_focus((96,64),1280,720,hud_bottom=210)
        self.assertGreaterEqual(64-pan[1],242)

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
