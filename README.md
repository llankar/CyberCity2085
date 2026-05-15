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
- XCOM2-inspired corporate command room frames budget, resources, upgrade sinks,
  district meters and fallout as angled tactical panels over the city skyline
- Each turn grants funds to invest in the corporation
- `1-4` add funds to research, security, politics and black ops
- Budget is refreshed automatically when all funds are spent
- `S` save game / `L` load game

### City View
- City control room presents budget networks, district pressure meters, faction
  pressure and operations feed in the same tactical command-shell language
- `7-9` allocate city budget

### RPG View
- Squad command deck frames planning with a squad bay, city ops table,
  operation intel panel and readiness/fallout rail
- Readiness Brief previews which agents may crack under the selected mission's stress
- Mission Board shows each operation's objective type, risk, target faction,
  launch pressure, complications and success/failure stakes
- `N` recruit new agent
- `B` start a battle

### Battle View
- Tactical combat HUD uses the command-shell frame for map selection, mission
  objective status, active HP and input actions
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
