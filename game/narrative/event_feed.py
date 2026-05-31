"""Aggregate compact narrative beats for agent-centered command feed."""

from __future__ import annotations

from dataclasses import dataclass


FEED_DEPTH_DEFAULT = 10
FEED_DEPTH_MIN = 8
FEED_DEPTH_MAX = 12


@dataclass(frozen=True)
class NarrativeFeedEntry:
    """Render-neutral narrative beat with a lightweight visual category."""

    category: str
    text: str


def clamp_feed_depth(depth: int) -> int:
    """Keep feed depth within readability bounds."""
    return max(FEED_DEPTH_MIN, min(FEED_DEPTH_MAX, int(depth)))


def _from_aftermath(latest_agent_aftermath: list[str]) -> list[NarrativeFeedEntry]:
    return [
        NarrativeFeedEntry("agent", line.removeprefix("Aftermath: "))
        for line in latest_agent_aftermath
        if line
    ]


def _from_recovery_dialogues(recovery_dialogues: list[dict]) -> list[NarrativeFeedEntry]:
    entries: list[NarrativeFeedEntry] = []
    for dialogue in recovery_dialogues:
        line = str(dialogue.get("line", "")).strip()
        if line:
            entries.append(NarrativeFeedEntry("agent", line))
    return entries


def _from_strategic_events(active_events: list[object], current_day: int) -> list[NarrativeFeedEntry]:
    entries: list[NarrativeFeedEntry] = []
    for event in active_events:
        days_remaining = event.days_remaining(current_day)
        entries.append(
            NarrativeFeedEntry(
                "mission",
                f"{event.title} ({event.category}) - D-{days_remaining} until expiration.",
            )
        )
    return entries


def _from_faction_rewards(faction_reward_journal: list[dict]) -> list[NarrativeFeedEntry]:
    entries: list[NarrativeFeedEntry] = []
    for reward in faction_reward_journal:
        text = str(reward.get("text", "")).strip()
        if not text:
            continue
        entries.append(NarrativeFeedEntry("faction", text))
    return entries


def _from_debrief_skill_checks(latest_mission_debrief: dict) -> list[NarrativeFeedEntry]:
    outcomes = latest_mission_debrief.get("skill_check_outcomes", [])
    return [
        NarrativeFeedEntry("mission", line)
        for line in outcomes
        if str(line).strip()
    ]


def build_narrative_event_feed(game_state, max_entries: int = FEED_DEPTH_DEFAULT) -> list[NarrativeFeedEntry]:
    """Build a short anti-chronological narrative feed across core story sources."""
    capped = clamp_feed_depth(max_entries)
    entries: list[NarrativeFeedEntry] = []
    entries.extend(_from_aftermath(getattr(game_state, "latest_agent_aftermath", [])))
    entries.extend(
        _from_recovery_dialogues(getattr(game_state, "latest_recovery_dialogues", []))
    )
    entries.extend(
        _from_strategic_events(
            getattr(game_state, "active_events", []),
            getattr(getattr(game_state, "calendar", None), "current_day", 0),
        )
    )
    entries.extend(_from_faction_rewards(getattr(game_state, "faction_reward_journal", [])))
    entries.extend(
        _from_debrief_skill_checks(getattr(game_state, "latest_mission_debrief", {}))
    )
    # Campaign intel fragments (most recent 3)
    entries.extend(_from_campaign_intel(game_state))

    # Source lists are append-only, so latest items live at the end.
    return entries[-capped:][::-1]


def _from_campaign_intel(game_state) -> list[NarrativeFeedEntry]:
    """Inject the 3 most recently discovered campaign intel fragments into the feed."""
    try:
        campaign = getattr(game_state, "campaign", None)
        if campaign is None:
            return []
        from game.campaign.intel_fragments import get_fragment

        recent = list(reversed(campaign.discovered_intel))[:3]
        result = []
        for fid in recent:
            frag = get_fragment(fid)
            if frag:
                result.append(
                    NarrativeFeedEntry(
                        category="intel",
                        text=f"[INTEL] {frag.title}: {frag.text[:100]}...",
                    )
                )
        return result
    except Exception:
        return []
