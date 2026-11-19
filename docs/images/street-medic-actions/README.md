# Street medic — actions applicables complètes

Validation native Windows du 19/11/2026 avec Godot 4.6.3 et NVIDIA RTX 5070 Ti.

- 144 frames authentiques : attente 16, marche 32, tir 16, mêlée 16, couvert 16, impact 16, état au sol 16 et soin 16.
- Huit orientations par action ; deux poses distinctes pour les actions brèves et quatre pour la marche.
- PSI est non applicable à cette soigneuse sans capacité PSI ; le pistolet visible et le dispositif médical justifient `fire` et `heal`.
- `audit.json` compte 8 ensembles complets sur 231 et aucun ensemble partiel.
- `animation-report.json` et les 48 captures `street-medic-*` proviennent de la scène tactique réelle.

Les neuf planches ont été générées en mode ImageGen intégré à partir de l'illustration de référence. Les prompts imposaient l'identité, huit orientations, des poses distinctes et un fond transparent sans miroir, rotation, socle ou décor. La première planche de soin, entourée d'un nuage gris, a été rejetée puis nettoyée avant import.
