from __future__ import annotations

import random

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .gamestate import GameState
from .i18n import t
from .enemy_themes import mission_enemy_theme
from .battle_maps import infer_battle_environment
from .consequences import Consequence
from .mission_templates import MissionTemplate, create_mission_templates
from .missions.complications import select_complications
from .missions.evacuation import create_evacuation_template
from .narrative.mission_briefing_conventions import (
    build_short_emotional_impact,
    normalize_mission_tags,
)


def _mission_seed(game_state: "GameState") -> int:
    """Build a deterministic seed from campaign state for stable daily boards."""
    return (
        game_state.calendar.current_day * 97
        + game_state.district.unrest * 11
        + game_state.district.media_heat * 7
        + (100 - game_state.district.stability) * 5
    )




def _build_emotional_impact_hint(mission: MissionTemplate, language: str | None = None) -> dict:
    """Estimate emotional impact based on objective pressure, risk, duration, and complications."""
    objective_weight = {
        "safe_extraction": 2,
        "extract": 2,
        "data_with_detour": 2,
        "data_theft": 1,
        "sabotage_window": 1,
        "sabotage": 1,
        "eliminate": 0,
    }.get(mission.objective_type, 1)
    score = (
        mission.risk_level
        + max(0, mission.duration_days - 1)
        + len(mission.possible_complications)
        + objective_weight
    )
    if score >= 8:
        level = "critical"
        text = t("mission.impact.critical", language)
    elif score >= 6:
        level = "high"
        text = t("mission.impact.high", language)
    elif score >= 4:
        level = "medium"
        text = t("mission.impact.medium", language)
    else:
        level = "low"
        text = t("mission.impact.low", language)
    short_text = build_short_emotional_impact(level, text)
    risk_explanation = t(
        "mission.impact.risk_explanation",
        language,
        risk=mission.risk_level,
        duration=mission.duration_days,
        complications=len(mission.possible_complications),
    )
    return {
        "level": level,
        "text": text,
        "short_text": short_text,
        "emotional_impact_summary": short_text,
        "risk_explanation": risk_explanation,
        "expected_stress_band": level,
    }


def generate_mission_board(game_state: "GameState", board_size: int | None = None) -> list[MissionTemplate]:
    """Generate a small daily mission board based on district pressure."""
    templates = create_mission_templates(game_state.district.name)
    for template in templates:
        template.battle_environment = "city"
        template.enemy_theme = "raider" if template.id in {"extraction", "sabotage"} else "corp_37"
    templates.extend(_regional_missions(game_state.district.name))
    district_pressure = game_state.district.unrest + game_state.district.media_heat
    evac_probability = min(0.65, max(0.15, district_pressure / 140))
    if random.Random(_mission_seed(game_state) + 404).random() < evac_probability:
        templates.append(create_evacuation_template(game_state.district.name, district_pressure))
    if not templates:
        return []

    rng = random.Random(_mission_seed(game_state))
    pressure_score = game_state.district.unrest + game_state.district.media_heat
    pressure_mod = max(0, pressure_score - game_state.district.stability) // 20

    generated: list[MissionTemplate] = []
    slots = board_size if board_size is not None else random.Random(_mission_seed(game_state) + 313).randint(5, 6)
    slots = max(1, slots)
    candidates = list(templates)
    rng.shuffle(candidates)
    environment_counts: dict[str, int] = {}
    seen_themes: set[str] = set()
    seen_objectives: set[str] = set()
    for slot in range(slots):
        if not candidates:
            candidates = list(templates)
            rng.shuffle(candidates)
        def variety_score(candidate):
            environment = infer_battle_environment(candidate)
            theme = mission_enemy_theme(candidate)
            return (
                40 * (environment not in environment_counts)
                + 24 * (theme not in seen_themes)
                + 12 * (candidate.objective_type not in seen_objectives)
                - 5 * environment_counts.get(environment, 0)
            )
        base = max(candidates, key=variety_score)
        candidates.remove(base)
        environment = infer_battle_environment(base)
        environment_counts[environment] = environment_counts.get(environment, 0) + 1
        seen_themes.add(mission_enemy_theme(base))
        seen_objectives.add(base.objective_type)
        mission = MissionTemplate.from_dict(base.to_dict())
        risk_delta = rng.choice([-1, 0, 1]) + pressure_mod
        mission.risk_level = max(1, mission.risk_level + risk_delta)
        mission.fund_reward = max(20, mission.fund_reward + mission.risk_level * 5)
        mission.starting_enemy_count = max(1, mission.starting_enemy_count + max(0, risk_delta))
        mission.id = f"{mission.id}_d{game_state.calendar.current_day}_s{slot}"
        mission.title = f"{mission.title} {t('mission.board.day_suffix', game_state.ui_language, day=game_state.calendar.current_day)}"
        mission_tag_names = [tag.name for tag in mission.tags]
        mission.possible_complications.extend(
            select_complications(
                district_pressure=pressure_score,
                mission_tags=mission_tag_names,
                seed=_mission_seed(game_state) + slot,
            )
        )
        mission.possible_complications = mission.possible_complications[:2]
        mission.emotional_impact_hint = _build_emotional_impact_hint(mission, game_state.ui_language)
        mission.emotional_impact_hint["normalized_tags"] = normalize_mission_tags(mission.tags)
        mission.enemy_theme = mission_enemy_theme(mission)
        generated.append(mission)

    # ── Story mission injection ───────────────────────────────────────────────
    _inject_story_mission(game_state, generated)

    rng.shuffle(generated)
    # Keep the first visible cards diverse too, even when the UI shows only three.
    ordered: list[MissionTemplate] = []
    while generated:
        if not ordered:
            chosen = generated[0]
        else:
            environments = {infer_battle_environment(m) for m in ordered}
            themes = {mission_enemy_theme(m) for m in ordered}
            chosen = max(generated, key=lambda m: (
                40 * (infer_battle_environment(m) not in environments)
                + 20 * (mission_enemy_theme(m) not in themes)
                + 10 * (m.objective_type not in {item.objective_type for item in ordered})
            ))
        ordered.append(chosen)
        generated.remove(chosen)
    return ordered


def _regional_missions(district_name: str) -> list[MissionTemplate]:
    """Playable contracts with explicit factions, environments and supported objectives."""
    contracts = [
        ("road_relay", "Sabotage : relais du convoi", "Détruire le relais des pillards sur la route de poussière avant le départ du convoi.", "Wasteland Raiders", "raider", "wasteland", "sabotage", 3),
        ("shelter_hostages", "Sauvetage : abri assiégé", "Libérer les survivants enfermés dans un abri des terres désolées et sécuriser leur sortie.", "Wasteland Raiders", "raider", "wasteland", "civilian_rescue", 2),
        ("mutant_signal", "Reconnaissance : signal irradié", "Relever les données de la balise perdue dans le bassin irradié occupé par les mutants.", "Mutant Clans", "mutant", "wasteland", "recon_scan", 3),
        ("starver_clinic", "Extraction : les derniers patients", "Ouvrir une voie de sortie pour les patients d'une clinique urbaine encerclée par les affamés.", "Starver Swarm", "starver", "city", "safe_extraction", 2),
        ("samurai_archive", "Infiltration : archives du clan", "Pirater le terminal d'archives du clan samouraï et récupérer les ordres de surveillance.", "Samurai Consortium", "corp_samurai", "city", "data_theft", 4),
        ("robot_factory", "Sabotage : chaîne autonome", "Arrêter le contrôleur de production d'une usine défendue par des robots de sécurité.", "Three Sevens Corp", "corp_37_robot", "city", "sabotage", 4),
        ("mutant_overpass", "Nettoyage : passage effondré", "Éliminer la meute mutante qui bloque le passage effondré et rouvrir la route des réfugiés.", "Mutant Clans", "mutant", "wasteland", "eliminate", 3),
        ("starver_depot", "Récupération : médicaments perdus", "Récupérer les données du dépôt médical abandonné avant que les affamés ne ferment les accès.", "Starver Swarm", "starver", "wasteland", "data_theft", 2),
    ]
    missions = []
    for key, title, objective, faction, theme, environment, objective_type, risk in contracts:
        missions.append(MissionTemplate(
            id=key, title=title, objective_text=objective, target_faction=faction,
            district=district_name, district_pressure={"unrest": 3, "media_heat": 1},
            starting_enemy_count=2 + risk // 2, enemy_theme=theme,
            battle_environment=environment, objective_type=objective_type,
            risk_level=risk, fund_reward=65 + risk * 20,
            duration_days=2 if environment == "wasteland" else 1,
            success_consequences=[Consequence(
                affected_district=district_name, affected_faction=faction, severity=1,
                narrative_text=f"{title} : objectif accompli, les routes et les refuges gagnent en sécurité.",
                mechanical_effects={"stability": 3, "unrest": -3})],
            failure_consequences=[Consequence(
                affected_district=district_name, affected_faction=faction, severity=2,
                narrative_text=f"{title} : l'échec renforce la pression sur les habitants.",
                mechanical_effects={"unrest": 4, "media_heat": 2})],
        ))
    return missions


def _inject_story_mission(
    game_state: "GameState",
    board: list[MissionTemplate],
) -> None:
    """Insert one story mission per act into the board if conditions are met."""
    try:
        from game.campaign.story_missions import story_missions_for_act
        from game.campaign.acts import ACT_TITLES
    except Exception:
        return

    c = game_state.campaign
    act_missions = story_missions_for_act(c.current_act)
    if not act_missions:
        return

    # Pick the first story mission whose id hasn't been completed yet
    completed_ids = set(c.act_triggers_seen)
    completed_story_missions = set(getattr(c, "completed_story_missions", []))
    for sm in act_missions:
        completed_key = f"story_complete_{sm.id}"
        if completed_key in completed_ids or sm.id in completed_story_missions:
            continue
        mt = story_mission_to_template(sm, game_state)
        # Insert at front of board (replace last regular mission if board is full)
        if len(board) >= 3:
            board[-1] = mt
        else:
            board.insert(0, mt)
        return  # only one story mission at a time


def story_mission_to_template(sm, game_state: "GameState") -> MissionTemplate:
    """Use the same authored story parameters for the board and pure QA."""
    # Build a MissionTemplate from the StoryMissionTemplate
    from game.consequences import Consequence
    mt = MissionTemplate(
        id=sm.id,
        title=f"[STORY] {sm.title}",
        objective_text=sm.objective_text,
        target_faction={"mutant": "Mutant Clans", "raider": "Wasteland Raiders", "starver": "Starver Swarm", "corp_samurai": "Samurai Consortium"}.get(sm.enemy_theme, "Three Sevens Corp"),
        district=game_state.district.name,
        district_pressure={"unrest": game_state.district.unrest},
        starting_enemy_count=max(3, sm.risk_level // 2),
        enemy_theme=sm.enemy_theme,
        objective_type=sm.objective_type,
        risk_level=sm.risk_level,
        fund_reward=sm.fund_reward,
        duration_days=2,
        emotional_impact_hint={
            "level": "critical",
            "text": sm.briefing[:120],
            "short_text": sm.briefing[:60],
            "normalized_tags": sm.tags,
        },
    )
    mt.enemy_theme = mission_enemy_theme(mt)
    return mt
