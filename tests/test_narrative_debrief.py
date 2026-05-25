"""Mission debrief narrative generation tests."""

import unittest

from game.character import Character
from game.consequences import Consequence
from game.mission_templates import MissionComplication, MissionTemplate
from game.narrative.debrief import build_mission_debrief_report
from game.savage_fate import tag_from_library


def _mission(title: str = "Signal Collapse") -> MissionTemplate:
    return MissionTemplate(
        id="debrief-test",
        title=title,
        objective_text="Secure the relay",
        target_faction="Starvers",
        district="Chrome Warrens",
        district_pressure={},
        starting_enemy_count=2,
        risk_level=3,
    )


def _complication() -> MissionComplication:
    return MissionComplication(
        key="retaliation",
        name="Faction Retaliation",
        trigger_text="Enemy reprisals ignite.",
        risk_threshold=1,
        tags=[tag_from_library("faction_retaliation")],
        consequence=Consequence(severity=3),
    )


class NarrativeDebriefTest(unittest.TestCase):
    def test_generation_is_deterministic_for_same_input(self):
        agent = Character("Nyx", stress=44)
        report_one = build_mission_debrief_report([agent], _mission(), True, None)
        report_two = build_mission_debrief_report([agent], _mission(), True, None)

        self.assertEqual(report_one.to_dict(), report_two.to_dict())

    def test_report_contains_agent_centered_line(self):
        report = build_mission_debrief_report([Character("Echo", stress=20)], _mission(), True)

        self.assertTrue(report.lines)
        self.assertIn("Echo", report.lines[0].text)
        self.assertEqual(report.lines[0].agent_name, "Echo")

    def test_tone_varies_with_stress_injury_and_failure(self):
        frayed = Character("Frayed", stress=90)
        injured = Character("Injured", stress=20, recovery_turns=2)
        injured.injuries.append("Shrapnel")

        report = build_mission_debrief_report(
            [frayed, injured], _mission("Glass Rupture"), False, _complication()
        )

        tones = {line.agent_name: line.emotional_tone for line in report.lines}
        types = {line.agent_name: line.consequence_type for line in report.lines}
        self.assertEqual(tones["Frayed"], "fractured")
        self.assertEqual(types["Injured"], "injured")
        self.assertTrue(any("Complication" in line.text for line in report.lines))

    def test_report_adds_endscreen_story_blocks(self):
        frayed = Character("Frayed", stress=88)
        report = build_mission_debrief_report([frayed], _mission("Neon Dusk"), False, _complication())

        self.assertIn("Neon Dusk", report.decision_key)
        self.assertIn("Risque", report.risk_taken)
        self.assertIn("Frayed", report.heroic_action)

    def test_report_links_to_rpg_layers(self):
        lead = Character("Lead", stress=70)
        lead.relationships["Echo"] = 3
        lead.stats.level = 4
        scout = Character("Scout", stress=30)

        report = build_mission_debrief_report([lead, scout], _mission(), True)

        self.assertEqual(len(report.rpg_links), 3)
        self.assertTrue(any("Stress:" in line for line in report.rpg_links))
        self.assertTrue(any("Relations:" in line for line in report.rpg_links))
        self.assertTrue(any("Progression:" in line for line in report.rpg_links))


if __name__ == "__main__":
    unittest.main()
