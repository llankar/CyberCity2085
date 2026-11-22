from game.narrative.agent_memory import latest_tactical_memory, tactical_memory_summary


def test_selects_latest_known_tactical_memory_only() -> None:
    history = [
        "Routine certification renewed.",
        "Old Mission: held on at 1 HP and neutralized a hostile.",
        "New Mission: saw Rook fall under fire.",
    ]

    assert latest_tactical_memory(history) == history[-1]
    assert tactical_memory_summary(history) == "saw Rook fall under fire"


def test_returns_empty_for_non_tactical_or_missing_history() -> None:
    assert latest_tactical_memory(["Joined the squad."]) == ""
    assert tactical_memory_summary(None) == ""
