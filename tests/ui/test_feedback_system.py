import unittest

from game.ui.action_feedback import action_message, confirm_message, push_action
from game.ui.feedback.error_banner import build_error_banner
from game.ui.widgets.notification_center import NotificationCenter


class FeedbackSystemTest(unittest.TestCase):
    def test_action_message_standard_structure(self):
        level, text = action_message("save", True, "funds +0, stress +0, time +0")
        self.assertEqual(level, "success")
        self.assertIn("Action:", text)
        self.assertIn("Result:", text)
        self.assertIn("Impact:", text)
        self.assertIn("Next:", text)

    def test_confirm_messages_for_costly_irreversible_actions(self):
        self.assertIn("Confirmation required", confirm_message("spend_funds"))
        self.assertIn("overwrites", confirm_message("load"))

    def test_dispatch_pushes_notification(self):
        center = NotificationCenter(max_items=3)
        message = push_action(center, "recruitment", True, "funds -5, stress +1, time +0")
        self.assertIn("Action:", message)
        self.assertTrue(any("[SUCCESS]" in line for line in center.latest_text_lines(1)))

    def test_error_banner_used_on_failure(self):
        center = NotificationCenter(max_items=3)
        message = push_action(center, "load", False, "save file missing")
        self.assertIn("[ERROR]", message)
        self.assertEqual(build_error_banner("load", "save file missing"), "[ERROR] load: save file missing")


if __name__ == "__main__":
    unittest.main()
