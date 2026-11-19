# Docteure PSI — actions applicables complètes

Validation native Windows du 19/11/2026 avec Godot 4.6.3 et NVIDIA RTX 5070 Ti.

- 144 frames authentiques : attente 16, marche 32, mêlée 16, couvert 16, impact 16, épuisement 16, PSI 16 et soin 16.
- Huit orientations par action ; deux poses distinctes pour les actions brèves et quatre pour la marche.
- Le tir est non applicable : l'illustration et le rôle ne comportent aucune arme, l'action distante étant PSI.
- `audit.json` compte 7 ensembles complets sur 231 et aucun ensemble partiel.
- `animation-report.json` et les 48 captures `psi-doctor-*` proviennent de la scène tactique réelle.

Les neuf planches ont été générées en mode ImageGen intégré à partir de l'illustration de référence, avec fond transparent. Les prompts imposaient l'identité, huit orientations, des poses réellement distinctes et l'absence de miroir, rotation, socle ou décor. Une attente à fond blanc, une mêlée transformée à tort en PSI et une réaction noyée dans un nuage ont été rejetées puis corrigées avant import.
