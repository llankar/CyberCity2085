"""Explicit recovery after Continue; never silently rerun a campaign reward."""
from game.combat.return_snapshot import complete_return,resume_return
from game.mission_templates import MissionTemplate


def show_combat_recovery(window,state):
    for session_id,record in reversed(list(state.combat_sessions.items())):
        if record.get('status') not in {'pending','applied'}:continue
        if 'mission' not in record:continue
        mission=MissionTemplate.from_dict(record['mission'])
        if record.get('status')=='applied':
            from game.combat.session_protocol import acknowledge_applied_session
            try:
                acknowledge_applied_session(record,session_id)
            except OSError:
                state.add_event('Combat already resolved; acknowledgement could not be refreshed. The old Godot window may need closing manually.')
            resolved=resume_return(state,mission,session_id)
            if resolved is None:return False
            context,survivors,units=resolved;context.window=window
            context.on_return_complete=lambda:complete_return(state,session_id)
            from .mission_return import show_mission_debrief
            show_mission_debrief(context,context._victory,survivors,units)
            return True
        from pathlib import Path
        from game.combat.godot_bridge import GodotCombatLaunchResult
        from .godot_combat_handoff_view import GodotCombatHandoffView
        launch=GodotCombatLaunchResult(Path(record['session']['result_path']).parent/'handoff.json',[],False,
            'Combat interrompu. Vérification du résultat enregistré…',
            session_id=session_id,result_path=Path(record['session']['result_path']))
        window.show_view(GodotCombatHandoffView(state,mission,launch,window=window))
        return True
    return False
