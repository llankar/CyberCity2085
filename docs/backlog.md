TODO:
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

Done:
- Recovery-room support dialogues: added `game/narrative/recovery_dialogues.py` with a small deterministic generator driven by stress threshold, affinity priority (same squad then complementary roles), and one-day anti-repetition memory persisted in `GameState.recovery_narrative_memory`; output remains render-neutral (`line` + metadata) to keep narrative modular and memorable without UI coupling.
- Mission narrative debrief API: added `game/narrative/debrief.py` with pure `DebriefLine`/`DebriefReport` data structures, deterministic emotional template mapping from stress/injury/recovery/outcome, post-mission integration in battle resolution, and persisted `latest_mission_debrief` on `GameState` for later UI consumption without view coupling.
- Corporate tower base UI: Corp, City, RPG, and Battle screens now share a
  stacked room cross-section, resource HUD slots, pressure meters, and bottom
  action bars inspired by XCOM2 command-room readability.
- Graphical command backdrop: screens now load `assets/ui/corporate_tower_base.png`
  and overlay room hotspots/glass HUD panels so the UI is image-backed instead of
  primarily text blocks.
- Click-first rooms: Corp, City, RPG, and battle drop-zone selection let players
  click highlighted rooms, expand them full-screen, and trigger actions from
  icon-only buttons.
- Image-aligned hit zones: room rectangles are normalized against
  `assets/ui/corporate_tower_base.png`, keeping clicks on the painted rooms
  across window sizes.
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

Automation status:
- [done] Add roadmap next-steps generator script (`tools/docs/generate_docs.py`)
- [done] Add unit tests for generator stability/format (`tests/test_generate_docs.py`)
- [done] Generate and publish `## Next 20 Coding Steps` block in `docs/roadmap.md`

- [x] Add lightweight relational tracking contract (mentor links)
  - Field location: `Character.mentor_links` (dictionary keyed by other `agent_id`).
  - Payload per link: `{"agent_id": str, "bond_level": int>=0, "strategic_day": int>=0}`.
  - Invariants: one entry per counterpart, monotonic `bond_level`, monotonic `strategic_day`, no empty `agent_id`.
  - Lifecycle: seeded on recruitment (`game/recruitment.py`), evolved after mission progression (`game/agent_aftermath.py`), persisted by regular character serialization (`to_dict`/`from_dict`) used by save/load.

- [x] Relier les blessures graves à des séquelles narratives temporaires
  - Module ajouté: `game/narrative/temporary_scars.py`.
  - Scope strict: narratif-only (tonalité/tags/logs), sans buff/debuff gameplay.
  - Dissipation journalière via calendrier stratégique (`GameState.advance_one_day`) et suppression automatique à expiration.
  - Exposition UI data: résumé lisible dans le dossier agent, rendu non imposé.
