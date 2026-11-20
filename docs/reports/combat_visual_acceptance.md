# Combat Visual — bilan reproductible

**CHANTIER GLOBAL INCOMPLET**

Tâches DONE : 47 / 62. Ce ratio porte sur le registre, pas sur la finition artistique.
Cartes : 0 / 122 chargées ; 0 artistiquement vérifiées.
Animations complètes : 64 / 233 ; 0 partielles.
Objets artistiques complets / attendus : **inconnus**, ne pas calculer de pourcentage.

| Critère obligatoire | Résultat | Preuve / limite |
|---|---|---|
| MAP-SOURCE — Intégrité des cartes et relevés | PASS | 122 / 122 cartes relevées ; 0 empreintes invalides. |
| MAP-LOAD — Chargement natif et projection | NOT VERIFIED | 0 / 122 cartes dans les preuves natives compatibles avec la signature actuelle. Ne valide pas leur finition. |
| MAP-ART — Finition artistique de chaque carte | NOT VERIFIED | Revue périmée : le rendu ou les ressources ont changé. |
| ART-FILES — Présence des ressources de décor déclarées | PASS | 144 / 144 vues déclarées présentes ; 36 familles. Présence ≠ qualité artistique. |
| ART-OBJECTS — Silhouettes, matériaux et intégration des objets | NOT VERIFIED | 219 placements sur 107 cartes ; 3383 entrées source conservées. Nombre total d’objets artistiques attendus inconnu ; une entrée peut regrouper plusieurs objets. Revue périmée : le rendu ou les ressources ont changé. |
| UNIT-SCALE — Échelle PJ/PNJ/robots/armures/véhicules sur les 122 cartes | NOT VERIFIED | 122 / 122 cartes documentées pour cette passe. Comparer aux portes, voitures du décor, mobilier et rues ; ne pas assimiler le profil visuel existant à une validation. Revue périmée : le rendu ou les ressources ont changé. |
| UNIT-ART — Identité et qualité de toutes les unités | NOT VERIFIED | 253 références source auditées, dont 233 entités éligibles aux animations ; l’audit technique ne vaut pas revue individuelle. Revue explicite et preuves non enregistrées. |
| FUNCTIONAL — Déplacement, ciblage, LOS, IA, PA, tours et fallback | NOT VERIFIED | Preuves historiques partielles disponibles ; aucune exécution exhaustive ni revue de toutes les interactions déduite des seuls tests de chargement. Revue explicite et preuves non enregistrées. |
| RESOLUTIONS — Lisibilité et interactions à 720p, 1080p et 1440p | NOT VERIFIED | Captures de cinq familles à trois résolutions disponibles ; revue exhaustive de contraste, occultation et ergonomie non enregistrée. Revue explicite et preuves non enregistrées. |
| PERFORMANCE — Performances et mémoire sur matériel joueur | NOT VERIFIED | Benchmark natif Windows FPS/CPU/GPU/mémoire archivé ; sa portée matérielle reste celle de la machine mesurée. Revue périmée : le rendu ou les ressources ont changé. |
| ANIMATIONS — Actions multidirectionnelles complètes | FAIL | 64 / 233 ensembles complets pour toutes leurs actions applicables ; 0 partiels. Chaque exemption doit être justifiée par l’équipement ou le rôle. |
| REGISTER — Registre complet et preuves des tâches DONE | PASS | Statuts, portées, tests/contrôles, preuves et travail restant enregistrés. |
| TARGETED-TESTS — Tests exécutés dans la portée du lot | NOT VERIFIED | {'passed': 41, 'failed': 0, 'skipped': 3, 'not_executed': ['Actions de combat manquantes et autres unités', 'Suite intégrale du jeu'], 'scope': '44 cas ciblés : 41 réussis, 3 tests natifs X11 ignorés sous Windows ; acceptation globale, suivi artistique, animations, benchmark GPU et échelle 122 cartes ; trois passes natives Windows exécutées séparément'} |
| TASK-COMPLETION — Toutes les tâches obligatoires du registre réalisées | FAIL | 47 / 62 tâches DONE ; les lots suivants ne disparaissent pas du bilan. |

## Tests réellement enregistrés

{"passed": 41, "failed": 0, "skipped": 3, "not_executed": ["Actions de combat manquantes et autres unités", "Suite intégrale du jeu"], "scope": "44 cas ciblés : 41 réussis, 3 tests natifs X11 ignorés sous Windows ; acceptation globale, suivi artistique, animations, benchmark GPU et échelle 122 cartes ; trois passes natives Windows exécutées séparément"}

## Critères encore ouverts

MAP-LOAD, MAP-ART, ART-OBJECTS, UNIT-SCALE, UNIT-ART, FUNCTIONAL, RESOLUTIONS, PERFORMANCE, ANIMATIONS, TARGETED-TESTS, TASK-COMPLETION

## Prochaine action précise

ENV-FINAL : inspecter les recaptures 1440p corrigées de cybercity_street_10_civic_plaza et cybercity_street_11_civic_plaza dans E:/CyberCity2085-builds/map-planche-06-fix, puis afficher les cinq cartes restantes de la planche 06 à partir de cybercity_street_11_transit_interchange. ANIM-COMPLETE : produire une nouvelle source de enemy_giant_robot_02_quadruped_siege dont les vues cardinales et l'alternance diagonale des jambes sont vérifiables avant tout import, avec tests limités à cette unité.
