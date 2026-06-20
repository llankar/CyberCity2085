
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
- [ ] MISSION-FLOW-02 Pre-battle Deployment Phase: Add a deployment mode before combat starts; show the deployment zone, allow repositioning selected agents and support assets, hide enemies until battle begins, and start combat only after player confirms deployment.
- [x] MISSION-FLOW-03 Enhanced Post-battle Debrief: Created a stronger post-battle debrief screen showing objective result, victory/defeat, rewards, per-agent kills/damage/stress/injuries/XP, triggered complications, faction changes, district changes, narrative consequence lines, and continue button back to ManagementView. Added regression coverage for the required debrief summary fields. (completed June 20, 2026)
- [ ] MISSION-FLOW-04 Consequence Summary Panel: After mission resolution, display a compact consequence panel summarizing changes to city pressure, faction hostility/influence/legitimacy, tags gained, agent scars, rewards, unavailable missions, intel unlocks, and campaign state changes.
- [ ] MISSION-FLOW-05 End-to-end Mission Flow Regression: Add tests for mission selection -> launch -> battle fallback or Godot handoff -> mission resolution -> debrief/consequences -> return to management.

### Phase 2 — Make CyberCity 2085 Identity Visible

- [ ] LORE-01 Expand Core Faction Set: Add first-class faction/content entries for Starvers, Three Sevens, Pharmacorp, Novatek, raiders, mutants, corporate security, hidden AI factions, and local city factions while keeping current vertical slice factions compatible.
- [ ] LORE-02 Starvers / Hungry Tide Integration: Make the Hungry Tide visible in the Intel/Global Scenario UI, showing its progress, threat level, affected regions, expected New York impact, and consequences if ignored.
- [ ] LORE-03 Three Sevens Campaign Presence: Strengthen Three Sevens as a campaign antagonist through story mission injection, intel fragments, event choices, special enemies, propaganda, Warsaw references, and late-campaign escalation.
- [ ] LORE-04 Pharmacorp Cure Thread: Add mission/intel/event hooks around Pharmacorp, the hidden cure, cured Starvers, moral ambiguity, containment failures, and black-market medical choices.
- [ ] LORE-05 Novatek Experiment Thread: Add mission/intel/event hooks around Novatek experiments, cyborg-Starver hybrids, mutant escalation, failed containment sites, and special enemy themes.
- [ ] LORE-06 Hidden AI Conspiracy Thread: Add late-act intel and event hooks for two hidden AI factions: one trying to protect humanity/creators, one seeking human extinction. Do not reveal them too early in the campaign.

### Phase 3 — Global Scenario & Intel Room

- [ ] CAMPAIGN-UI-01 Global Scenario Panel: Create or expand the Intel room panel to display current act, act title, act progress, Hungry Tide percentage, New York status, Warsaw status, discovered intel count, major known threats, and unresolved global events.
- [ ] CAMPAIGN-UI-02 Intel Fragment Browser: Add a readable browser for discovered intel fragments grouped by act/source/faction, distinguish known and unknown entries, and show short lore text plus mechanical relevance.
- [ ] CAMPAIGN-UI-03 World State Change Feed: Add a campaign feed that records major world changes such as New York siege escalation, Warsaw occupation, faction breakthroughs, AI hints, and Starver tide milestones.
- [ ] CAMPAIGN-UI-04 Act Transition Presentation: When an act advances, show a dedicated overlay or screen with act number, title, summary, newly revealed stakes, and immediate strategic consequences.

### Phase 4 — Agent Attachment & RPG Continuity

- [ ] AGENT-RPG-01 Recovery Room Dialogues: Add small post-mission recovery/support dialogue snippets between stressed, wounded, traumatized, or bonded agents.
- [ ] AGENT-RPG-02 Relationship and Mentor Events: Make mentor/protege links and relationships produce occasional event-log lines, recovery bonuses, stress modifiers, or mission banter.
- [ ] AGENT-RPG-03 Temporary Scar Presentation: Make serious wounds and temporary scars visible in agent sheets, debriefs, mission readiness, and recovery panels.
- [ ] AGENT-RPG-04 Agent Nicknames and Reputation: Allow agents to earn nicknames or reputation tags after standout mission events, such as killing an elite, surviving a critical injury, saving a civilian, or failing a traumatic objective.
- [ ] AGENT-RPG-05 Personality-driven Mission Logs: Expand existing personality modulation so mission logs, complications, debrief lines, and stress reactions reflect each agent's personality traits.

### Phase 5 — Tactical Combat Readability and Feel

- [ ] BATTLE-FEEL-01 Floating Damage / Healing / Miss Text: Add short-lived floating combat text for damage, healing, criticals, misses, suppression, and status changes.
- [ ] BATTLE-FEEL-02 Combat Log Side Panel: Make the combat log accessible during battle, ideally with a Tab toggle, category icons, and the latest events.
- [ ] BATTLE-FEEL-03 Status Effects System: Add `status_effects` to units and implement at least suppressed, bleeding, stunned, burning, contaminated, and panicked. Show status badges in the HUD.
- [ ] BATTLE-FEEL-04 Objective Marker Clarity: Ensure all non-elimination objectives have visible map markers, interaction prompts, progress indicators, and failure/success conditions.
- [ ] BATTLE-FEEL-05 Enemy AI Upgrade: Improve enemy AI with cover-seeking, flanking preference, target scoring, commander aura/buffs, and objective pressure behavior.
- [ ] BATTLE-FEEL-06 In-battle Pause Menu: Add an Escape pause overlay with Resume, Settings, Abandon Mission, and Return options where appropriate.

### Phase 6 — Mission Objective Variety

- [ ] OBJECTIVE-01 Extraction Objective: Implement an objective where the squad must reach a target, secure it, and evacuate.
- [ ] OBJECTIVE-02 Sabotage Objective: Implement an objective where the squad must plant a charge or hack a device, then survive or evacuate.
- [ ] OBJECTIVE-03 Data Theft Objective: Implement an objective where an agent must remain near a terminal for a number of turns while the team protects them.
- [ ] OBJECTIVE-04 Containment Objective: Implement an objective where the squad must prevent Starvers or mutants from crossing a threshold or breaching a zone.
- [ ] OBJECTIVE-05 Civilian Rescue Objective: Implement an objective where the squad must rescue multiple civilians or cured Starvers before they are killed or lost.
- [ ] OBJECTIVE-06 Recon / Scan Objective: Implement an objective where the squad must scan several points and may win without eliminating all enemies.

### Phase 7 — Architecture and Maintainability

- [ ] ARCH-01 GameState Domain Split Plan: Document a safe incremental plan to reduce `GameState` god-object risk by moving logic into domain services while keeping save compatibility.
- [ ] ARCH-02 Extract Campaign Service: Keep campaign ticking, act progression, intel reveal, and world state transitions in campaign-specific modules with tests.
- [ ] ARCH-03 Extract Mission Flow Service: Separate mission board generation, launch, handoff, objective resolution, rewards, and consequence presentation from UI screens.
- [ ] ARCH-04 Keep UI Code in `game/ui/screens/`: Continue the existing migration rule: new view-level UI goes into `game/ui/screens/`, while compatibility wrappers stay thin.
- [ ] ARCH-05 Save Migration Tests: Add tests for loading older save payloads and preserving new fields such as campaign state, intel, scars, selected assets, faction tags, and mission board state.
- [ ] ARCH-06 Godot Handoff Contract Tests: Add tests validating that `runtime/godot_combat/mission_handoff.json` contains campaign, mission, map, squad, support assets, tactical actions, and schema version.

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

- [ ] BATTLE-P01 Camera pan: activate existing Camera2D with Shift+arrows; Home re-centers on active unit; clamp to map bounds. Keeps HUD screen-anchored.
- [ ] BATTLE-P02 Floating damage numbers: short-lived text sprites above hit units (`-N` red, `+N` green, `MISS` grey); float 40 px upward, fade over 0.8 s; separate `damage_popups` list in BattleView.
- [ ] BATTLE-P03 Action bar icon pass: extend `draw_action_button` in `battle_hud.py` to accept Unicode icon glyph + label; no new assets required.
- [ ] BATTLE-P04 In-battle pause menu: Escape key during player turn opens Resume/Settings/Abandon overlay; Abandon reuses `confirm_dialog.py`; blocked during enemy turn.
- [ ] BATTLE-P05 Combat log side panel: promote existing `combat_log_panel.py` to player-accessible Tab-toggle side column (8 events, category icons).

### Phase 2 — Full Mission Arc

- [x] BATTLE-A01 Mission Briefing Screen: `MissionBriefingView` now sits between the world-map mission selector and BattleView/Godot handoff, showing mission name/objectives/intel/map thumbnail/squad roster/support assets/emotional impact/stress/reward preview with DEPLOY or ABORT actions. (completed June 20, 2026)
- [ ] BATTLE-A02 Pre-battle Deployment Phase: deployment-mode state in BattleView before turn 1 — highlighted deployment zone, movable unit sprites, DEPLOYMENT phase banner, Enter to begin; enemy units hidden until battle starts.
- [x] BATTLE-A03 Enhanced Post-battle Debrief: `battle_debrief_view.py` now shows per-agent damage/kills/stress/injuries/XP plus objectives, rewards, triggered complications, faction/district changes, narrative consequence lines, and CONTINUE routing back to management. (completed June 20, 2026)

### Phase 3 — Gameplay Depth

- [x] BATTLE-G01 Terrain pathfinding: reduced to one shared tactical movement rule in `game/combat/movement.py`; BattleView deployment/keyboard movement and enemy AI now use the same terrain + occupancy checks. (completed June 7, 2026)
- [ ] BATTLE-G02 Enhanced enemy AI: cover-seeking before attacking; flanking preference using `cover_system.py::flanking_detection`; commander subtype buffs adjacent grunt/heavy AGI.
- [x] BATTLE-G03 Dynamic mid-battle events: added a render-independent `game/combat/events.py` layer for complication-triggered reinforcements and blackout, with `CombatEngine` returning descriptive results for `BattleView` to translate into sprites, sound, screen shake, logs, and fog changes. (completed June 7, 2026)
- [ ] BATTLE-G04 Status effects: add `status_effects: list[str]` to `Unit`; support `suppressed` (−2 move AP), `bleeding` (−1 HP/turn), `stunned` (skip next action); icon badges on unit labels in HUD.

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
