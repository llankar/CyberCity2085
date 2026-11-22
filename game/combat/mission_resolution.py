"""Campaign resolution shared by Arcade battles and validated Godot sessions.

The context carries real units, mission and GameState; no window or engine API.
"""
from game.agent_aftermath import apply_mission_aftermath
from game.deployment import sanitize_selected_agent_names
from game.narrative.debrief import build_mission_debrief_report
from game.narrative.relationship_consequences import apply_tactical_relationship_consequences


def resolve_campaign_battle(self, victory: bool, *, defeated_override=None):
    funds_before=self.game_state.available_funds
    transaction_start = len(self.game_state.funds.transaction_history)
    remaining_enemies = len(getattr(self, "enemy_units", []))
    defeated = max(0, self.initial_enemy_count - remaining_enemies)
    if defeated_override is not None:
        defeated = defeated_override
    if victory:
        # Existing campaign victory policy: full encounter reward, not a kill statistic.
        defeated = self.initial_enemy_count
    if victory:
        self.game_state.x += 50 * defeated
    processed_character_ids = set()
    surviving_participants = []
    all_player_units = list(self.player_units) + list(self.defeated_player_units)
    for unit in all_player_units:
        if unit.stats is not None:
            unit.extraction_max_hp = unit.stats.max_hp
        if not unit.character or id(unit.character) in processed_character_ids:
            continue
        processed_character_ids.add(id(unit.character))
        unit.character._pre_battle_stress = getattr(unit.character, "stress", 0)
        unit.character._pre_battle_level = getattr(unit.character.stats, "level", 1)
        unit.character._mission_xp_gained = 0
        if hasattr(unit, "reported_stress"):
            unit.character.stress = unit.reported_stress
        if unit.health <= 0:
            self.resolve_defeated_player_unit(unit)
            continue
        if unit.spec_ops_asset is None:
            unit.character.stats.hp = unit.health
        surviving_participants.append(unit.character)
        if victory:
            xp_award = 50 * defeated
            unit.character._mission_xp_gained = xp_award
            unit.character.gain_xp(xp_award)
    self.game_state.selected_agent_names = sanitize_selected_agent_names(
        self.game_state.characters, self.game_state.selected_agent_names
    )
    resource_awards=self.game_state.award_mission_resources(self.mission, victory, defeated)
    self.resolve_mission_outcome(victory)
    aftermath_lines = apply_mission_aftermath(
        surviving_participants,
        self.mission,
        victory,
        self.triggered_complication,
    )
    self.game_state.latest_agent_aftermath = aftermath_lines[-4:]
    performance_by_agent = {}
    combat_state = getattr(self, "combat_state", None)
    objective_contributions = (
        combat_state.tactical_flags.get("objective_contributions", {})
        if combat_state is not None
        else {}
    )
    for unit in all_player_units:
        if not unit.character:
            continue
        performance_by_agent[unit.character.name] = {
            "kills": getattr(unit, "_kills", 0),
            "damage_dealt": getattr(unit, "_damage_dealt", 0),
            "damage_taken": getattr(unit, "_damage_taken", 0),
            "kia": unit.health <= 0,
            "xp_gained": getattr(unit.character, "_mission_xp_gained", 0),
            "objective_type": getattr(self.mission, "objective_type", ""),
            "saved_civilian": bool(getattr(unit, "_saved_civilian", False)),
            "objective_contribution": int(
                objective_contributions.get(unit.character.name, 0)
            ),
        }
    for unit in all_player_units:
        if unit.character and getattr(unit,"external_metrics",False):
            for metric in ["kills","damage_dealt","damage_taken"]:
                if not hasattr(unit,"_"+metric):
                    performance_by_agent[unit.character.name].pop(metric,None)
    tactical_moments = (
        combat_state.tactical_flags.get("agent_moments", [])
        if combat_state is not None
        else []
    )
    from .agent_moments import remember_objective_contribution
    existing_objective_agents = {
        moment.get("agent_name") for moment in tactical_moments
        if moment.get("kind") == "objective_specialist"
    }
    by_name = {unit.character.name: unit.character for unit in all_player_units if unit.character}
    for agent_name, count in objective_contributions.items():
        character = by_name.get(agent_name)
        if character is None or agent_name in existing_objective_agents:
            continue
        moment = remember_objective_contribution(character, self.mission, int(count))
        if moment is not None:
            tactical_moments.append(moment)
    relationship_characters = []
    relationship_character_ids = set()
    for unit in all_player_units:
        if unit.character and id(unit.character) not in relationship_character_ids:
            relationship_character_ids.add(id(unit.character))
            relationship_characters.append(unit.character)
    relationship_changes = apply_tactical_relationship_consequences(
        relationship_characters,
        tactical_moments,
    )
    debrief_report = build_mission_debrief_report(
        surviving_participants,
        self.mission,
        victory,
        self.triggered_complication,
        performance_by_agent=performance_by_agent,
        tactical_moments=tactical_moments,
    )
    from game.narrative.agent_reputation import apply_agent_reputation_awards

    reputation_lines = apply_agent_reputation_awards(
        surviving_participants,
        debrief_report.reputation_awards,
    )
    self.game_state.latest_mission_debrief = debrief_report.to_dict()
    self.game_state.latest_mission_debrief["relationship_changes"] = relationship_changes
    mission_payout = sum(
        transaction.amount
        for transaction in self.game_state.funds.transaction_history[transaction_start:]
        if transaction.kind == "income" and transaction.source == "mission_reward"
    )
    self.game_state.latest_mission_debrief["campaign_rewards"] = {
        "resources": resource_awards,
        "mission_payout": mission_payout,
        "net_funds_change": self.game_state.available_funds - funds_before,
    }
    outcomes = []
    for unit in all_player_units:
        if not unit.spec_ops_asset or not unit.stats:
            continue
        asset = unit.spec_ops_asset
        max_hp = max(1, unit.stats.max_hp)
        damage_pct = int(max(0, min(100, (max_hp - max(0, unit.health)) * 100 / max_hp)))
        asset.maintenance.integrity = max(0, asset.maintenance.integrity - damage_pct)
        asset.maintenance.cooldown_days = 1 if damage_pct >= 30 else 0
        outcomes.append(
            {
                "id": asset.id,
                "name": asset.name,
                "damage": damage_pct,
                "repair_cost": asset.maintenance.repair_cost,
                "cooldown_days": asset.maintenance.cooldown_days,
            }
        )
    self.game_state.latest_spec_ops_outcomes = outcomes
    for line in aftermath_lines:
        self.game_state.add_event(line)
    for line in reputation_lines:
        self.game_state.add_event(line)
    for change in relationship_changes:
        self.game_state.add_event(str(change["text"]))

    return surviving_participants, all_player_units
