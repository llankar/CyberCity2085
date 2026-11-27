"""Strategic event generation, expiry, and command choices."""

import unittest

from game.character import Character
from game.gamestate import GameState
from game.mission_system import ensure_mission_templates, launch_selected_mission
from game.management.events import (
    ActiveEvent,
    EventChoice,
    EventTemplate,
    EVENT_CATEGORIES,
    apply_event_choice,
    apply_event_effects,
    create_event_templates,
    expire_events,
)
from game.ui.command_deck import build_event_panel_lines


class FixedRoller:
    """Deterministic RNG that always allows and selects the first weighted event."""

    def random(self):
        return 0.0

    def choices(self, population, weights=None, k=1):
        return [population[0]]


class StrategicEventsTest(unittest.TestCase):
    def test_event_generation_uses_requested_threat_categories(self):
        game_state = GameState()
        game_state.district.stability = 12
        game_state.district.unrest = 90
        game_state.district.media_heat = 80

        event = game_state.roll_strategic_event(FixedRoller())

        self.assertIsNotNone(event)
        self.assertIn(event.category, EVENT_CATEGORIES)
        self.assertEqual(len(game_state.active_events), 1)
        self.assertEqual(
            game_state.active_events[0].expires_day,
            game_state.calendar.current_day + event.template.expiration_days - 1,
        )
        panel_lines = build_event_panel_lines(
            game_state.active_events, game_state.calendar.current_day
        )
        self.assertIn(event.title, panel_lines[0])
        self.assertIn("1.1", panel_lines[1])

    def test_active_event_exposes_template_description_for_ui_rendering(self):
        event = ActiveEvent(
            id="event-ui",
            template=EventTemplate(
                title="Signal Drift",
                category="social unrest",
                description="A hostile signal spoofs trusted orders.",
                severity=2,
                choices=[],
            ),
            created_day=1,
            expires_day=2,
        )

        self.assertEqual(event.description, event.template.description)
        self.assertIn("trusted orders", event.description)

    def test_event_expiration_applies_unattended_consequences(self):
        game_state = GameState()
        starting_unrest = game_state.district.unrest
        template = EventTemplate(
            title="Ignored Riot",
            category="social unrest",
            description="A riot is left to burn.",
            severity=2,
            choices=[],
            consequences={"city_unrest": 9, "city_stability": -4},
            expiration_days=1,
        )
        game_state.active_events.append(
            ActiveEvent(
                id="event-test",
                template=template,
                created_day=game_state.calendar.current_day,
                expires_day=game_state.calendar.current_day,
            )
        )
        game_state.calendar.advance_one_day()

        expired = expire_events(game_state)

        self.assertEqual([event.id for event in expired], ["event-test"])
        self.assertEqual(game_state.active_events, [])
        self.assertEqual(game_state.district.unrest, starting_unrest + 9)
        self.assertTrue(any("Expired event" in entry for entry in game_state.event_log))

    def test_crisis_closes_only_an_optional_inactive_route(self):
        from game.campaign.story_missions import STORY_MISSIONS_BY_ID

        state = GameState()
        ensure_mission_templates(state)
        story = next(mission for mission in state.mission_templates if mission.id in STORY_MISSIONS_BY_ID)
        optional = [mission for mission in state.mission_templates if mission.id not in STORY_MISSIONS_BY_ID]
        state.active_mission = optional[0]
        state.mission_templates = [story, *optional]
        state.unavailable_mission_ids = [story.id, "retired-operation"]

        apply_event_effects(state, {"mission_availability": -1})
        self.assertEqual(state.unavailable_mission_ids, [optional[1].id])
        state.active_mission = None
        self.assertEqual(launch_selected_mission(state).id, story.id)
        apply_event_effects(state, {"mission_availability": 1})
        self.assertEqual(state.unavailable_mission_ids, [])

    def test_board_vote_applies_pressure_to_aegis(self):
        game_state = GameState()
        aegis = game_state.get_faction("Aegis Dynamics")
        rival = max(game_state.factions, key=lambda faction: faction.hostility_to_player)
        aegis_before, rival_before = aegis.hostility_to_player, rival.hostility_to_player
        template = next(item for item in create_event_templates() if item.title == "Board Knife Vote")
        day = game_state.calendar.current_day
        game_state.active_events.append(ActiveEvent("board", template, day, day + 1))

        self.assertTrue(apply_event_choice(game_state, "board", "lobby"))
        self.assertEqual(aegis.hostility_to_player, aegis_before - 5)
        self.assertEqual(rival.hostility_to_player, rival_before)

    def test_event_choice_changes_funds_agents_factions_city_and_missions(self):
        game_state = GameState()
        game_state.characters = [Character(name="Vega", stress=10)]
        starting_funds = game_state.available_funds
        starting_stability = game_state.district.stability
        hostile_faction = max(
            game_state.factions, key=lambda faction: faction.hostility_to_player
        )
        starting_hostility = hostile_faction.hostility_to_player
        ensure_mission_templates(game_state)
        first_mission_id = game_state.mission_templates[0].id
        template = EventTemplate(
            title="Council Knife",
            category="city politics",
            description="Council pressure demands an answer.",
            severity=3,
            choices=[
                EventChoice(
                    key="refuse",
                    label="Refuse leverage",
                    effects={
                        "funds": -12,
                        "agent_stress": 7,
                        "faction_pressure": 5,
                        "city_stability": -6,
                        "mission_availability": -1,
                    },
                )
            ],
            consequences={},
            expiration_days=2,
        )
        game_state.active_events.append(
            ActiveEvent(
                id="event-choice",
                template=template,
                created_day=game_state.calendar.current_day,
                expires_day=game_state.calendar.current_day + 1,
            )
        )

        game_state.funds.current_funds = 11
        self.assertFalse(apply_event_choice(game_state, "event-choice", "refuse"))
        self.assertEqual(game_state.available_funds, 11)
        self.assertEqual(len(game_state.active_events), 1)
        self.assertEqual(game_state.characters[0].stress, 10)
        self.assertEqual(game_state.district.stability, starting_stability)
        self.assertEqual(hostile_faction.hostility_to_player, starting_hostility)
        self.assertNotIn(first_mission_id, game_state.unavailable_mission_ids)
        game_state.funds.current_funds = starting_funds

        applied = apply_event_choice(game_state, "event-choice", "refuse")

        self.assertTrue(applied)
        self.assertEqual(game_state.active_events, [])
        self.assertEqual(game_state.available_funds, starting_funds - 12)
        self.assertEqual(game_state.characters[0].stress, 17)
        self.assertEqual(hostile_faction.hostility_to_player, starting_hostility + 5)
        self.assertEqual(game_state.district.stability, starting_stability - 6)
        self.assertIn(first_mission_id, game_state.unavailable_mission_ids)
        with self.assertRaises(ValueError):
            launch_selected_mission(game_state)


if __name__ == "__main__":
    unittest.main()
