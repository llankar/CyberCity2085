import unittest

from game.ui.components.combat.combat_log_panel import (
    EVENT_EMOTIONAL,
    EVENT_STRESS,
    CombatLogEvent,
    apply_combat_log_filter,
    build_combat_log_expanded_lines,
    build_combat_log_hud_lines,
)


class CombatLogPanelTest(unittest.TestCase):
    def test_filter_keeps_only_requested_type(self):
        events = [
            CombatLogEvent("Nyx hits the target.", "combat"),
            CombatLogEvent("Patch keeps calm.", EVENT_EMOTIONAL),
            CombatLogEvent("Stress +4 for Nyx.", EVENT_STRESS),
        ]

        filtered = apply_combat_log_filter(events, active_filter=EVENT_STRESS)

        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0].text, "Stress +4 for Nyx.")

    def test_hud_version_is_short_and_latest_first(self):
        events = [
            CombatLogEvent("Opening turn.", "system"),
            CombatLogEvent("Nyx neutralizes a threat.", "combat"),
            CombatLogEvent("Patch reassures Nyx.", EVENT_EMOTIONAL),
            CombatLogEvent("Stress +3 for Patch.", EVENT_STRESS),
        ]

        lines = build_combat_log_hud_lines(events, max_lines=2)

        self.assertEqual(len(lines), 2)
        self.assertIn("Stress +3", lines[0].text)
        self.assertIn("Patch reassures Nyx", lines[1].text)

    def test_expanded_debug_marks_emotional_and_stress_events(self):
        events = [
            CombatLogEvent("Fire line secured.", "system"),
            CombatLogEvent("Nyx hesitates before the assault.", EVENT_EMOTIONAL),
            CombatLogEvent("Stress +5 (sustained pressure).", EVENT_STRESS),
        ]

        lines = build_combat_log_expanded_lines(events)

        emotional = next(line for line in lines if "[EMOTIONAL]" in line.text)
        stress = next(line for line in lines if "[STRESS]" in line.text)
        self.assertEqual(emotional.emphasis, "accent")
        self.assertEqual(stress.emphasis, "accent")


if __name__ == "__main__":
    unittest.main()
