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
- Action buttons include short labels for recruit, level-up, navigation, and
  launch actions
- `Esc` closes the open room and returns to the base map
- Each day grants passive operating funds; crossing into a new strategic week
  also deposits projected corporate funding based on stipend, city support,
  political pressure, and upkeep
- Advancing the calendar can roll unresolved strategic events from city pressure,
  faction hostility, or weighted threat odds, including enemy corporation
  attacks, mutant invasions, Starvers outbreaks, social unrest, corporate
  politics, and city politics
- Corporate rooms show the next weekly income date and projected payment
- `1-4` add funds to research, security, politics and black ops
- Budget is refreshed automatically when all funds are spent
- `S` save game / `L` load game

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
