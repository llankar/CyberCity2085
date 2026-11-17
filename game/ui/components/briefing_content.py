"""Read-only, localized presentation helpers for mission intelligence."""

from game.i18n import t
from game.narrative.mission_briefing_conventions import translate_legacy_briefing_text
from game.ui.components.squad_mission import mission_art_path
from game.ui.portraits import portrait_path_for_robot, portrait_path_for_power_armor


def consequence_text(value):
    if isinstance(value, str):
        return value
    return getattr(value, "narrative_text", "") or str(value)


def support_art(asset):
    explicit = getattr(asset, "portrait_path", None)
    if explicit:
        return explicit
    if getattr(asset, "asset_type", "") == "power_armor":
        return portrait_path_for_power_armor(asset.id)
    if getattr(asset, "asset_type", "") == "combat_robot":
        return portrait_path_for_robot(asset.id)
    return None


def briefing_lines(gs, mission, facts):
    """No forecasts or consequences are invented by the presentation."""
    tr = lambda key, **kw: t("briefing." + key, gs.ui_language, **kw)
    hint = getattr(mission, "emotional_impact_hint", {})
    full_impact = hint.get("text") if isinstance(hint, dict) else None
    impact_text = (
        translate_legacy_briefing_text(full_impact)
        if full_impact
        else facts["emotional_impact"]
    )
    impact = [
        (
            tr("none_impact")
            if impact_text == "No unusual emotional impact forecast."
            else impact_text
        )
    ]
    impact.extend(facts["temporary_scar_summary"])
    if mission.tags:
        from game.ui.screens.mission_briefing_view import mission_tag_label

        impact.append(
            tr("tags")
            + ": "
            + ", ".join(mission_tag_label(tag) for tag in mission.tags)
        )
    return {
        "objective": [mission.objective_text],
        "complications": facts["complications"] or [tr("none_complications")],
        "impact": impact,
        "success": [consequence_text(c) for c in mission.success_consequences]
        or [tr("none_consequences")],
        "failure": [consequence_text(c) for c in mission.failure_consequences]
        or [tr("none_consequences")],
    }
