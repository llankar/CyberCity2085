## Source-faithful obstacle faces (November 17, 2026)

- [x] SF-01 Preserve original salvage/rock/debris silhouettes and outdoor wasteland art without rectangular plinths or floor replacement.
- [x] SF-02 Source-derived cached facade swatches, correct texel density and source-toned edges for retained architectural/furniture volumes.
- [x] SF-03 Catalogue/source-integrity and native interaction tests, plus corrected real captures at multiple resolutions.
- [x] SF-04 Document the visual correction and publish under the user's standing push/merge authorization.

Evidence: [Source-faithful faces](combat_visual_23.md#source-faithful-faces-correction).

## Combat Visual 2.3 (November 17, 2026)

- [x] CV23-01 Render-only, bounded elevation profiles and dedicated facade materials across surveyed map obstacles.
- [x] CV23-02 Multipart furniture, sloped supported canopies and source-UV top surfaces without stretched walls.
- [x] CV23-03 Cached local floor completion, ground shadows, depth sorting and moving-unit/route occlusion.
- [x] CV23-04 F10 flat-render fallback, persisted preference and quality tiers, preserving camera/HUD/character proportions.
- [x] CV23-05 Complete-catalogue geometry/rules tests and real before/after captures on five environments at three resolutions.

Evidence and reproduction: [Combat Visual 2.3](combat_visual_23.md).

## Combat Visual 2.2 (November 17, 2026)

- [x] CV22-01 Cached map-emissive lighting profiles, restrained reflections and quality-dependent local pools.
- [x] CV22-02 Soft ground contact, directional permanent rims and animated red enemy identification, preserving character dimensions.
- [x] CV22-03 Discreet reachable cells, animated actual routes/PA and bounded action flash/spark/heal effects.
- [x] CV22-04 Preserve HUD organization; refine hover, text fitting, target-card occlusion and footer input protection.
- [x] CV22-05 Native four-environment/three-resolution captures, legacy/quality checks, 13 targeted tests and publication authorized by the user.

Evidence and reproduction: [Combat Visual 2.2](combat_visual_22.md).

## Combat feedback and interior vehicles (November 17, 2026)

- [x] CFI-01 Prioritize out-of-range feedback with actual distance/range, consistently in the target card and click message; describe LOS blockers as obstacles.
- [x] CFI-02 Omit all interior arrival/decorative vehicles and enemy vehicle combat units at encounter generation; retain exterior vehicles and interior power armor.
- [x] CFI-03 Real-scene regression for feedback, unchanged rejected-shot AP/HP, interior catalogue generation and power-armor support.

Evidence: [Combat Visual 2.1 corrections](combat_visual_21.md#combat-feedback-and-interior-vehicles).

## Combat Visual 2.1 (November 17, 2026)

- [x] CV21-01 Replace fabricated stretched wall extrusions with source-aligned painted cutouts and calibrated isometric projection.
- [x] CV21-02 Enlarge visible bodies to 70% tile width, preserve sprite proportions/sole anchoring and all-unit occlusion.
- [x] CV21-03 Responsive squad framing, closer cursor-anchored zoom and exact tactical picking.
- [x] CV21-04 Map-sampled local lighting, tactical indicators and animated HUD accents, preserving quality/legacy controls.
- [x] CV21-05 Complete-catalogue geometry/rules regression and real Godot captures across four environments and three resolutions.

Evidence: [Combat Visual 2.1](combat_visual_21.md).

## Squad Command UI 2.0 (November 17, 2026)

- [x] SCUI-01 Dedicated responsive three-column Arcade command deck, shared holographic typography/panels and illustrated equipment/vector resources.
- [x] SCUI-02 Real portrait roster, readiness and squad selection, equipment cycling, attribute controls and complete agent-sheet routes.
- [x] SCUI-03 Dynamic mission artwork/intelligence and all downtime activities, localized chrome and accessible text-size adaptations.
- [x] SCUI-04 Eleven icon commands, settings/World Map return routes, keyboard/paging, original save/load/recruit/remove handlers and no hidden legacy hit targets.
- [x] SCUI-05 Real 720p/941p/1080p/1440p captures, native interaction/regression validation and documented visual comparison; push/merge authorized by the user.

Evidence and reproduction: [Squad Command UI 2.0](squad_command_2.md).

## Always-visible unit outlines (November 17, 2026)

- [x] OUTLINE-01 Clear cyan outlines on all living allies and red outlines on all living enemies, with stronger selection emphasis.
- [x] OUTLINE-02 Native pixel checks for unselected/untargeted units and updated real capture/documentation.

## Reference-based unit presentation (November 17, 2026)

- [x] UREF-01 Solid bodies, state-dependent cyan/red silhouette emphasis, grounded selection and visible-body targeting brackets.
- [x] UREF-02 Enemy-linked portrait card with actual combat values, responsive placement, camera tracking and click-through prevention.
- [x] UREF-03 Real movement/targeting captures and native presentation/interaction regression coverage; existing scale and rules preserved.

Evidence: [unit reference presentation](tactical_reference.md#reference-based-ally-and-enemy-presentation).

## Tactical agent visibility (November 17, 2026)

- [x] VIS-01 Isolated character material: solid living bodies, brighter art and screen-sized silhouette contour on static/animated units.
- [x] VIS-02 Real framebuffer tests for opacity, lighting, transparent margins and animation parity; market movement and launch regressions.
- [x] VIS-03 Documented actual before/after captures and preserved tactical geometry.

Evidence: [agent visibility](tactical_reference.md#agent-visibility-on-detailed-terrain).

## World Map Visual 2.0 and reference combat framing (November 17, 2026)

- [x] WMV2-01 Reusable, cached holographic beacons for every combat/narrative mission, category colors and hover/selection animations.
- [x] WMV2-02 Collision-aware cartouches and selected briefing connection; original map, cities and legends preserved.
- [x] WMV2-03 Readable dynamic, scrollable briefing and existing mission/squad/navigation routes preserved across resolutions.
- [x] WMV2-04 Reference initial/maximum combat zoom and +10% token presentation without changing tactical geometry.
- [x] WMV2-05 Real Arcade/Godot captures, interaction/runtime regression tests and documentation; publication authorized by the user.

Evidence and reproduction: [World Map Visual 2.0](world_map_visual_2.md) and
[combat reference](tactical_reference.md).


## Release 1.0 — Finishable Campaign (active November 2026)

Authoritative scope and release gates: [`docs/release_plan.md`](release_plan.md).
This batch is intentionally limited to five tasks.

- [x] RELEASE-01 Serialisable campaign-ending state and deterministic outcome evaluator. (completed November 12, 2026)
- [x] RELEASE-02 Fifteen authored story missions, reachable Act V finale trigger, idempotent mission completion, and resolved-campaign tick guard. (completed November 12, 2026)
- [x] RELEASE-03 Ending presentation with world consequences and named agent epilogues. (completed November 12, 2026)
- [x] RELEASE-04 Save migration, round-trip, finale, and full-campaign smoke tests. (completed November 12, 2026)
- [x] RELEASE-05 Player-facing progression/release documentation and canonical test gate: 427 tests plus 8 subtests passing. (completed November 12, 2026)

Engine decision: retain Python/Arcade as the release authority and keep Godot as
an optional tactical presentation client until a complete versioned result
round trip is proven. A full migration is not part of the 1.0 scope.

## Release 1.0 — Strategic Management Pass (completed November 2026)

- [x] MGMT-01 Read-only weekly forecast for income, upkeep, readiness, district pressure, and urgent events.
- [x] MGMT-02 Three mutually exclusive weekly directives composed from existing funds, city pressure, agents, and strategic resources.
- [x] MGMT-03 Persistent directive state with old-save compatibility and one-choice-per-week enforcement.
- [x] MGMT-04 Command-room presentation with explicit costs, benefits, drawbacks, lock state, threat tier, and event deadline.
- [x] MGMT-05 Focused/full regression coverage plus management documentation and backlog update.

Design decision: replace the command room's shallow repeated allocation buttons
with one forecasted weekly commitment. Research, city investment, recruitment,
equipment, and assets remain in their dedicated rooms; command now answers the
more interesting question: what does the corporation prioritize this week?

## Release 1.0 — Tactical Identity Pass (completed November 2026)

- [x] TACT-01 Six readable doctrine families for Hungry packs, mutants, raiders, corporate strike teams, Three Sevens, and Novatek hybrids.
- [x] TACT-02 Doctrine-driven target scoring, cover/flank/objective biases, inspectable action reasons, and non-stacking commander auras.
- [x] TACT-03 Deterministic next-action intent prediction derived from the same doctrine used by the AI.
- [x] TACT-04 World-space HUD intent badges and target lines for visible enemies during the player turn.
- [x] TACT-05 Focused/full regression coverage plus tactical documentation and backlog update.

Design decision: enemy factions differ through priorities the player can read and
counter, not hidden accuracy bonuses. Intent telegraphs expose the likely action
without guaranteeing hit results, preserving uncertainty while enabling plans.

## Wave 5 — Gameplay Depth, Spectacle & Mission Variety (completed May 2026)

- [x] BATTLE-W5A2 AI target scoring: enemies now pick the most dangerous/weakest target instead of always attacking index 0.
- [x] BATTLE-W5A3 Narrative debrief: tone-coloured lines from `DebriefReport.lines` displayed in the debrief right panel.
- [x] BATTLE-W5B1 Mission intro: 2-second scan-line + title fade-in overlay on battle start.
- [x] BATTLE-W5B2 Critical hits: 12% chance, double damage, "CRITICAL!" popup, extra shake + white flash.
- [x] BATTLE-W5B3 XP floats: "+50 XP" text popup above the killing unit on each kill.
- [x] BATTLE-W5B4 Ambient atmosphere: scanlines, neon edge glow, rain particles on rain/fog maps, blackout darkening.
- [x] BATTLE-W5C1 Defend objective: hold N turns mechanic; enemy breach → defeat; countdown in turn log.
- [x] BATTLE-W5C2 Assassination objective: pulsing red diamond over high-value target; instant win on kill.
- [x] BATTLE-W5D1 Agent promotion view: sequenced level-up screen (portrait + level badge + stat gains) between battle and debrief.
- [x] BATTLE-W5D2 Morale cascade: 30% chance each surviving agent becomes SUPPRESSED when an ally is KIA.

## Wave 6 — Campaign Coherence, Mission Flow & CyberCity Identity (planned)

This wave turns existing systems into a coherent playable campaign loop.

### Phase 1 — Complete the Core Mission Loop

- [x] MISSION-FLOW-01 Mission Briefing Screen: Created a full mission briefing screen before battle launch showing mission title, objective, target faction, district, risk level, expected stress band, emotional impact, complications, map thumbnail, squad roster, selected support assets, reward preview, and clear DEPLOY / ABORT actions. Added regression coverage for the required briefing fields. (completed June 20, 2026)
- [x] MISSION-FLOW-02 Pre-battle Deployment Phase: Added a deployment mode before combat starts; shows the deployment zone, allows repositioning selected agents and support assets, hides enemies until battle begins, and starts combat only after player confirms deployment. Added regression coverage for deployment gating, hidden enemies, and support asset repositioning. (completed June 20, 2026)
- [x] MISSION-FLOW-03 Enhanced Post-battle Debrief: Created a stronger post-battle debrief screen showing objective result, victory/defeat, rewards, per-agent kills/damage/stress/injuries/XP, triggered complications, faction changes, district changes, narrative consequence lines, and continue button back to ManagementView. Added regression coverage for the required debrief summary fields. (completed June 20, 2026)
- [x] MISSION-FLOW-04 Consequence Summary Panel: After mission resolution, display a compact consequence panel summarizing changes to city pressure, faction hostility/influence/legitimacy, tags gained, agent scars, rewards, unavailable missions, intel unlocks, and campaign state changes. Added regression coverage for consequence summary lines. (completed June 20, 2026)
- [x] MISSION-FLOW-05 End-to-end Mission Flow Regression: Added regression coverage for mission selection -> launch -> Arcade fallback after Godot handoff unavailability -> mission resolution -> debrief/consequences -> return to management. (completed June 20, 2026)

### Phase 2 — Make CyberCity 2085 Identity Visible

- [x] LORE-01 Expand Core Faction Set: Added first-class faction/content entries for Starvers, Three Sevens, Pharmacorp, Novatek, raiders, mutants, corporate security, hidden AI factions, and local city factions while keeping the current vertical slice faction factory compatible. Added regression coverage for required names, categories, and hidden-AI omission. (completed June 23, 2026)
- [x] LORE-02 Starvers / Hungry Tide Integration: Made the Hungry Tide visible in the Intel/Global Scenario UI, showing its progress, threat level, affected regions, expected New York impact, and consequences if ignored. Added regression coverage for Hungry Tide summary states. (completed June 20, 2026)
- [x] LORE-03 Three Sevens Campaign Presence: Strengthened Three Sevens as a campaign antagonist through visible story mission hooks, intel fragments, event hooks, special enemy themes, propaganda, Warsaw references, and late-campaign escalation in the Global Scenario UI. Added regression coverage for Three Sevens campaign presence. (completed June 20, 2026)
- [x] LORE-04 Pharmacorp Cure Thread: Added mission, intel, and event hooks around Pharmacorp, the hidden P-77 cure, cured Starvers, moral ambiguity, containment failures, and black-market medical choices. Added Intel-room summary coverage for the thread. (completed June 23, 2026)
- [x] LORE-05 Novatek Experiment Thread: Added mission, intel, and event hooks around Novatek experiments, cyborg-Starver hybrids, mutant escalation, failed containment sites, and a `novatek_hybrid` special enemy theme. Added regression coverage for the thread summary and enemy-theme routing. (completed June 23, 2026)
- [x] LORE-06 Hidden AI Conspiracy Thread: Added a gated late-act Intel-room summary for two hidden AI factions: Preservationist AIs trying to protect humanity/creators and Exterminator AIs seeking human extinction. The summary stays hidden before Act IV and links late-act intel and event hooks. (completed June 23, 2026)

### Phase 3 — Global Scenario & Intel Room

- [x] CAMPAIGN-UI-01 Global Scenario Panel: Expanded the Intel room panel to display current act, act title, act progress, Hungry Tide percentage, New York status, Warsaw status, discovered intel count, major known threats, and unresolved global events. Added regression coverage for the Global Scenario summary. (completed June 20, 2026)
- [x] CAMPAIGN-UI-02 Intel Fragment Browser: Added a readable Intel-room browser for fragments grouped by act, source, and faction; it distinguishes known and locked entries and shows lore excerpts plus mechanical relevance. Added regression coverage for grouping and known/unknown rows. (completed June 23, 2026)
- [x] CAMPAIGN-UI-03 World State Change Feed: Added a compact campaign feed that records major world changes such as New York siege escalation, Warsaw occupation, faction breakthroughs, AI hints, Starver tide milestones, and recent global intel log lines. Added regression coverage for the required feed categories. (completed June 23, 2026)
- [x] CAMPAIGN-UI-04 Act Transition Presentation: Expanded the act-advance overlay with act number, title, summary, newly revealed stakes, and immediate strategic consequences. Added regression coverage for the transition presentation contract. (completed June 23, 2026)

### Phase 4 — Agent Attachment & RPG Continuity

- [x] AGENT-RPG-01 Recovery Room Dialogues: Added daily recovery/support dialogue snippets between stressed, wounded, traumatized, scarred, or bonded agents and persisted the latest recovery beats for the narrative feed. Added regression coverage for recovery-room triggers and day-advance logging. (completed June 23, 2026)
- [x] AGENT-RPG-02 Relationship and Mentor Events: Mentor links and relationships now influence recovery dialogue pairing and produce event-log recovery bond lines with a small stress relief modifier. Added regression coverage for mentor-linked recovery bonuses. (completed June 23, 2026)
- [x] AGENT-RPG-03 Temporary Scar Presentation: Serious wounds and temporary scars are now visible through agent dossier lines, debrief consequence summaries, mission briefing readiness facts, and recovery/command-deck panel text. Added regression coverage for briefing and debrief scar titles. (completed June 23, 2026)
- [x] AGENT-RPG-04 Agent Nicknames and Reputation: Added deterministic post-mission reputation awards and first nickname assignment for standout events such as high kills, critical survival, civilian rescue, or traumatic failure. Awards appear in debrief data, event lines, agent dossiers, and saved agent payloads. Added regression coverage for award rules and serialization. (completed June 23, 2026)
- [x] AGENT-RPG-05 Personality-driven Mission Logs: Expanded personality modulation into mission debrief lines and high-stress reactions while preserving existing mission complication log modulation. Added regression coverage for trait-colored debrief text, secondary trait suffixes, and neutral fallback. (completed June 23, 2026)

### Phase 5 — Tactical Combat Readability and Feel

- [x] BATTLE-FEEL-01 Floating Damage / Healing / Miss Text: Added short-lived floating combat text for damage, healing, criticals, misses, suppression, and status changes. Added regression coverage for combat popup payloads. (completed June 20, 2026)
- [x] BATTLE-FEEL-02 Combat Log Side Panel: BattleView exposes the combat log during battle through a Tab-toggled side panel showing the latest events, backed by the existing modular combat log builders and new keyboard/HUD regressions. (completed June 23, 2026)
- [x] BATTLE-FEEL-03 Status Effects System: Added `status_effects` support for suppressed, bleeding, stunned, burning, contaminated, and panicked; turn start applies damage/AP effects and the HUD renders status badges. Added regression coverage for required statuses and turn-start effects. (completed June 20, 2026)
- [x] BATTLE-FEEL-04 Objective Marker Clarity: Objective markers now show the objective label, interaction prompt, progress text, and explicit success/failure condition metadata for non-elimination objectives. Added regression coverage for marker prompt/progress rendering and objective contracts. (completed June 23, 2026)
- [x] BATTLE-FEEL-05 Enemy AI Upgrade: Improved enemy AI with inspectable target scoring, cover-seeking decision reasons, flanking reposition preference against covered targets, commander aura AGI buffs, and containment/defend objective-pressure movement. Added focused regression coverage for each decision path. (completed June 23, 2026)
- [x] BATTLE-FEEL-06 In-battle Pause Menu: Escape opens an in-battle pause overlay with Resume, Settings, and Abandon actions where appropriate; Escape closes it again. Added HUD and BattleView keyboard regressions. (completed June 23, 2026)

### Phase 6 — Mission Objective Variety

- [x] OBJECTIVE-01 Extraction Objective: Extraction objectives now create a tactical WITNESS marker from both canonical and legacy safe-extraction mission types, requiring the squad to reach and secure the target before completion. Added regression coverage for alias routing and interaction prompts. (completed June 23, 2026)
- [x] OBJECTIVE-02 Sabotage Objective: Sabotage objectives now create a tactical RELAY marker from both canonical and legacy sabotage-window mission types, with explicit plant/hack prompt, success condition, and wipe-before-arm failure condition. Added regression coverage for alias routing and completion. (completed June 23, 2026)
- [x] OBJECTIVE-03 Data Theft Objective: Data-theft objectives now create a tactical CACHE marker from both canonical and legacy detour mission types and require two interaction turns before completion. Added regression coverage for multi-turn progress and completion text. (completed June 23, 2026)
- [x] OBJECTIVE-04 Containment Objective: Added a containment objective type with a BREACH LINE marker, explicit hold prompt, success/failure metadata, and a battle failure check when enemies cross the configured threshold. Added regression coverage for breach detection. (completed June 23, 2026)
- [x] OBJECTIVE-05 Civilian Rescue Objective: Added a civilian-rescue objective type with multi-group rescue progress, sequential marker positions, readable mission-board label, and completion after three extracted groups. Added regression coverage for multi-group progress. (completed June 23, 2026)
- [x] OBJECTIVE-06 Recon / Scan Objective: Added a recon-scan objective type with sequential scan markers, readable mission-board label, and completion after three scan points so missions can win without eliminating all enemies. Added regression coverage for scan-point advancement. (completed June 23, 2026)

### Phase 7 — Architecture and Maintainability

- [x] ARCH-01 GameState Domain Split Plan: Documented a safe incremental plan in `docs/architecture/gamestate_domain_split.md` to reduce `GameState` god-object risk by moving behavior into domain services while keeping save compatibility. (completed June 20, 2026)
- [x] ARCH-02 Extract Campaign Service: Added `game/campaign/service.py` as the stable campaign progression boundary while retaining `GameState` as the save-compatible state root. (completed November 13, 2026)
- [x] ARCH-03 Extract Mission Flow Service: Added `game/missions/flow.py` as the stable board/launch/objective/reward/resolution boundary and migrated release-path callers while preserving the legacy facade. (completed November 13, 2026)
- [x] ARCH-04 Keep UI Code in `game/ui/screens/`: Added an architecture contract proving management, map, briefing, debrief, and ending views remain in `game/ui/screens/`; the legacy battle shell remains an explicit compatibility path. (completed November 13, 2026)
- [x] ARCH-05 Save Migration Tests: Added legacy-payload defaults plus round-trip coverage for campaign state, intel, scars, selected assets, faction tags, and mission board state. (completed November 13, 2026)
- [x] ARCH-06 Godot Handoff Contract Tests: Added a versioned validator for campaign, mission, map, squad, support assets, tactical actions, and schema version; invalid handoffs are rejected before writing. (completed November 13, 2026)

### Recommended implementation order

1. MISSION-FLOW-01 Mission Briefing Screen
2. MISSION-FLOW-03 Enhanced Post-battle Debrief
3. MISSION-FLOW-04 Consequence Summary Panel
4. CAMPAIGN-UI-01 Global Scenario Panel
5. LORE-02 Starvers / Hungry Tide Integration
6. LORE-03 Three Sevens Campaign Presence
7. MISSION-FLOW-02 Pre-battle Deployment Phase
8. BATTLE-FEEL-01 Floating Damage / Healing / Miss Text
9. BATTLE-FEEL-03 Status Effects System
10. ARCH-01 GameState Domain Split Plan

Design intent:
CyberCity2085 should not simply gain more isolated features. The goal of Wave 6 is to make the existing systems form a readable emotional loop: strategic choice, mission briefing, squad preparation, tactical action, debrief, visible consequences, and world escalation.

## Mission View Professional Upgrade — Planned

Three-phase plan to bring the battle/mission view to professional tactical-RPG standard. Tasks are tracked in `tools/docs/generate_docs.py` (BATTLE-* entries) and will be promoted to the roadmap on next generation run.

### Phase 1 — Visual Polish & In-Battle UX

- [x] BATTLE-P01 Camera pan: Shift+arrows now pan within overscanned map bounds and Home focuses the active unit while the HUD stays screen-anchored. (completed November 13, 2026)
- [x] BATTLE-P02 Floating damage numbers: short-lived text sprites above hit units (`-N` red, `+N HP` green, `MISS` grey, status labels); float 40 px upward, fade quickly; separate `damage_popups` list in BattleView. (completed June 20, 2026)
- [x] BATTLE-P03 Action bar icon pass: Added distinct code-drawn icons for move, fire, melee, psi, aid, missiles, overwatch, defend, and end turn without new asset dependencies. (completed November 13, 2026)
- [x] BATTLE-P04 In-battle pause menu: Escape key opens the in-battle Resume/Settings/Abandon overlay and Escape closes it again; covered by HUD and BattleView keyboard regressions. (completed June 23, 2026)
- [x] BATTLE-P05 Combat log side panel: Existing `combat_log_panel.py` functionality is player-accessible through the BattleView Tab-toggle side column with latest-event display and regression coverage. (completed June 23, 2026)

### Phase 2 — Full Mission Arc

- [x] BATTLE-A01 Mission Briefing Screen: `MissionBriefingView` now sits between the world-map mission selector and BattleView/Godot handoff, showing mission name/objectives/intel/map thumbnail/squad roster/support assets/emotional impact/stress/reward preview with DEPLOY or ABORT actions. (completed June 20, 2026)
- [x] BATTLE-A02 Pre-battle Deployment Phase: deployment-mode state in BattleView before turn 1 with highlighted deployment zone, movable agent/support asset sprites, DEPLOYMENT phase banner, Enter to begin, and enemy units hidden until battle starts. (completed June 20, 2026)
- [x] BATTLE-A03 Enhanced Post-battle Debrief: `battle_debrief_view.py` now shows per-agent damage/kills/stress/injuries/XP plus objectives, rewards, triggered complications, faction/district changes, narrative consequence lines, and CONTINUE routing back to management. (completed June 20, 2026)

### Phase 3 — Gameplay Depth

- [x] BATTLE-G01 Terrain pathfinding: reduced to one shared tactical movement rule in `game/combat/movement.py`; BattleView deployment/keyboard movement and enemy AI now use the same terrain + occupancy checks. (completed June 7, 2026)
- [x] BATTLE-G02 Enhanced enemy AI: Enemy AI now covers target scoring, cover-seeking, flanking preference using `cover_system.py`, commander subtype AGI buffs for adjacent units, and objective-pressure movement for defensive missions. (completed June 23, 2026)
- [x] BATTLE-G03 Dynamic mid-battle events: added a render-independent `game/combat/events.py` layer for complication-triggered reinforcements and blackout, with `CombatEngine` returning descriptive results for `BattleView` to translate into sprites, sound, screen shake, logs, and fog changes. (completed June 7, 2026)
- [x] BATTLE-G04 Status effects: `Unit.status_effects` now covers suppressed, bleeding, stunned, burning, contaminated, and panicked with turn-start effects and HUD badges on unit labels. (completed June 20, 2026)

---

## Gameplay systems explicit status

- [x] BATTLE-UI-GODOT Combat mission UI handoff: mission briefing now exports selected mission/squad/map state to `runtime/godot_combat/mission_handoff.json`, resolves the project and handoff paths before launch so Godot reads the written payload, uses the in-app Settings screen file browser path before environment variables, persists that executable path immediately after selection, and the dedicated `godot/combat_missions_ui` project now renders a live tactical HUD that stays visually close to the older mission combat screen with a battlefield grid, deployed agent list, and right-side action deck when Godot is available, while still falling back to the Arcade battle view when no Godot executable is configured. Movement stays free-form in this slice; no blocking layer is included. (completed June 7, 2026)
- [x] BATTLE-UI-GODOT-ASSETS Support asset deployment in Godot UI: selected robots and power armor from `support_assets` now become player-side Godot combat units after the selected squad, with asset actions, HP, defense, initiative, and robot scale carried through the handoff. (completed June 13, 2026)
- [x] UI-59 Tactical move highlight compactness: movement range overlays now render at half-size in both the Arcade battle HUD and the Godot battlefield, making the preview less visually dominant without changing AP cost or pathing rules. (completed June 11, 2026)
- [x] UI-60 Godot move highlight density: Godot movement previews keep the same half-size diamonds but anchor them to the active unit on a tighter preview lattice, removing the wide blank gutters from the screenshot without changing AP cost, reachable cells, or click targets. (completed June 11, 2026)
- [x] BATTLE-ENG1 Combat engine package: added `game/combat/` as a pure tactical state/transition boundary and wired `BattleView` through it for turn/AP checks. (completed Jun 7, 2026)
- [x] UI-51 Combat movement unrestricted: removed terrain and occupancy gating from the battle window so player and enemy moves are no longer blocked by path rules inside combat. (completed May 28, 2026)
- [x] UI-50 Battle map walkability masks: battle terrain now prefers explicit `*.walkable.png` sidecars instead of reading movement from the art directly, with a small generator tool so shipped maps can keep an editable collision layer. (completed May 28, 2026)
- [x] UI-49 Terrain classifier correction: replaced the battle map brightness-only walkability guess with a brightness-plus-texture score so open ground and blocked objects no longer get treated the same just because they share similar lighting. (completed May 28, 2026)
- [x] UI-48 Combat movement debug tint: temporarily color blocked movement tiles in a distinct red debug overlay across the whole battlefield, so terrain and occupancy path restrictions are visible everywhere while diagnosing path blocking. (completed May 28, 2026)
- [x] UI-47 Battle HUD top bar stack: moved the contextual shortcut banner and the aftermath feedback strip to the top of the window, centering both lines, and increased their label size so tactical hints read as a single stacked HUD cluster instead of drifting over the map. (completed May 28, 2026)
- [x] UI-46 Battle HUD shortcut banner center: centered the top help text banner so the active shortcut line reads from the middle of the window instead of hugging the left edge. (completed May 28, 2026)
- [x] UI-45 Battle HUD active-unit panel dock: moved the lower-left portrait/stats card down to the bottom edge so the active agent readout anchors to the HUD base instead of floating above the portrait strip. (completed May 28, 2026)
- [x] UI-44 Agent and asset portrait expansion: added 50 new legacy agent portraits plus 50 new asset portraits split across power armor and robot pools, and routed the UI to use the full expanded sets so agents and spec-ops assets stop repeating the same faces. (completed May 28, 2026)
- [x] UI-43 Legacy agent portrait expansion: added 50 new generic agent headshots in the original agent_01..agent_24 cyberpunk style, now extending the legacy fallback pool through agent_74 so the oldest roster routes still have fresh faces. (completed May 27, 2026)
- [x] UI-42 Agent sheet spacing pass: the full dossier now gives the readiness stats a calmer two-row layout, separates the recovery/status lines from the stress meter, lowers the stress bar itself, and moves the skill training control into a full-width banner so the sheet no longer feels cramped. (updated May 27, 2026)
- [x] UI-40 Recruit chooser modal: the recruit flow now opens a dedicated recruitment window with 6-9 randomized candidates, each showing portrait-led profiles, price tags, stat previews, skill ranks, background, and advantages so the roster choice reads like a proper RPG hiring screen. (completed May 27, 2026)
- [x] UI-41 Portrait pool expansion: agent portrait routing now splits into 50 female, 50 male, and 50 robot portraits so recruitment and hangar cards stop repeating the same faces. (completed May 27, 2026)
- [x] UI-38 Double-click agent card opens full character sheet in Squad room: added a dedicated full-sheet modal (attributes, core skills, derived stats, and loadout snapshot) while preserving single-click deploy selection; ESC closes the modal. (completed May 27, 2026)
- [x] UI-39 Agent sheet modal polish: the full agent sheet now opens as a topmost portrait-led dossier with stat-card spending, skill-training controls, and a stronger RPG layout so point allocation reads like a real character sheet. (completed May 27, 2026)
- [x] AGENT-09 Agent sheet visibilité in-game: le panneau Agent Barracks affiche désormais une ligne "Sheet" compacte (STR/AGI/PSI, Firearms/Tactics, Aim/Resolve) par agent, pour rendre les données de fiche enfin actionnables pendant la sélection d'escouade; test UI mis à jour pour verrouiller ce rendu. (completed May 26, 2026)
- [x] AGENT-08 Level-up choice model in RPG armory flow: added Option A (+1 attribute, capped) and Option B (+2 skill ranks split across allowed skills, capped), surfaced projected derived-stat deltas directly in room action labels before click confirm, and covered with RPG view regression tests. (completed May 26, 2026)
- [x] AGENT-07 Agent sheet calculations extraction: added pure `game/agents/sheet_calculations.py` (`compute_derived_stats`, `skill_total`) with documented integer-friendly formulas, refactored combat/readiness/stress entry points to consume shared sheet math instead of scattered inline arithmetic, and added regression tests for totals + stress-state penalties. (completed May 26, 2026)

- [x] AGENT-06 Agent sheet schema defaults: added modular `game/agents/sheet_schema.py` with typed attributes/skills/derived-stat builders, wired defaults into recruitment/character constructors, and backfilled legacy save payloads during `Character.from_dict`; added regression tests for default creation + migration safety. (completed May 26, 2026)

- [x] UI-37 Terrain sampler spawn clearance: adaptive map walkability now relaxes overly dark maps and keeps a small walkable halo around forced unit spawns so whole squads are not trapped by generated obstacles. (completed May 25, 2026)

- [x] UI-36 Hide fogged enemies from target selection: battle target acquisition now requires visibility as well as range, and the confirm step refuses stale hidden targets so agents cannot aim or attack unseen enemies. (completed May 25, 2026)

- [x] UI-35 Display-screen selector in settings: added a monitor picker to `SettingsView` so players can choose which screen the game uses, with persistence in `saves/settings.json`, fullscreen apply support, and windowed positioning on the selected display. (completed May 25, 2026)
- [x] UI-52 Text size setting in settings: added a global text size selector with small, medium, and large presets so players can scale UI readability from the settings screen, with persistence in `saves/settings.json`, runtime application at startup, and a stronger large preset for readability. (completed May 30, 2026)
- [x] UI-53 Themed enemy asset wave: added themed enemy portrait and combat-token families for starvers, mutants, raiders, cyber samurai, and corp 37 variants, including robot and power-armor variants, with mission and battle routing wired to the new theme keys. (completed May 30, 2026)
- [x] UI-54 Battle map catalog and token scale: generated 50 real city battle maps from the current map textures, kept the original map set as the wasteland pool, and scaled battle tokens to 1.5x for better readability. (completed May 30, 2026)
- [x] UI-55 Mission map environment routing: mission briefing thumbnails and battle setup now pull from the inferred city or wasteland pool inside `assets/maps`, so outside-city missions do not preview or launch on city maps and vice versa. (completed May 31, 2026)
- [x] UI-56 Mission token sizing pass: non-robot mission tokens now render at half the base battle scale while robot tokens keep the full-size silhouette, so human and organic units read smaller without shrinking machine assets. (completed May 31, 2026)
- [x] UI-57 Mission selection world map: the squad mission panel now opens a dedicated full-screen selector using `assets/worldmap/Player_World_Map_1778155726161.png`, so next missions are chosen from pins on the world map and then launched from that selector. (completed May 31, 2026)
- [x] UI-58 Mission selection world map layout pass: the selector now gives the map almost the whole screen and collapses mission briefing into a floating card with separate header rows, English summary lines, and legacy French briefing text normalization instead of a fixed right-side panel, keeping the tactical map readable at a glance. (completed June 6, 2026)

- [x] UI-34 Guard invalid rectangle draw bounds in squad mission panel: `_rect` now skips impossible LRBT coordinates (`left >= right` or `bottom >= top`) to avoid `arcade.draw_lrbt_rectangle_filled` runtime crashes during dynamic panel layout compression, with a focused regression test in management hub UI tests. (completed May 25, 2026)

- [x] UI-33 Action aftermath HUD slot: ajout d'une ligne temporaire causale après move/skill/tir (`DMG`, `STATUT`, `SUPPRESSION`) affichée dans une zone fixe du HUD pour éviter le clutter visuel, avec timer court et tests dédiés. (completed May 25, 2026)

- funds: **functional**
- calendar: **functional**
- research: **in progress**
- events: **functional**
- equipment: **in progress**
- stress: **functional**
- recovery: **functional**
- faction rewards: **functional**
- aftermath: **functional**
- mission generation: **functional**
- battle objectives: **functional**
- blocked action reasons UI: **in progress**
- static game-flow regression tests: **in progress**

Status vocabulary: `not started`, `in progress`, `functional`, `polished`.

- [x] BATTLE-21 Stabiliser la rÃ©solution de fin de mission: correction de la sÃ©lection du leader via `selected_agent_names` (plus d'accÃ¨s Ã  `GameState.selected_agents`) et garde-fou HUD quand `active_index` sort de la plage aprÃ¨s pertes d'unitÃ©s; couverture test ajoutÃ©e. (completed May 22, 2026)
- [x] UI-20 Fix mission-screen return path + save slots: added direct navigation back to Corp/City from squad mission UI, introduced 5 explicit save slots (`saves/slot_1.json` to `slot_5.json`) with room actions to pick slot before Save/Load, and wired Save/Load actions to the selected slot with regression tests for slot bounds. (completed May 22, 2026)
- [x] UI-21 Fix save-slot startup NameError: imported `SaveSystemResult` in `game/views.py` so save/load action helpers keep their typed return signatures at import time, and added regression check `tests/ui/test_views_imports.py`. (completed May 22, 2026)
- [x] UI-19 Fix expanded-room Save/Load discoverability: added explicit `Save game` and `Load game` room actions across corp/city/squad rooms, raised button baseline to keep labels visible, wired click handlers to `SaveSystem`, and added regression coverage for action availability + label-safe placement. (completed May 22, 2026)
- [x] UI-17 Contrat de layouts 4 zones: templates `OverviewLayout`/`DecisionLayout`/`RosterLayout`/`TacticalLayout` dans `game/ui/layouts/screen_templates.py`, mission board enrichi (risque, durÃ©e, coÃ»t, impact Ã©motionnel, consÃ©quence + recommended action), recommandations contextualisÃ©es en Ã©crans de gestion, et tests de contrat `tests/ui/test_screen_layout_contracts.py`. (completed May 22, 2026)
- [x] UI-16 Migration UI modulaire (phase 1): crÃ©ation des sous-rÃ©pertoires `screens/command_center|command_deck|facility|battle_hud`, `components/cards|lists|agent|shared`, `layouts/grid|split|overlays`, `navigation/focus|input`, `feedback/toast|dialog|banner`; extraction initiale `command_deck` vers `game/ui/screens/command_deck/layout.py`; wrappers de compatibilitÃ© maintenus; mutualisation badge upgrade + rendu cartes agents via composants dÃ©diÃ©s. (completed May 22, 2026)
- [x] UI-15 Foundation design-system split: crÃ©ation `theme/spacing.py`, `theme/elevation.py`, `theme/radii.py`, normalisation des couleurs sÃ©mantiques, ajout de `game/ui/components/foundation/` (Panel/Button/Badge/Divider/ProgressBar/Tooltip), rÃ¨gle progressive anti-hardcode sur `game/ui/screens/`, docs design-system et tests dÃ©diÃ©s. (completed May 22, 2026)
- [x] UI-14 Arborescence Ã©crans UI incrÃ©mentale: crÃ©ation de `game/ui/screens/`, dÃ©placement progressif des modules de vue (`command_center`, `dashboard`, `facility`, `mission_board`, `research_lab`) avec wrappers de compatibilitÃ© temporaires dans `game/ui/`, et test de non-rÃ©gression d'imports `tests/ui/test_screen_wrappers.py`. (completed May 22, 2026)
- [x] UI-11 Feedback system modulaire: crÃ©ation de `game/ui/feedback/` (`toast_center.py`, `confirm_dialog.py`, `error_banner.py`), standardisation des messages `Action/Result/Impact/Next`, confirmations pour actions coÃ»teuses/irrÃ©versibles (mission risquÃ©e, dÃ©penses, load), et tests de rendu/dispatch `tests/ui/test_feedback_system.py`.
- [x] UI-12 Fix room-action pulse helper import in graphical panels: `draw_action_button`/`draw_close_button` now resolve `pulse_from_elapsed` from `game/ui/theme/motion.py`, with a regression test to keep expanded-room buttons rendering safely. (completed May 22, 2026)
- [x] UI-18 Fix Next Step research loop: guidance now recognizes active/completed research momentum (not only unlock flags), preventing the "Start a research project" loop after starting multiple projects; covered by regression in `tests/test_next_action_guidance.py`. (completed May 22, 2026)
- [x] UI-22 Refresh title-screen background art: swapped the start screen to a new widescreen corporate skyline image with a cleaner center frame for the logo and menu, keeping the same cyberpunk tower mood as the rest of the game. (completed May 23, 2026)
- [x] UI-23 Research UI tree presentation: research lab summary now renders available projects as a compact dependency tree (roots + child branches) so players can read progression paths at a glance; kept button actions unchanged and covered by research UI tests. (completed May 23, 2026)
- [x] UI-24 Fix research tree state visibility: research lab now renders a compact stateful tree showing completed (âœ“), active (â–¶), and currently available (â—‹) projects so selecting research immediately reveals prior and next branch context; added regression coverage in research management tests. (completed May 23, 2026)
- [x] UI-25 Show all available research branches: removed research-lab tree clipping so the panel no longer collapses with an ellipsis and now lists every currently available branch line; added regression coverage. (completed May 23, 2026)
- [x] UI-26 Split squad UI transition logic into dedicated controllers (`mission_controller`, `room_actions_controller`, `focus_controller`), keeping `views.py` orchestration-only for input/render bindings; added targeted controller unit tests and architecture doc. (completed May 24, 2026)
- [x] UI-27 Action panel combat preview: added min/max damage, estimated hit/crit, and line-of-fire/friendly-fire warning in tactical action deck using shared combat preview helpers wired to the existing combat resolution inputs; added regression tests. (completed May 25, 2026)
- [x] UI-28 Initiative timeline tactique: ajout d'un composant dédié `game/ui/components/combat/initiative_timeline.py` affichant les 8 prochaines activations, branché à la logique de tour actuelle (source initiative via AGI) avec surlignage de l'unité active et indicateur THREAT pour ennemis à fort impact (`sniper`/`elite`/`commander`); tests dédiés ajoutés. (completed May 25, 2026)
- [x] UI-29 Combat HUD contextual shortcuts: added a tactical shortcuts banner that adapts hints for keyboard/mouse vs controller-like inputs, plus a soft confirmation gate for the irreversible `end_turn` action to prevent accidental turn lock; covered with battle HUD regression tests. (completed May 25, 2026)
- [x] UI-30 Combat log panel modulaire: ajout de `game/ui/components/combat/combat_log_panel.py` avec filtres par type (combat/system/emotional/stress), version HUD courte (latest-first) et version étendue toggle pour debug joueur; événements émotionnels/stress explicitement mis en avant; tests dédiés `tests/ui/test_combat_log_panel.py`. (completed May 25, 2026)
- [x] UI-31 Initiative timeline tactique: ajout d'un composant dédié `game/ui/components/combat/initiative_timeline.py` affichant les 8 prochaines activations, branché à la logique de tour actuelle (source initiative via AGI) avec surlignage de l'unité active et indicateur THREAT pour ennemis à fort impact (`sniper`/`elite`/`commander`); tests dédiés ajoutés. (completed May 25, 2026)
- [x] UI-32 End-screen debrief émotionnel: l'écran de fin affiche désormais 3 blocs narratifs ("Décision clé", "Risque pris", "Action héroïque") extraits du debrief de combat + états critiques, avec pont RPG explicite (stress, relations, progression agent) pour guider la phase management; rendu compact côté panneau debrief et couverture test enrichie. (completed May 25, 2026)
- [x] UI-32 Overwatch direction preview UX: sélection overwatch passe en mode visée avant validation, affiche ligne + cône de couverture de réaction, met en évidence les cases déclencheuses, et autorise la rotation avec ←/→ avant confirmation; couverture HUD ajoutée. (completed May 25, 2026)
TODO:

- [x] RESEARCH-03 3X-style branching research trees + power-armor pilot replacement in mission manifests: piloted agents are hidden from mission roster and represented by the suit unit; expanded compact research branches (weapons/armor/equipment/robots/power-armor/vehicles/psy) with corp budget and advanced gear progression; tests and gameplay doc updated. (completed May 23, 2026)
- [x] RESEARCH-04 Expand branch depth to at least 20 projects: added a third progression tier for each research branch (vehicles/weapons/armor/psy/equipment/robots/power-armor) for a total of 21 projects, while keeping the tree compact and prerequisite-driven; tests and status docs updated. (completed May 23, 2026)
- [x] UI-13 Feed narratif modulaire: crÃ©ation de `game/ui/widgets/narrative/` (`feed_list.py`, `feed_item.py`, `feed_filters.py`), prioritÃ© visuelle `agent`/`consequence` avant `system`/`base`, signaux UX (icÃ´ne, tonalitÃ©, timestamp relatif lisible), filtres rapides (All/Agents/Missions/Factions), et couverture tests ordre/clipping/filtres dans `tests/ui/test_narrative_feed_panel.py`. (completed May 22, 2026)
- [x] UI-10 Polish motion/audio: centralisation des timings/easings (`game/ui/theme/motion.py`), harmonisation transition room-expanded + sÃ©lection mission, micro-animations lÃ©gÃ¨res sur boutons, feedback audio optionnel (toggle `M`) pour actions majeures, checklist `docs/ui/polish-checklist.md`.
- [x] UI-09 Design system modulaire: sÃ©paration `theme/` (tokens/typography/colors), crÃ©ation de composants partagÃ©s `game/ui/components/`, remplacement des styles hardcodÃ©s critiques dans les Ã©crans de commande, documentation `docs/ui/design-system.md` + rÃ©fÃ©rence README, et validation par tests UI ciblÃ©s.
- [x] UI-08 Keyboard-first navigation/accessibility: modÃ¨le de focus commun (rooms/actions/missions), bandeau de hints contextuels par vue, paritÃ© souris/clavier sur actions room + sÃ©lection mission, aide interactive synthÃ©tique (toggle `H`), et tests `tests/ui/test_keyboard_navigation.py`.
- [x] UI-07 Notifications/confirmations: centre de notifications UI lÃ©ger, messages standardisÃ©s pour recrutement/allocation/mission/save-load, confirmation explicite des lancements risquÃ©s, transition de room harmonisÃ©e (durÃ©e/easing), et tests UI de non-rÃ©gression.
- [x] UI-06 AccessibilitÃ© UI: palette vÃ©rifiable (texte/fond/alerte), Ã©tats cliquables normal/hover/active/disabled/focus, indicateurs non chromatiques dans widgets, mode high-contrast via GameState, et tests ciblÃ©s.
- [x] UI-05 Tokeniser les rÃ¨gles visuelles (typo/espacements/opacitÃ©/z-order), appliquer la hiÃ©rarchie titre-section-mÃ©ta dans les room-expanded, et documenter les conventions UI.
- [x] Add full multi-view save/load system with slot-path support and user-facing status log messages
[x] Create mission UI
[x] Add city/corporate tactical command deck to RPG UI
[x] Redesign management and tactical UI shell for city/corporate XCOM2 mood
[x] Redo UI as corporate tower base instead of ship/skyline shell
[x] Add graphical corporate base backdrop image and room hotspots
[x] Replace text panels with clickable room expansion and icon actions
[x] Align clickable room hit zones to generated backdrop rooms
[x] Show cropped room art during room expansion
[x] Add room title, room info, bottom actions, and Esc close behavior
[x] Add labeled actions for black-ops recruitment, leveling, and mission launch
[x] Display the squad roster as graphical personalized agent cards
[x] Fix pending-upgrade roster card rendering
[x] Add click-select squad cards with generated portraits and point counters
[x] Create dedicated corporate funds ledger and show available funds in command UI
[x] Add strategic calendar with daily income, pending fallout, and recovery ticks
[x] Add compact agent equipment loadouts with primary, sidearm, armor, utility, psi focus, and special gear slots
[x] Add mission fund rewards with default post-mission allocation
[x] Add weekly recurring corporate funding tied to the strategic calendar
[x] Add mission duration days to mission templates, board UI, and calendar resolution
[x] Add small strategic event deck for corporate, mutant, Starvers, social, and political threats
[x] Add starter research management with timed funded projects and lab UI
[x] Add spec-ops robot and power-armor assets with deployment, combat conversion, and maintenance costs
[x] Add contextual battle action bar for selected unit combat choices
[x] Create Agent data model
[x] Create district data model
[x] Create mission generation system
[x] Create stress system
[x] Add mission debrief narrative module with GameState persistence and tests
[x] Add reusable squad morale widget (global + per-agent trend)

- [x] Add evacuation mission template focused on living-agent extraction with survival-first scoring, pressure-gated generation odds, and emotional-briefing metadata to reinforce attachment to squad outcomes over kill counts

Done:
- MISSION-02 [done]: Added `game/missions/evacuation.py` as a compact extraction-first mission module, including pressure-scaled constraints, survival-priority scoring, and UI briefing fields (risk/reward/emotional impact); integrated controlled spawn probability into mission generation and covered with dedicated tests. Design justification: emotional attachment is strongest when mission value is tied to who returns alive, not enemy body count.
- MISSION-01 [done]: Objective branches now use 3 compact phase templates (extraction, sabotage, data detour) with a testable evaluation API and UI-readable summaries.
- Recovery-room support dialogues: added `game/narrative/recovery_dialogues.py` with a small deterministic generator driven by stress threshold, affinity priority (same squad then complementary roles), and one-day anti-repetition memory persisted in `GameState.recovery_narrative_memory`; output remains render-neutral (`line` + metadata) to keep narrative modular and memorable without UI coupling.
- Mission narrative debrief API: added `game/narrative/debrief.py` with pure `DebriefLine`/`DebriefReport` data structures, deterministic emotional template mapping from stress/injury/recovery/outcome, post-mission integration in battle resolution, and persisted `latest_mission_debrief` on `GameState` for later UI consumption without view coupling.
- Corporate tower base UI: Corp, City, RPG, and Battle screens now share a
  stacked room cross-section, resource HUD slots, pressure meters, and bottom
  action bars inspired by XCOM2 command-room readability.
- Graphical command backdrop: screens now load `assets/ui/corporate_tower_base.png` and the room-based hub reads as a true tower cutaway instead of a text-heavy shell.
- Click-first rooms: the corporate tower hub opens command, city, squad, assets, research, and intel rooms directly from the painted backdrop, with expansion animation and icon-only actions.
- Image-aligned hit zones: room rectangles are normalized against
  `assets/ui/corporate_tower_base.png`, keeping clicks on the painted rooms
  across window sizes.
- Hub overlay cleanup: the animated room shell no longer paints the generic
  title/info layer over the legacy room renderers, so each room shows only its
  real room UI content.
- Legacy action strip cleanup: the old room-specific action buttons are
  suppressed in hub mode so the icon strip is the only interactive control
  layer in expanded rooms.
- Hub interaction refresh: restored the squad, assets, research, command, and
  city click regions after the tower migration, and widened the intel log and
  debrief text so it stays readable inside the room panels.
- Lower room crop alignment: `assets/ui/rooms/low_left.png` and
  `assets/ui/rooms/low_right.png` were recropped from the tower base so the
  expanded room art matches the painted lower rooms.
- Room crops: each visible base room has a crop in `assets/ui/rooms/`, and the
  expanded room animation renders that image before showing icon actions.
- Expanded room layout: the room title sits at the top, room-specific game info
  sits below it with reserved spacing, icon actions stay at bottom center, and
  Esc closes the room back to the base map.
- Labeled room actions: expanded-room buttons now explain the action textually,
  including Black Ops recruitment, agent stat leveling, and launch mission.
- Graphical roster: squad rooms display current agents as personalized cards
  with role colors, portrait marks, HP/stress bars, selection, recovery, and
  upgrade state; pending-upgrade pips now draw with valid Arcade coordinates.
- Squad card interaction: expanded squad rooms now distinguish the active agent
  from deployment selection, let card clicks choose the active agent, show
  remaining upgrade points, and use 24 generated portrait assets.
- Corporate funds ledger: the global game state now owns a small funds module
  tracking available cash, income, expenses, and transaction history for
  management decisions. Mission successes now add fund rewards through that
  ledger and automatically split payouts into agent morale, research,
  equipment, maintenance, and reserves.
- Strategic calendar: GameState now owns a small campaign calendar that advances
  after mission success/failure or manual command-deck orders, then ticks passive
  income, pending fallout review, weekly planning beats, and agent recovery.
- Weekly corporate funding: a small corporation finance model projects recurring
  stipends after city support, political pressure, and upkeep; crossing into a
  new strategic week deposits that funding through the funds ledger and displays
  the next payment date in corporate management rooms.
- Agent equipment loadouts: characters now reference modular loadouts with
  explicit weapon, armor, utility, psi focus, and special gear slots; combat
  setup reads those items for stat/action adjustments while the character model
  stays data-focused.
- City/corporate tactical command deck: RPG View has separate agent barracks,
  operations table, intel lab, and medbay/fallout panels over the tower base.
- Mission UI: RPG view mission board has selectable rows plus a selected-mission
  detail panel for launch pressure, fund rewards, complications, tags, and
  outcome stakes. Mission templates now carry `duration_days` (defaulting to
  one day), and the board shows that operation duration before launch.
- Mission generation system: mission board entries now regenerate once per strategic day from district pressure, with deterministic day seeds for readable planning and small risk/reward variations.
- Mission duration pacing: mission resolution advances the strategic calendar by
  the mission's `duration_days`, so existing generated missions consume one
  campaign day while later templates can opt into longer operations.
- Strategic events: calendar pressure can now surface unresolved command events
  across enemy corporation attacks, mutant invasions, Starvers outbreaks, social
  unrest, corporate politics, and city politics. Events expire if ignored, and
  response choices can touch funds, agent stress, faction hostility, city
  stability/unrest, and temporary mission availability.
- Research management: the Research Lab now offers one starter project per
  vehicle, weapon, armor, psy, equipment, robot, and power-armor category.
  Projects spend corporate funds up front, tick down with the strategic
  calendar, then apply small unlock flags and stat modifiers to GameState.
- Spec-ops assets: combat robots and power armor now have small data models for
  armor, hardpoints, missile capacity, pilot requirements, and maintenance.
  Deployment can include selected support assets beside selected agents, combat
  setup converts them into distinct Units, and the funds ledger can pay their
  upkeep/repair costs without making them the emotional center of the squad.
- Contextual battle action bar: the battle map now has a reusable selected-unit
  action deck that shows only sensible move, fire, melee, psi, first-aid,
  missile, defend, and end-turn options from pure combat action rules.

- Daily stress recovery now ticks from the strategic calendar: every day lowers
  agent stress by 1, while agents in medical recovery decompress by 2 and log
  visible command-room updates to keep emotional consequences readable.

- Squad morale widget + logic split: added `game/management/morale.py` for
  reusable aggregate morale computation (global score, trend delta, per-agent
  contributions with stable/declining/critical states) and
  `game/ui/widgets/squad_morale_panel.py` for compact render-neutral panel
  lines; RPG room info now consumes the same widget output instead of duplicating
  morale rendering logic.

- [x] Ajouter des rÃ©compenses narratives de faction post-mission (scope compact)
  - Nouveau module: `game/narrative/faction_rewards.py`.
  - RÃ¨gle: attribution uniquement en cas de succÃ¨s mission (`victory=True`), aucune attribution en Ã©chec total.
  - Nature des rÃ©compenses: retours narratifs courts (rumeur/contact/confiance), sans buff systÃ¨me.
  - Fallback: entrÃ©e neutre pour factions non mappÃ©es.
  - Persistance: journal dÃ©diÃ© `GameState.faction_reward_journal` sauvegardÃ©/chargÃ©.
  - Limite de scope: aucun nouveau systÃ¨me Ã©conomique/combat, seulement mÃ©moire narrative et event-log.

- [x] Improve command UI readability: increased typography scale and reduced panel opacity so backdrop art remains visible while text is easier to read.
- [x] UI correction pass: widened intel/debrief wrapping, lifted tactical HUD typography, restored squad roster flow into the room shell, and added readability regressions for title, hub, and battle UI surfaces.

Automation status:
- [done] Add roadmap next-steps generator script (`tools/docs/generate_docs.py`)
- [done] Add unit tests for generator stability/format (`tests/test_generate_docs.py`)
- [done] Generate and publish `## Next 20 Coding Steps` block in `docs/roadmap.md`

- [x] Add lightweight relational tracking contract (mentor links)
  - Field location: `Character.mentor_links` (dictionary keyed by other `agent_id`).
  - Payload per link: `{"agent_id": str, "bond_level": int>=0, "strategic_day": int>=0}`.
  - Invariants: one entry per counterpart, monotonic `bond_level`, monotonic `strategic_day`, no empty `agent_id`.
  - Lifecycle: seeded on recruitment (`game/recruitment.py`), evolved after mission progression (`game/agent_aftermath.py`), persisted by regular character serialization (`to_dict`/`from_dict`) used by save/load.

- [x] Relier les blessures graves Ã  des sÃ©quelles narratives temporaires
  - Module ajoutÃ©: `game/narrative/temporary_scars.py`.
  - Scope strict: narratif-only (tonalitÃ©/tags/logs), sans buff/debuff gameplay.
  - Dissipation journaliÃ¨re via calendrier stratÃ©gique (`GameState.advance_one_day`) et suppression automatique Ã  expiration.
  - Exposition UI data: rÃ©sumÃ© lisible dans le dossier agent, rendu non imposÃ©.

[x] AGENT-05 Personality-trait mission log modulation (compact set + neutral fallback + tests)

- UI-01 [done]: Added a compact narrative feed contract (`game/narrative/event_feed.py`) and widget presentation layer (`game/ui/widgets/narrative_feed_panel.py`) with category badges (`agent`, `mission`, `faction`, `base`), anti-chronological ordering, and bounded depth (8-12) to keep command-center readability centered on agent consequences.

- [x] MISSION-03 Complications modulaires lÃ©gÃ¨res (pression + tags)
  - Nouveau module: `game/missions/complications.py` avec table courte par niveau de pression (`low`/`medium`/`high`).
  - API pure: `select_complications(district_pressure, mission_tags, seed=None)` pour sortie dÃ©terministe et testable.
  - IntÃ©gration: enrichissement du briefing via `game/mission_generation.py` sans hausse systÃ©mique (complications narratif-first, consÃ©quences neutres).
  - Scope control: plafond strict Ã  1-2 complications par mission.
  - Contrainte design: systÃ¨me lÃ©ger, lisible, modulaire, non-systÃ©mique lourd.


[x] UI-04 Mission impact summary: payload enrichi cÃ´tÃ© gÃ©nÃ©ration (`normalized_tags` + `short_text`), affichage liste + dÃ©tail avec hiÃ©rarchie sobre dans `game/ui/mission_board.py`, conventions d'Ã©criture centralisÃ©es (`game/narrative/mission_briefing_conventions.py`) et tests de rendu couvrant tags absents/multiples + impact absent/prÃ©sent.

- [x] UI navigation: focus manager + input map + contextual hints overlay (keyboard/mouse parity for rooms, missions, agents).

- [x] Refactor mission board into sectioned mission detail subcomponents (mission_card, mission_detail, impact_badges) with lock-state messaging and UI-ready emotional risk fields. (completed May 22, 2026)

## Latest UI onboarding slice

[x] Add first-session onboarding package (`game/ui/onboarding`) with separated tutorial steps, overlay state, and English copy
[x] Add persistent cross-view Help panel content (Corp/City/RPG/Battle) with objective, controls, and next action
[x] Add contextual tooltip dictionaries for command center/deck, mission board, and facility interactive elements
[x] Save tutorial progress in `GameState` with replay/skip support
[x] Add UI tests for tutorial progression, overlay visibility, and help panel English content

- [x] UI-17 Spec-Ops assets clarity pass: dedicated guide panel module (`game/ui/screens/spec_ops_assets.py`), acquisition/deployment state copy, battle HUD asset labeling, and post-mission outcomes persisted for debrief/base management; plus docs `docs/gameplay/robots_power_armor.md` and coverage updates in `tests/test_spec_ops_assets.py`.

- [done] Add persistent Next Step guidance system with clickable room/screen routing and stalled-state fallback rules.

- [x] UI-26 Internationalisation compacte (FR/EN): nouveau sous-rÃ©pertoire `game/i18n/` (`fr.py`, `en.py`, helper `t()`), extraction des chaÃ®nes visibles mission/feed/impact, `GameState.ui_language` avec fallback stable, et tests de non-rÃ©gression pour fallback de clÃ©s + rendu mission impact/feed. (completed May 24, 2026)

- [x] UI correction pass: visible resource summaries for credits/intel/salvage/influence, defense surfaced in squad and target UI, and the launch mission button lowered to clear the lower control stack. Added regressions for resource labels, defense readouts, and button placement.
- [x] Agent progression slice: named recruit chooser, compact role specialization tree, terrain-aware battle movement, and a batch of generated tactical map PNG variants based on the existing map set.
- [x] Agent naming cleanup: placeholder labels like `Agent 1` now normalize to role codenames on creation/load, and the recruit chooser sits above the lower HUD controls instead of overlapping them.
- [x] Roster management: added squad-room agent removal from the roster, with selection cleanup and regression coverage.
- [x] Mission/UI readability pass: standardized skill-check one-liners now include check name, roll/total breakdown, threshold, and outcome across action feedback, combat aftermath, mission debrief payload, and narrative feed aggregation.


- [x] Squad management: add Downtime menu (activities consume day/resources and affect morale/stress/traits).

## Engine evaluation spikes

- [x] GODOT-SPIKE-01 Evaluate Godot without migrating the game: isolated project under `experiments/godot_combat_spike/`, minimal 2-agent/2-enemy grid mission, JSON state contract, comparison report, and regression checks. Decision: keep disconnected from the Arcade runtime until a documented migration plan exists.

## Release visual QA and packaging

- [x] UI-QA-01 Keep all three new-campaign difficulty descriptions inside their cards.
- [x] UI-QA-02 Label collapsed-base rooms with names and F1-F6 shortcuts.
- [x] UI-QA-03 Prevent recruitment feedback from overlapping downtime actions.
- [x] PKG-01 Add a Windows onedir PyInstaller release specification.
- [x] PKG-02 Gate the Windows build on tests and document the distribution flow.

## Tactical deployment continuity

- [x] TACTICAL-01 Give each recruit role a distinct battle-ready starter kit.
- [x] TACTICAL-02 Auto-assign new recruits while the active squad has capacity.
- [x] TACTICAL-03 Surface assigned/armed readiness and named kits before launch.
- [x] TACTICAL-04 Preview the enemy faction doctrine on the mission world map.
- [x] TACTICAL-05 Validate recruitment → briefing → deployment → battle visually;
  keep 6-9 candidate pools readable, sanitize technical mission-tag payloads,
  and present pressure plus mission fallout without raw data or clipped copy.

## Management command-card and squad forecast polish

- [x] PREFLIGHT-01 Summarize frontline, ranged, control, and support coverage.
- [x] PREFLIGHT-02 Forecast the likely post-mission recovery load from stress and risk.
- [x] MGMT-UI-01 Replace square icon tiles with compact responsive command cards.
- [x] MGMT-UI-02 Give primary, destructive, system, and standard commands distinct hierarchy.
- [x] MGMT-UI-03 Validate Command Core, Squad Ops, and mission preflight visually;
  keep eleven-command layouts on one row at 1920px and covered by regression tests.

## Tactical Combat Retrofit (active November 2026)

The completed release backlog below remains closed. The new tactical-combat
retrofit is tracked separately in [`tactical_backlog.md`](tactical_backlog.md),
with its evidence-based target in
[`tactical_combat_retrofit.md`](tactical_combat_retrofit.md). Work proceeds in
validated slices of no more than five tasks while Arcade remains authoritative.

## All-map 8K rollout — November 16, 2026

- [x] MAP8K-01 Promote all 122 playable backgrounds to 7680-pixel width while preserving each original aspect ratio; reuse the accepted neon market restoration.
- [x] MAP8K-02 Preserve all obstacle IDs, grid cells, normalized outlines and flags; refresh only image dimensions and SHA-256; retain manual trace files byte-for-byte.
- [x] MAP8K-03 Record source/output fingerprints and restoration sizes, with five resample-only exceptions after three distinct image-generation rejections.
- [x] MAP8K-04 Validate 92 distinct image/survey pairs, inspect six overview sheets and pass all 24 focused map/catalogue/geometry tests.
- [x] MAP8K-05 Publish assets and documentation on `codex/all-maps-8k`, then merge into `main`; production asset names and paths stay unchanged.

The result follows the accepted restoration-plus-resampling workflow; it is not
native 8K generation. Individual visual collision contours remain available for
in-game review. Details: [8K map restoration](maps_8k.md).

## Tactical reference and continuity follow-up — November 16, 2026

- [x] REF-01 Deploy encounters in the main connected floor region; fix the underground market's isolated perimeter without changing wall surveys.
- [x] REF-02 Match the reference route/arrow/AP badge, active ground marker and segmented beveled HP bars with zoom-stable strokes and visible sprite/atlas anchors.
- [x] REF-03 Pause/resume soundtrack transport across UI changes, reuse physical-file aliases and transfer playback positions across the Godot handoff/result boundary.
- [x] REF-04 Pass 37 focused tests, verify connected deployment on all 122 maps and execute/capture a real rightward market move with correct AP and animation.
- [x] REF-05 Document the behavior and capture; publish the verified changes and merge into main.

Details and actual game capture: [Tactical reference](tactical_reference.md).


## Character Sheet Visual 2.0 and healing downtime — November 17, 2026

- [x] CSUI-01 Build reusable dossier geometry, read-only model and shared holographic chrome.
- [x] CSUI-02 Present real portraits, identity, attributes and readiness with existing upgrade actions.
- [x] CSUI-03 Expose all skills and role-specific talent cards with prerequisites, hover details and responsive paging.
- [x] CSUI-04 Add Rest and Hospital for the displayed injured agent; preserve other downtime behavior.
- [x] CSUI-05 Verify native interactions, resolutions and persistence; retain real captures and documentation.

Details: [Character sheet and medical downtime](character_sheet_visual_2.md).
Publication authorized on November 17, 2026: push the verified feature branch and merge into main.

## Mission Briefing Visual 2.0 — November 17, 2026

- [x] MBUI-01 Build responsive three-column geometry and reuse cached holographic primitives.
- [x] MBUI-02 Present contextual mission scenes, all objectives and exact enlarged tactical-map inspection.
- [x] MBUI-03 Render real metrics, roster, selected support, emotional details and distinct consequence panels.
- [x] MBUI-04 Preserve launch/abort routing and add independent overflow controls and accessible responsive card counts.
- [x] MBUI-05 Test native interactions, source-data integrity and resolutions; compare and retain real captures.

Details: [Mission Briefing Visual 2.0](mission_briefing_visual_2.md).
Publication authorized on November 17, 2026: push the verified feature branch and merge into main.

## Main Menu Visual 2.0 — November 17, 2026

- [x] MMUI-01 Generate a cinematic city and metallic wordmark; preserve the original artwork fallback.
- [x] MMUI-02 Build responsive cached chrome, real menu buttons and bounded atmospheric effects.
- [x] MMUI-03 Preserve actions/music/navigation and safely resume actual saves without creating phantom campaigns.
- [x] MMUI-04 Persist reduced motion and display truthful source/packaged build identity in the footer.
- [x] MMUI-05 Verify native controls, resolutions, settings and packaging; retain real captures and publish the validated result.

Details: [Main Menu Visual 2.0](main_menu_visual_2.md).
Push and merge are authorized by the user's standing publication preference.

## Headquarters Visual 2.0 — November 17, 2026

- [x] HQUI-01 Refresh six distinct tower interiors while retaining the original base artwork as fallback.
- [x] HQUI-02 Share calibrated responsive geometry across frames, labels, hover, clicks and footer access.
- [x] HQUI-03 Add live holographic resources, strong single-room focus and restrained cached ambient effects.
- [x] HQUI-04 Preserve department actions and shortcuts with image-aligned expansion and reduced-motion support.
- [x] HQUI-05 Verify native interactions, immutable overview rendering, save/load and resolutions; retain captures and publish the result.

Details: [Headquarters Visual 2.0](headquarters_visual_2.md).
Push and merge are authorized by the user's standing publication preference.

## UI Visual Unification Pass — 17 novembre 2026

- [x] UIUP-01 Extraire le kit graphique partagé de Squad Command : thème, textes et textures en cache, panneaux, cartes, jauges, actions et lecteurs paginés.
- [x] UIUP-02 Moderniser Asset Bay, Command Core, City Grid, Research Lab et Intel Archive avec leurs vraies données et contrôleurs.
- [x] UIUP-03 Unifier recrutement, paramètres, création de campagne, promotions, débriefing, épilogue, missions narratives et liaison Godot.
- [x] UIUP-04 Vérifier les interactions, sauvegardes, langues et résolutions ; corriger la désérialisation des types d’assets du catalogue et conserver les captures réelles.
- [x] UIUP-05 Documenter les composants et la validation, publier la branche validée et fusionner dans main conformément à l’autorisation explicite de l’utilisateur.

Détails et captures : [UI Visual Unification Pass](ui_visual_unification.md).

## Combat Visual 2.4 — 17 novembre 2026

- [x] CV24-01 Remplacer les extrusions de collisions par des annotations visuelles liées aux SHA-256 sources, avec fallback 2D sûr.
- [x] CV24-02 Créer neuf familles d’assemblages et annoter 28 objets identifiés sur quatre environnements.
- [x] CV24-03 Séparer revêtements, faces latérales, contacts, silhouettes et occultation sans modifier les données tactiques.
- [x] CV24-04 Vérifier les 122 cartes, les interactions natives et cinq environnements à trois résolutions ; conserver les captures avant/après.
- [x] CV24-05 Documenter la couverture et les limites ; publier puis fusionner la branche vérifiée conformément à l’autorisation permanente de l’utilisateur.

Détails : [Combat Visual 2.4](combat_visual_24.md).

## Combat — vue de haut 2.5D et échelle des cartes — 17 novembre 2026

- [x] TOP-01 Projeter les décors sans rotation ni compression, avec inverse de clic et cases adaptés.
- [x] TOP-02 Séparer l’échelle artistique des unités des cellules tactiques, avec 122 réglages explicites et zoom adapté.
- [x] TOP-03 Reconstruire et vérifier les 122 relevés / 3 597 obstacles ; conserver les données identiques et rétablir le mobilier source dans la vue de haut.
- [x] TOP-04 Tester les interactions, l’IA, le changement de vue et les trois résolutions ; inspecter les captures de cinq environnements.
- [x] TOP-05 Documenter, archiver les captures et publier/fusionner le résultat vérifié selon l’autorisation permanente de l’utilisateur.

Détails : [Vue de haut 2.5D](combat_top_down.md).

## Échap en combat Godot — 17 novembre 2026

- [x] ESC-01 Remplacer la fermeture du processus par la fermeture des panneaux, sans changer l’état de la mission.
- [x] ESC-02 Vérifier les événements clavier répétés dans les deux HUD ; documenter et publier la correction.

## Cases de déplacement visibles — 17 novembre 2026

- [x] MOVEVIS-01 Renforcer le remplissage cyan et les contours avec contraste sombre, sans modifier les cases accessibles.
- [x] MOVEVIS-02 Vérifier huit tests dont le contraste natif sur trois fonds, inspecter une capture Godot et publier la correction.

## Combat Visual 2.5 — 17 novembre 2026 — couverture artistique partielle

- [x] ART25-01 Inventorier les 122 cartes / 92 illustrations et ajouter des annotations visuelles séparées, avec conservation explicite des cas incertains.
- [x] ART25-02 Produire 16 familles Blender / 64 orientations, finitions artistiques de huit familles et outils reproductibles.
- [x] ART25-03 Intégrer les sprites sans plateforme, leurs silhouettes et les couches sources ; conserver le fallback et les données tactiques.
- [x] ART25-04 Rééquilibrer les portées/dégâts Godot à la demande explicite de l’utilisateur, avec profils courts/longs et tests de tirs réels.
- [ ] ART25-05 Achever la reconstruction artistique de tous les éléments des 122 cartes : gros œuvre, accessoires, raccords et revues détaillées restent à réaliser. La livraison vérifiée documente cette limite.

Détails : [Combat Visual 2.5](combat_visual_25.md) et inventaire/captures par carte.


### Combat Visual 2.5 — extension des décors et des entités

- [x] ART25B-01 Examiner 218 découpes, conserver les décisions et motifs, réutiliser uniquement les illustrations de SHA identique.
- [x] ART25B-02 Produire 10 familles supplémentaires / 40 orientations et finaliser trois familles techniques existantes ; garder les sources Blender et les empreintes de production.
- [x] ART25B-03 Étendre les substitutions à 187 objets sur 108 cartes, conserver les orientations validées et les fallbacks lorsque les ressources ne conviennent pas.
- [x] ART25B-04 Ajouter les ombres de silhouettes aux agents, ennemis, power armors, véhicules et robots ; corriger le chargement typé des actions de soutien sans changer leurs règles.
- [x] ART25B-05 Terminer les contrôles natifs des 122 cartes, exporter les comparaisons et publier cette extension vérifiée. La reconstruction artistique complète reste ouverte sous ART25-05.


### Combat Visual 2.5 — assemblages et avancement global, 18 novembre 2026

- [x] ART25C-01 Créer un suivi global généré, avec historique, preuves de validation et distinction entre rendu natif et finition artistique.
- [x] ART25C-02 Produire six familles composées / 24 vues et les sources Blender ; conserver les variantes incompatibles en fallback.
- [x] ART25C-03 Examiner 145 découpes supplémentaires, annoter les nombres de composants et les débordements visuels séparés des collisions.
- [x] ART25C-04 Achever les contrôles natifs et les comparaisons à trois résolutions ; préserver les agents, ennemis et soutiens.
- [x] ART25C-05 Exporter les preuves, actualiser le fichier d’avancement, push et merge. La reconstruction artistique complète reste ouverte sous ART25-05.

Suivi de la tâche complète : [combat_visual_25_progress.md](combat_visual_25_progress.md).


### Combat Visual 2.5 — proportions du mobilier, 18 novembre 2026

- [x] ART25D-01 Examiner les variantes de lits et de mobilier encore incompatibles.
- [x] ART25D-02 Produire des ressources dédiées aux proportions observées.
- [x] ART25D-03 Intégrer les annotations et contrôler les silhouettes sans modifier la géométrie tactique.
- [x] ART25D-04 Vérifier les rendus natifs, les interactions et les entités aux résolutions cibles.
- [x] ART25D-05 Exporter les comparaisons, mettre à jour le suivi et publier la passe.


### Combat Visual 2.5 — mobilier aux proportions naturelles

- [x] ART25D-01 Revoir visuellement les couchages et bancs, sans déduire leur nature des collisions.
- [x] ART25D-02 Produire quatre variantes adaptées et leurs vues : lit simple, lit de camp, bancs métalliques deux et quatre places.
- [x] ART25D-03 Intégrer uniquement les correspondances validées ; conserver les variantes incertaines et les géométries tactiques.
- [x] ART25D-04 Vérifier le catalogue natif, les interactions et les entités ; comparer les détails à trois résolutions.
- [x] ART25D-05 Actualiser inventaire, preuves et suivi ; pousser et fusionner cette passe. La finition artistique globale reste ouverte.


### Combat Visual 2.5 — priorité aux entités

- [x] ART25E-01 Auditer le rendu des agents, ennemis, robots, power armors et véhicules.
- [x] ART25E-02 Corriger les profils de présentation sans modifier les caractéristiques ni les unités géantes déclarées.
- [x] ART25E-03 Améliorer contours et détails métalliques en préservant l’opacité et la lecture des équipes.
- [x] ART25E-04 Vérifier les interactions, le catalogue et les comparaisons réelles aux trois résolutions.
- [x] ART25E-05 Actualiser les preuves et l’avancement global, puis push et merge.


### Combat Visual 2.5 — premières animations directionnelles réelles

- [x] ART25F-01 Produire des poses détaillées au style des sprites existants pour quatre références, sans utiliser le modèle procédural rejeté.
- [x] ART25F-02 Livrer 192 frames : marche et attente dans huit directions pour un agent, un ennemi, une power armor et un robot.
- [x] ART25F-03 Intégrer ancrage, ombres, phase continue entre cases et chargement avec fallback, sans changer les mécaniques.
- [x] ART25F-04 Vérifier les 128 sélections de frames, le clic réel et les PA ; capturer trois résolutions et cinq environnements.
- [x] ART25F-05 Publier cette passe partielle avec preuves animées et couverture explicite, puis push et merge.

La tâche artistique globale reste ouverte : **4 références sur 231 partiellement animées, zéro ensemble de neuf actions complet**. Les autres agents/ennemis, les autres robots/armures et les véhicules gardent leurs ressources précédentes. Tir, mêlée, couverture, impact, mort, PSI et soin restent à produire.

[Avancement complet](combat_visual_25_progress.md) · [Détails des animations](combat_directional_animation.md).

Le prototype de rig procédural rejeté reste isolé dans `work/`, hors production. Il n’est pas utilisé dans cette livraison.

### Continuité des chantiers — registre et acceptation globale

- [x] GOV-01 Préciser cinq tâches par lot, préserver les règles qualité et permettre les lots successifs.
- [x] GOV-02 Structurer le registre persistant avec états, fichiers, tests, preuves et reste à faire.
- [x] GOV-03 Documenter les critères réels et distinguer chargement, présence de ressources et finition artistique.
- [x] GOV-04 Exécuter et examiner le vérificateur reproductible sur le dépôt réel.
- [x] GOV-05 Vérifier le bilan et le périmètre sans gameplay, puis sauvegarder localement la passe.

Les états détaillés et la prochaine action sont dans [CODEX_PROGRESS.md](CODEX_PROGRESS.md). Le ratio des tâches DONE du registre n’est pas un pourcentage de finition artistique.

### Échelle des entités — passe complète du catalogue

- [x] SCALE-CATALOGUE Revoir les 122 cartes et adapter la taille visuelle des PJ, PNJ, robots, power armors et véhicules aux repères propres à chaque décor (portes, mobilier, voitures intégrées, rues). Profils 0,015 urbain/wasteland et 0,020 intérieur/industrie ; 122 cartes à trois résolutions, clics et zoom vérifiés, sans toucher aux règles, collisions ou sources. Ce contrôle reste distinct de la finition artistique.
- [x] GPU-BENCH Mesurer un combat animé natif Windows à 1440p sur GPU joueur avec FPS/p95, CPU, GPU et mémoire : RTX 5070 Ti, 2 400 frames, 180,53 FPS moyens, p95 8,064 ms après trois atlas complets. Portée limitée à cette machine, sans extrapolation aux exigences minimales.

### Lot suivant d’animations — deux agentes distinctes

- [x] ART-NEXT-01 Contrôler les six planches depuis les deux identités originales.
- [x] ART-NEXT-02 Importer et examiner les deux atlas, huit orientations et marges.
- [x] ART-NEXT-03 Vérifier les six références (192 sélections natives) et 55 tests ciblés du rendu.
- [x] ART-NEXT-04 Capturer les deux déplacements réels, 4 PA chacun, et les trois résolutions.
- [x] ART-NEXT-05 Archiver le catalogue natif, régénérer les bilans et sauvegarder la passe.

Total actuel : 352 frames, six références avec marche/attente ; une agente possède toutes ses actions applicables complètes. Les 230 autres entités restent à compléter.

### Animations applicables — agente aux lames

- [x] ANIM-BLADE-01 Produire des poses authentiques de mêlée, couvert, impact et mort, deux phases × huit orientations.
- [x] ANIM-BLADE-02 Déclarer et justifier l’applicabilité : tir, PSI et soin non applicables à cet équipement et ce rôle.
- [x] ANIM-BLADE-03 Vérifier l’atlas anti-doublons, les ancrages, marges, huit directions et transitions non bouclées.
- [x] ANIM-BLADE-04 Exécuter Godot 4.6.3 natif Windows sur RTX 5070 Ti et capturer la mêlée dans la scène tactique réelle.

Résultat : **1 / 231 ensembles complets**, 5 partiels. Preuves dans [neon-blade-actions](images/neon-blade-actions/README.md). Le chantier animations reste ouvert.

### Animations applicables — agente au pistolet magenta

- [x] ANIM-MAGENTA-01 Produire tir, mêlée, couvert, impact et mort, deux phases × huit orientations.
- [x] ANIM-MAGENTA-02 Justifier PSI et soin non applicables ; conserver toutes les actions tactiques réellement disponibles.
- [x] ANIM-MAGENTA-03 Vérifier atlas, doublons, marges, ancrages et transitions non bouclées.
- [x] ANIM-MAGENTA-04 Capturer cinq actions × huit orientations dans Godot Windows natif.

Résultat cumulé : **2 / 231 ensembles complets**, 4 partiels. Preuves dans [magenta-pistol-actions](images/magenta-pistol-actions/README.md).

### Animations applicables — tireur au manteau

- [x] ANIM-SNIPER-01 Produire tir, mêlée, couvert, impact et mort, deux phases × huit orientations.
- [x] ANIM-SNIPER-02 Justifier PSI et soin non applicables et préserver le fusil unique.
- [x] ANIM-SNIPER-03 Vérifier atlas, doublons, marges, ancrages et transitions.
- [x] ANIM-SNIPER-04 Capturer cinq actions × huit orientations dans Godot Windows natif.

Résultat cumulé à ce checkpoint : **18 / 231 ensembles complets**, 0 partiel. Nouvelles preuves : [armored-vanguard-actions](images/armored-vanguard-actions/README.md) et [chrome-medic-actions](images/chrome-medic-actions/README.md). Les deux familles ont été capturées et inspectées dans Godot Windows natif, soin technologique compris.

### Animations applicables — briseur lourd et frappe jaune

- [x] ANIM-BREACHER-01 Produire attente, marche, tir, mêlée, couvert, impact et mort, avec huit orientations et phases distinctes.
- [x] ANIM-YELLOW-01 Produire attente, marche, tir, mêlée, couvert, impact et mort, avec huit orientations et phases distinctes.
- [x] ANIM-BREACHER-YELLOW-02 Justifier PSI et soin non applicables et préserver les identités/équipements des références.
- [x] ANIM-BREACHER-YELLOW-03 Vérifier les atlas, l’audit anti-doublons et 640 sélections natives Godot.
- [x] ANIM-BREACHER-YELLOW-04 Capturer et inspecter tir, couvert, impact et mort dans Godot Windows natif à 1920×1080.

Résultat cumulé : **20 / 231 ensembles complets**, 0 partiel. Nouvelles preuves : [heavy-breacher-actions](images/heavy-breacher-actions/README.md) et [yellow-strike-actions](images/yellow-strike-actions/README.md). Catalogue Windows 122/122 inspecté et benchmark 1440p régénérés pour la signature `5ea21be0c3ad851669acc5878fcb3f022ea97042a02da7f968f43cf323f292b5`.

### Animations applicables — red enforcer et drone handler

- [x] Produire et auditer 128 frames authentiques par unité, huit orientations et toutes actions applicables.
- [x] Refuser puis régénérer la planche arrière opaque et la fausse mort debout du drone handler.
- [x] Vérifier 704 sélections de frames et capturer les deux unités dans Godot Windows natif.

Résultat cumulé : **22 / 231 ensembles complets**, 0 partiel. Preuves : [red-enforcer-actions](images/red-enforcer-actions/README.md) et [drone-handler-actions](images/drone-handler-actions/README.md). Catalogue Windows 122/122 inspecté et benchmark 1440p régénérés pour la signature `7dd8b0f7b836ec214748eaef76bd6d5ca57708cb1e32417f813ff0dff5be9557`.

### Animations applicables — cyber doc et twin-blade adept

- [x] Produire et auditer les actions applicables, dont le soin cybernétique, sans inventer de tir ou PSI.
- [x] Rejeter et régénérer une mort opaque et une marche arrière à volutes parasites.
- [x] Vérifier 768 sélections natives et les poses de soin, mêlée et mort dans Godot Windows.

Résultat cumulé : **24 / 231 ensembles complets**, 0 partiel. Preuves : [cyber-doc-actions](images/cyber-doc-actions/README.md) et [twin-blade-actions](images/twin-blade-actions/README.md). Catalogue Windows 122/122 inspecté et benchmark 1440p régénérés pour la signature `74b28af121f2f3fea725c972b7ed6c28b107d93047041b6c8b9f5eb5fbe7e729`.

- [x] ANIM-25 Produire et valider nativement l’inquisiteur vétéran : 8 orientations, 128 frames authentiques couvrant `idle`, `move`, `fire`, `melee`, `cover`, `hit`, `death`; `psi` et `heal` explicitement non applicables. Preuves : [veteran-inquisitor-actions](images/veteran-inquisitor-actions/README.md).

Résultat cumulé : **29 / 231 ensembles complets**, 0 partiel. Reste 202 références éligibles ; prochaine référence : `agent_samurai`.

- [x] ANIM-26 Produire et valider nativement la tireuse à dreadlocks : 8 orientations, 128 frames authentiques couvrant `idle`, `move`, `fire`, `melee`, `cover`, `hit`, `death`; `psi` et `heal` explicitement non applicables. Une première planche arrière contaminée a été rejetée puis remplacée. Preuves : [dreadlock-rifle-actions](images/dreadlock-rifle-actions/README.md).
- [x] ANIM-27 Produire et valider nativement le psion encapuchonné : 8 orientations, 144 frames authentiques couvrant `idle`, `move`, `fire`, `melee`, `cover`, `hit`, `death`, `psi`; `heal` explicitement non applicable. Validation ciblée uniquement : 32 sélections natives, 2 tests Python réussis et inspection sur Safehouse.

Résultat cumulé : **29 / 231 ensembles complets**, 0 partiel. Reste 202 références éligibles ; prochaine référence déterminée par l’audit ordonné.

- [x] ANIM-28 Produire et valider nativement la redline runner : 8 orientations, 128 frames authentiques couvrant idle, move, fire, melee, cover, hit et death ; psi et heal non applicables. Validation ciblee sur Safehouse uniquement.

Resultat courant : **29 / 231 ensembles complets**, 0 partiel. Reste 202 references eligibles ; prochaine reference : agent_samurai.

- [x] ANIM-29 Produire et valider nativement agent_psi : 8 orientations, 128 frames authentiques couvrant idle, move, melee, cover, hit, death et psi ; fire et heal non applicables. Validation ciblee sur Safehouse uniquement.

Resultat courant : **29 / 231 ensembles complets**, 0 partiel. Reste 202 references eligibles ; prochaine reference : agent_samurai.

### SCALE — profils et repères du catalogue

- [x] SCALE-01 Inventorier les 122 profils, les 92 illustrations, les empreintes et les alias ; distinguer estimations et mesures.
- [x] SCALE-02 Mesurer et comparer les repères réels des familles et variantes sur les onze planches couvrant 122 cartes.
- [x] SCALE-03 Appliquer des profils visuels par carte et catégorie après mesures ; règles et sources conservées.
- [x] SCALE-04 Vérifier les 122 cartes et les interactions à trois résolutions.
- [x] SCALE-05 Archiver les preuves et ne cocher que les cartes réellement revues.

Les quatre premiers diagnostics utilisent des overrides de capture uniquement ; aucun facteur de taille n’a été appliqué aux profils de production.

### Unified Experience — lot 1 retour de combat

- [x] UE1-01 Auditer et isoler les sessions/résultats versionnés.
- [x] UE1-02 Séparer préparation, consultation et confirmation dans Godot ; ACK et panneau visible.
- [x] UE1-03 Réutiliser la résolution de campagne, valider avant mutation et retirer le raccourci simplifié.
- [x] UE1-04 Débriefing → promotions → HQ, sans statistiques individuelles inventées.
- [x] UE1-05 Vérifier 67 tests distincts et trois parcours natifs Linux ; conserver les limites Windows/crash.

Le chantier global reste incomplet : voir [UNIFIED_EXPERIENCE_PROGRESS.md](UNIFIED_EXPERIENCE_PROGRESS.md).

### Unified Experience — lot 2 récupération durable

- [x] UE2-01 Checkpoints Python atomiques avant et après résolution.
- [x] UE2-02 Continuer reprend le résultat/débriefing et les promotions sans rejouer les récompenses.
- [x] UE2-03 Mailboxes versionnées readiness/résultat et délai d’initialisation.
- [ ] UE2-04 Intégration Win32 améliorée, validation graphique Windows bloquée.
- [x] UE2-05 Crash avant confirmation, reprise du débriefing, captures réelles et régressions ciblées.

Les trois issues réelles et le parcours HQ → Godot → débriefing → HQ sont vérifiés nativement sous Windows. Alt+Tab et réduction/restauration sont PASS ; redimensionnement, DPI multi-écrans et écoute audio restent ouverts. Le préchauffage est écarté après mesure froide à 2,109–3,625 s avec musique Arcade continue.

### Unified Experience — lot 3 continuité musicale

- [x] UE3-01 Ne transférer la lecture qu’après readiness, avec bookmark actualisé.
- [x] UE3-02 Restituer la propriété à Arcade après erreur ou retour.
- [x] UE3-03 Vérifier l’ordre de transfert dans les tests et un vrai processus Godot.

Audio Dummy : pas de validation auditive ni de fondu certifié.

### Unified Experience — lot 4 reprise tactique

- [x] UE4-01 Contrat versionné et frontières de l’état logique documentés.
- [x] UE4-02 Instantanés atomiques différés après les actions.
- [x] UE4-03 Validation double, restauration des unités/PA/objectifs/postures/caméra et modes graphiques.
- [x] UE4-04 Reprise explicite dans un nouvel UUID, annulation des instances précédentes et renvoi d’ACK après crash.
- [x] UE4-05 Tests ciblés et captures natives sur trois résolutions.

Ouverts : mission de campagne entièrement jouée sans issue forcée, mesure/préchauffage, validation Windows et écoute audio réelle. Les jets futurs et les animations en cours ne sont pas repris à l’identique.

- [x] Récupérer les résultats de retraite Godot dont le nom affiché diffère du nom de campagne. Vérifier le rechargement et la réapplication.

- [x] Ouvrir automatiquement le débriefing après récupération d’un résultat Godot et réserver les choix de secours aux interruptions.

- [x] Structurer le débriefing et afficher les libellés des pages de rapport en anglais.
- [ ] Vérifier sur Windows l’absence de flash au démarrage après réduction de la fenêtre initiale et désactivation du logo Godot.

- [x] Audio Overhaul 1.0 : inventorier les bruitages et préparer le manifeste de production.
- [ ] Audio Overhaul 1.0 : générer, écouter et intégrer le lot pilote ElevenLabs. Bloqué par l’absence d’accès au fournisseur.
- [x] Audio Overhaul 1.0 : retirer les 19 anciens SFX et les 3 anciennes musiques WAV, router tous les événements vers la nouvelle banque CC0/CC-BY/utilisateur et utiliser exclusivement les 7 MP3 du nouveau soundtrack. Validation technique automatisée ; écoute artistique encore requise. (19 novembre 2026)
- [x] Audio combat : supprimer les bips de substitution sur fins de mouvement, changements de tour et clics ; conserver uniquement les pas enregistrés et `ui_click_01.wav` pour ces interactions. (19 novembre 2026)
- [x] Audio combat : rendre silencieuses les commandes système `NEXT`, `END TURN` et `RETREAT`, dont la double confirmation de fin de tour produisait deux clics successifs. (19 novembre 2026)
- [x] Audio combat : supprimer le clic ajouté par l'auto-sélection du personnage suivant lorsqu'un agent atteint 0 AP ; le son de l'action reste seul. (19 novembre 2026)
- [x] Interface joueur : retirer de l'écran de déploiement les noms de moteurs, runtimes, processus et détails d'exception ; conserver uniquement un vocabulaire fictionnel. (19 novembre 2026)
- [x] Combat : ne plus afficher de cases de déplacement ou d'attaque lorsqu'un agent sélectionné n'a plus aucun AP. (19 novembre 2026)
- [x] Interface joueur : retirer entièrement le mode de secours de la page de déploiement, y compris son bouton, son raccourci clavier et son ancien chemin de lancement. (19 novembre 2026)
- [x] Combat psi : restaurer `Mind Spike` comme attaque psi ciblée distincte de `Psi Focus`, qui reste le pouvoir de réduction du stress de l'équipe. (19 novembre 2026)
- [x] Interface : imposer l'anglais sur toute la copie joueur Arcade/Godot, migrer implicitement les anciennes sauvegardes françaises, traduire les missions régionales et retirer les réglages techniques du moteur. (19 novembre 2026)
- [x] Godot : traduire les derniers libellés du HUD tactique et donner automatiquement le focus à la carte de combat prête, sans clic préalable dans Arcade. (19 novembre 2026)
- [x] Godot : auditer tous les littéraux du projet, remplacer `JOURNAL DE COMBAT` et `interface classique`, puis retirer le titre moteur et le diagnostic `WALL TEST` de la copie joueur. (19 novembre 2026)
- [x] Régression Godot : corriger l'indentation GDScript cassée pendant la traduction du HUD et ajouter un contrôle natif de parsing ainsi qu'un test réel de deux missions sur le runtime persistant. (19 novembre 2026)
