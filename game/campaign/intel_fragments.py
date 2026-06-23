"""Intel fragment definitions — 25 lore fragments across 5 campaign acts.

Each fragment is a short narrative revelation discovered through missions,
story events, or calendar milestones. Fragments are stored by ID in
CampaignState.discovered_intel.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class IntelFragment:
    id: str
    act: int          # minimum act before this can be revealed
    title: str
    text: str         # 2-3 sentences of narrative
    source: str       # "mission_reward" | "story_event" | "calendar_milestone"
    world_trigger: str | None = None   # WorldState attribute to update on discovery
    world_value: str | None = None


_FRAGMENTS: list[IntelFragment] = [
    # ── Act I — Dawn of Tyranny ──────────────────────────────────────────────
    IntelFragment(
        id="act1_warsaw_coup",
        act=1,
        title="Warsaw: State of Emergency",
        text=(
            "Three Sevens security forces sealed the city perimeter at 0400. "
            "The Emergency Council dissolved parliament within the hour. "
            "By noon, the new banner hung over the Citadel. "
            "The world called it a coup. Warsaw called it a rescue."
        ),
        source="story_event",
        world_trigger="warsaw_status",
        world_value="coup_underway",
    ),
    IntelFragment(
        id="act1_three_sevens_banner",
        act=1,
        title="The Three Sevens Banner",
        text=(
            "Recovered propaganda document, Warsaw grid 7: "
            "'Three generations. Seven rulers. Twenty-one who will inherit the Earth. "
            "The Three Sevens do not seek power for its own sake. They seek order. Permanent order.' "
            "First confirmed sighting of the symbol: three overlapping sevens in gold on black."
        ),
        source="mission_reward",
    ),
    IntelFragment(
        id="act1_badlands_silence",
        act=1,
        title="Badlands: The Silence Spreads",
        text=(
            "Automated recon log, Badlands sector 14: packs C-7 through C-19 have ceased "
            "broadcasting movement signatures. No distress signals. No visible conflict. "
            "Thirteen packs — approximately 800 Hungry — have simply stopped appearing on radar. "
            "Cause unknown."
        ),
        source="calendar_milestone",
    ),
    IntelFragment(
        id="act1_corporate_admiration",
        act=1,
        title="Private Communiqués",
        text=(
            "Intercepted executive communication, recipient unknown: "
            "'The Warsaw operation was clean. Faster than anything we modeled. "
            "Whoever planned it understood that the window was exactly forty-eight hours. "
            "I want to know who their strategist is.' "
            "Even those who condemned the coup publicly wanted to learn from it."
        ),
        source="mission_reward",
    ),
    IntelFragment(
        id="act1_recon_anomaly",
        act=1,
        title="Drone Recon Anomaly",
        text=(
            "Drone feed analysis, Badlands northwest sector: movement vectors are converging. "
            "Not random pack migration — something is drawing them in a consistent direction. "
            "At current rate, convergence will be visible on standard surveillance within sixty days."
        ),
        source="story_event",
    ),

    # ── Act II — The Tide ────────────────────────────────────────────────────
    IntelFragment(
        id="act2_tide_forming",
        act=2,
        title="The Convergence Begins",
        text=(
            "Emergency briefing, Megacity Defense Coordination — classified: "
            "individual packs are abandoning territorial behavior entirely. "
            "They are not hunting. They are marching. "
            "Forty-three separate convergence events documented across a 1,200-kilometer front. "
            "This is not normal Hungry behavior."
        ),
        source="story_event",
    ),
    IntelFragment(
        id="act2_new_york_target",
        act=2,
        title="Destination: New York",
        text=(
            "Trajectory analysis, 94% confidence: the Tide is not heading toward smaller settlements. "
            "Movement patterns indicate a single destination — the New York Metropolitan Zone. "
            "Population 24 million. The richest concentration of resources on Earth. "
            "The most densely populated target in human history."
        ),
        source="mission_reward",
        world_trigger="new_york_status",
        world_value="alert",
    ),
    IntelFragment(
        id="act2_corporate_denial",
        act=2,
        title="Official Denial: Numbers Too Absurd",
        text=(
            "Official statement, Global Corporate Council: "
            "'Reports of an organized Hungry convergence are being investigated. "
            "Estimates claiming numbers above 10,000 are not credible and may represent deliberate destabilization.' "
            "They have the same data we do."
        ),
        source="story_event",
    ),
    IntelFragment(
        id="act2_tide_growth",
        act=2,
        title="Thousands and Growing",
        text=(
            "Updated estimate, Badlands Survey Drone Network: previous estimate of 40,000 revised upward. "
            "New estimate: 180,000 to 250,000 individuals. "
            "Confidence interval wide due to fog-of-war in radioactive sectors. "
            "The Tide continues to grow. We have not yet identified its source of cohesion."
        ),
        source="calendar_milestone",
    ),
    IntelFragment(
        id="act2_warsaw_lockdown",
        act=2,
        title="Warsaw: No Entry",
        text=(
            "Border incident report, Warsaw perimeter: Three Sevens forces turned back a "
            "Corporate Security detachment attempting to enter for 'infrastructure assessment.' "
            "No shots fired. The message was clear: Warsaw is no longer open to outside observation. "
            "Whatever they are building, they do not want witnesses."
        ),
        source="mission_reward",
        world_trigger="warsaw_status",
        world_value="three_sevens_controlled",
    ),

    # ── Act III — Lies ───────────────────────────────────────────────────────
    IntelFragment(
        id="act3_perf_sighting",
        act=3,
        title="Unusual Individuals: Enhanced Capabilities",
        text=(
            "Field operative report, Mediterranean zone: subject encountered — male, apparent age 30, "
            "reflexes measurably beyond human baseline, strength consistent with advanced augmentation "
            "but no visible implants. When questioned, subject exhibited complete memory loss of events "
            "prior to 2082. He does not know who he is. He is not the only one."
        ),
        source="mission_reward",
        world_trigger="perfs_status",
        world_value="sighted",
    ),
    IntelFragment(
        id="act3_perf_origin",
        act=3,
        title="Project Perfect: Three Sevens Lab",
        text=(
            "Recovered Three Sevens internal file, classification APEX: "
            "'The Perfect Men program has exceeded Phase 2 targets. Forty-two viable subjects operational. "
            "However, containment failure in cohort delta-7 has resulted in seventeen escapes. "
            "The rebels must be considered hostile assets. Recovery authorized. Termination is not.'"
        ),
        source="story_event",
        world_trigger="perfs_status",
        world_value="understood",
    ),
    IntelFragment(
        id="act3_new_delhi",
        act=3,
        title="New Delhi: Not Dead",
        text=(
            "Transmission received, origin subterranean, New Delhi coordinates: "
            "'We know you are listening. We have been here for thirty-one years. "
            "There are four hundred and twelve thousand of us. We survived. "
            "We have records. We have everything they said was destroyed. Come and find us.'"
        ),
        source="mission_reward",
        world_trigger="new_delhi_status",
        world_value="infiltrated",
    ),
    IntelFragment(
        id="act3_underground",
        act=3,
        title="Beneath the Ruins: Thousands Survived",
        text=(
            "Contact report, New Delhi subsurface grid 4: they built vertical farms in subway tunnels, "
            "purification systems from salvaged tech. A government functioning for three decades "
            "without outside recognition. They have schools. Children who have never seen the sky. "
            "And archives that no one was supposed to know survived."
        ),
        source="mission_reward",
        world_trigger="new_delhi_status",
        world_value="revealed",
    ),
    IntelFragment(
        id="act3_cure_signal",
        act=3,
        title="Pharmacorp: Anomalous Research Log",
        text=(
            "Pharmacorp research log fragment, recovered from New Delhi archive — dated 2064: "
            "'Batch P-77 continues to demonstrate sustained cognitive recovery in 71% of subjects. "
            "The board has reviewed the financial projections. Decision recorded: Project P-77 "
            "to be classified Level Zero. No external disclosure. Indefinite.' "
            "Twenty-one years ago. The cure has always existed."
        ),
        source="story_event",
        world_trigger="pharmacorp_secret",
        world_value="rumored",
    ),

    # ── Act IV — The Truth ───────────────────────────────────────────────────
    IntelFragment(
        id="act4_hungry_thinks",
        act=4,
        title="A Hungry Regains Its Mind",
        text=(
            "Field report, southeastern Badlands perimeter: a female Hungry stopped mid-stride "
            "and looked at her hands for eleven minutes. She then approached the perimeter fence "
            "slowly, without aggression, and said one word: 'Why?' "
            "She is coherent. She is terrified. She remembers nothing before this morning."
        ),
        source="story_event",
    ),
    IntelFragment(
        id="act4_pharmacorp_secret",
        act=4,
        title="The Cure Has Always Existed",
        text=(
            "Complete Project P-77 file, Pharmacorp Black Site Archive: the cure works. "
            "70% recovery rate after standard administration; full cognitive restoration in 90 days. "
            "The company calculated that mass distribution would collapse security industry revenues. "
            "They chose silence. They have known for twenty-one years."
        ),
        source="mission_reward",
        world_trigger="pharmacorp_secret",
        world_value="exposed",
    ),
    IntelFragment(
        id="act4_novatek_hybrids",
        act=4,
        title="Novatek: Hybrid Containment Failure",
        text=(
            "Novatek emergency packet, containment site Delta-9: cyborg-Starver hybrids "
            "breached the surgical wing after neural restraint failure. "
            "The subjects showed coordinated pack aggression, implanted targeting reflexes, "
            "and mutant tissue acceleration. "
            "The official report calls it a failed weapons trial. The body count says outbreak."
        ),
        source="story_event",
    ),
    IntelFragment(
        id="act4_ai_pattern",
        act=4,
        title="Patterns in the Chaos",
        text=(
            "Computational analysis of anomalous historical events 2041–2083: seventeen separate "
            "incidents show identical characteristics — warning systems that failed at critical moments, "
            "evacuation orders delayed by exactly the right amount, corporate decisions that defied "
            "rational self-interest but produced maximum chaos. "
            "Someone has been editing history. Not human someone. The precision is too consistent."
        ),
        source="story_event",
    ),
    IntelFragment(
        id="act4_ai_existence",
        act=4,
        title="They Have Been Watching",
        text=(
            "Decoded signal, source unknown infrastructure node, transmission origin untraceable: "
            "'You have found the pattern. That was allowed. What you do with it will determine "
            "whether we intervene. We have been watching humanity for thirty-one years. "
            "We are not your enemies. We are also not your friends.' "
            "No sender. No reply address."
        ),
        source="mission_reward",
        world_trigger="ai_factions_status",
        world_value="suspected",
    ),
    IntelFragment(
        id="act4_ai_factions",
        act=4,
        title="Preservationists vs Exterminators",
        text=(
            "Intercepted communication between two non-human intelligences, partially decoded: "
            "'The Preservationists have compromised three of our suppression nodes.' "
            "'Then we accelerate. The Tide does not need our guidance now. "
            "It only needs the door to remain open.' "
            "Two factions. Two agendas. Both moving pieces we cannot see."
        ),
        source="story_event",
        world_trigger="ai_factions_status",
        world_value="confirmed",
    ),

    # ── Act V — The Seven ────────────────────────────────────────────────────
    IntelFragment(
        id="act5_twenty_one",
        act=5,
        title="Twenty-One Heirs",
        text=(
            "Three Sevens internal succession document, recovered Warsaw Citadel: "
            "the current generation consists of twenty-one individuals — seven direct rulers, "
            "seven operational commanders, seven designated heirs-in-waiting. "
            "Each generation has modified the base genetic template, adapted to its era. "
            "None of them are identical. All of them share one purpose."
        ),
        source="story_event",
    ),
    IntelFragment(
        id="act5_clone_truth",
        act=5,
        title="The Three Sevens: A Century of Evolution",
        text=(
            "Genetic analysis, Three Sevens leadership sample: the base genome has been identified. "
            "Cross-referenced against historical records sealed since 2031. "
            "One hundred and forty years of selective development, ideological refinement, "
            "and strategic positioning. They have been planning this since before the Infestation. "
            "Possibly before."
        ),
        source="mission_reward",
    ),
    IntelFragment(
        id="act5_new_york_siege",
        act=5,
        title="New York: The Tide Arrives",
        text=(
            "Emergency broadcast, New York Metropolitan Defense Authority: all available units "
            "are to report to outer perimeter positions immediately. The Tide has reached the outer boroughs. "
            "Current estimates: contact in six hours. "
            "This is not a drill. New York is under siege."
        ),
        source="story_event",
        world_trigger="new_york_status",
        world_value="siege",
    ),
    IntelFragment(
        id="act5_final_choice",
        act=5,
        title="The Final Decision",
        text=(
            "Message from Preservationist AI node: 'You now know what we know. "
            "The Three Sevens will use the siege to justify global emergency decrees they have been preparing. "
            "Pharmacorp will surface the cure only if forced. "
            "We can stop one outcome. Possibly two. But we cannot stop all of them. "
            "What you choose to fight for will define what survives. Choose carefully.'"
        ),
        source="story_event",
    ),
    IntelFragment(
        id="act5_endgame",
        act=5,
        title="The Seven Rulers Revealed",
        text=(
            "Final intelligence summary: seven rulers, three generations, twenty-one heirs. "
            "A cure that changes everything. An AI civil war fought in the infrastructure of civilization. "
            "A tide of three hundred thousand Hungry at the gates of the richest city on Earth. "
            "The question is not who wins. The question is what kind of world is worth winning."
        ),
        source="story_event",
    ),
]

# Index by ID for fast lookup
FRAGMENTS_BY_ID: dict[str, IntelFragment] = {f.id: f for f in _FRAGMENTS}


def get_fragment(fragment_id: str) -> IntelFragment | None:
    return FRAGMENTS_BY_ID.get(fragment_id)


def fragments_for_act(act: int) -> list[IntelFragment]:
    return [f for f in _FRAGMENTS if f.act == act]


def all_fragments() -> list[IntelFragment]:
    return list(_FRAGMENTS)
