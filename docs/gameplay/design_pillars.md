# CyberCity 2085 — Management and Tactical Design Pillars

CyberCity is built around one repeating promise:

> Make a difficult strategic commitment, live through it tactically, then see
> the city and the agents remember what happened.

## Reference vocabulary

The project uses existing games as design references, not as content or system
templates to copy.

- **XCOM**: preparation tension, scarce availability, readable percentages,
  wounds that reshape the next operation, and a base that expresses campaign
  pressure.
- **Star Wars: Zero Company**: a compact squad campaign in which operatives,
  relationships, and mission preparation share the spotlight with tactics.
- **Command & Conquer**: immediate silhouettes, strong faction readability,
  decisive audiovisual feedback, urgent alerts, and a command interface that
  feels active rather than administrative.
- **Pathfinder and Baldur's Gate**: companions with persistent histories,
  contextual choices, relationships that affect scenes, and epilogues derived
  from accumulated decisions.

## Pillar 1 — Strategic management

Management is a forecasting game, not a collection of resource buttons.

Before committing to a mission or advancing time, the player should understand:

1. what will be gained or spent;
2. which threat will worsen if ignored;
3. which agents and assets will become unavailable;
4. what the likely district and faction consequences are;
5. which future option this decision opens or closes.

The preferred design unit is one weekly planning dilemma that composes existing
funds, research, recovery, events, assets, and mission pressure. Avoid adding a
parallel economy when a meaningful trade-off can be expressed through current
systems.

Visual direction: a living cyberpunk command surface with clear hierarchy,
projected deltas, threat movement, responsive rooms, and concise after-action
changes. Animation and sound must indicate state, urgency, or consequence.

## Pillar 2 — Tactical combat

Combat is an objective-driven positioning game, not an exchange of attacks.

Each encounter should clearly communicate:

1. the mission objective and failure pressure;
2. enemy intent before resolution;
3. cover, flank, range, and danger;
4. faction-specific behavior and silhouette;
5. what happened, why it happened, and what it changed.

The existing shared combat engine remains authoritative. Improvements should
deepen cover, flanking, objective pressure, faction profiles, encounter
composition, camera, audio, particles, and action feedback in small tested
slices. Godot may enhance presentation, but it must not fork the campaign rules.

Visual direction: neon tactical diorama, strong unit outlines, restrained but
decisive impacts, readable intent lines, and maps whose atmosphere supports the
mission. Spectacle is useful only when it clarifies action or consequence.

The first tactical-identity pass expresses six counterplay patterns:

- Hungry packs rush bodies and defensive objectives;
- mutants breach toward close combat;
- raiders circle cover and isolate wounded targets;
- corporate strike teams seek protected angles and specialists;
- Three Sevens units coordinate around mission objectives;
- Novatek hybrids hunt wounded agents aggressively.

World-space intent badges expose the predicted action and target during the
player turn. They reveal doctrine, not dice results: a telegraphed shot can still
miss, and player movement can invalidate the prediction before resolution.

## The consequence bridge

The two pillars are one loop:

`forecast → commit → deploy → resolve → remember → adapt`

- Management choices alter tactical conditions, squad readiness, support, and
  opportunity cost.
- Tactical outcomes alter wounds, stress, reputation, relationships, factions,
  districts, intel, and future management pressure.
- Briefing and debrief screens must expose this bridge explicitly.
- The final epilogue evaluates world state and agent history accumulated through
  that loop.

## Scope test for future features

A proposed feature belongs in the release when it strengthens at least one
pillar and visibly feeds the consequence bridge. If it merely adds content,
currency, or decoration without changing a decision or its feedback, defer it.
