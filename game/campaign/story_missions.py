"""Story mission templates — 10 special missions (2 per act) that advance the campaign.

Story missions appear on the mission board with a [STORY] marker. Completing them
awards intel fragments and updates world state.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class StoryMissionTemplate:
    id: str
    act: int
    title: str
    briefing: str         # 1-paragraph atmospheric briefing for the mission board
    objective_text: str   # short objective for the battle HUD
    objective_type: str   # reuse existing BattleObjective types
    risk_level: int       # 1-10
    fund_reward: int
    enemy_theme: str = "generic"
    intel_rewards: list[str] = field(default_factory=list)  # fragment IDs on success
    world_effects: dict[str, str] = field(default_factory=dict)  # WorldState updates
    tags: list[str] = field(default_factory=list)


STORY_MISSIONS: list[StoryMissionTemplate] = [
    # ── Act I ────────────────────────────────────────────────────────────────
    StoryMissionTemplate(
        id="sm_act1_espionage",
        act=1,
        title="Operation: Ivory Static",
        briefing=(
            "Corporate signals intelligence has intercepted an unusual encrypted broadcast "
            "originating from the Warsaw grid. The transmission uses a cipher not registered "
            "with any known megacorporation. Your team is to penetrate the relay station, "
            "copy the archive, and extract before Three Sevens security sweeps the area. "
            "What we find may explain the new banner flying over Warsaw."
        ),
        objective_text="Extract data from Warsaw relay station",
        objective_type="data_theft",
        risk_level=4,
        fund_reward=2500,
        enemy_theme="corp_37",
        intel_rewards=["act1_three_sevens_banner"],
        tags=["espionage", "three_sevens", "story"],
    ),
    StoryMissionTemplate(
        id="sm_act1_recon",
        act=1,
        title="Badlands Survey: Grid 7",
        briefing=(
            "Recon drones in Badlands sector 7 have gone dark. Three consecutive units lost "
            "contact over 48 hours — unusual even for the irradiated zones. "
            "Your team will insert by vehicle, recover the final drone's data core, "
            "and document any Hungry activity in the area. "
            "Command wants eyes on whatever is making the packs disappear."
        ),
        objective_text="Recover drone data core from sector 7",
        objective_type="extract",
        risk_level=5,
        fund_reward=2000,
        enemy_theme="starver",
        intel_rewards=["act1_badlands_silence", "act1_recon_anomaly"],
        tags=["recon", "badlands", "hungry", "story"],
    ),

    # ── Act II ───────────────────────────────────────────────────────────────
    StoryMissionTemplate(
        id="sm_act2_drone",
        act=2,
        title="Recover Drone 7-Whiskey",
        briefing=(
            "Megacity Defense Command has confirmed a long-range surveillance drone "
            "carrying classified Tide telemetry has been shot down over contested territory. "
            "The data it carries — raw movement vectors for the converging Hungry front — "
            "is worth more than the hardware. Extract the data core before scavengers or "
            "Three Sevens agents reach the crash site. "
            "What the drone recorded will change how we see the Tide."
        ),
        objective_text="Recover crashed drone data from combat zone",
        objective_type="extract",
        risk_level=5,
        fund_reward=3000,
        enemy_theme="corp_37_robot",
        intel_rewards=["act2_tide_forming", "act2_new_york_target"],
        world_effects={"new_york_status": "alert"},
        tags=["recovery", "tide", "megacorporation", "story"],
    ),
    StoryMissionTemplate(
        id="sm_act2_data",
        act=2,
        title="Corporate Archive: Tide Estimates",
        briefing=(
            "Internal Global Corporate Council records show a classified assessment "
            "of the Hungry convergence that contradicts their public statements. "
            "They know. They have known for months. "
            "Your mission is to breach the Council's local archive node and copy "
            "the suppressed estimate files before scheduled purge at 0600. "
            "The world deserves to know what its leaders are hiding."
        ),
        objective_text="Copy suppressed Tide estimate files",
        objective_type="data_theft",
        risk_level=6,
        fund_reward=2800,
        enemy_theme="corp_samurai",
        intel_rewards=["act2_corporate_denial", "act2_tide_growth"],
        tags=["data_theft", "corporate", "cover_up", "story"],
    ),

    # ── Act III ──────────────────────────────────────────────────────────────
    StoryMissionTemplate(
        id="sm_act3_perf",
        act=3,
        title="Extraction: Memory Subject Alpha",
        briefing=(
            "One of the Perfs — an individual with enhanced physical capabilities and "
            "complete memory loss — has been identified in the Warrens district. "
            "She is disoriented and being tracked by Three Sevens recovery teams. "
            "Extract her before they do. Alive. Unharmed. "
            "She may not remember who she was, but what her genome contains "
            "could tell us everything about what Three Sevens is building."
        ),
        objective_text="Extract the Perf before Three Sevens agents arrive",
        objective_type="extract",
        risk_level=7,
        fund_reward=3500,
        enemy_theme="corp_samurai_power_armor",
        intel_rewards=["act3_perf_sighting", "act3_perf_origin"],
        world_effects={"perfs_status": "understood"},
        tags=["extraction", "perf", "three_sevens", "story"],
    ),
    StoryMissionTemplate(
        id="sm_act3_delhi",
        act=3,
        title="Infiltrate New Delhi Grid 12",
        briefing=(
            "A signal from deep beneath the officially-dead ruins of New Delhi "
            "has been confirmed as human in origin — structured, deliberate, repeating. "
            "Someone survived. Possibly many people. "
            "Your team will insert through the outer exclusion zone and make contact. "
            "The corporate blockade on New Delhi information means we go in without backup. "
            "Whatever they have preserved could rewrite history."
        ),
        objective_text="Make contact with New Delhi underground survivors",
        objective_type="extract",
        risk_level=8,
        fund_reward=4000,
        enemy_theme="raider",
        intel_rewards=["act3_new_delhi", "act3_underground", "act3_cure_signal"],
        world_effects={"new_delhi_status": "revealed", "pharmacorp_secret": "rumored"},
        tags=["infiltration", "new_delhi", "archive", "story"],
    ),

    # ── Act IV ───────────────────────────────────────────────────────────────
    StoryMissionTemplate(
        id="sm_act4_hungry",
        act=4,
        title="Follow the Cured Subject",
        briefing=(
            "A Hungry who spontaneously regained consciousness has been tracked "
            "to a facility in the industrial sector. Pharmacorp security is on site. "
            "The facility is not listed in any public record. "
            "Your mission: breach the perimeter, reach the research wing, "
            "extract documentation on whatever treatment was administered. "
            "This could be the most important building in the world right now."
        ),
        objective_text="Breach Pharmacorp black site and extract research data",
        objective_type="data_theft",
        risk_level=8,
        fund_reward=5000,
        enemy_theme="mutant",
        intel_rewards=["act4_hungry_thinks", "act4_pharmacorp_secret"],
        world_effects={"pharmacorp_secret": "exposed"},
        tags=["pharmacorp", "cure", "infiltration", "story"],
    ),
    StoryMissionTemplate(
        id="sm_act4_archive",
        act=4,
        title="Breach the AI Node Cache",
        briefing=(
            "An anomalous network node has been pinpointed beneath the old financial district. "
            "It is not human infrastructure. The computing architecture is unlike anything "
            "in any engineering catalog. It has been operational — undetected — for decades. "
            "Someone has been using humanity's own communications backbone "
            "to watch, record, and possibly steer events. "
            "Breach the physical housing. Copy what you find. "
            "Get out before the second faction's response team arrives."
        ),
        objective_text="Breach the AI node and extract its activity logs",
        objective_type="sabotage",
        risk_level=9,
        fund_reward=6000,
        enemy_theme="corp_samurai_robot",
        intel_rewards=["act4_ai_pattern", "act4_ai_existence", "act4_ai_factions"],
        world_effects={"ai_factions_status": "confirmed"},
        tags=["ai", "infiltration", "archive", "story"],
    ),

    # ── Act V ────────────────────────────────────────────────────────────────
    StoryMissionTemplate(
        id="sm_act5_citadel",
        act=5,
        title="Warsaw Citadel Raid",
        briefing=(
            "The information is confirmed. The rulers of the Three Sevens are not who "
            "the world believes them to be. The genetic evidence is in the Citadel's "
            "biometric archive — the one system they trusted enough to never encrypt remotely. "
            "This is the most heavily defended target we have ever approached. "
            "But if we get the data out, the world will know the truth. "
            "All of it. Everything they have spent a century hiding."
        ),
        objective_text="Breach Warsaw Citadel biometric archive",
        objective_type="data_theft",
        risk_level=10,
        fund_reward=8000,
        enemy_theme="corp_37_power_armor",
        intel_rewards=["act5_twenty_one", "act5_clone_truth"],
        tags=["three_sevens", "warsaw", "finale", "story"],
    ),
    StoryMissionTemplate(
        id="sm_act5_expose",
        act=5,
        title="Broadcast: The Pharmacorp File",
        briefing=(
            "New York is under siege. The Three Sevens are preparing emergency decrees "
            "that will give them global authority over disaster response. "
            "The Pharmacorp cure exists. The data is in our hands. "
            "One broadcast tower in New York's media district can reach every megacity simultaneously. "
            "If we reach it — if we can hold it long enough — the secret ends tonight. "
            "The world will know there is a cure. And nothing will ever be the same."
        ),
        objective_text="Hold the broadcast tower and transmit the Pharmacorp file",
        objective_type="defend",
        risk_level=10,
        fund_reward=10000,
        enemy_theme="corp_37_robot",
        intel_rewards=["act5_final_choice", "act5_endgame"],
        world_effects={"pharmacorp_secret": "exposed", "new_york_status": "siege"},
        tags=["pharmacorp", "new_york", "broadcast", "finale", "story"],
    ),
]

STORY_MISSIONS_BY_ID: dict[str, StoryMissionTemplate] = {m.id: m for m in STORY_MISSIONS}


def story_missions_for_act(act: int) -> list[StoryMissionTemplate]:
    return [m for m in STORY_MISSIONS if m.act == act]


def get_story_mission(mission_id: str) -> StoryMissionTemplate | None:
    return STORY_MISSIONS_BY_ID.get(mission_id)
