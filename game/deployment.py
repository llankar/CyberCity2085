"""Mission deployment selection helpers."""

from __future__ import annotations

from .character import Character, is_deployable


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
