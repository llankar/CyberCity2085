"""Mission deployment selection helpers."""

from __future__ import annotations

from dataclasses import dataclass

from .character import Character, is_deployable
from .management.spec_ops_assets import SpecOpsAsset
from .combat.tactical_identity import profile_for_theme


def deployable_agents(characters: list[Character]) -> list[Character]:
    """Return agents who can currently be assigned to an operation."""
    return [character for character in characters if is_deployable(character)]


def selected_deployable_agents(
    characters: list[Character], selected_agent_names: list[str]
) -> list[Character]:
    """Return selected agents, preserving roster order and deployment safety."""
    selected_names = set(selected_agent_names)
    return [
        character
        for character in characters
        if character.name in selected_names and is_deployable(character)
    ]


def sanitize_selected_agent_names(
    characters: list[Character], selected_agent_names: list[str]
) -> list[str]:
    """Drop unavailable or no-longer-rostered agents from deployment selection."""
    deployable_names = {character.name for character in deployable_agents(characters)}
    sanitized: list[str] = []
    for name in selected_agent_names:
        if name in deployable_names and name not in sanitized:
            sanitized.append(name)
    return sanitized


def toggle_agent_selection(
    characters: list[Character], selected_agent_names: list[str], index: int,
    capacity: int | None = None,
) -> tuple[list[str], str]:
    """Toggle a roster slot and return the updated selection plus a readable result."""
    if index < 0 or index >= len(characters):
        return (
            sanitize_selected_agent_names(characters, selected_agent_names),
            "No agent selected.",
        )

    character = characters[index]
    sanitized = sanitize_selected_agent_names(characters, selected_agent_names)
    if not is_deployable(character):
        return sanitized, f"{character.name} is unavailable for deployment."

    if character.name in sanitized:
        sanitized.remove(character.name)
        return sanitized, f"{character.name} removed from the squad."

    if capacity is not None and len(sanitized) >= max(0, int(capacity)):
        return sanitized, f"Squad capacity reached ({capacity}). Upgrade the Hangar."

    sanitized.append(character.name)
    return sanitized, f"{character.name} added to the squad."


def remove_agent_from_roster(
    characters: list[Character],
    assets: list[SpecOpsAsset] | None,
    selected_agent_names: list[str],
    selected_asset_ids: list[str] | None,
    index: int,
) -> tuple[Character | None, list[str], list[str]]:
    """Remove an agent from the roster and clean dependent strategic selection."""
    if index < 0 or index >= len(characters):
        sanitized_agents = sanitize_selected_agent_names(characters, selected_agent_names)
        selected_agents = selected_deployable_agents(characters, sanitized_agents)
        sanitized_assets = sanitize_selected_asset_ids(
            assets or [], selected_asset_ids or [], selected_agents
        )
        return None, sanitized_agents, sanitized_assets

    removed = characters.pop(index)
    sanitized_agents = sanitize_selected_agent_names(characters, selected_agent_names)
    selected_agents = selected_deployable_agents(characters, sanitized_agents)
    sanitized_assets = sanitize_selected_asset_ids(
        assets or [], selected_asset_ids or [], selected_agents
    )
    return removed, sanitized_agents, sanitized_assets


@dataclass(frozen=True)
class DeploymentManifest:
    """Selected deployable agents plus support assets for one operation."""

    agents: list[Character]
    assets: list[SpecOpsAsset]

    @property
    def has_units(self) -> bool:
        return bool(self.agents or self.assets)

    @property
    def pilot_count(self) -> int:
        return len(self.agents)


def deployable_assets(
    assets: list[SpecOpsAsset], selected_agents: list[Character] | None = None
) -> list[SpecOpsAsset]:
    """Return robots/suits ready for deployment without replacing agent checks."""
    pilot_count = len(selected_agents or [])
    pilot_names = {agent.name for agent in selected_agents or []}
    reserved_names = set()
    deployable: list[SpecOpsAsset] = []
    pilots_reserved = 0
    for asset in assets:
        if not asset.is_deployable:
            continue
        if asset.pilot_required:
            name = asset.pilot_agent_name
            if name and (name not in pilot_names or name in reserved_names):
                continue
            if pilot_count <= pilots_reserved:
                continue
            pilots_reserved += 1
            if name:
                reserved_names.add(name)
        deployable.append(asset)
    return deployable


def selected_deployable_assets(
    assets: list[SpecOpsAsset],
    selected_asset_ids: list[str],
    selected_agents: list[Character] | None = None,
) -> list[SpecOpsAsset]:
    """Return selected deployable assets, preserving hangar order."""
    selected_ids = set(selected_asset_ids)
    return deployable_assets([asset for asset in assets if asset.id in selected_ids], selected_agents)


def sanitize_selected_asset_ids(
    assets: list[SpecOpsAsset],
    selected_asset_ids: list[str],
    selected_agents: list[Character] | None = None,
) -> list[str]:
    """Drop damaged, missing, duplicate, or unpiloted assets from selection."""
    deployable_ids = {asset.id for asset in selected_deployable_assets(assets, selected_asset_ids, selected_agents)}
    sanitized: list[str] = []
    for asset_id in selected_asset_ids:
        if asset_id in deployable_ids and asset_id not in sanitized:
            sanitized.append(asset_id)
    return sanitized


def selected_deployment_manifest(
    characters: list[Character],
    selected_agent_names: list[str],
    assets: list[SpecOpsAsset] | None = None,
    selected_asset_ids: list[str] | None = None,
) -> DeploymentManifest:
    """Build one tactical manifest where piloted armor replaces pilot entries."""
    agents = selected_deployable_agents(characters, selected_agent_names)
    selected_assets = selected_deployable_assets(
        assets or [], selected_asset_ids or [], agents
    )
    piloted_names = {
        asset.pilot_agent_name
        for asset in selected_assets
        if asset.pilot_required and getattr(asset, "pilot_agent_name", None)
    }
    mission_agents = [agent for agent in agents if agent.name not in piloted_names]
    return DeploymentManifest(agents=mission_agents, assets=selected_assets)


def toggle_asset_selection(
    assets: list[SpecOpsAsset],
    selected_asset_ids: list[str],
    selected_agents: list[Character] | None = None,
) -> tuple[list[str], str]:
    """Toggle one ready support asset while keeping agents as the squad focus."""
    deployable = deployable_assets(assets, selected_agents)
    sanitized = sanitize_selected_asset_ids(assets, selected_asset_ids, selected_agents)
    if not deployable:
        return sanitized, "No ready support assets in the hangar."

    for asset in deployable:
        if asset.id not in sanitized:
            sanitized.append(asset.id)
            return sanitized, f"{asset.name} added as support asset."

    removed_id = sanitized.pop(0)
    removed = next((asset for asset in assets if asset.id == removed_id), None)
    name = removed.name if removed else removed_id
    return sanitized, f"{name} removed from support assets."


@dataclass(frozen=True)
class TacticalBriefing:
    """Compact bridge between strategic squad preparation and tactical play."""

    enemy_label: str
    doctrine: str
    squad_count: int
    armed_count: int
    loadout_summary: str
    capability_summary: str
    tactical_gap: str
    recovery_load: str

    @property
    def ready(self) -> bool:
        return self.squad_count > 0 and self.armed_count == self.squad_count


def build_tactical_briefing(mission: object, selected_agents: list[Character]) -> TacticalBriefing:
    """Describe the opposition and whether the selected squad can fight immediately."""
    profile = profile_for_theme(getattr(mission, "enemy_theme", "generic"))
    armed = [agent for agent in selected_agents if agent.loadout.primary_weapon is not None]
    kits = [
        f"{agent.name}: {agent.loadout.primary_weapon.name if agent.loadout.primary_weapon else 'UNARMED'}"
        for agent in selected_agents[:3]
    ]
    if len(selected_agents) > 3:
        kits.append(f"+{len(selected_agents) - 3} more")

    roles = {str(agent.role).lower() for agent in selected_agents}
    ranges = [
        int(agent.loadout.primary_weapon.range_cells)
        for agent in selected_agents
        if agent.loadout.primary_weapon is not None
    ]
    capabilities: list[str] = []
    if roles & {"samurai", "robot"} or any(value <= 2 for value in ranges):
        capabilities.append("frontline")
    if "sniper" in roles or any(value >= 4 for value in ranges):
        capabilities.append("ranged")
    if "psi" in roles:
        capabilities.append("control")
    if roles & {"medic", "support"}:
        capabilities.append("support")

    if not selected_agents:
        tactical_gap = "Assign agents"
    elif len(selected_agents) < 2:
        tactical_gap = "Understrength squad"
    elif "frontline" not in capabilities:
        tactical_gap = "No frontline anchor"
    elif "ranged" not in capabilities:
        tactical_gap = "No ranged pressure"
    elif not ({"control", "support"} & set(capabilities)):
        tactical_gap = "No control/support specialist"
    else:
        tactical_gap = "Balanced response"

    average_stress = (
        sum(int(agent.stress) for agent in selected_agents) // len(selected_agents)
        if selected_agents
        else 0
    )
    recovery_score = average_stress + int(getattr(mission, "risk_level", 1)) * 8
    if len(selected_agents) == 1:
        recovery_score += 12
    recovery_load = (
        "CRITICAL" if recovery_score >= 95
        else "HIGH" if recovery_score >= 70
        else "MODERATE" if recovery_score >= 40
        else "LOW"
    )
    return TacticalBriefing(
        enemy_label=profile.label,
        doctrine=profile.doctrine,
        squad_count=len(selected_agents),
        armed_count=len(armed),
        loadout_summary=" | ".join(kits) if kits else "No agents assigned",
        capability_summary=" / ".join(capabilities).upper() if capabilities else "NONE",
        tactical_gap=tactical_gap,
        recovery_load=recovery_load,
    )
