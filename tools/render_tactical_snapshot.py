"""Render a fixture with real Arcade/OpenGL in an explicitly hidden window."""

import argparse
import json
from pathlib import Path
from unittest.mock import patch


def render_snapshot(output, width=1280, height=720, title="Relay Defense", *,
                    deployment=False, camera_pan=(0, 0), begin_battle=False,
                    targeting=False, show_log=True, cancel_targeting=False, exercise_fire=False,
                    settle_effects=False, exercise_turn=False):
    import arcade
    from game.character import Character
    from game.gamestate import GameState
    from game.management.equipment import equip_starter_loadout
    from game.mission_templates import MissionTemplate
    from game.views import BattleView

    characters=[Character(name,role=role) for name,role in
                (("Rook","samurai"),("Longshot","sniper"),("Oracle","psi"),("Echo","medic"))]
    for character in characters:
        equip_starter_loadout(character.loadout,character.role)
    state=GameState(characters=characters,selected_agent_names=[c.name for c in characters])
    mission=MissionTemplate("render_fixture",title,"Hold the relay","Three Sevens Corp",
                            "Chrome Warrens",{},4,enemy_theme="corp_37",objective_type="defend",duration_days=2)
    window=arcade.Window(width,height,"CyberCity render fixture",visible=False,enable_polling=False)
    try:
        with patch("game.audio.SoundManager.get"):
            view=BattleView(state)
            view.setup(mission)
            view._deploying=deployment
            view._cam_pan_x, view._cam_pan_y = camera_pan
            view._intro_active=False
            view.message="Select an action or preview a move."
            view._show_combat_log=show_log
            before=[unit.position for unit in view.player_units]
            from game.ui.components.combat import world_labels
            captions = []
            omitted_captions = []
            original_place = world_labels.place_caption
            def checked_place(*args, **kwargs):
                box = original_place(*args, **kwargs)
                bounds = kwargs.get("bounds")
                if box is None:
                    omitted_captions.append(list(args[:3]))
                elif bounds is not None:
                    if not (bounds[0] <= box[0] < box[2] <= bounds[2]
                            and bounds[1] <= box[1] < box[3] <= bounds[3]):
                        raise RuntimeError("A caption leaves the visible camera bounds")
                    for other in args[3][:-1]:
                        if (box[0] < other[2]+6 and box[2] > other[0]-6
                                and box[1] < other[3]+6 and box[3] > other[1]-6):
                            raise RuntimeError("A caption overlaps a reserved panel or earlier caption")
                    captions.append(list(box))
                return box
            deployment_pan = None
            input_checks = None
            turn_checks = None
            if begin_battle:
                if not deployment:
                    raise ValueError("begin_battle requires deployment")
                view.on_draw()
                deployment_pan = [view._cam_pan_x, view._cam_pan_y]
                view._handle_deployment_key(arcade.key.ENTER)
                if view._deploying:
                    raise RuntimeError("Deployment did not finish")
            if targeting:
                if view._deploying:
                    raise ValueError("Targeting requires combat")
                player = view.player_units[view.active_index]
                enemy = view.enemy_units[0]
                occupied = {unit.position for unit in view.player_units}
                candidates = [cell for cell in view.terrain_profile.walkable_cells
                              if cell not in occupied and 0 < ((cell[0]-player.position[0])**2+
                                                               (cell[1]-player.position[1])**2) <= 64**2]
                enemy.position = min(candidates, key=lambda cell: (
                    (cell[0]-player.position[0])**2+(cell[1]-player.position[1])**2, cell))
                enemy.sprite.center_x, enemy.sprite.center_y = enemy.position
                enemy.visible = True
                if exercise_fire:
                    enemy.health = enemy.stats.hp = enemy.stats.max_hp = 100
                view._begin_target_action(player, "fire")
                if not view.selecting_target:
                    raise RuntimeError("Target fixture did not enter real targeting mode")
                if cancel_targeting:
                    view.on_key_press(arcade.key.ESCAPE, 0)
                    if view.selecting_target:
                        raise RuntimeError("Escape did not leave targeting mode")
                if exercise_fire:
                    from tools.tactical_input_checks import exercise_fire_controls
                    input_checks = exercise_fire_controls(view, enemy, settle=settle_effects)
            from game.ui.screens import battle_hud
            if exercise_turn:
                from tools.tactical_input_checks import exercise_turn_controls
                turn_checks = exercise_turn_controls(view)
            import game.views as views_module
            ap_before = [unit.action_points for unit in view.player_units]
            with patch.object(arcade,"draw_texture_rect",wraps=arcade.draw_texture_rect) as draws, \
                    patch.object(world_labels,"place_caption",side_effect=checked_place), \
                    patch.object(battle_hud,"draw_target_lock_panel",wraps=battle_hud.draw_target_lock_panel) as lock_draw, \
                    patch.object(battle_hud,"draw_combat_log_side_panel",wraps=battle_hud.draw_combat_log_side_panel) as log_draw, \
                    patch.object(views_module,"draw_initiative_timeline",wraps=views_module.draw_initiative_timeline) as timeline_draw:
                view.on_draw()
            if ap_before != [unit.action_points for unit in view.player_units]:
                raise RuntimeError("Rendering spent allied AP")
            background_rect=next(call.args[1] for call in draws.call_args_list if call.args[0] is view.background)
            terrain_size=[view.terrain_profile.width,view.terrain_profile.height]
            if [background_rect.width,background_rect.height] != terrain_size:
                raise RuntimeError("Background draw size differs from terrain coordinates")
            if before != [unit.position for unit in view.player_units]:
                raise RuntimeError("Rendering moved tactical units")
            window.ctx.finish()
            output=Path(output)
            output.parent.mkdir(parents=True,exist_ok=True)
            frame=arcade.get_image(0,0,width,height)
            frame.save(output)
            return {"output":str(output),"width":width,"height":height,"visible_window":False,
                    "framebuffer_size":list(frame.size),
                    "background_world_size":terrain_size,
                    "bounded_caption_count":len(captions),
                    "omitted_captions":omitted_captions,
                    "targeting":view.selecting_target,
                    "input_checks":input_checks,
                    "turn_checks":turn_checks,
                    "sidebar_draws":{"target_lock":lock_draw.called,"combat_log":log_draw.called,
                                     "initiative":timeline_draw.called},
                    "deployment":view._deploying,
                    "deployment_pan_before_combat":deployment_pan,
                    "camera_pan":[view._cam_pan_x, view._cam_pan_y],
                    "active_unit_screen":[view.player_units[view._deploy_cursor if deployment else view.active_index].position[0]-view._cam_pan_x,
                                          view.player_units[view._deploy_cursor if deployment else view.active_index].position[1]-view._cam_pan_y],
                    "renderer":"real Arcade/OpenGL", "fixture_only":True, "map":view.map_path}
    finally:
        window.close()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--width",type=int,default=1280)
    parser.add_argument("--height",type=int,default=720)
    parser.add_argument("--title",default="Relay Defense")
    parser.add_argument("--deployment",action="store_true")
    parser.add_argument("--begin-battle",action="store_true")
    parser.add_argument("--targeting",action="store_true")
    parser.add_argument("--cancel-targeting",action="store_true")
    parser.add_argument("--exercise-fire",action="store_true")
    parser.add_argument("--settle-effects",action="store_true")
    parser.add_argument("--exercise-turn",action="store_true")
    parser.add_argument("--hide-log",action="store_true")
    parser.add_argument("--pan-x",type=float,default=0)
    parser.add_argument("--pan-y",type=float,default=0)
    args=parser.parse_args()
    result = render_snapshot(args.output,args.width,args.height,args.title,
                                    deployment=args.deployment,camera_pan=(args.pan_x,args.pan_y),
                                    begin_battle=args.begin_battle,targeting=args.targeting,
                                    show_log=not args.hide_log,cancel_targeting=args.cancel_targeting,
                                    exercise_fire=args.exercise_fire,settle_effects=args.settle_effects,
                                    exercise_turn=args.exercise_turn)
    args.output.with_suffix(".json").write_text(json.dumps(result,indent=2),encoding="utf-8")
    print(json.dumps(result))


if __name__=="__main__":
    main()
