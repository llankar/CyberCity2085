# Agente aux lames — actions applicables complètes

Validation du 19/11/2026 sur Windows avec Godot 4.6.3 et NVIDIA RTX 5070 Ti.

- 112 frames authentiques : attente 16, marche 32, mêlée 16, couvert 16, impact 16, mort 16.
- Huit orientations par action ; deux poses distinctes pour chaque action brève, quatre pour la marche.
- Tir, PSI et soin sont non applicables à cette agente aux deux lames, sans arme à distance, rôle PSI ni capacité médicale.
- `audit.json` compte 1 ensemble complet sur 231 et 5 ensembles partiels.
- `animation-report.json` provient de la scène tactique réelle. Les 16 captures `melee-*` montrent les deux phases dans les huit directions ; `scene-1920x1080.png` confirme l’intégration au décor et au HUD.
- Le test natif a affiché `DIRECTIONAL_ANIMATION_CHECKS_PASSED 192 actual frame selections`, puis a vérifié mêlée, couvert, impact et mort sur huit directions sans modifier les données tactiques.

Les planches de production et leurs SHA-256 restent enregistrés sous `assets/combat_visual/source_sheets/agent_diverse_01_neon_blade/` et dans le manifeste de l’atlas.
