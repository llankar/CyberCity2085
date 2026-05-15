# Phase 1
- Cool and smart UI
  - Progress: Mission Board now shows selectable missions, objective type, risk,
    fund rewards, duration, pressure, complications, and success/failure stakes
    before launch.
  - Progress: RPG View now uses a focused city/corporate command tower: agent
    barracks, operations table, intel lab, and medbay/fallout floors for a more
    tactical XCOM-like planning mood without changing combat systems.
  - Progress: Corp, City, RPG, and Battle screens now share a corporate tower
    base UI with stacked rooms, resource HUD slots, pressure meters, and bottom
    action strips so the whole game reads as one city command center.
  - Progress: Command screens now use a generated raster corporate-base
    backdrop with room hotspots and glass panels, shifting the presentation away
    from text-only management screens.
  - Progress: Corp, City, RPG, and battle drop-zone selection now use click-first
    room expansion with icon-only action buttons instead of text panels.
  - Progress: Room hit zones now use normalized coordinates measured from the
    generated base art, so clicks line up with the visible rooms as the window
    scales.
  - Progress: Each visible base room now has a cropped room image, and expanded
    rooms render that crop during the grow animation.
  - Progress: Expanded rooms now place the room title at the top, room-specific
    game info below it, icon actions at the bottom center, and Esc returns to
    the base map.
  - Progress: Action buttons now include readable labels, and the graphical room
    flow supports black-ops recruitment, agent leveling, and mission launch.
  - Progress: Squad rooms now render the roster as graphical agent cards with
    role colors, stylized portraits, HP/stress meters, selection state, recovery,
    and upgrade indicators.
  - Progress: Agent cards now use 24 generated portrait assets, strong
    active-agent brackets, click-to-select behavior, and numbered upgrade-point
    badges/buttons for leveling.
  - Progress: Corporate management now has a dedicated funds ledger owned by
    GameState, with available funds shown in command HUD and room info.
    Successful missions now pay a small `fund_reward` through the ledger and
    auto-allocate it across agent morale/pay, research, equipment,
    robot/power-armor maintenance, and corporate reserves.
  - Progress: Strategic time now has a small calendar owned by GameState;
    resolved missions advance by each mission's `duration_days` (one day for
    existing generated missions), while manual command-deck day advances trigger
    daily income, pending fallout review, weekly planning beats, and recovery
    timers.
  - Progress: Corporate finance now has a weekly recurring funding model: the
    calendar pays the funds ledger whenever a new week opens, after stipend,
    city-support, political-pressure, and upkeep calculations.
  - Progress: Agent barracks now supports a small modular equipment slice: each
    agent has loadout slots for primary weapon, sidearm, armor, utility item,
    psi focus/implant, and special gear, and combat unit creation applies those
    bonuses without hard-coding combat behavior into Character.
- District system
- Mission generation
- Black ops

# Phase 2
- Agent system
  - Progress: Loadouts are now a first small agent-system slice, giving agents
    memorable gear choices while preserving scope and modularity.
- Media system
- Relationships
- outside the city missions (wastelands)

# Phase 3
- Corporate politics
- Dynamic factions
- Consequences
