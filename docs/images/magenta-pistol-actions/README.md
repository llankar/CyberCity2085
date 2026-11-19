# Agente au pistolet magenta — actions applicables complètes

Validation native Windows du 19/11/2026 avec Godot 4.6.3 et NVIDIA RTX 5070 Ti.

- 128 frames authentiques : attente 16, marche 32, tir 16, mêlée 16, couvert 16, impact 16, mort 16.
- Huit orientations par action ; deux poses distinctes pour chaque action brève, quatre pour la marche.
- PSI et soin sont non applicables à cette agente sans rôle PSI ni capacité médicale.
- `audit.json` compte désormais 2 ensembles complets sur 231 et 4 ensembles partiels.
- `animation-report.json` et les 40 captures `magenta-*` proviennent de la scène tactique réelle : cinq actions × huit orientations.
- Le test natif a validé les sélections de frames, l’ancrage, l’ombre et l’absence de mutation des données tactiques.

Les planches de production et leurs SHA-256 restent sous `assets/combat_visual/source_sheets/agent_diverse_03_magenta_pistol/` et dans le manifeste de l’atlas.
