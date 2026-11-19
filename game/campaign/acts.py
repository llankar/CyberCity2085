"""Act metadata — titles, opening texts, and faction reveal logic."""

from __future__ import annotations

ACT_TITLES: dict[int, str] = {
    1: "Dawn of Tyranny",
    2: "The Tide",
    3: "Lies",
    4: "The Truth",
    5: "The Seven",
}

ACT_OPENING_TEXTS: dict[int, str] = {
    1: (
        "The Three Sevens Corporation has seized Warsaw. "
        "The world watches. Strange reports arrive from the Badlands. "
        "Something has begun."
    ),
    2: (
        "Recon drones detect something impossible. "
        "Hundreds of Hungry packs are converging. Then thousands. "
        "Their destination: New York."
    ),
    3: (
        "Exceptional individuals begin appearing — enhanced, amnesiac, hunted. "
        "Deep beneath the ruins of New Delhi, four hundred thousand people still live. "
        "And somewhere in a black-site archive, a cure that should not exist."
    ),
    4: (
        "A Hungry regains her mind. History shows the fingerprints of invisible hands. "
        "Something non-human has been watching from the infrastructure of civilization. "
        "Two factions. Two agendas. Both older than any living person."
    ),
    5: (
        "New York is under siege. The Three Sevens prepare global authority decrees. "
        "Twenty-one individuals have been building toward this moment for a century. "
        "The question is not who wins. The question is what kind of world is worth winning."
    ),
}

ACT_WORLD_FACTIONS: dict[int, list[str]] = {
    1: ["Three Sevens Corp"],
    2: ["Three Sevens Corp"],
    3: ["Three Sevens Corp", "Pharmacorp"],
    4: ["Three Sevens Corp", "Pharmacorp", "Preservationist AIs", "Exterminator AIs"],
    5: ["Three Sevens Corp", "Pharmacorp", "Preservationist AIs", "Exterminator AIs"],
}


def factions_revealed_at_act(act: int) -> list[str]:
    """Return faction names that become visible to the player at this act."""
    revealed = []
    if act >= 1:
        revealed.append("Three Sevens Corp")
    if act >= 3:
        revealed.append("Pharmacorp")
    if act >= 4:
        revealed.extend(["Preservationist AIs", "Exterminator AIs"])
    return revealed
