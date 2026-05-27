"""Click-through management hub tests."""

import sys
import types
import unittest


class _FakeView:
    def __init__(self, *args, **kwargs):
        self.window = None

    def clear(self):
        pass


fake_arcade = types.SimpleNamespace(
    View=_FakeView,
        key=types.SimpleNamespace(
        B=66,
        N=78,
        C=67,
        A=65,
        D=68,
        X=88,
        R=82,
        T=84,
        S=83,
        L=76,
        V=86,
        H=72,
        M=77,
        TAB=9,
            F1=1001,
            F2=1002,
            F3=1003,
            F4=1004,
            F5=1005,
        F6=1006,
        LEFT=1007,
        RIGHT=1008,
        SPACE=32,
        ENTER=13,
        RETURN=13,
        ESCAPE=27,
        KEY_1=49,
        KEY_2=50,
        KEY_3=51,
        KEY_4=52,
        KEY_5=53,
        KEY_6=54,
        KEY_7=55,
        KEY_8=56,
        KEY_9=57,
        MOD_CTRL=2,
    ),
    draw_text=lambda *args, **kwargs: None,
    draw_lrbt_rectangle_filled=lambda *args, **kwargs: None,
    draw_line=lambda *args, **kwargs: None,
    draw_texture_rect=lambda *args, **kwargs: None,
    draw_circle_outline=lambda *args, **kwargs: None,
    draw_circle_filled=lambda *args, **kwargs: None,
    draw_rect_outline=lambda *args, **kwargs: None,
    draw_lrbt_rectangle_outline=lambda *args, **kwargs: None,
    Camera2D=lambda *args, **kwargs: None,
    SpriteList=lambda *args, **kwargs: types.SimpleNamespace(
        draw=lambda: None,
        append=lambda sprite: None,
        __iter__=lambda self: iter([]),
        __len__=lambda self: 0,
    ),
    Sprite=lambda *args, **kwargs: types.SimpleNamespace(
        kill=lambda: None,
        center_x=kwargs.get("center_x", 0),
        center_y=kwargs.get("center_y", 0),
        width=32,
        height=32,
        visible=True,
    ),
    set_background_color=lambda *args, **kwargs: None,
    LBWH=lambda *args, **kwargs: None,
    load_texture=lambda *args, **kwargs: None,
    color=types.SimpleNamespace(),
)
sys.modules["arcade"] = fake_arcade

from game.gamestate import GameState
from game.management.spec_ops_assets import default_spec_ops_assets
from game.recruitment import create_character
import game.ui.screens.management_screen as management_screen
import game.ui.panels as panels
import game.ui.components.agent.cards as agent_cards
from game.ui.screens.facility import build_facility_rooms
from game.ui.screens.management_screen import ManagementView
from game.ui.room_interaction import open_room
from game.ui.widgets.notification_center import NotificationCenter


class _FakeWindow:
    def __init__(self):
        self.width = 1280
        self.height = 720
        self.shown_view = None
        self.activated = False

    def show_view(self, view):
        self.shown_view = view

    def activate(self):
        self.activated = True


class ManagementHubUITest(unittest.TestCase):
    def _seed_interactive_state(self, view: ManagementView) -> None:
        view.game_state.characters = [
            create_character("Rook", "samurai"),
            create_character("Longshot", "sniper"),
            create_character("Oracle", "psi"),
            create_character("Katana", "samurai"),
        ]
        view.game_state.characters[0].pending_points = 5
        view.game_state.selected_agent_names = [view.game_state.characters[0].name]
        view.game_state.spec_ops_assets = default_spec_ops_assets()


    def test_double_click_agent_card_opens_full_sheet(self):
        view = ManagementView(GameState())
        view.window = _FakeWindow()
        view.setup()
        self._seed_interactive_state(view)

        view._dispatch("agent_card", 0)
        view._dispatch("agent_card", 0)

        self.assertEqual(view.expanded_agent_sheet_index, 0)

    def test_opening_and_closing_agent_sheet_toggles_topmost_focus(self):
        view = ManagementView(GameState())
        view.window = _FakeWindow()
        view.setup()
        self._seed_interactive_state(view)

        calls = []
        original = management_screen._set_window_topmost

        def _capture(window, enabled):
            calls.append(enabled)

        management_screen._set_window_topmost = _capture
        try:
            view._dispatch("agent_card", 0)
            view._dispatch("agent_card", 0)
            view.on_key_press(management_screen.arcade.key.ESCAPE, 0)
        finally:
            management_screen._set_window_topmost = original

        self.assertGreaterEqual(calls.count(True), 1)
        self.assertEqual(calls[-1], False)
        self.assertIsNone(view.expanded_agent_sheet_index)

    def test_expanded_agent_sheet_draws_allocation_hits(self):
        view = ManagementView(GameState())
        view.window = _FakeWindow()
        view.setup()
        self._seed_interactive_state(view)
        view.expanded_agent_sheet_index = 0

        view.on_draw()

        stat_hit = next(hit for hit in view._modal_hits if hit.action == "sheet_spend_stat")
        train_hit = next(hit for hit in view._modal_hits if hit.action == "sheet_train_skills")
        before_points = view.game_state.characters[0].pending_points
        before_str = view.game_state.characters[0].stats.str

        view.on_mouse_press((stat_hit.left + stat_hit.right) // 2, (stat_hit.bottom + stat_hit.top) // 2, 0, 0)
        self.assertEqual(view.game_state.characters[0].pending_points, before_points - 1)
        self.assertGreater(view.game_state.characters[0].stats.str, before_str)

        view.game_state.characters[0].pending_points = 1
        before_skills = dict(view.game_state.characters[0].skills)
        view.on_mouse_press((train_hit.left + train_hit.right) // 2, (train_hit.bottom + train_hit.top) // 2, 0, 0)
        self.assertEqual(view.game_state.characters[0].pending_points, 0)
        self.assertTrue(
            any(view.game_state.characters[0].skills[key] > before_skills.get(key, 0) for key in before_skills)
        )

    def test_escape_closes_expanded_agent_sheet(self):
        view = ManagementView(GameState())
        view.window = _FakeWindow()
        view.setup()
        self._seed_interactive_state(view)
        view.expanded_agent_sheet_index = 0

        view.on_key_press(management_screen.arcade.key.ESCAPE, 0)

        self.assertIsNone(view.expanded_agent_sheet_index)
    def test_management_view_uses_the_hub_room_model(self):
        view = ManagementView(GameState())
        view.window = _FakeWindow()
        view.setup()

        rooms = build_facility_rooms(view.window.width, view.window.height, "hub")
        command = rooms[0]

        self.assertEqual(view.room_ui.mode, "hub")
        self.assertEqual([room.key for room in rooms], ["command", "city", "squad", "assets", "research", "intel"])

        view.on_mouse_press(command.left + 1, command.bottom + 1, 0, 0)

        self.assertTrue(view.room_ui.is_open)
        self.assertEqual(view.room_ui.active_room_key, "command")
        self.assertTrue(any(button.action.key == "advance_day" for button in view.room_ui.action_buttons))

    def test_keyboard_shortcut_opens_the_correct_room(self):
        view = ManagementView(GameState())
        view.window = _FakeWindow()
        view.setup()

        original_key_ns = management_screen.arcade.key
        management_screen.arcade.key = types.SimpleNamespace(
            F1=1001,
            F2=1002,
            F3=1003,
            F4=1004,
            F5=1005,
            F6=1006,
        )
        try:
            view.on_key_press(1003, 0)
        finally:
            management_screen.arcade.key = original_key_ns

        self.assertEqual(view.room_ui.active_room_key, "squad")
        self.assertTrue(any(button.action.key == "launch_mission" for button in view.room_ui.action_buttons))

    def test_room_info_lines_use_the_current_room_content_sources(self):
        view = ManagementView(GameState())
        view.window = _FakeWindow()
        view.setup()

        lines = view._room_info_lines()

        self.assertTrue(any("Funds" in line or "Turn" in line for line in lines["command"]))
        self.assertTrue(any("District" in line or "Control faction" in line for line in lines["city"]))
        self.assertTrue(any("Squad morale" in line for line in lines["squad"]))
        self.assertTrue(any("Spec Ops Assets Guide" in line for line in lines["assets"]))
        self.assertTrue(any("Research tree" in line for line in lines["research"]))
        self.assertTrue(any("Event log entries" in line for line in lines["intel"]))

    def test_legacy_room_renderer_is_used_for_open_rooms(self):
        view = ManagementView(GameState())
        view.window = _FakeWindow()
        view.setup()
        open_room(view.room_ui, view.window.width, view.window.height, "command")
        view.room_ui.expansion = 1.0
        called = []

        def _record(*args, **kwargs):
            called.append((args, kwargs))

        view._draw_command_tab = _record
        view._draw_legacy_room_content()

        self.assertTrue(called)

    def test_draw_path_no_longer_paints_summary_text_over_rooms(self):
        view = ManagementView(GameState())
        view.window = _FakeWindow()
        view.setup()

        captured = {}

        def _capture(width, height, state, resources, room_info_lines=None, roster_cards=None, available_funds=None, draw_controls=None):
            captured["room_info_lines"] = room_info_lines
            captured["roster_cards"] = roster_cards

        original = management_screen.draw_graphical_command_surface
        management_screen.draw_graphical_command_surface = _capture
        try:
            view.on_draw()
        finally:
            management_screen.draw_graphical_command_surface = original

        self.assertEqual(captured["room_info_lines"], {})
        self.assertEqual(captured["roster_cards"], [])

    def test_squad_room_passes_roster_cards_to_the_graphical_shell(self):
        view = ManagementView(GameState())
        view.window = _FakeWindow()
        view.setup()
        self._seed_interactive_state(view)
        open_room(view.room_ui, view.window.width, view.window.height, "squad")
        view.room_ui.expansion = 1.0

        captured = {}

        def _capture(width, height, state, resources, room_info_lines=None, roster_cards=None, available_funds=None, draw_controls=None):
            captured["roster_cards"] = roster_cards

        original = management_screen.draw_graphical_command_surface
        management_screen.draw_graphical_command_surface = _capture
        try:
            view.on_draw()
        finally:
            management_screen.draw_graphical_command_surface = original

        self.assertGreater(len(captured["roster_cards"]), 0)

    def test_resource_strip_shows_all_resource_labels(self):
        calls = []
        original = panels.arcade.draw_text

        def _capture(text, *args, **kwargs):
            calls.append((text, args, kwargs))

        panels.arcade.draw_text = _capture
        try:
            panels.draw_icon_resource_hud(
                1280,
                720,
                {"credits": 12, "intel": 3, "salvage": 5, "influence": 7},
                available_funds=2500,
            )
        finally:
            panels.arcade.draw_text = original

        drawn_text = {call[0] for call in calls}
        self.assertIn("INFLUENCE", drawn_text)
        self.assertTrue(any(text.startswith("¥ 2,500") for text in drawn_text))
        funds_call = next(call for call in calls if call[0] == "FUNDS")
        influence_label_call = next(call for call in calls if call[0] == "INFLUENCE")
        influence_value_call = next(call for call in calls if call[0] == "7")
        self.assertGreaterEqual(funds_call[2].get("font_size", 0), 8)
        self.assertGreaterEqual(influence_label_call[2].get("font_size", 0), 8)
        self.assertGreaterEqual(influence_value_call[2].get("font_size", 0), 12)

    def test_agent_card_shows_defense_stat(self):
        calls = []
        original = agent_cards.arcade.draw_text

        def _capture(text, *args, **kwargs):
            calls.append((text, args, kwargs))

        agent_cards.arcade.draw_text = _capture
        try:
            agent_cards.draw_agent_card(
                {
                    "name": "Agent 1",
                    "role": "samurai",
                    "defense": 6,
                    "active": True,
                    "selected": True,
                    "portrait_path": None,
                    "pending_points": 0,
                },
                10,
                20,
                260,
                140,
                management_screen.palette.HEADER,
                lambda *args, **kwargs: None,
                lambda *args, **kwargs: None,
                lambda *args, **kwargs: None,
            )
        finally:
            agent_cards.arcade.draw_text = original

        self.assertTrue(any(text == "DEF 6" for text, *_ in calls))

    def test_intel_room_wraps_long_text_with_explicit_width(self):
        view = ManagementView(GameState())
        view.window = _FakeWindow()
        view.setup()
        view.game_state.event_log = [
            "Intel relay: a very long event log entry that should wrap instead of running off the right side of the panel.",
        ]

        calls = []
        original = management_screen.arcade.draw_text

        def _capture(text, *args, **kwargs):
            calls.append((text, args, kwargs))

        management_screen.arcade.draw_text = _capture
        try:
            view._draw_intel_tab(100, 50, 520, 430)
        finally:
            management_screen.arcade.draw_text = original

        wrapped = next(call for call in calls if "right side of the panel" in call[0])
        kwargs = wrapped[2]
        self.assertEqual(kwargs.get("align"), "left")
        self.assertGreaterEqual(kwargs.get("font_size", 0), 11)
        content_w = 520 - 100 - 10
        expected_left_width = min(max(240, int(content_w * 0.60)), max(120, content_w - 150))
        self.assertEqual(kwargs.get("width"), max(10, expected_left_width - 24))

    def test_notification_toast_moves_toward_the_center(self):
        notifications = NotificationCenter()
        notifications.success("Campaign saved to slot 1")

        calls = []
        original = management_screen.arcade.draw_text

        def _capture(text, *args, **kwargs):
            calls.append((text, args, kwargs))

        management_screen.arcade.draw_text = _capture
        try:
            management_screen._draw_notification_toast(notifications, 1920, 1080)
        finally:
            management_screen.arcade.draw_text = original

        toast = next(call for call in calls if call[0].startswith("[SUCCESS]"))
        x = toast[1][0]
        panel_w = min(760, max(460, int(1920 * 0.40)))
        expected_x = ((1920 + panel_w) // 2) - panel_w + 8
        self.assertEqual(x, expected_x)
        self.assertLess(x, 1000)

    def test_hub_overlay_does_not_draw_the_generic_room_title_layer(self):
        view = ManagementView(GameState())
        view.window = _FakeWindow()
        view.setup()
        open_room(view.room_ui, view.window.width, view.window.height, "command")
        view.room_ui.expansion = 1.0

        import game.ui.panels as panels

        called = []
        original = panels.draw_room_title_and_info

        def _record(*args, **kwargs):
            called.append((args, kwargs))

        panels.draw_room_title_and_info = _record
        try:
            view.on_draw()
        finally:
            panels.draw_room_title_and_info = original

        self.assertFalse(called)

    def test_hub_rooms_keep_their_original_click_regions_and_dispatch(self):
        view = ManagementView(GameState())
        view.window = _FakeWindow()
        view.setup()
        self._seed_interactive_state(view)

        cases = {
            "command": ("corp_upgrade_",),
            "city": ("city_upgrade_",),
            "squad": ("agent_card", "spend_stat_point", "equip_prev", "equip_next", "select_mission"),
            "assets": ("asset_select", "asset_repair", "asset_deploy_toggle", "catalog_acquire", "catalog_scroll"),
            "research": ("start_research_",),
        }

        for room_key, expected_prefixes in cases.items():
            with self.subTest(room=room_key):
                open_room(view.room_ui, view.window.width, view.window.height, room_key)
                view.room_ui.expansion = 1.0
                view.on_draw()
                actions = [hit.action for hit in view._hits]
                self.assertTrue(
                    any(
                        action == prefix or action.startswith(prefix)
                        for prefix in expected_prefixes
                        for action in actions
                    ),
                    msg=f"missing expected hit regions for {room_key}: {actions}",
                )
                if room_key == "squad":
                    first_agent = next(hit for hit in view._hits if hit.action == "agent_card")
                    first_stat = next(hit for hit in view._hits if hit.action == "spend_stat_point")
                    first_equip = next(hit for hit in view._hits if hit.action == "equip_next")
                    second_mission = next(hit for hit in view._hits if hit.action == "select_mission" and hit.data == 1)

                    agent_name = view.game_state.characters[0].name
                    before_points = view.game_state.characters[0].pending_points
                    before_str = view.game_state.characters[0].stats.str
                    before_item = view.game_state.characters[0].loadout.item_for_slot("primary_weapon")

                    view.on_mouse_press((first_agent.left + first_agent.right) // 2, (first_agent.bottom + first_agent.top) // 2, 0, 0)
                    self.assertNotIn(agent_name, view.game_state.selected_agent_names)

                    view.on_mouse_press((first_stat.left + first_stat.right) // 2, (first_stat.bottom + first_stat.top) // 2, 0, 0)
                    self.assertEqual(view.game_state.characters[0].pending_points, before_points - 1)
                    self.assertGreater(view.game_state.characters[0].stats.str, before_str)

                    view.on_mouse_press((first_equip.left + first_equip.right) // 2, (first_equip.bottom + first_equip.top) // 2, 0, 0)
                    after_item = view.game_state.characters[0].loadout.item_for_slot("primary_weapon")
                    self.assertIsNotNone(after_item)
                    self.assertNotEqual(after_item, before_item)

                    view.on_mouse_press((second_mission.left + second_mission.right) // 2, (second_mission.bottom + second_mission.top) // 2, 0, 0)
                    self.assertEqual(view.game_state.selected_mission_index, 1)

    def test_rect_skips_invalid_lrbt_inputs(self):
        calls = []
        original = management_screen.arcade.draw_lrbt_rectangle_filled

        def _capture(*args, **kwargs):
            calls.append((args, kwargs))

        management_screen.arcade.draw_lrbt_rectangle_filled = _capture
        try:
            management_screen._rect(100, 120, 80, 200, (255, 255, 255, 255))
            management_screen._rect(100, 220, 180, 200, (255, 255, 255, 255))
            management_screen._rect(100, 120, 180, 200, (255, 255, 255, 255))
        finally:
            management_screen.arcade.draw_lrbt_rectangle_filled = original

        self.assertEqual(len(calls), 1)

    def test_recruit_prompt_opens_a_named_candidate_list(self):
        view = ManagementView(GameState())
        view.window = _FakeWindow()
        view.setup()
        view.game_state.add_funds(100, "test", "Recruitment test budget")

        view._do_recruit_prompt()

        self.assertGreater(len(view.pending_recruit_candidates), 0)
        self.assertTrue(all(candidate.name for candidate in view.pending_recruit_candidates))
        self.assertTrue(all(candidate.role in {"samurai", "sniper", "psi"} for candidate in view.pending_recruit_candidates))
        self.assertNotIn("Agent 1", {candidate.name for candidate in view.pending_recruit_candidates})

        recruited_name = view.pending_recruit_candidates[0].name
        view._do_recruit_candidate(0)

        self.assertEqual(len(view.pending_recruit_candidates), 0)
        self.assertIn(recruited_name, {character.name for character in view.game_state.characters})

    def test_squad_room_can_remove_agent_from_roster(self):
        view = ManagementView(GameState())
        view.window = _FakeWindow()
        view.setup()
        self._seed_interactive_state(view)
        view.deployment_cursor = 0
        removed_name = view.game_state.characters[0].name

        open_room(view.room_ui, view.window.width, view.window.height, "squad")
        remove_button = next(
            button for button in view.room_ui.action_buttons if button.action.key == "remove_agent"
        ).rect

        view._do_remove_agent()

        self.assertEqual(len(view.game_state.characters), 3)
        self.assertNotIn(removed_name, {character.name for character in view.game_state.characters})
        self.assertNotIn(removed_name, view.game_state.selected_agent_names)

    def test_launch_mission_footer_is_lower_and_separated_from_room_text(self):
        view = ManagementView(GameState())
        view.window = _FakeWindow()
        view.setup()
        self._seed_interactive_state(view)

        open_room(view.room_ui, view.window.width, view.window.height, "squad")
        view.room_ui.expansion = 1.0
        view.on_draw()

        launch_hit = next(
            button for button in view._hits
            if button.action == "launch_mission"
        )
        self.assertGreater(launch_hit.bottom, 120)
        self.assertLess(launch_hit.bottom, 190)
        self.assertLess(launch_hit.top, 240)

        strip_bottom = min(button.rect.bottom for button in view.room_ui.action_buttons)
        self.assertGreater(strip_bottom, 60)
        self.assertLess(strip_bottom, 110)


if __name__ == "__main__":
    unittest.main()
