"""Shared Debrief → Promotions → Headquarters navigation."""

def show_mission_debrief(self, victory, surviving_participants, all_player_units):
    # Collect promotion records (agents who levelled up)
    from game.ui.screens.agent_promotion_view import AgentPromotionView, PromotionRecord
    from game.ui.portraits import portrait_path_for_character as _ppfc
    promotions: list[PromotionRecord] = []
    for char in surviving_participants:
        old_lvl = getattr(char, "_pre_battle_level", char.stats.level)
        new_lvl = char.stats.level
        if new_lvl > old_lvl:
            try:
                _ppath = _ppfc(char)
            except Exception:
                _ppath = None
            promotions.append(PromotionRecord(
                character=char,
                old_level=old_lvl,
                new_level=new_lvl,
                portrait_path=_ppath,
            ))

    # Build per-agent debrief stats from tracked data
    from game.ui.screens.battle_debrief_view import AgentDebriefStat, BattleDebriefView
    from game.ui.portraits import portrait_path_for_character
    agent_stats: list[AgentDebriefStat] = []
    for unit in all_player_units:
        if not unit.character:
            continue
        try:
            portrait = portrait_path_for_character(unit.character)
        except Exception:
            portrait = None
        old_stress = getattr(unit.character, "_pre_battle_stress", unit.character.stress)
        agent_stats.append(AgentDebriefStat(
            name=unit.character.name,
            role=unit.character.role,
            portrait_path=portrait,
            damage_dealt=getattr(unit, "_damage_dealt", None if getattr(unit,"external_metrics",False) else 0),
            damage_taken=getattr(unit, "_damage_taken", None if getattr(unit,"external_metrics",False) else 0),
            actions_used=getattr(unit, "_actions_used", None if getattr(unit,"external_metrics",False) else 0),
            kills=getattr(unit, "_kills", None if getattr(unit,"external_metrics",False) else 0),
            kia=(unit.character not in self.game_state.characters),
            stress_delta=unit.character.stress - old_stress,
            xp_gained=getattr(unit.character, "_mission_xp_gained", 0),
            injuries=list(getattr(unit.character, "injuries", [])),
            hp_remaining=unit.health,max_hp_at_extraction=getattr(unit,"extraction_max_hp",None),
        ))

    debrief_view = BattleDebriefView(
        self.game_state,
        victory,
        self.mission,
        agent_stats,
        self.triggered_complication,
    )
    def completed():
        callback=getattr(self,"on_return_complete",None)
        if callback is not None:callback()

    if promotions:
        def after_debrief():
            if self.game_state.campaign.ending is not None:
                from game.ui.screens.campaign_ending_view import CampaignEndingView
                next_view=CampaignEndingView(self.game_state)
            else:
                from game.ui.screens.management_screen import ManagementView
                next_view=ManagementView(self.game_state)
                next_view.setup()
            self.window.show_view(AgentPromotionView(self.game_state, promotions, next_view, on_complete=completed))
            return True
        debrief_view.after_debrief = after_debrief
    else:
        debrief_view.after_debrief=completed
    self.window.show_view(debrief_view)

