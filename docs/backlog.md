TODO:
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
[x] Add compact agent equipment loadouts with primary, sidearm, armor, utility, psi focus, and special gear slots
[x] Create Agent data model
[ ] Create district data model
[ ] Create mission generation system
[ ] Create stress system

Done:
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
  management decisions.
- Agent equipment loadouts: characters now reference modular loadouts with
  explicit weapon, armor, utility, psi focus, and special gear slots; combat
  setup reads those items for stat/action adjustments while the character model
  stays data-focused.
- City/corporate tactical command deck: RPG View has separate agent barracks,
  operations table, intel lab, and medbay/fallout panels over the tower base.
- Mission UI: RPG view mission board has selectable rows plus a selected-mission
  detail panel for launch pressure, complications, tags, and outcome stakes.
