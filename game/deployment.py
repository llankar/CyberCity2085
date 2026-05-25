"""Mission deployment selection helpers."""

from __future__ import annotations

from dataclasses import dataclass

from .character import Character, is_deployable
from .management.spec_ops_assets import SpecOpsAsset


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
    characters: list[Character], selected_agent_names: list[str], index: int
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
    deployable: list[SpecOpsAsset] = []
    pilots_reserved = 0
    for asset in assets:
        if not asset.is_deployable:
            continue
        if asset.pilot_required:
            if pilot_count <= pilots_reserved:
                continue
            pilots_reserved += 1
        deployable.append(asset)
    return deployable


def selected_deployable_assets(
    assets: list[SpecOpsAsset],
    selected_asset_ids: list[str],
    selected_agents: list[Character] | None = None,
) -> list[SpecOpsAsset]:
    """Return selected deployable assets, preserving hangar order."""
    selected_ids = set(selected_asset_ids)
    return [
        asset
        for asset in deployable_assets(assets, selected_agents)
        if asset.id in selected_ids
    ]


def sanitize_selected_asset_ids(
    assets: list[SpecOpsAsset],
    selected_asset_ids: list[str],
    selected_agents: list[Character] | None = None,
) -> list[str]:
    """Drop damaged, missing, duplicate, or unpiloted assets from selection."""
    deployable_ids = {asset.id for asset in deployable_assets(assets, selected_agents)}
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
