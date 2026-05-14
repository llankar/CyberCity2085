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
- District Pulse and Latest Fallout panels surface unrest, media heat and consequences
- Each turn grants funds to invest in the corporation
- `1-4` add funds to research, security, politics and black ops
- Budget is refreshed automatically when all funds are spent
- `S` save game / `L` load game

### City View
- District Pressure, Faction Pressure and Operations Log panels show city consequences
- `7-9` allocate city budget

### RPG View
- Readiness Brief previews which agents may crack under the selected mission's stress
- `N` recruit new agent
- `B` start a battle

### Battle View
- Arrow keys move the unit
- `Space` melee attack
- `F` shoot at range
- `P` psi attack
- `V` psi defense
- `D` defend against physical attacks
- PC and enemy icons are displayed on the map
- `Esc` return to management
- On first entering, choose a background image from `assets/maps`
