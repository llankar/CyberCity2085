# CyberCity2085

Prototype project mixing corporation management, RPG progression and tactical battles built with [Arcade](https://api.arcade.academy/).

Run with:
```bash
pip install -r requirements.txt
python main.py
```

## Project structure
- `assets/` – game art and other assets
- `scenes/` – Tiled TMX maps
- `game/` – core game modules
- `main.py` – starts the game window and initial view

## Controls

### Corp View
- XCOM2-inspired corporate tower frames budget, resources, upgrade sinks,
  district meters and fallout over a generated stacked-base backdrop image
- Click a highlighted room to expand it into a full-screen room; icon buttons
  perform that room's action without text panels
- Room click zones are aligned to the painted rooms in the backdrop image and
  scale with the game window
- Expanded rooms show cropped room art from `assets/ui/rooms/` during the grow
  animation, so the opened room matches the clicked background room
- Open rooms show the room title at the top, room-specific game info beneath it,
  and icon actions at the bottom center
- UI visual rules are tokenized in `game/ui/theme/` (typography hierarchy: title/section/meta; spacing; stroke; opacity; z-order) and reused by expanded-room panels, roster cards, and action buttons to avoid magic numbers
- Action buttons include short labels for recruit, level-up, navigation, and
  launch actions
- Accessibility pass: UI now exposes a dedicated accessibility palette
  (text/background/alert), explicit clickable states (normal/hover/active/
  disabled/focus), and non-chromatic indicators (icon + text prefix) in widget
  lines so meaning is not conveyed by color alone
- High-contrast mode is centrally toggleable via `GameState.ui_high_contrast`
- `Esc` closes the open room and returns to the base map
- Each day grants passive operating funds; crossing into a new strategic week
  also deposits projected corporate funding based on stipend, city support,
  political pressure, and upkeep
- Advancing the calendar can roll unresolved strategic events from city pressure,
  faction hostility, or weighted threat odds, including enemy corporation
  attacks, mutant invasions, Starvers outbreaks, social unrest, corporate
  politics, and city politics
- Corporate rooms show the next weekly income date and projected payment
- The Research Lab lists starter vehicle, weapon, armor, psy, equipment, robot,
  and power-armor projects; each project spends funds, advances with campaign
  days, and completes into unlock flags or small stat modifiers
- `1-4` add funds to research, security, politics and black ops
- Budget is refreshed automatically when all funds are spent
- `S` save game / `L` load game (available from Corp, City, RPG, and Battle views)
- Save files now support nested slot paths (for example `saves/slot_a/campaign.json`)

### City View
- City control tower presents budget networks, district pressure meters, faction
  pressure, active strategic events, and operations feed over the same
  image-backed corporate base
- Click city rooms to expand them and use icon buttons for investment actions
  or the first active event response choices shown in the records room
- `7-9` allocate city budget

### RPG View
- Squad command tower frames planning with agent barracks, operations table,
  intel lab and medbay/fallout floors highlighted over the base art
- Click rooms to recruit agents, cycle agents, select the squad, cycle
  operations, and launch through icon-only controls
- The Black Ops Cell can recruit agents, and Armory/Dossier rooms expose level-up
  stat buttons when the selected agent has pending points
- Squad rooms show the current roster as graphical agent cards with role color,
  generated portraits, HP/stress bars, active-agent brackets, squad-selection
  marks, recovery warnings, and numbered upgrade pips
- Click an agent card in an expanded squad room to make that agent current; level
  buttons show the remaining upgrade-point count for that current agent
- Readiness Brief previews which agents may crack under the selected mission's stress
- Mission Board shows each operation's objective type, risk, target faction,
  launch pressure, complications and success/failure stakes
- `N` recruit new agent
- `B` start a battle

### Battle View
- Tactical combat HUD uses the corporate tower frame for map selection, mission
  objective status, active HP and input actions over the graphical base backdrop
- Drop-zone selection uses the same room expansion and icon-button flow
- Arrow keys move the unit
- `E` interact with tactical objective markers
- `Space` melee attack
- `F` shoot at range
- `P` psi attack
- `V` psi defense
- `D` defend against physical attacks
- PC, enemy and objective markers are displayed on the map
- Complete the battlefield objective or eliminate all enemies to win
- `Esc` return to management
- On first entering, choose a background image from `assets/maps`

## Roadmap generation
- Generate the next prioritized roadmap slice with:
  - `python tools/docs/generate_docs.py`
- The script writes the markdown block to:
  - `docs/roadmap.md`

## UI design system
- Conventions UI et hiérarchie visuelle: `docs/ui/design-system.md`
- Generated output format is stable:
  - `## Next 20 Coding Steps`
  - numbered list from `1` to `20`
  - domain tags such as `[agent]`, `[mission]`, `[ui]`, `[tests]`, `[docs]`

## Mission Board UI Refactor (May 22, 2026)
- Mission details now render in four sections: summary, risk/complications, squad emotional impact, rewards/opportunity cost.
- Mission generation now provides UI-ready fields: `emotional_impact_summary`, `risk_explanation`, `expected_stress_band`.
- Mission detail view now exposes explicit launch lock reasons when missions are unavailable.


## UI architecture migration (May 22, 2026)
- Introduced a dedicated screen-layer package: `game/ui/screens/` for view-level builders (`command_center`, `dashboard`, `facility`, `mission_board`, `research_lab`).

- UI cartographie (phase migration incrémentale):
  - `game/ui/screens/` → `command_center/`, `command_deck/`, `facility/`, `battle_hud/`
  - `game/ui/components/` → `cards/`, `lists/`, `mission/`, `agent/`, `shared/`
  - `game/ui/layouts/` → `grid/`, `split/`, `overlays/`
  - `game/ui/navigation/` → `focus/`, `input/`
  - `game/ui/feedback/` → `toast/`, `dialog/`, `banner/`
  - Wrappers de compatibilité conservés temporairement (`game/ui/command_deck.py`, `game/ui/command_center.py`, `game/ui/facility.py`).
- Existing imports remain stable through temporary compatibility wrappers in `game/ui/*.py` that re-export screen modules.
- Migration strategy is incremental (no big-bang): new extractions should target `game/ui/screens/` first, then remove wrappers once external imports are updated.
