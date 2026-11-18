"""Explicit recovery after Continue; never silently rerun a campaign reward."""
from game.combat.return_snapshot import complete_return,resume_return
from game.mission_templates import MissionTemplate


def show_combat_recovery(window,state):
    for session_id,record in reversed(list(state.combat_sessions.items())):
        if record.get('status') not in {'pending','applied'}:continue
        if 'mission' not in record:continue
        mission=MissionTemplate.from_dict(record['mission'])
        if record.get('status')=='applied':
            resolved=resume_return(state,mission,session_id)
            if resolved is None:continue
            context,survivors,units=resolved;context.window=window
            context.on_return_complete=lambda:complete_return(state,session_id)
            from .mission_return import show_mission_debrief
            show_mission_debrief(context,context._victory,survivors,units)
            return True
        from pathlib import Path
        from game.combat.godot_bridge import GodotCombatLaunchResult
        from .godot_combat_handoff_view import GodotCombatHandoffView
        launch=GodotCombatLaunchResult(Path(record['session']['result_path']).parent/'handoff.json',[],False,
            'Combat interrompu. C : confirmer le résultat récupérable ; R : relancer Godot ; F : choisir Arcade explicitement.',
            session_id=session_id,result_path=Path(record['session']['result_path']))
        window.show_view(GodotCombatHandoffView(state,mission,launch,window=window))
        return True
    return False
