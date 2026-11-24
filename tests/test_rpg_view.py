"""RPG view mission launch guards."""

import sys
import tempfile
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
    def test_pointer_move_previews_then_executes_two_real_grid_steps(self):
        from unittest.mock import Mock
        from types import SimpleNamespace
        from game.combat import CombatEngine, CombatState
        from game.unit import Unit
        from game.stats import PlayerStats, EnemyStats
        actor=Unit(position=(64,64),stats=PlayerStats())
        enemy=Unit(position=(640,400),stats=EnemyStats(),unit_type="enemy")
        view=views.BattleView.__new__(views.BattleView)
        view.window=SimpleNamespace(width=1280,height=720)
        view.player_units=[actor]
        view.enemy_units=[enemy]
        view.combat_state=CombatState(None,[actor],[enemy])
        view.combat_engine=CombatEngine(view.combat_state)
        view.game_state=SimpleNamespace(mark_tutorial_event=Mock())
        view._pointer_camera_offset=(64,64)
        view._pointer_moving=True
        view.can_move_to=lambda x,y,exclude=None: True
        for name in ("_sync_view_from_combat_state","_set_action_aftermath","_log_move","check_active_player"):
            setattr(view,name,Mock())
        view._handle_pointer_move(actor,64,0)
        self.assertEqual(actor.position,(64,64))
        self.assertEqual(actor.action_points,2)
        self.assertEqual(view._pointer_move_path,[(64,64),(96,64),(128,64)])
        view._handle_pointer_move(actor,64,0)
        self.assertEqual(actor.position,(128,64))
        self.assertEqual(actor.action_points,0)
        self.assertFalse(view._pointer_moving)
        view.check_active_player.assert_called_once()

    def test_pointer_move_does_not_commit_an_unreachable_or_newly_blocked_path(self):
        from unittest.mock import Mock
        from types import SimpleNamespace
        from game.combat import CombatEngine, CombatState
        from game.unit import Unit
        actor=Unit(position=(64,64))
        view=views.BattleView.__new__(views.BattleView)
        view.window=SimpleNamespace(width=1280,height=720)
        view.player_units=[actor]
        view.enemy_units=[]
        view.combat_state=CombatState(None,[actor],[])
        view.combat_engine=CombatEngine(view.combat_state)
        view._pointer_moving=True
        view.can_move_to=lambda x,y,exclude=None: True
        view._try_move_active_player=Mock()
        view._handle_pointer_move(actor,128,64)
        view.can_move_to=lambda x,y,exclude=None: (x,y)!=(96,64)
        view._handle_pointer_move(actor,128,64)
        view._try_move_active_player.assert_not_called()
        self.assertIsNone(view._pointer_move_path)
        self.assertEqual(actor.action_points,2)

    def test_mouse_target_selection_requires_second_click_and_right_click_cancels(self):
        from unittest.mock import Mock
        from types import SimpleNamespace
        from game.unit import Unit
        actor=Unit(position=(64,64))
        target=Unit(position=(480,384))
        view=views.BattleView.__new__(views.BattleView)
        for key,value in dict(map_index=0,_paused=False,pending_end_turn_confirmation=False,
                              turn="player",player_units=[actor],active_index=0,combat_action_buttons=[],
                              selecting_target=True,target_candidates=[target],selected_target_idx=0,
                              _deploying=False,_pointer_camera_offset=(64,32)).items():
            setattr(view,key,value)
        view.window=SimpleNamespace(width=1280,height=720)
        view.on_key_press=Mock()
        view.on_mouse_press(416,352,1,0)
        view.on_key_press.assert_not_called()
        self.assertEqual(view.last_input_mode,"keyboard_mouse")
        view.on_mouse_press(416,352,1,0)
        view.on_key_press.assert_called_once_with(views.arcade.key.ENTER,0)
        view.on_key_press.reset_mock()
        view.on_mouse_press(416,352,4,0)
        view.on_key_press.assert_called_once_with(views.arcade.key.ESCAPE,0)
        view.on_key_press.reset_mock()
        view._show_combat_log=True
        view._pointer_camera_offset=(0,0)
        target.position=(1100,260)  # The visible target-lock panel blocks input.
        view.on_mouse_press(1100,260,1,0)
        view.on_mouse_press(1100,260,1,0)
        view.on_key_press.assert_not_called()
        self.assertIsNone(view._mouse_selected_target)
        target.position=(1100,350)  # The journal is hidden during targeting.
        view.on_mouse_press(1100,350,1,0)
        view.on_mouse_press(1100,350,1,0)
        view.on_key_press.assert_called_once_with(views.arcade.key.ENTER,0)

    def test_first_aid_opens_allied_selection_without_spending_ap(self):
        from types import SimpleNamespace
        from game.unit import Unit
        medic_char=Character("Echo",role="medic")
        patient_char=Character("Rook")
        medic=Unit(position=(0,0),stats=medic_char.stats,character=medic_char)
        medic.health=medic.stats.max_hp
        patient=Unit(position=(32,0),stats=patient_char.stats,character=patient_char)
        patient.health=1
        view=views.BattleView.__new__(views.BattleView)
        view.turn="player"
        view.player_units=[medic,patient]
        view.active_index=0
        before=medic.action_points
        self.assertTrue(view._perform_combat_action("first_aid"))
        self.assertEqual(view.target_candidates,[patient])
        self.assertTrue(view.selecting_target)
        self.assertEqual(view.pending_attack,"first_aid")
        self.assertEqual(medic.action_points,before)
        from unittest.mock import Mock
        from game.combat import CombatEngine, CombatState
        from game.stats import EnemyStats
        enemy=Unit(position=(256,0),stats=EnemyStats(),unit_type="enemy")
        view.combat_engine=CombatEngine(CombatState(None,[medic,patient],[enemy]))
        for name in ("_sync_view_from_combat_state","_add_healing_popup","_spawn_particles",
                     "_flash_unit","_set_action_aftermath","check_active_player"):
            setattr(view,name,Mock())
        view._treat_selected_ally(medic,patient)
        self.assertEqual(patient.health,3)
        self.assertEqual(medic.action_points,before-1)
        self.assertFalse(view.selecting_target)
        view._add_healing_popup.assert_called_once_with(patient,2)

    def test_roster_displays_incurable_countdown_and_converted_dossier(self):
        char = Character("Rook")
        char.starver_infection_days = 2
        card = views.build_roster_cards([char], [char.name])[0]
        self.assertIn("INCURABLE", card["infection_status"])
        self.assertIn("2d", card["infection_status"])
        from game.starver_infection import advance_infection
        advance_infection(char)
        advance_infection(char)
        card = views.build_roster_cards([char], [])[0]
        self.assertEqual(card["role"], "starver")
        self.assertIn("LOST TO THE SQUAD", card["infection_status"])

    def test_godot_child_exit_shows_error_without_switching_engine(self):
        from unittest.mock import Mock, patch
        from game.ui.screens.godot_combat_handoff_view import GodotCombatHandoffView
        process = Mock()
        process.poll.return_value = 1
        launch = types.SimpleNamespace(process=process, process_pid=123)
        bridge = GodotCombatHandoffView(GameState(), _mission(), launch, window=_FakeWindow())
        bridge._cleanup_godot = Mock()
        bridge._fallback_to_arcade_battle = Mock()
        with patch("game.combat.godot_bridge.read_godot_combat_result", return_value=None):
            bridge.on_update(0.3)
            bridge.on_update(0.3)
        bridge._cleanup_godot.assert_called_once()
        bridge._fallback_to_arcade_battle.assert_not_called()
        self.assertTrue(bridge._launch_failed)

    def test_godot_result_before_overlay_is_applied_once_without_relaunch(self):
        from unittest.mock import Mock, patch
        from game.ui.screens.godot_combat_handoff_view import GodotCombatHandoffView
        process = Mock()
        process.poll.return_value = 0
        bridge = GodotCombatHandoffView(GameState(), _mission(), types.SimpleNamespace(process=process, process_pid=123), window=_FakeWindow())
        bridge._cleanup_godot = Mock()
        bridge._apply_combat_result = Mock()
        bridge._fallback_to_arcade_battle = Mock()
        result = {"outcome": "defeat", "funds_earned": 0}
        with tempfile.TemporaryDirectory() as folder:
            bridge.launch_result.result_path = Path(folder) / "result.json"
            bridge.launch_result.result_path.write_text("{}", encoding="utf-8")
            def mark_applied(_result):
                bridge._result_applied = True
            bridge._apply_combat_result.side_effect = mark_applied
            with patch("game.combat.godot_bridge.read_godot_combat_result", return_value=result):
                bridge.on_update(0.3)
                bridge.on_update(0.3)
        bridge._apply_combat_result.assert_called_once_with(result)
        bridge._fallback_to_arcade_battle.assert_not_called()

    def test_new_campaign_routes_to_godot(self):
        from unittest.mock import patch
        state = GameState(characters=[Character("Ready")], selected_agent_names=["Ready"], mission_templates=[_mission()])
        self.assertEqual(state.combat_mission_ui_engine, "godot")
        view = views.RPGView(state)
        view.window = _FakeWindow()
        view.setup()
        launch = types.SimpleNamespace(launched=True,message="Godot started",process=None,process_pid=None)
        with patch.object(views, "BattleView", _FakeBattleView), patch("game.combat.godot_bridge.launch_godot_combat_ui", return_value=launch) as process:
            view.launch_selected_mission()
        process.assert_called_once()
        self.assertIs(view.window.shown_view.mission, state.active_mission)

    def test_godot_failure_stays_on_error_view_without_applying_rewards(self):
        from unittest.mock import patch
        state = GameState(characters=[Character("Ready")], selected_agent_names=["Ready"], mission_templates=[_mission()])
        state.combat_mission_ui_engine = "godot"
        view = views.RPGView(state)
        view.window = _FakeWindow()
        view.setup()
        failure = types.SimpleNamespace(launched=False, message="unavailable")
        with patch.object(views, "BattleView", _FakeBattleView), patch("game.combat.godot_bridge.launch_godot_combat_ui", return_value=failure):
            view.launch_selected_mission()
        self.assertTrue(view.window.shown_view._launch_failed)
        self.assertEqual(state.combat_mission_ui_engine, "godot")

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
            and not text.startswith(("₦", "¥", "Ą"))
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

        self.assertTrue(Path(city_view.map_path).name.startswith(("city_", "cybercity_")))
        self.assertTrue(Path(wasteland_view.map_path).name.startswith("wasteland_"))

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

        self.assertEqual(len(scales), 3)
        infantry, robot, enemy = scales
        self.assertAlmostEqual(infantry, enemy)
        self.assertAlmostEqual(robot, 2 * infantry)

    def test_battle_view_starts_in_deployment_until_confirmed(self):
        game_state = GameState(
            characters=[Character("Alpha")],
            selected_agent_names=["Alpha"],
            mission_templates=[_mission()],
        )
        view = views.BattleView(game_state)
        view.window = _FakeWindow()
        view.setup(game_state.mission_templates[0])

        self.assertTrue(view._deploying)
        self.assertEqual(view.combat_state.logs, [])
        self.assertIn("Deployment phase", view.message)
        for enemy in view.enemy_units:
            enemy.sprite.visible = True
        self.assertEqual(view.enemy_units_visible_for_render(), [])
        self.assertTrue(all(not enemy.sprite.visible for enemy in view.enemy_units))

        view._handle_deployment_key(views.arcade.key.ENTER)

        self.assertFalse(view._deploying)
        self.assertTrue(any("Turn 1" in line for line in view.combat_state.logs))
        self.assertEqual(view.message, "Squad deployed. Combat begins.")
        self.assertEqual(view.enemy_units_visible_for_render(), view.enemy_units)

    def test_authored_interior_map_refits_units_sprites_and_deployment_without_wall_holes(self):
        from game.battle_maps import build_battle_map_catalog
        from unittest.mock import patch
        entry = next(e for e in build_battle_map_catalog() if e.filename == "cybercity_inner_02_safehouse.png")
        state = GameState(characters=[Character("Alpha")], selected_agent_names=["Alpha"], mission_templates=[_mission()])
        view = views.BattleView(state)
        view.window = _FakeWindow()
        with patch.object(views, "battle_map_pool_for_mission", return_value=[entry]), patch.object(views, "select_battle_map_entry", return_value=entry):
            view.setup(state.mission_templates[0])
        self.assertEqual(view.terrain_profile.source, "manual_wall_traces_v1")
        self.assertGreater(min(y for x, y in view._deployment_cells), 112)
        for unit in view.player_units + view.enemy_units:
            self.assertTrue(view.terrain_profile.is_walkable(*unit.position))
            self.assertEqual((unit.sprite.center_x, unit.sprite.center_y), unit.position)
        self.assertFalse(view.combat_state.tactical_flags["access_lanes"])
        self.assertFalse(view.can_deploy_to(640, 352, exclude=view.player_units[0]))
        view._deploying = False
        old_profile = view.terrain_profile
        view._load_battle_map(0)
        self.assertIs(view.terrain_profile, old_profile)
        self.assertIn("deployment only", view.message)

    def test_deployment_repositions_support_assets_and_ignores_hidden_enemies(self):
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
        view._deploy_cursor = 1
        support_unit = view.player_units[1]
        start = support_unit.position
        moves = [(32, 0, views.arcade.key.RIGHT), (-32, 0, views.arcade.key.LEFT),
                 (0, 32, views.arcade.key.UP), (0, -32, views.arcade.key.DOWN)]
        dx, dy, key = next((dx, dy, key) for dx, dy, key in moves
                          if view.can_deploy_to(start[0]+dx, start[1]+dy, exclude=support_unit))
        destination = (start[0]+dx, start[1]+dy)
        for enemy in view.enemy_units:
            enemy.position = destination

        view._handle_deployment_key(key)

        self.assertEqual(support_unit.position, destination)
        self.assertTrue(view.can_deploy_to(*destination, exclude=support_unit))

    def test_combat_popups_cover_damage_healing_miss_and_status(self):
        view = views.BattleView.__new__(views.BattleView)
        view.damage_popups = []
        unit = types.SimpleNamespace(position=(100, 120))

        view._add_damage_popup(unit, 7)
        view._add_damage_popup(unit, 0)
        view._add_healing_popup(unit, 5)
        view._add_status_popup(unit, "suppressed")

        texts = [popup["text"] for popup in view.damage_popups]
        self.assertEqual(texts, ["-7", "MISS", "+5 HP", "SUPPRESSED"])
        self.assertTrue(all(popup["max_age"] <= 1.0 for popup in view.damage_popups))
        self.assertEqual(view.damage_popups[0]["color"], (255, 80, 60))
        self.assertEqual(view.damage_popups[1]["color"], (160, 160, 160))
        self.assertEqual(view.damage_popups[2]["color"], (70, 230, 120))

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
        game_state.combat_mission_ui_engine = "arcade"  # Explicit legacy launch coverage.
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
        game_state.combat_mission_ui_engine = "arcade"  # Explicit legacy launch coverage.
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
        game_state.combat_mission_ui_engine = "arcade"  # Explicit legacy launch coverage.
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
        game_state.combat_mission_ui_engine = "arcade"  # Explicit legacy launch coverage.
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
        game_state.combat_mission_ui_engine = "arcade"  # Explicit legacy launch coverage.
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
