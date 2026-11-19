# Rail sniper — actions applicables complètes

Validation native Windows du 19/11/2026 avec Godot 4.6.3 et NVIDIA RTX 5070 Ti.

- 128 frames authentiques : attente 16, marche 32, tir 16, mêlée 16, couvert 16, impact 16 et mort 16.
- PSI et soin sont non applicables : aucun pouvoir PSI ni matériel médical.
- `audit.json` compte 14 ensembles complets sur 231 et aucun ensemble partiel.
- `animation-report.json` et les 40 captures `rail-sniper-*` proviennent de la scène tactique réelle.

Les huit planches ont été générées en mode ImageGen intégré depuis l’illustration de référence, avec identité, long rail rifle unique, huit orientations, poses distinctes et vraie transparence. Une première marche avant à fond gris a été rejetée. À l’inspection, trois sorties avaient été mal nommées : la couverture et l’impact ont été réaffectés à leur action correcte, et une mort explicite debout → genoux → corps au sol a été régénérée. Aucun miroir, rotation mécanique, socle ni décor n’est accepté.
