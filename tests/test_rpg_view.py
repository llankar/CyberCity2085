"""RPG view mission launch guards."""

import sys
import types
import unittest
from pathlib import Path

from game.management.spec_ops_assets import default_spec_ops_assets


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
        KEY_1=49,
        KEY_2=50,
        KEY_3=51,
        KEY_4=52,
        KEY_5=53,
        KEY_7=55,
        KEY_8=56,
        KEY_9=57,
        C=67,
        H=72,
        M=77,
        R=82,
        X=88,
        S=83,
        L=76,
        TAB=9,
        UP=1000,
        DOWN=1001,
        LEFT=1002,
        RIGHT=1003,
        A=65,
        D=68,
        E=69,
        F=70,
        P=80,
        V=86,
        SPACE=32,
        ENTER=13,
        RETURN=13,
        ESCAPE=27,
        MOD_SHIFT=1,
        MOD_CTRL=2,
    ),
    color=types.SimpleNamespace(
        WHITE=(255, 255, 255),
        AQUA=(0, 255, 255),
        LIGHT_GRAY=(200, 200, 200),
        YELLOW=(255, 255, 0),
        DARK_RED=(100, 0, 0),
        GREEN=(0, 255, 0),
        RED=(255, 0, 0),
    ),
    draw_text=lambda *args, **kwargs: None,
    draw_lrbt_rectangle_filled=lambda *args, **kwargs: None,
    draw_lrbt_rectangle_outline=lambda *args, **kwargs: None,
    draw_rect_outline=lambda *args, **kwargs: None,
    draw_line=lambda *args, **kwargs: None,
    draw_texture_rect=lambda *args, **kwargs: None,
    Camera2D=lambda *args, **kwargs: None,
    SpriteList=lambda: types.SimpleNamespace(
        draw=lambda: None,
        append=lambda s: None,
        __iter__=lambda self: iter([]),
        __len__=lambda self: 0,
    ),
    Sprite=lambda *args, **kwargs: types.SimpleNamespace(
        kill=lambda: None,
        center_x=0, center_y=0, width=32, height=32, visible=True,
    ),
    LBWH=lambda *args, **kwargs: None,
    load_texture=lambda *args, **kwargs: None,
    draw_circle_outline=lambda *args, **kwargs: None,
    draw_circle_filled=lambda *args, **kwargs: None,
)
sys.modules.setdefault("arcade", fake_arcade)

from game.character import Character
from game.gamestate import GameState
from game.mission_templates import MissionTemplate
from game.recruitment import recruit_agent
from game import views


class _FakeWindow:
    def __init__(self):
        self.shown_view = None
        self.height = 720
        self.width = 1280

    def show_view(self, view):
        self.shown_view = view


def _mission(
    mission_id="stress_gate",
    title="Relay Burn",
    risk_level=3,
    objective_text="Burn the relay before the city notices.",
    district="Chrome Warrens",
):
    return MissionTemplate(
        id=mission_id,
        title=title,
        objective_text=objective_text,
        target_faction="Test Faction",
        district=district,
        district_pressure={},
        starting_enemy_count=1,
        risk_level=risk_level,
    )


class _FakeBattleView:
    def __init__(self, game_state):
        self.game_state = game_state
        self.mission = None
        self.setup_called = False

    def setup(self, mission):
        self.mission = mission
        self.setup_called = True


class RPGViewMissionLaunchTest(unittest.TestCase):
    def test_launch_without_agents_sets_message_and_keeps_rpg_view(self):
        game_state = GameState()
        view = views.RPGView(game_state)
        view.window = _FakeWindow()
        view.setup()

        view.on_key_press(views.arcade.key.B, None)

        self.assertIsNone(view.window.shown_view)
        self.assertIsNone(game_state.active_mission)
        self.assertEqual(
            view.message,
            "Recruit at least one deployable agent before launching an operation.",
        )

    def test_launch_with_only_recovering_agent_sets_message(self):
        game_state = GameState(characters=[Character("Wounded", recovery_turns=2)])
        view = views.RPGView(game_state)
        view.window = _FakeWindow()
        view.setup()

        view.on_key_press(views.arcade.key.B, None)

        self.assertIsNone(view.window.shown_view)
        self.assertIsNone(game_state.active_mission)
        self.assertEqual(
            view.message,
            "Recruit at least one deployable agent before launching an operation.",
        )

    def test_rpg_view_uses_graphical_state_instead_of_recovery_text(self):
        drawn_text = []
        original_draw_text = views.arcade.draw_text
        views.arcade.draw_text = lambda text, *args, **kwargs: drawn_text.append(text)
        game_state = GameState(characters=[Character("Wounded", recovery_turns=3)])
        view = views.RPGView(game_state)
        view.window = _FakeWindow()
        view.setup()
        try:
            view.on_draw()
        finally:
            views.arcade.draw_text = original_draw_text

        self.assertFalse(any("RECOVERING" in text.upper() for text in drawn_text))

    def test_rpg_view_shows_selection_as_graphical_state_not_text(self):
        drawn_text = []
        original_draw_text = views.arcade.draw_text
        views.arcade.draw_text = lambda text, *args, **kwargs: drawn_text.append(text)
        game_state = GameState(
            characters=[Character("Marked")], selected_agent_names=["Marked"]
        )
        view = views.RPGView(game_state)
        view.window = _FakeWindow()
        view.setup()
        try:
            view.on_draw()
        finally:
            views.arcade.draw_text = original_draw_text

        self.assertFalse(any("SELECT" in text.upper() for text in drawn_text))

    def test_management_views_draw_graphical_surfaces_without_text(self):
        drawn_text = []
        original_draw_text = views.arcade.draw_text
        views.arcade.draw_text = lambda text, *args, **kwargs: drawn_text.append(text)
        game_state = GameState()
        corp_view = views.CorpView(game_state)
        corp_view.window = _FakeWindow()
        corp_view.setup()
        city_view = views.CityView(game_state)
        city_view.window = _FakeWindow()
        city_view.setup()
        try:
            corp_view.on_draw()
            city_view.on_draw()
        finally:
            views.arcade.draw_text = original_draw_text

        allowed = {"FUNDS", "CREDITS", "INTEL", "SALVAGE", "INFLUENCE"}
        unexpected = [
            text
            for text in drawn_text
            if text not in allowed
            and not text.isdigit()
            and not text.startswith(("¥", "Ą"))
        ]
        self.assertEqual(unexpected, [])

    def test_battle_view_setup_auto_selects_map(self):
        """BattleView must auto-select a map on setup (no manual pick screen)."""
        game_state = GameState(mission_templates=[_mission()])
        view = views.BattleView(game_state)
        view.window = _FakeWindow()
        view.setup(game_state.mission_templates[0])
        # Auto-selection: map_index must not be None after setup
        self.assertIsNotNone(view.map_index)
        self.assertIsInstance(view.map_index, int)

    def test_battle_view_uses_city_and_wasteland_map_pools(self):
        city_game_state = GameState(mission_templates=[_mission()])
        city_view = views.BattleView(city_game_state)
        city_view.window = _FakeWindow()
        city_view.setup(city_game_state.mission_templates[0])

        wasteland_mission = _mission(
            mission_id="badlands_scout",
            title="Badlands Survey",
            objective_text="Recover the drone core from the wasteland",
            district="Badlands Fringe",
        )
        wasteland_game_state = GameState(mission_templates=[wasteland_mission])
        wasteland_view = views.BattleView(wasteland_game_state)
        wasteland_view.window = _FakeWindow()
        wasteland_view.setup(wasteland_mission)

        self.assertTrue(Path(city_view.map_path).name.startswith("city_"))
        self.assertFalse(Path(wasteland_view.map_path).name.startswith("city_"))

    def test_battle_view_scales_robot_tokens_full_size_and_other_units_half_size(self):
        scales = []
        original_sprite = views.arcade.Sprite

        def _capture_sprite(*args, **kwargs):
            scales.append(kwargs.get("scale"))
            return types.SimpleNamespace(
                kill=lambda: None,
                center_x=0,
                center_y=0,
                width=32,
                height=32,
                visible=True,
            )

        views.arcade.Sprite = _capture_sprite
        try:
            game_state = GameState(
                characters=[Character("Alpha")],
                selected_agent_names=["Alpha"],
                spec_ops_assets=default_spec_ops_assets(),
                selected_asset_ids=["robot_k9_01"],
                mission_templates=[_mission()],
            )
            view = views.BattleView(game_state)
            view.window = _FakeWindow()
            view.setup(game_state.mission_templates[0])
        finally:
            views.arcade.Sprite = original_sprite

        self.assertIn(0.75, scales)
        self.assertIn(1.5, scales)

    def test_invisible_enemies_are_not_targetable(self):
        game_state = GameState(
            characters=[Character("Ghost", role="sniper")],
            selected_agent_names=["Ghost"],
            mission_templates=[_mission()],
        )
        view = views.BattleView(game_state)
        view.window = _FakeWindow()
        view.setup(game_state.mission_templates[0])

        player = view.player_units[0]
        for enemy in view.enemy_units:
            enemy.visible = False
            enemy.position = (player.position[0] + 32, player.position[1])

        view._begin_target_action(player, "fire")

        self.assertFalse(view.selecting_target)
        self.assertEqual(view.target_candidates, [])
        self.assertEqual(view.message, "No visible enemy in range")

    def test_rpg_room_click_recruits_from_icon_button(self):
        from game.ui.facility import build_facility_rooms, facility_room_by_key

        game_state = GameState()
        view = views.RPGView(game_state)
        view.window = _FakeWindow()
        view.setup()
        barracks = facility_room_by_key(
            build_facility_rooms(view.window.width, view.window.height, "squad"),
            "barracks",
        )

        view.on_mouse_press(
            barracks.left + barracks.width // 2,
            barracks.bottom + barracks.height // 2,
            None,
            None,
        )
        recruit_button = view.room_ui.action_buttons[0].rect
        view.on_mouse_press(
            recruit_button.center_x, recruit_button.center_y, None, None
        )

        self.assertEqual(len(game_state.characters), 1)
        self.assertLess(game_state.budget_pool, game_state.compute_budget())

    def test_expanded_room_draws_title_and_room_info(self):
        from game.ui.facility import build_facility_rooms, facility_room_by_key

        drawn_text = []
        original_draw_text = views.arcade.draw_text
        views.arcade.draw_text = lambda text, *args, **kwargs: drawn_text.append(text)
        game_state = GameState()
        view = views.CorpView(game_state)
        view.window = _FakeWindow()
        view.setup()
        room = facility_room_by_key(
            build_facility_rooms(view.window.width, view.window.height, "corp"),
            "research",
        )
        view.on_mouse_press(
            room.left + room.width // 2,
            room.bottom + room.height // 2,
            None,
            None,
        )
        view.on_update(0.25)
        try:
            view.on_draw()
        finally:
            views.arcade.draw_text = original_draw_text

        self.assertIn("RESEARCH LAB", drawn_text)
        self.assertTrue(any("Intel reserve" in text for text in drawn_text))
        self.assertIn("FUND RESEARCH", drawn_text)

    def test_black_ops_room_can_recruit_agents(self):
        from game.ui.facility import build_facility_rooms, facility_room_by_key

        game_state = GameState()
        view = views.CorpView(game_state)
        view.window = _FakeWindow()
        view.setup()
        room = facility_room_by_key(
            build_facility_rooms(view.window.width, view.window.height, "corp"),
            "black_ops",
        )
        view.on_mouse_press(
            room.left + room.width // 2,
            room.bottom + room.height // 2,
            None,
            None,
        )
        recruit_button = next(
            button
            for button in view.room_ui.action_buttons
            if button.action.key == "recruit_sniper"
        ).rect

        view.on_mouse_press(recruit_button.center_x, recruit_button.center_y, None, None)

        self.assertEqual(len(game_state.characters), 1)
        self.assertEqual(game_state.characters[0].role, "sniper")

    def test_armory_room_can_spend_level_up_points(self):
        from game.ui.facility import build_facility_rooms, facility_room_by_key

        agent = Character("Leveler", pending_points=1)
        game_state = GameState(characters=[agent])
        view = views.RPGView(game_state)
        view.window = _FakeWindow()
        view.setup()
        room = facility_room_by_key(
            build_facility_rooms(view.window.width, view.window.height, "squad"),
            "armory",
        )
        view.on_mouse_press(
            room.left + room.width // 2,
            room.bottom + room.height // 2,
            None,
            None,
        )
        str_before = agent.stats.str
        level_button = next(
            button
            for button in view.room_ui.action_buttons
            if button.action.key == "level_str"
        ).rect

        view.on_mouse_press(level_button.center_x, level_button.center_y, None, None)

        self.assertEqual(agent.stats.str, str_before + 1)
        self.assertEqual(agent.pending_points, 0)


    def test_armory_room_option_b_spends_one_point_and_adds_two_skill_ranks(self):
        from game.ui.facility import build_facility_rooms, facility_room_by_key

        agent = Character("Leveler", pending_points=1)
        game_state = GameState(characters=[agent])
        view = views.RPGView(game_state)
        view.window = _FakeWindow()
        view.setup()
        room = facility_room_by_key(
            build_facility_rooms(view.window.width, view.window.height, "squad"),
            "armory",
        )
        view.on_mouse_press(room.left + room.width // 2, room.bottom + room.height // 2, None, None)
        before = dict(agent.skills)
        b_button = next(button for button in view.room_ui.action_buttons if button.action.key == "skillup_auto").rect

        view.on_mouse_press(b_button.center_x, b_button.center_y, None, None)

        self.assertEqual(agent.pending_points, 0)
        gained = sum(max(0, agent.skills.get(k, 0) - before.get(k, 0)) for k in before)
        self.assertEqual(gained, 2)

    def test_insertion_room_launches_selected_mission(self):
        from game.ui.facility import build_facility_rooms, facility_room_by_key

        game_state = GameState(characters=[Character("Ready")])
        view = views.RPGView(game_state)
        view.window = _FakeWindow()
        view.setup()
        game_state.selected_agent_names = ["Ready"]
        room = facility_room_by_key(
            build_facility_rooms(view.window.width, view.window.height, "squad"),
            "insertion",
        )
        view.on_mouse_press(
            room.left + room.width // 2,
            room.bottom + room.height // 2,
            None,
            None,
        )
        launch_button = view.room_ui.action_buttons[0].rect
        original_battle_view = views.BattleView
        views.BattleView = _FakeBattleView
        try:
            view.on_mouse_press(
                launch_button.center_x, launch_button.center_y, None, None
            )
        finally:
            views.BattleView = original_battle_view

        self.assertIsInstance(view.window.shown_view, _FakeBattleView)
        self.assertIs(view.window.shown_view.mission, game_state.active_mission)

    def test_squad_room_displays_graphical_roster_cards(self):
        from game.ui.facility import build_facility_rooms, facility_room_by_key

        drawn_text = []
        original_draw_text = views.arcade.draw_text
        views.arcade.draw_text = lambda text, *args, **kwargs: drawn_text.append(text)
        game_state = GameState(
            characters=[
                Character("Vega", role="sniper"),
                Character("Knox", role="samurai", pending_points=2),
            ],
            selected_agent_names=["Vega"],
        )
        view = views.RPGView(game_state)
        view.window = _FakeWindow()
        view.setup()
        room = facility_room_by_key(
            build_facility_rooms(view.window.width, view.window.height, "squad"),
            "barracks",
        )
        view.on_mouse_press(
            room.left + room.width // 2,
            room.bottom + room.height // 2,
            None,
            None,
        )
        view.on_update(0.25)
        try:
            view.on_draw()
        finally:
            views.arcade.draw_text = original_draw_text

        self.assertIn("VEGA", drawn_text)
        self.assertIn("KNOX", drawn_text)
        self.assertIn("SNIPER", drawn_text)
        self.assertIn("SAMURAI", drawn_text)

    def test_roster_cards_have_active_state_and_portrait_assets(self):
        cards = views.build_roster_cards(
            [Character("Vega", role="sniper"), Character("Knox", role="samurai")],
            ["Vega"],
            cursor_index=1,
        )

        self.assertFalse(cards[0]["active"])
        self.assertTrue(cards[0]["selected"])
        self.assertTrue(cards[1]["active"])
        self.assertFalse(cards[1]["selected"])
        for card in cards:
            self.assertTrue(Path(card["portrait_path"]).exists())

    def test_clicking_roster_card_changes_active_agent(self):
        from game.ui.facility import build_facility_rooms, facility_room_by_key
        from game.ui.room_interaction import active_room_rect, layout_roster_card_rects

        game_state = GameState(
            characters=[Character("Vega", role="sniper"), Character("Knox", role="samurai")]
        )
        view = views.RPGView(game_state)
        view.window = _FakeWindow()
        view.setup()
        room = facility_room_by_key(
            build_facility_rooms(view.window.width, view.window.height, "squad"),
            "barracks",
        )
        view.on_mouse_press(
            room.left + room.width // 2,
            room.bottom + room.height // 2,
            None,
            None,
        )
        view.on_update(0.25)
        active = active_room_rect(view.room_ui, view.window.width, view.window.height)
        self.assertIsNotNone(active)
        _, expanded_rect = active
        card_rects = layout_roster_card_rects(
            expanded_rect, view.room_ui.action_buttons, len(game_state.characters)
        )

        view.on_mouse_press(
            card_rects[1].center_x, card_rects[1].center_y, None, None
        )

        self.assertEqual(view.deployment_cursor_index, 1)

    def test_armory_room_can_remove_active_agent_from_roster(self):
        from game.ui.facility import build_facility_rooms, facility_room_by_key

        game_state = GameState(
            characters=[Character("Vega", role="sniper"), Character("Knox", role="samurai")]
        )
        view = views.RPGView(game_state)
        view.window = _FakeWindow()
        view.setup()
        room = facility_room_by_key(
            build_facility_rooms(view.window.width, view.window.height, "squad"),
            "armory",
        )
        view.on_mouse_press(
            room.left + room.width // 2,
            room.bottom + room.height // 2,
            None,
            None,
        )
        remove_button = next(
            button for button in view.room_ui.action_buttons if button.action.key == "remove_agent"
        ).rect
        removed_name = game_state.characters[0].name

        view.on_mouse_press(remove_button.center_x, remove_button.center_y, None, None)

        self.assertEqual(len(game_state.characters), 1)
        self.assertNotIn(removed_name, {character.name for character in game_state.characters})

    def test_leveling_room_displays_remaining_points(self):
        from game.ui.facility import build_facility_rooms, facility_room_by_key

        drawn_text = []
        original_draw_text = views.arcade.draw_text
        views.arcade.draw_text = lambda text, *args, **kwargs: drawn_text.append(text)
        game_state = GameState(characters=[Character("Knox", pending_points=3)])
        view = views.RPGView(game_state)
        view.window = _FakeWindow()
        view.setup()
        room = facility_room_by_key(
            build_facility_rooms(view.window.width, view.window.height, "squad"),
            "armory",
        )
        view.on_mouse_press(
            room.left + room.width // 2,
            room.bottom + room.height // 2,
            None,
            None,
        )
        view.on_update(0.25)
        try:
            view.on_draw()
        finally:
            views.arcade.draw_text = original_draw_text

        self.assertTrue(any("Upgrade points 3" in text for text in drawn_text))
        self.assertTrue(any(text.startswith("A: +1 STR") for text in drawn_text))
        self.assertTrue(any(text.startswith("B: +2 SKILLS") for text in drawn_text))
        self.assertIn("PTS 3", drawn_text)

    def test_pending_upgrade_roster_card_uses_valid_rectangles(self):
        from game.ui import panels
        from game.ui.facility import build_facility_rooms, facility_room_by_key

        original_draw_rect = panels.arcade.draw_lrbt_rectangle_filled

        def validate_rect(left, right, bottom, top, *args, **kwargs):
            self.assertLessEqual(left, right)
            self.assertLessEqual(bottom, top)

        panels.arcade.draw_lrbt_rectangle_filled = validate_rect
        game_state = GameState(characters=[Character("Knox", pending_points=1)])
        view = views.RPGView(game_state)
        view.window = _FakeWindow()
        view.setup()
        room = facility_room_by_key(
            build_facility_rooms(view.window.width, view.window.height, "squad"),
            "barracks",
        )
        view.on_mouse_press(
            room.left + room.width // 2,
            room.bottom + room.height // 2,
            None,
            None,
        )
        view.on_update(0.25)
        try:
            view.on_draw()
        finally:
            panels.arcade.draw_lrbt_rectangle_filled = original_draw_rect

    def test_escape_closes_expanded_room_before_navigation(self):
        from game.ui.facility import build_facility_rooms, facility_room_by_key

        game_state = GameState()
        view = views.CorpView(game_state)
        view.window = _FakeWindow()
        view.setup()
        room = facility_room_by_key(
            build_facility_rooms(view.window.width, view.window.height, "corp"),
            "research",
        )
        view.on_mouse_press(
            room.left + room.width // 2,
            room.bottom + room.height // 2,
            None,
            None,
        )

        view.on_key_press(views.arcade.key.ESCAPE, None)

        self.assertFalse(view.room_ui.is_open)
        self.assertIsNone(view.window.shown_view)

    def test_launch_with_agents_but_none_selected_sets_selection_message(self):
        game_state = GameState(
            characters=[Character("Calm", stress=40)],
            mission_templates=[_mission()],
        )
        view = views.RPGView(game_state)
        view.window = _FakeWindow()
        view.setup()

        view.on_key_press(views.arcade.key.B, None)

        self.assertIsNone(view.window.shown_view)
        self.assertIsNone(game_state.active_mission)
        self.assertEqual(
            view.message,
            "Select at least one deployable agent before launching an operation.",
        )

    def test_recovering_agent_cannot_be_selected_for_launch(self):
        game_state = GameState(
            characters=[Character("Wounded", recovery_turns=2)],
            selected_agent_names=["Wounded"],
            mission_templates=[_mission()],
        )
        view = views.RPGView(game_state)
        view.window = _FakeWindow()
        view.setup()

        view.on_key_press(views.arcade.key.ENTER, None)
        view.on_key_press(views.arcade.key.B, None)

        self.assertEqual(game_state.selected_agent_names, [])
        self.assertIsNone(view.window.shown_view)
        self.assertIsNone(game_state.active_mission)
        self.assertEqual(
            view.message,
            "Recruit at least one deployable agent before launching an operation.",
        )

    def test_stable_agent_launches_without_breakdown_confirmation(self):
        game_state = GameState(
            characters=[Character("Calm", stress=40)],
            mission_templates=[_mission()],
        )
        view = views.RPGView(game_state)
        view.window = _FakeWindow()
        view.setup()
        original_battle_view = views.BattleView
        views.BattleView = _FakeBattleView
        try:
            view.on_key_press(views.arcade.key.ENTER, None)
            view.on_key_press(views.arcade.key.B, None)
        finally:
            views.BattleView = original_battle_view

        self.assertIsInstance(view.window.shown_view, _FakeBattleView)
        self.assertFalse(view.pending_breakdown_confirmation)
        self.assertFalse(
            any("Command forced" in event for event in game_state.event_log)
        )

    def test_breaking_risk_blocks_first_launch_attempt_with_warning(self):
        game_state = GameState(
            characters=[Character("Ghost", stress=80)],
            selected_agent_names=["Ghost"],
            mission_templates=[_mission()],
        )
        view = views.RPGView(game_state)
        view.window = _FakeWindow()
        view.setup()

        view.on_key_press(views.arcade.key.B, None)

        self.assertIsNone(view.window.shown_view)
        self.assertIsNone(game_state.active_mission)
        self.assertTrue(view.pending_breakdown_confirmation)
        self.assertEqual(view.pending_breakdown_mission_id, "stress_gate")
        self.assertEqual(
            view.message,
            "Ghost is at breakdown risk. Press B again to force deployment.",
        )

    def test_second_breaking_risk_launch_attempt_proceeds_and_logs_event(self):
        game_state = GameState(
            characters=[Character("Ghost", stress=80)],
            selected_agent_names=["Ghost"],
            mission_templates=[_mission()],
        )
        view = views.RPGView(game_state)
        view.window = _FakeWindow()
        view.setup()
        original_battle_view = views.BattleView
        views.BattleView = _FakeBattleView
        try:
            view.on_key_press(views.arcade.key.B, None)
            view.on_key_press(views.arcade.key.B, None)
        finally:
            views.BattleView = original_battle_view

        self.assertIsInstance(view.window.shown_view, _FakeBattleView)
        self.assertIs(view.window.shown_view.mission, game_state.active_mission)
        self.assertFalse(view.pending_breakdown_confirmation)
        self.assertTrue(
            any(
                "Command forced Ghost into Relay Burn despite breakdown risk." in event
                for event in game_state.event_log
            )
        )

    def test_breaking_confirmation_only_applies_to_same_selected_mission(self):
        game_state = GameState(
            characters=[Character("Ghost", stress=80)],
            selected_agent_names=["Ghost"],
            mission_templates=[
                _mission("relay_burn", "Relay Burn"),
                _mission("black_ice", "Black Ice Sweep"),
            ],
        )
        view = views.RPGView(game_state)
        view.window = _FakeWindow()
        view.setup()

        view.on_key_press(views.arcade.key.B, None)
        view.on_key_press(views.arcade.key.KEY_2, None)
        view.on_key_press(views.arcade.key.B, None)

        self.assertIsNone(view.window.shown_view)
        self.assertIsNone(game_state.active_mission)
        self.assertTrue(view.pending_breakdown_confirmation)
        self.assertEqual(view.pending_breakdown_mission_id, "black_ice")

    def test_breakdown_warning_only_checks_selected_agents(self):
        risky = Character("Ghost", stress=80)
        calm = Character("Calm", stress=10)
        game_state = GameState(
            characters=[risky, calm],
            selected_agent_names=["Calm"],
            mission_templates=[_mission()],
        )
        view = views.RPGView(game_state)
        view.window = _FakeWindow()
        view.setup()
        original_battle_view = views.BattleView
        views.BattleView = _FakeBattleView
        try:
            view.on_key_press(views.arcade.key.B, None)
        finally:
            views.BattleView = original_battle_view

        self.assertIsInstance(view.window.shown_view, _FakeBattleView)
        self.assertFalse(view.pending_breakdown_confirmation)
        self.assertFalse(
            any("Command forced Ghost" in event for event in game_state.event_log)
        )

    def test_recruit_then_launches_selected_mission(self):
        game_state = GameState()
        recruit_agent(game_state.characters, "samurai")
        view = views.RPGView(game_state)
        view.window = _FakeWindow()
        view.setup()
        original_battle_view = views.BattleView
        views.BattleView = _FakeBattleView
        try:
            view.on_key_press(views.arcade.key.ENTER, None)
            view.on_key_press(views.arcade.key.B, None)
        finally:
            views.BattleView = original_battle_view

        self.assertIsInstance(view.window.shown_view, _FakeBattleView)
        self.assertTrue(view.window.shown_view.setup_called)
        self.assertIs(view.window.shown_view.mission, game_state.active_mission)


if __name__ == "__main__":
    unittest.main()
