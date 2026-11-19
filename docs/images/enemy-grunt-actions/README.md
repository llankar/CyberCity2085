# Fantassin de sécurité — actions applicables complètes

Validation native Windows du 19/11/2026 avec Godot 4.6.3 et NVIDIA RTX 5070 Ti.

- 128 frames authentiques : attente 16, marche 32, tir 16, mêlée 16, couvert 16, impact 16, arrêt d'armure 16.
- Huit orientations par action ; deux poses distinctes pour les actions brèves et quatre pour la marche.
- PSI et soin sont non applicables à ce fantassin standard sans rôle PSI ni capacité médicale.
- `audit.json` compte 4 ensembles complets sur 231 et 2 ensembles partiels.
- `animation-report.json` et les 40 captures `grunt-*` proviennent de la scène tactique réelle.

Les planches et leurs SHA-256 sont conservés sous `assets/combat_visual/source_sheets/enemy_grunt/` et dans le manifeste.

Les cinq nouvelles planches ont été générées en mode ImageGen intégré, fond transparent, à partir du design cyan/orange existant : entraînement de tir/recul, mouvement de crosse non tiré, prise de couvert, récupération d'équilibre et arrêt contrôlé de l'armure. Les prompts imposaient une grille 4×4, huit orientations, deux poses réellement distinctes, le corps entier, l'absence de miroir/copie, de socle, de décor et de fausse extrusion. Une première proposition de mêlée trop proche du tir a été rejetée et remplacée avant import.
