"""Spec-ops assets guide and UI copy helpers."""

from __future__ import annotations

from game.deployment import deployable_assets, selected_deployable_agents


def build_spec_ops_assets_guide_lines() -> list[str]:
    return [
        "Spec Ops Assets Guide",
        "Robots are autonomous support units that deploy beside agents.",
        "Power armor is a suit module: each selected suit reserves one pilot.",
        "Prerequisites: complete relevant research and keep integrity >= 50.",
        "Upkeep: each asset pays base maintenance plus repair from damage.",
        "Deployment rules: ready assets only; pilot-gated suits need selected agents.",
    ]


def build_spec_ops_acquisition_lines(game_state) -> list[str]:
    completed = set(getattr(game_state, "completed_research", []))
    unlocks = [
        project.id
        for project in game_state.research_tree.projects.values()
        if project.category in {"robot", "power_armor"} and project.id in completed
    ]
    return [
        "Acquisition flow",
        f"Unlock in Research Lab ({len(unlocks)} completed robot/power-armor projects).",
        "Purchase/assign in Armory and Spec-Ops room via Toggle support.",
        "Power armor users: requires one selected deployable agent per suit.",
    ]


def build_mission_prep_asset_state_lines(game_state) -> list[str]:
    selected_agents = selected_deployable_agents(
        game_state.characters, game_state.selected_agent_names
    )
    ready_assets = deployable_assets(game_state.spec_ops_assets, selected_agents)
    selected_ids = set(game_state.selected_asset_ids)
    selected_assets = [asset for asset in ready_assets if asset.id in selected_ids]
    total_fuel = sum(a.maintenance.fuel_cost_per_deploy for a in selected_assets)
    total_ammo = sum(a.maintenance.ammo_cost_per_deploy for a in selected_assets)
    return [
        "Mission prep asset state",
        f"Selected support assets: {len(selected_assets)}",
        f"Slot limits: {len(selected_assets)}/{len(ready_assets)} ready slots",
        f"Projected fuel cost: {total_fuel}",
        f"Projected ammo cost: {total_ammo}",
        f"Projected maintenance/repair cycle: {sum(a.maintenance.maintenance_cost for a in selected_assets)}",
    ]


def battle_unit_label_and_hint(unit) -> tuple[str, str]:
    if unit.spec_ops_asset:
        label = "Support Asset"
        hint = "Asset actions: Fire/Missiles/Defend; does not use morale abilities."
        return label, hint
    return "Agent", "Agent actions: Fire/Melee/Psi/First Aid based on loadout."


def build_asset_outcome_lines(game_state) -> list[str]:
    outcomes = getattr(game_state, "latest_spec_ops_outcomes", [])
    if not outcomes:
        return ["Spec-ops outcomes", "No deployed support assets in last mission."]
    lines = ["Spec-ops outcomes"]
    for row in outcomes:
        lines.append(
            f"{row['name']}: damage {row['damage']}%, repair {row['repair_cost']}, cooldown {row['cooldown_days']}d"
        )
    return lines
