"""English-only tutorial and help copy for first-session onboarding."""

from __future__ import annotations

TUTORIAL_TITLES = {
    "enter_rooms": "Open a room",
    "select_agents": "Select an agent",
    "form_squad": "Form your squad",
    "open_mission_board": "Open mission board",
    "launch_mission": "Launch mission",
    "basic_battle_controls": "Learn battle controls",
}

TUTORIAL_OBJECTIVES = {
    "enter_rooms": "Open any highlighted room in Corp or City command.",
    "select_agents": "Move agent focus and toggle at least one agent.",
    "form_squad": "Select at least two deployable agents.",
    "open_mission_board": "Open the squad Operations Table room.",
    "launch_mission": "Launch the selected mission from Insertion or Ops.",
    "basic_battle_controls": "Use one move and one attack control in battle.",
}

HELP_COPY = {
    "corp": {
        "next": "Open rooms to allocate resources, then transition to Squad (R).",
        "controls": ["H help", "Click rooms", "R squad", "C city", "D advance day"],
    },
    "city": {
        "next": "Stabilize district pressure, then hand off to Squad (R).",
        "controls": ["H help", "Click rooms", "R squad", "D advance day"],
    },
    "squad": {
        "next": "Pick a mission, select agents, then launch.",
        "controls": ["H help", "A/D agent", "Space toggle", "B launch", "Click cards/actions"],
    },
    "battle": {
        "next": "Advance, attack, and complete the objective marker.",
        "controls": ["Arrows move", "F fire", "Space melee", "P psi", "E interact", "Enter end turn"],
    },
}
