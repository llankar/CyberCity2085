# Lot 2 — deux agentes supplémentaires

**CHANTIER GLOBAL INCOMPLET.** Ce lot ajoute les références `agent_diverse_01_neon_blade` et `agent_diverse_03_magenta_pistol`, avec leurs véritables tenues et équipements : deux lames pour la première, pistolet et tenue magenta pour la seconde.

## Preuves dans le véritable combat

- [Huit directions dans Godot](native-eight-directions.gif) : 32 captures avec phases contrôlées, pour les deux agentes, un ennemi, une power armor et un robot. Cette galerie n’est pas présentée comme une marche autonome.
- [Déplacement par clic de l’agente aux lames](native-click-movement.gif).
- [Déplacement par clic de l’agente au pistolet](native-secondary-movement.gif).
- [Rapport des positions, frames, ressources et PA](animation-report.json) : chacune dépense réellement 4 PA, atteint sa destination et revient à l’attente ; aucune campagne enregistrée.

Les mouvements proviennent de 40 images successives par agente. Les GIF conservent les intervalles réels des images retenues. Ils ne sont pas accélérés ; l’échantillonnage sur llvmpipe ne constitue pas un benchmark de fluidité sur GPU joueur.

## Comparaison et résolutions

[Avant : fallback statique d’origine](before-static-1920x1080.webp) · [Après : phase de marche, caméra identique](directions-00-00.webp).

[1280×720](scene-1280x720.webp) · [1920×1080](scene-1920x1080.webp) · [2560×1440](scene-2560x1440.webp).

Les captures WebP sont sans perte ; les empreintes RGB sont dans [le manifeste](capture-rgb-sha256.json). Les sources PNG du jeu n’ont pas été modifiées.

## Ressources et couverture

| Unité | Aperçu de l’atlas sur fond neutre |
|---|---|
| Agente aux lames — nouvelle | [Marche](agent_diverse_01_neon_blade.gif) |
| Agente au pistolet — nouvelle | [Marche](agent_diverse_03_magenta_pistol.gif) |
| Agent en manteau — précédent | [Marche](agent_diverse_04_trench_sniper.gif) |
| Ennemi standard — précédent | [Marche](enemy_grunt.gif) |
| Power armor — précédente | [Marche](enemy_corp_37_power_armor_grunt.gif) |
| Robot de combat — précédent | [Marche](robot_combat.gif) |

Les aperçus de ressources ne sont pas des captures du jeu. Les deux nouveaux atlas ajoutent **96 frames** ; total **288 frames**, **6 / 231 références partiellement animées**, **zéro ensemble complet des neuf actions**. Chaque référence dispose de deux poses d’attente et quatre phases de marche dans huit directions. Tir, mêlée, couverture, impact, mort, PSI et soin restent à produire. Les véhicules conservent leurs ressources précédentes.

## Vérifications

- Suite ciblée du rendu : **55 tests réussis**, dont **192 sélections de frames natives** sur les six références ; ombres, ancrage, absence de déformation, phase continue et données tactiques préservées.
- Suivi/acceptation après ajout du critère d’échelle : **28 tests réussis**. Les suites se recoupent ; le bilan fusionné compte **56 tests distincts**, pas 83 tests différents.
- [JUnit du rendu](../../reports/roster_batch2_runtime_tests.xml) · [JUnit du suivi](../../reports/roster_batch2_acceptance_tests.xml) · [Union des cas distincts](../../reports/roster_batch2_tests.xml).
- La première tentative a rencontré quatre échecs liés à l’absence de X11 après redémarrage. Le serveur a été rétabli, puis la suite entière a été réexécutée avec succès.
- [Rapport natif des 122 cartes](native-report.json). Le chargement, les nombres de ressources et le picking ne constituent pas une finition artistique ni une validation des tailles relatives au décor.

Planches du catalogue : [1](catalogue-01.jpg), [2](catalogue-02.jpg), [3](catalogue-03.jpg), [4](catalogue-04.jpg), [5](catalogue-05.jpg), [6](catalogue-06.jpg), [7](catalogue-07.jpg), [8](catalogue-08.jpg), [9](catalogue-09.jpg), [10](catalogue-10.jpg), [11](catalogue-11.jpg).

## Travail encore ouvert

La demande de recalibrage des PJ, PNJ, robots, armures et véhicules par rapport aux décors est enregistrée comme **SCALE-CATALOGUE**, avec **0 / 122 cartes vérifiées**. Les repères devront être examinés carte par carte : portes, voitures intégrées, mobilier et rues. Les profils actuels sont des estimations, pas des mesures validées. Aucun facteur de taille n’a été appliqué dans ce lot d’animations.

[Registre persistant](../../CODEX_PROGRESS.md) · [Critères globaux](../../COMBAT_VISUAL_ACCEPTANCE.md) · [Bilan reproductible](../../reports/combat_visual_acceptance.md).
