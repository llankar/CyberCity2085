import unittest
from collections import defaultdict

import arcade

from game.ui.screens import battle_hud
from game.stats import EnemyStats, PlayerStats
from game.unit import Unit


captured_draw_text = []
captured_rects = []


def _draw_text(text, *args, **kwargs):
    captured_draw_text.append((text, args, kwargs))


def _draw_lrbt_rectangle_filled(left, right, bottom, top, color):
    captured_rects.append((float(left), float(right), float(bottom), float(top), color))


def _draw_lrbt_rectangle_outline(*args, **kwargs):
    return None


def _draw_rect_outline(*args, **kwargs):
    return None


def _draw_line(*args, **kwargs):
    return None


class _DummyUnit:
    def __init__(self, name, subtype="grunt"):
        self.name = name
        self.subtype = subtype
        self.position = (0, 0)
        self.action_points = 1


class BattleHUDUITest(unittest.TestCase):
    def test_only_incoming_damage_gets_a_thin_low_alpha_edge_cue(self):
        captured_rects.clear()
        battle_hud.draw_attack_flash(960,640,True,160)
        self.assertEqual(captured_rects,[])
        battle_hud.draw_attack_flash(960,640,False,200)
        self.assertEqual(len(captured_rects),4)
        for left,right,bottom,top,color in captured_rects:
            self.assertTrue(right-left == 8 or top-bottom == 8)
            self.assertLessEqual(color[3],60)

    def test_damage_popups_fit_camera_bounds_avoid_labels_and_leave_payloads_unchanged(self):
        from copy import deepcopy
        bounds = (64,-146+218,64+960-8,-146+640-42)
        popups = [{"x":0,"y":90,"text":"CRITICAL! -12","color":(255,60,20),"age":0,"max_age":1.2},
                  {"x":1000,"y":800,"text":"-4","color":(255,60,20),"age":0.4,"max_age":0.8}]
        before = deepcopy(popups)
        boxes = [(100,100,300,140)]
        battle_hud.draw_damage_popups(popups,label_boxes=boxes,label_bounds=bounds)
        self.assertEqual(popups,before)
        self.assertEqual(len(boxes),3)
        for box in boxes[1:]:
            self.assertTrue(bounds[0] <= box[0] < box[2] <= bounds[2])
            self.assertTrue(bounds[1] <= box[1] < box[3] <= bounds[3])
        self.assertEqual([call[0] for call in captured_draw_text],["CRITICAL! -12","-4"])
        captured_draw_text.clear()
        expired = {**popups[0],"age":2}
        battle_hud.draw_damage_popups([expired],label_boxes=boxes,label_bounds=bounds)
        self.assertEqual(captured_draw_text,[])

    def test_enemy_intent_plate_reserves_counterplay_and_avoids_neighbouring_labels(self):
        from types import SimpleNamespace
        from game.combat.tactical_identity import EnemyIntent
        enemy = Unit(position=(96,64),health=20,stats=EnemyStats(),unit_type="enemy")
        target = Unit(position=(128,64),health=20,stats=PlayerStats())
        intent = EnemyIntent(enemy,"LOCK",target,"Rook","Precision",(255,80,70))
        boxes = [(64,80,200,120)]
        bounds = (0,0,960,640)
        battle_hud.draw_enemy_intents([],[],None,0,reserved_intents=[intent],
                                      label_boxes=boxes,label_bounds=bounds)
        self.assertEqual(len(boxes),2)
        self.assertEqual(boxes[-1][3]-boxes[-1][1],40)
        a,b = boxes
        self.assertTrue(a[2]+6 <= b[0] or b[2]+6 <= a[0] or a[3]+6 <= b[1] or b[3]+6 <= a[1])
        self.assertTrue(bounds[0] <= b[0] and b[2] <= bounds[2])
        texts = [call[0] for call in captured_draw_text]
        self.assertIn("LOCK  ROOK",texts)
        self.assertIn("2 AP / 30% CRIT - MOVE OR CUT SIGHT",texts)
        self.assertEqual(enemy.position,(96,64))

    def test_stale_hidden_or_dead_enemy_intents_draw_no_links_or_plates(self):
        from unittest.mock import patch
        from game.combat.tactical_identity import EnemyIntent
        enemy = Unit(position=(96,64),health=20,stats=EnemyStats(),unit_type="enemy")
        intent = EnemyIntent(enemy,"HUNT",None,"Rook","Interrupted",(255,80,70))
        for visible,health in ((False,20),(True,0)):
            enemy.visible,enemy.health = visible,health
            boxes = []
            with patch.object(arcade,"draw_line") as lines:
                battle_hud.draw_enemy_intents([],[],None,0,reserved_intents=[intent],label_boxes=boxes)
            lines.assert_not_called()
            self.assertEqual(boxes,[])

    def test_target_hp_anchors_inside_panel_right_edge(self):
        from unittest.mock import patch
        player = Unit(position=(32,32), stats=PlayerStats())
        enemy = Unit(position=(64,32), stats=EnemyStats(), unit_type="enemy")
        with patch.object(arcade,"draw_texture_rect",create=True):
            battle_hud.draw_target_lock_panel(960,enemy,"fire",player)
        call = next(call for call in captured_draw_text if str(call[0]).startswith("HP "))
        self.assertEqual(call[1][0], battle_hud.target_lock_bounds(960)[2]-10)
        self.assertEqual(call[2]["anchor_x"], "right")

    def test_target_lock_replaces_other_sidebar_panels_in_shared_hud_geometry(self):
        for width,height in ((960,640),(1280,720),(1920,1000)):
            regions = battle_hud.battlefield_hud_regions(width,height,target_lock=True,
                                                       show_log=True,timeline_slots=8)
            self.assertIn(battle_hud.target_lock_bounds(width),regions)
            self.assertNotIn(battle_hud.combat_log_bounds(width,height),regions)
            timeline = (width-334,height-92-34-30*8,width-14,height-92)
            self.assertNotIn(timeline,regions)
            left,bottom,right,top = battle_hud.target_lock_bounds(width)
            self.assertTrue(battle_hud.hud_blocks_battlefield_pointer(
                width,height,(left+right)/2,(bottom+top)/2,target_lock=True,show_log=True,timeline_slots=8))
            normal = battle_hud.battlefield_hud_regions(width,height,timeline_slots=8)
            self.assertIn(timeline,normal)
            journal = battle_hud.battlefield_hud_regions(width,height,show_log=True,timeline_slots=8)
            self.assertIn(battle_hud.combat_log_bounds(width,height),journal)
            self.assertNotIn(timeline,journal)

    def test_crowded_unit_plates_keep_identity_status_and_hp_without_overlapping(self):
        from types import SimpleNamespace
        from game.character import Character
        units = []
        for name in ("Rook", "Longshot", "Oracle"):
            character = Character(name)
            unit = Unit(position=(96, 64), stats=character.stats, character=character)
            unit.sprite = SimpleNamespace(center_x=96, center_y=64, width=32, height=48)
            units.append(unit)
        units[1].on_overwatch = True
        units[1].status_effects = ["suppressed", "bleeding"]
        hidden = Unit(position=(96, 64), stats=EnemyStats(), unit_type="enemy")
        hidden.sprite = units[0].sprite
        hidden.visible = False
        boxes = []
        before = [unit.position for unit in units]
        battle_hud.draw_unit_labels(units, [hidden], 1, label_boxes=boxes)
        self.assertEqual(len(boxes), 3)
        for i, a in enumerate(boxes):
            for b in boxes[i+1:]:
                self.assertTrue(a[2]+6 <= b[0] or b[2]+6 <= a[0] or a[3]+6 <= b[1] or b[3]+6 <= a[1])
        texts = [call[0] for call in captured_draw_text]
        self.assertEqual(texts[0], "LONGSHOT / OW")
        self.assertIn("SUP", texts)
        self.assertIn("BLD", texts)
        self.assertIn("ROOK", texts)
        self.assertNotIn("ENEMY", texts)
        self.assertEqual(before, [unit.position for unit in units])

    def test_portrait_names_use_the_full_card_row_below_the_portrait(self):
        from game.character import Character
        from unittest.mock import patch
        character = Character("Longshot")
        unit = Unit(position=(64, 64), stats=character.stats, character=character)
        with patch.object(arcade, "draw_texture_rect", create=True):
            battle_hud.draw_unit_portrait_strip([unit], 0, 960, 0)
        name_call = next(call for call in captured_draw_text if call[0] == "LONGSHOT")
        self.assertEqual(name_call[1][1], 158)
        self.assertEqual(name_call[2]["font_size"], 8)
        guard_call = next(call for call in captured_draw_text if call[0] == "GUARD")
        self.assertGreater(guard_call[1][1], name_call[1][1]+12)

    def test_header_keeps_phase_and_resources_apart_and_limits_long_titles(self):
        for width,height in ((960,640),(1280,720),(1920,1000)):
            captured_rects.clear()
            captured_draw_text.clear()
            battle_hud.draw_resource_summary(width,height,{},100)
            battle_hud.draw_phase_banner(width,height,"player",18,0)
            resources,phase=captured_rects[:2]
            self.assertLess(resources[1],phase[0])
            self.assertLessEqual(phase[3],height-38)
            title="Operation: a very long mission title that must leave room for squad and enemy counts"
            battle_hud.draw_mission_status_bar(width,height,title,4,8,18)
            rendered=[str(c[0]) for c in captured_draw_text]
            if len(title)>max(12,(width-460)//14):
                self.assertTrue(any(text.endswith("...") and len(text)<len(title) for text in rendered))
            else:
                self.assertIn(title.upper(),rendered)
            self.assertIn("TURN 18",rendered)

    def test_status_and_portraits_use_upper_row_without_covering_commands(self):
        from game.stats import PlayerStats
        units=[Unit(position=(64+i*32,64),stats=PlayerStats()) for i in range(4)]
        battle_hud.draw_unit_status_panel(960,640,units[0],"player")
        self.assertTrue(any(rect[:4]==(12,312,130,210) for rect in captured_rects))
        captured_rects.clear()
        battle_hud.draw_unit_portrait_strip(units,0,960,0)
        cards=[r for r in captured_rects if r[3]-r[2]==76 and r[1]-r[0]==battle_hud._STRIP_CARD_W]
        self.assertEqual(len(cards),4)
        self.assertTrue(all(r[0]>=324 and r[1]<=944 for r in cards))
        self.assertTrue(battle_hud.unit_status_panel_visible(960,4))
        self.assertFalse(battle_hud.unit_status_panel_visible(960,10))

    def test_psi_role_indicator_renders_independently_of_samurai_branch(self):
        from game.character import Character
        from unittest.mock import patch
        for role in ("samurai","psi"):
            character=Character("Oracle",role=role)
            unit=Unit(position=(64,64),stats=character.stats,character=character)
            with patch.object(arcade,"draw_line") as lines:
                battle_hud.draw_role_signature_indicator(unit,100,130,0)
            for call in lines.call_args_list:
                x1,y1,x2,y2=call.args[:4]
                self.assertTrue(100<=x1<=100+battle_hud._STRIP_CARD_W)
                self.assertTrue(100<=x2<=100+battle_hud._STRIP_CARD_W)
                self.assertTrue(130<=y1<=210 and 130<=y2<=210)
        self.assertIn("CONTROL",[call[0] for call in captured_draw_text])
        self.assertFalse(any("STANCE." in str(call[0]) for call in captured_draw_text))

    def test_pointer_occlusion_matches_log_geometry_and_reserved_hud_areas(self):
        for width,height in ((960,640),(1280,720),(1920,1000)):
            left,bottom,right,top=battle_hud.combat_log_bounds(width,height)
            x,y=(left+right)/2,(bottom+top)/2
            self.assertTrue(battle_hud.hud_blocks_battlefield_pointer(width,height,x,y,show_log=True))
            self.assertFalse(battle_hud.hud_blocks_battlefield_pointer(width,height,x,y,show_log=False))
            self.assertTrue(battle_hud.hud_blocks_battlefield_pointer(width,height,width/2,160))
            left,bottom,right,top=battle_hud.target_lock_bounds(width)
            self.assertTrue(battle_hud.hud_blocks_battlefield_pointer(width,height,(left+right)/2,(bottom+top)/2,target_lock=True))
        battle_hud.draw_combat_log_side_panel(1280,720,[])
        left,bottom,right,top=battle_hud.combat_log_bounds(1280,720)
        self.assertTrue(any(rect[:4]==(left,right,bottom,top) for rect in captured_rects))

    def test_containment_boundary_matches_failure_cells_and_viewport_width(self):
        from unittest.mock import patch
        from types import SimpleNamespace
        from game.mission_objectives import objective_failed_by_enemy_positions
        for width, threshold in ((960, 192), (1920, 207), (1280, 256)):
            objective = SimpleNamespace(kind="containment", position=(448, 320), completed=False,
                                        label="BREACH LINE", breach_y=threshold, failure_condition="Breached")
            last_row = (threshold // 32) * 32
            edge = last_row + 16
            with patch.object(arcade, "draw_line") as lines:
                battle_hud.draw_objective_marker(objective, 0, battlefield_width=width)
            self.assertTrue(any(call.args[:4] == (336.0, edge, 560.0, edge) for call in lines.call_args_list))
            self.assertTrue(objective_failed_by_enemy_positions([(448, last_row)], objective)[0])
            self.assertFalse(objective_failed_by_enemy_positions([(448, last_row+32)], objective)[0])
            self.assertFalse(objective_failed_by_enemy_positions([(64, last_row)], objective)[0])
            self.assertIn("BREACH ZONE - KEEP HOSTILES OUT", [call[0] for call in captured_draw_text])
            objective.completed = True
            captured_draw_text.clear()
            battle_hud.draw_objective_marker(objective, 0, battlefield_width=width)
            self.assertNotIn("BREACH ZONE - KEEP HOSTILES OUT", [call[0] for call in captured_draw_text])

    def test_defense_marker_shows_the_full_nine_cell_breach_zone(self):
        from types import SimpleNamespace
        objective = SimpleNamespace(kind="defend", position=(192, 128), completed=False, label="POSITION",
                                    interaction_prompt="Keep hostiles out", progress_text="Hold position")
        battle_hud.draw_objective_marker(objective, 0)
        self.assertTrue(any(rect[:4] == (144.0, 240.0, 80.0, 176.0) for rect in captured_rects))
        self.assertIn("KEEP HOSTILES OUT", [call[0] for call in captured_draw_text])
        captured_rects.clear()
        objective.completed = True
        battle_hud.draw_objective_marker(objective, 0)
        self.assertFalse(any(rect[:4] == (144.0, 240.0, 80.0, 176.0) for rect in captured_rects))

    def test_compact_objective_and_hazards_share_disjoint_caption_boxes(self):
        from types import SimpleNamespace
        from unittest.mock import patch
        from game.combat.battlefield import HazardZone
        objective = SimpleNamespace(kind="defend", position=(192, 128), completed=False,
                                    label="POSITION", interaction_prompt="Long duplicated instruction")
        boxes = []
        with patch.object(arcade, "draw_circle_filled", create=True), patch.object(arcade, "draw_circle_outline", create=True):
            battle_hud.draw_hazard_zones([HazardZone("fire", (192, 152))], label_boxes=boxes)
            battle_hud.draw_objective_marker(objective, 0, compact=True, label_boxes=boxes)
        self.assertEqual(len(boxes), 2)
        a, b = boxes
        self.assertTrue(a[2]+6 <= b[0] or b[2]+6 <= a[0] or a[3]+6 <= b[1] or b[3]+6 <= a[1])
        texts = [call[0] for call in captured_draw_text]
        self.assertIn("FIRE -2 HP", texts)
        self.assertIn("HOLD / KEEP HOSTILES OUT", texts)
        self.assertNotIn("Long duplicated instruction", texts)
        self.assertEqual(objective.position, (192, 128))

    def test_authored_deployment_overlay_tints_legal_cells_instead_of_a_solid_bottom_band(self):
        battle_hud.draw_deployment_overlay(1280, 720, [], 0, 0, deployment_cells={(64, 256), (96, 256)})
        self.assertIn((52.0, 76.0, 244.0, 268.0, (60, 200, 120, 40)), captured_rects)
        self.assertFalse(any(rect[:4] == (0.0, 1280.0, 0.0, 128.0) for rect in captured_rects))

    def test_deployment_cells_and_selected_ring_follow_camera_but_controls_stay_fixed(self):
        from unittest.mock import patch
        unit = Unit(position=(96, 128), stats=PlayerStats())
        with patch.object(arcade, "draw_circle_outline", create=True) as circles:
            battle_hud.draw_deployment_overlay(1280, 720, [unit], 0, 0,
                                              deployment_cells={(96, 128)}, camera_offset=(64, -32))
        self.assertIn((20., 44., 148., 172., (60, 200, 120, 40)), captured_rects)
        self.assertEqual(circles.call_args.args[:2], (32, 160))
        self.assertTrue(any(rect[:4] == (0., 1280., 0., 40.) for rect in captured_rects))
        self.assertEqual(unit.position, (96, 128))

    def test_precision_lock_shows_reserved_target_cost_counterplay_and_interruption(self):
        from unittest.mock import patch
        from game.character import Character
        from game.combat import CombatEngine, CombatState
        character = Character("Rook")
        target = Unit(position=(160, 64), stats=character.stats, health=20, character=character)
        enemy = Unit(position=(32, 64), stats=EnemyStats(), health=20, attack_range=6,
                     unit_type="enemy", enemy_theme="corp_37_robot", enemy_subtype="elite")
        engine = CombatEngine(CombatState(None, [target], [enemy]))
        engine.start_player_turn()
        with patch.object(arcade, "draw_circle_outline", create=True) as circles:
            battle_hud.draw_enemy_intents([], [], None, 0, reserved_intents=engine.enemy_intents())
        self.assertEqual(circles.call_args.args[:2], (160, 64))
        self.assertIn("LOCK  ROOK", [call[0] for call in captured_draw_text])
        self.assertIn("2 AP / 30% CRIT - MOVE OR CUT SIGHT", [call[0] for call in captured_draw_text])
        target.position = (160, 96)
        captured_draw_text.clear()
        battle_hud.draw_enemy_intents([], [], None, 0, reserved_intents=engine.enemy_intents())
        self.assertIn("! HUNT  ROOK", [call[0] for call in captured_draw_text])
        self.assertFalse(any("30% CRIT" in str(call[0]) for call in captured_draw_text))

    def test_mutant_projection_and_sludge_show_the_mark_and_its_consequences(self):
        from unittest.mock import patch
        from game.combat import CombatEngine, CombatState
        from game.combat.battlefield import HazardZone
        enemy = Unit(position=(32, 64), stats=EnemyStats(), health=20,
                     unit_type="enemy", enemy_theme="mutant", enemy_subtype="heavy")
        target = Unit(position=(96, 64), stats=PlayerStats(), health=20)
        engine = CombatEngine(CombatState(None, [target], [enemy]))
        engine.start_player_turn()
        with patch.object(arcade, "draw_circle_outline", create=True) as outline:
            battle_hud.draw_enemy_intents([], [], None, 0, reserved_intents=engine.enemy_intents())
        self.assertEqual(outline.call_args.args[:2], (96, 64))
        self.assertTrue(any("TOXIN  MARKED TILE" in str(call[0]) for call in captured_draw_text))
        with patch.object(arcade, "draw_circle_filled", create=True), patch.object(arcade, "draw_circle_outline", create=True):
            battle_hud.draw_hazard_zones([HazardZone("sludge", (96, 64), 0)])
        self.assertIn("SLUDGE -1 HP / -1 AP", [call[0] for call in captured_draw_text])

    def test_swarm_approach_marker_uses_the_reserved_destination(self):
        from types import SimpleNamespace
        from unittest.mock import patch
        from game.combat.tactical_identity import EnemyIntent
        enemy = SimpleNamespace(position=(64, 96), health=20)
        target = SimpleNamespace(position=(160, 96))
        intent = EnemyIntent(enemy, "SWARM", target, "Rook", "Approach", (255, 82, 64), destination=(128, 96))
        with patch.object(arcade, "draw_circle_outline", create=True) as circles:
            battle_hud.draw_enemy_intents([], [], None, 0, reserved_intents=[intent])
        self.assertEqual(circles.call_args.args[:3], (128, 96, 6))
        self.assertIn("SWARM  ROOK", [call[0] for call in captured_draw_text])

    def test_command_link_marker_does_not_disclose_a_hidden_commander_position(self):
        from types import SimpleNamespace
        from unittest.mock import patch
        from game.combat.tactical_identity import EnemyIntent
        enemy = SimpleNamespace(position=(96, 64), health=20)
        target = SimpleNamespace(position=(160, 64))
        commander = SimpleNamespace(position=(900, 900), visible=False)
        intent = EnemyIntent(enemy, "SUPPRESS", target, "Rook", "COMMAND LINK", (80, 190, 255), commander)
        with patch.object(arcade, "draw_line") as lines:
            shown = battle_hud.draw_enemy_intents([], [], None, 0.0, reserved_intents=[intent])
        self.assertIs(shown[0], intent)
        self.assertIn("SUPPRESS  ROOK [LINK]", [call[0] for call in captured_draw_text])
        self.assertFalse(any(call.args[2:4] == (900, 900) for call in lines.call_args_list))
        commander.visible = True
        with patch.object(arcade, "draw_line") as lines:
            battle_hud.draw_enemy_intents([], [], None, 0.0, reserved_intents=[intent])
        self.assertTrue(any(call.args[2:4] == (900, 900) for call in lines.call_args_list))

    def test_map_obstacle_contours_do_not_obscure_the_background(self):
        from game.cover_system import CoverNode

        battle_hud.draw_cover_nodes([
            CoverNode(4, 4, "high", passable=False),
            CoverNode(4, 5, "high", passable=False),
        ])
        self.assertEqual(captured_rects, [])
        self.assertEqual(captured_draw_text, [])

    def setUp(self) -> None:
        captured_draw_text.clear()
        captured_rects.clear()
        self._orig_draw_text = arcade.draw_text
        self._orig_rect = arcade.draw_lrbt_rectangle_filled
        self._orig_rect_outline = arcade.draw_lrbt_rectangle_outline
        self._orig_draw_rect_outline = arcade.draw_rect_outline
        self._orig_line = arcade.draw_line
        arcade.draw_text = _draw_text
        arcade.draw_lrbt_rectangle_filled = _draw_lrbt_rectangle_filled
        arcade.draw_lrbt_rectangle_outline = _draw_lrbt_rectangle_outline
        arcade.draw_rect_outline = _draw_rect_outline
        arcade.draw_line = _draw_line

    def tearDown(self) -> None:
        arcade.draw_text = self._orig_draw_text
        arcade.draw_lrbt_rectangle_filled = self._orig_rect
        arcade.draw_lrbt_rectangle_outline = self._orig_rect_outline
        arcade.draw_rect_outline = self._orig_draw_rect_outline
        arcade.draw_line = self._orig_line

    def _font_size_for_contains(self, needle: str) -> int:
        for text, args, kwargs in captured_draw_text:
            if needle in str(text):
                return int(kwargs.get("font_size", args[3] if len(args) > 3 else 0))
        raise AssertionError(f"Could not find text containing {needle!r}")

    def test_shortcut_banner_centers_the_help_text(self):
        battle_hud.draw_battle_shortcut_banner(
            1280,
            720,
            "Active shortcuts: Arrow keys move | E objective",
        )

        text_calls = [call for call in captured_draw_text if "Active shortcuts:" in str(call[0])]
        self.assertTrue(text_calls, "expected the shortcut banner to render text")
        text_x = float(text_calls[0][1][0])
        self.assertAlmostEqual(text_x, 640.0, delta=25.0)
        self.assertGreaterEqual(self._font_size_for_contains("Active shortcuts:"), 12)
        banner = captured_rects[0]
        self.assertEqual(banner[:4],(0,1280,0,18))

    def test_aftermath_line_replaces_footer_hints(self) -> None:
        battle_hud.draw_action_aftermath_line(1280, 720, "MOVE | DMG 0")

        text_calls = [call for call in captured_draw_text if call[0] == "MOVE | DMG 0"]
        self.assertTrue(text_calls, "expected the aftermath line to render text")
        text_x = float(text_calls[0][1][0])
        self.assertAlmostEqual(text_x, 640.0, delta=25.0)
        self.assertGreaterEqual(self._font_size_for_contains("MOVE | DMG 0"), 12)
        banner = captured_rects[0]
        self.assertEqual(banner[:4],(0,1280,0,18))

    def test_contextual_shortcut_banner_switches_with_input_mode(self) -> None:
        keyboard = battle_hud.battle_shortcut_banner("keyboard_mouse", False, False)
        controller = battle_hud.battle_shortcut_banner("controller", False, False)
        self.assertIn("Arrow keys move", keyboard)
        self.assertIn("LS move", controller)

    def test_contextual_shortcut_banner_prioritizes_end_turn_confirmation(self) -> None:
        confirm = battle_hud.battle_shortcut_banner("keyboard_mouse", True, True)
        self.assertIn("confirm end turn", confirm.lower())

    def test_enemy_intent_badge_names_action_and_target(self) -> None:
        target = Unit(
            position=(96, 64),
            stats=PlayerStats(hp=10, max_hp=10),
            health=10,
            character=type("Agent", (), {"name": "Mara", "role": "sniper"})(),
        )
        target.in_cover_bonus = 2
        enemy = Unit(
            position=(32, 64),
            stats=EnemyStats(hp=8, max_hp=8),
            health=8,
            attack_range=4,
            unit_type="enemy",
            enemy_theme="corp_samurai",
        )

        intents = battle_hud.draw_enemy_intents([enemy], [target], None, 0.5)

        self.assertEqual(intents[0].action, "FLANK")
        self.assertTrue(any("FLANK" in str(call[0]) and "MARA" in str(call[0]) for call in captured_draw_text))

    def test_overwatch_preview_cells_build_forward_line_and_cone(self) -> None:
        player = _DummyUnit("Agent 1", "sniper")
        player.position = (4, 4)
        triggers, coverage = battle_hud.overwatch_preview_cells(
            player,
            (1, 0),
            640,
            480,
            reach_cells=3,
        )
        self.assertEqual(triggers, [(36, 4), (68, 4), (100, 4)])
        self.assertIn((36, 36), coverage)
        self.assertIn((100, 100), coverage)

    def test_movement_range_draws_half_size_cells(self) -> None:
        unit = _DummyUnit("Agent 1")
        unit.position = (32, 32)

        battle_hud.draw_movement_range(unit, 96, 96)

        self.assertEqual(len(captured_rects), 5)
        for left, right, bottom, top, _color in captured_rects:
            self.assertAlmostEqual(right - left, 16.0)
            self.assertAlmostEqual(top - bottom, 16.0)
            self.assertAlmostEqual(left % 32.0, 8.0)
            self.assertAlmostEqual(bottom % 32.0, 8.0)

    def test_combat_log_side_panel_renders_latest_events_and_tab_hint(self) -> None:
        events = [f"event {idx}" for idx in range(10)]

        battle_hud.draw_combat_log_side_panel(1280, 720, events)

        rendered = [str(call[0]) for call in captured_draw_text]
        self.assertIn("COMBAT LOG  [Tab]", rendered)
        self.assertIn("event 9", rendered)
        self.assertIn("event 2", rendered)
        self.assertNotIn("event 1", rendered)

    def test_pause_overlay_exposes_resume_settings_and_abandon_actions(self) -> None:
        buttons = battle_hud.draw_pause_overlay(1280, 720)

        rendered = [str(call[0]) for call in captured_draw_text]
        self.assertIn("PAUSED", rendered)
        self.assertIn("RESUME", rendered)
        self.assertIn("SETTINGS", rendered)
        self.assertIn("ABANDON", rendered)
        self.assertEqual(
            [button[0] for button in buttons],
            [
                battle_hud.PAUSE_RESUME,
                battle_hud.PAUSE_SETTINGS,
                battle_hud.PAUSE_ABANDON,
            ],
        )

    def test_objective_marker_renders_label_prompt_and_progress(self) -> None:
        objective = type(
            "Objective",
            (),
            {
                "position": (448, 320),
                "completed": False,
                "label": "CACHE",
                "interaction_prompt": "Press E near CACHE to copy data.",
                "progress_text": "Progress: 1/2",
            },
        )()

        battle_hud.draw_objective_marker(objective, elapsed=0.0)

        rendered = [str(call[0]) for call in captured_draw_text]
        self.assertIn("OBJECTIVE: CACHE", rendered)
        self.assertIn("Press E near CACHE to copy data.", rendered)
        self.assertIn("Progress: 1/2", rendered)


if __name__ == "__main__":
    unittest.main()
