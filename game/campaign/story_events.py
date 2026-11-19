"""Act-gated story events for the global campaign scenario.

These are one-time events that fire at specific campaign milestones. They reuse
the existing EventTemplate/ActiveEvent system in game/management/events.py.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


# Story event definitions as dicts — converted to EventTemplate instances at runtime
# to avoid circular imports. Keys match EventTemplate/EventChoice field names.
STORY_EVENT_SPECS: list[dict] = [
    # ── Act I ────────────────────────────────────────────────────────────────
    {
        "id": "campaign_warsaw_coup",
        "act": 1,
        "trigger_id": "campaign_warsaw_coup",
        "title": "Warsaw Falls to the Three Sevens",
        "description": (
            "Warsaw has been seized by the Three Sevens Corporation in a coordinated overnight operation. "
            "Civil liberties suspended. All external communications now filtered. "
            "The megacorporate world is watching — and some are taking notes."
        ),
        "category": "CORPORATE_POLITICS",
        "severity": 6,
        "expiration_days": 7,
        "intel_reveal": "act1_warsaw_coup",
        "world_effect": {"warsaw_status": "coup_underway"},
        "choices": [
            {
                "key": "denounce",
                "label": "Issue public condemnation",
                "summary": "Denounce the coup publicly. Faction relations shift.",
                "effects": {"faction_pressure": -10},
            },
            {
                "key": "monitor",
                "label": "Monitor and gather intelligence",
                "summary": "Stay quiet. Gather data. Await opportunity.",
                "effects": {},
            },
        ],
    },
    {
        "id": "campaign_badlands_silence",
        "act": 1,
        "trigger_id": "campaign_badlands_silence",
        "title": "Badlands: The Silence Spreads",
        "description": (
            "Multiple Hungry packs in the Badlands have stopped broadcasting movement signatures. "
            "No conflict recorded. No bodies. Just silence. "
            "Whatever is pulling them has grown more powerful."
        ),
        "category": "MUTANT_INVASION",
        "severity": 5,
        "expiration_days": 5,
        "intel_reveal": "act1_badlands_silence",
        "world_effect": {},
        "choices": [
            {
                "key": "investigate",
                "label": "Fund recon insertion",
                "summary": "Spend resources to investigate. May yield intel.",
                "effects": {"funds": -1000},
            },
            {
                "key": "wait",
                "label": "Log it and wait",
                "summary": "Document and observe. Low cost.",
                "effects": {},
            },
        ],
    },

    # ── Act II ───────────────────────────────────────────────────────────────
    {
        "id": "campaign_tide_confirmed",
        "act": 2,
        "trigger_id": "campaign_tide_confirmed",
        "title": "The Tide is Real",
        "description": (
            "Satellite imagery now confirms it: a convergent mass of Hungry unlike any recorded event. "
            "Dozens of packs moving with apparent coordination toward a single destination. "
            "Megacity Defense Command has classified the report. The public does not know."
        ),
        "category": "MUTANT_INVASION",
        "severity": 8,
        "expiration_days": 10,
        "intel_reveal": "act2_tide_forming",
        "world_effect": {"new_york_status": "alert"},
        "choices": [
            {
                "key": "warn",
                "label": "Warn allied corporations privately",
                "summary": "Share intelligence. Build trust with potential allies.",
                "effects": {"faction_pressure": 5},
            },
            {
                "key": "exploit",
                "label": "Position for profit",
                "summary": "Buy security contracts before the news breaks.",
                "effects": {"funds": 3000},
            },
        ],
    },
    {
        "id": "campaign_corporate_denial",
        "act": 2,
        "trigger_id": "campaign_corporate_denial",
        "title": "Corporate Denial Holds",
        "description": (
            "The Global Corporate Council has issued a second official denial of the Tide estimates. "
            "Internal communications show they have the same data we do. "
            "New York's defensive spending remains at peacetime levels."
        ),
        "category": "CORPORATE_POLITICS",
        "severity": 6,
        "expiration_days": 7,
        "intel_reveal": "act2_corporate_denial",
        "world_effect": {},
        "choices": [
            {
                "key": "leak",
                "label": "Leak the data to independent media",
                "summary": "Break the story. Public panic possible. Truth wins.",
                "effects": {"city_unrest": 20},
            },
            {
                "key": "hold",
                "label": "Hold the data for now",
                "summary": "Wait for a better moment. Keep the advantage.",
                "effects": {},
            },
        ],
    },

    # ── Act III ──────────────────────────────────────────────────────────────
    {
        "id": "campaign_perf_encounter",
        "act": 3,
        "trigger_id": "campaign_perf_encounter",
        "title": "Perf Encountered in the Field",
        "description": (
            "One of your operative teams encountered a genetically enhanced individual "
            "with no memory of their past. Physical capabilities beyond any known augmentation. "
            "The Three Sevens recovery team was two minutes behind them."
        ),
        "category": "SOCIAL_UNREST",
        "severity": 7,
        "expiration_days": 6,
        "intel_reveal": "act3_perf_sighting",
        "world_effect": {"perfs_status": "sighted"},
        "choices": [
            {
                "key": "extract",
                "label": "Extract the subject",
                "summary": "Protect them. Risk conflict with Three Sevens.",
                "effects": {"faction_pressure": 15},
            },
            {
                "key": "observe",
                "label": "Observe and document",
                "summary": "Gather data without engagement.",
                "effects": {},
            },
        ],
    },
    {
        "id": "campaign_new_delhi_signal",
        "act": 3,
        "trigger_id": "campaign_new_delhi_signal",
        "title": "Signal from Below New Delhi",
        "description": (
            "An encrypted transmission from beneath the officially dead ruins of New Delhi "
            "has been decoded. Hundreds of thousands of people have survived underground "
            "for thirty years — with archives that were never supposed to exist."
        ),
        "category": "CITY_POLITICS",
        "severity": 7,
        "expiration_days": 8,
        "intel_reveal": "act3_underground",
        "world_effect": {"new_delhi_status": "infiltrated"},
        "choices": [
            {
                "key": "respond",
                "label": "Establish contact",
                "summary": "Open communication. Access to archives.",
                "effects": {},
            },
            {
                "key": "verify",
                "label": "Verify authenticity first",
                "summary": "Could be a trap. Run verification protocols.",
                "effects": {"funds": -500},
            },
        ],
    },

    # ── Act IV ───────────────────────────────────────────────────────────────
    {
        "id": "campaign_hungry_speaks",
        "act": 4,
        "trigger_id": "campaign_hungry_speaks",
        "title": "A Hungry Speaks",
        "description": (
            "In a Badlands containment zone, a Hungry individual has spontaneously regained consciousness. "
            "She is coherent, frightened, and has no memory of the past decade. "
            "Pharmacorp has dispatched a retrieval team. They know what she means."
        ),
        "category": "MUTANT_INVASION",
        "severity": 9,
        "expiration_days": 5,
        "intel_reveal": "act4_hungry_thinks",
        "world_effect": {},
        "choices": [
            {
                "key": "secure",
                "label": "Secure the subject before Pharmacorp",
                "summary": "Race to reach her first. High risk. High value.",
                "effects": {"faction_pressure": 20},
            },
            {
                "key": "document",
                "label": "Document and report",
                "summary": "Record the event. Let others act.",
                "effects": {},
            },
        ],
    },
    {
        "id": "campaign_black_market_cure_vials",
        "act": 4,
        "trigger_id": "campaign_black_market_cure_vials",
        "title": "Black-Market Cure Vials",
        "description": (
            "A street clinic offers three alleged P-77 cure vials taken from a Pharmacorp convoy. "
            "One vial may restore a Starver. One may kill them. One may be a tracker. "
            "Pharmacorp security wants the stock destroyed before anyone proves what it is."
        ),
        "category": "CITY_POLITICS",
        "severity": 8,
        "expiration_days": 4,
        "intel_reveal": "act4_pharmacorp_secret",
        "world_effect": {"pharmacorp_secret": "exposed"},
        "choices": [
            {
                "key": "protect_cured",
                "label": "Protect the treated Starvers",
                "summary": "Prioritize cured subjects as people. Pharmacorp hostility rises.",
                "effects": {"faction_pressure": 15, "funds": -1200},
            },
            {
                "key": "buy_samples",
                "label": "Buy samples from the clinic",
                "summary": "Gain medical leverage through the black market. Moral risk high.",
                "effects": {"funds": -2500},
            },
            {
                "key": "expose_failure",
                "label": "Expose the containment failure",
                "summary": "Force public scrutiny of Pharmacorp containment and P-77 secrecy.",
                "effects": {"city_unrest": 20},
            },
        ],
    },
    {
        "id": "campaign_novatek_containment_failure",
        "act": 4,
        "trigger_id": "campaign_novatek_containment_failure",
        "title": "Novatek Containment Site Delta-9",
        "description": (
            "A Novatek black site has gone dark after cyborg-Starver hybrid subjects "
            "breached containment. Mutant tissue growth is accelerating inside the facility. "
            "Corporate security wants the site erased before the hybrid program becomes public."
        ),
        "category": "MUTANT_INVASION",
        "severity": 9,
        "expiration_days": 5,
        "intel_reveal": "act4_novatek_hybrids",
        "world_effect": {},
        "choices": [
            {
                "key": "extract_data",
                "label": "Extract experiment data",
                "summary": "Recover Novatek hybrid files before the site burns.",
                "effects": {"funds": -1000},
            },
            {
                "key": "quarantine_site",
                "label": "Quarantine the failed site",
                "summary": "Contain mutant escalation and buy time for civilians nearby.",
                "effects": {"city_unrest": -10, "funds": -1800},
            },
            {
                "key": "expose_hybrids",
                "label": "Expose the hybrid program",
                "summary": "Reveal cyborg-Starver experiments and force Novatek into the open.",
                "effects": {"city_unrest": 25},
            },
        ],
    },
    {
        "id": "campaign_ai_signal",
        "act": 4,
        "trigger_id": "campaign_ai_signal",
        "title": "The AI Message",
        "description": (
            "A message has arrived from an untraceable source using infrastructure that "
            "does not appear in any network registry. "
            "It knows things that should be impossible to know. "
            "It has been watching."
        ),
        "category": "ENEMY_CORPORATION_ATTACK",
        "severity": 8,
        "expiration_days": 7,
        "intel_reveal": "act4_ai_existence",
        "world_effect": {"ai_factions_status": "suspected"},
        "choices": [
            {
                "key": "reply",
                "label": "Attempt to reply",
                "summary": "Engage the unknown contact. Learn what it wants.",
                "effects": {},
            },
            {
                "key": "analyze",
                "label": "Analyze and isolate",
                "summary": "Treat it as a potential threat. Technical analysis only.",
                "effects": {"funds": -800},
            },
        ],
    },

    # ── Act V ────────────────────────────────────────────────────────────────
    {
        "id": "campaign_new_york_siege",
        "act": 5,
        "trigger_id": "campaign_new_york_siege",
        "title": "New York: The Tide Arrives",
        "description": (
            "The Tide has reached New York's outer boroughs. Estimated contact: six hours. "
            "The Three Sevens have begun broadcasting emergency authority decrees. "
            "The Corporate Council is silent. The city is on its own."
        ),
        "category": "MUTANT_INVASION",
        "severity": 10,
        "expiration_days": 14,
        "intel_reveal": "act5_new_york_siege",
        "world_effect": {"new_york_status": "siege"},
        "choices": [
            {
                "key": "defend",
                "label": "Commit all assets to New York defense",
                "summary": "All available forces redirected. Maximum risk.",
                "effects": {"faction_pressure": 30},
            },
            {
                "key": "evacuate",
                "label": "Prioritize civilian evacuation corridors",
                "summary": "Save lives. Cede territory to the Tide.",
                "effects": {"city_stability": -30},
            },
        ],
    },
    {
        "id": "campaign_final_choice",
        "act": 5,
        "trigger_id": "campaign_final_choice",
        "title": "The Final Decision",
        "description": (
            "The Preservationist AI has sent a final message. "
            "The cure, the clone truth, the Tide, the AI factions — all pieces are now visible. "
            "The answer to what world survives depends on what you choose to fight for, "
            "and what you are willing to sacrifice."
        ),
        "category": "CORPORATE_POLITICS",
        "severity": 10,
        "expiration_days": 21,
        "intel_reveal": "act5_final_choice",
        "world_effect": {},
        "choices": [
            {
                "key": "expose",
                "label": "Expose everything — cure, clones, AIs",
                "summary": "Maximum disruption. Maximum truth. Unknown consequences.",
                "effects": {"city_unrest": 50, "funds": -5000},
            },
            {
                "key": "target",
                "label": "Focus on the Three Sevens",
                "summary": "Remove the immediate authoritarian threat. Let the rest emerge in time.",
                "effects": {"faction_pressure": 40},
            },
        ],
    },
]
