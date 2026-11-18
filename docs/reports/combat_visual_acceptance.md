# Combat Visual — bilan reproductible

**CHANTIER GLOBAL INCOMPLET**

Tâches DONE : 29 / 40. Ce ratio porte sur le registre, pas sur la finition artistique.
Cartes : 0 / 122 chargées ; 0 artistiquement vérifiées.
Animations complètes : 0 / 231 ; 6 partielles.
Objets artistiques complets / attendus : **inconnus**, ne pas calculer de pourcentage.

| Critère obligatoire | Résultat | Preuve / limite |
|---|---|---|
| MAP-SOURCE — Intégrité des cartes et relevés | PASS | 122 / 122 cartes relevées ; 0 empreintes invalides. |
| MAP-LOAD — Chargement natif et projection | NOT VERIFIED | 0 / 122 cartes dans les preuves natives compatibles avec la signature actuelle. Ne valide pas leur finition. |
| MAP-ART — Finition artistique de chaque carte | FAIL | 0 / 122 cartes déclarées finalisées ; revue artistique complète absente. |
| ART-FILES — Présence des ressources de décor déclarées | PASS | 144 / 144 vues déclarées présentes ; 36 familles. Présence ≠ qualité artistique. |
| ART-OBJECTS — Silhouettes, matériaux et intégration des objets | NOT VERIFIED | 221 placements sur 109 cartes ; 3381 entrées source conservées. Nombre total d’objets artistiques attendus inconnu ; une entrée peut regrouper plusieurs objets. Revue explicite et preuves non enregistrées. |
| UNIT-SCALE — Échelle PJ/PNJ/robots/armures/véhicules sur les 122 cartes | NOT VERIFIED | 0 / 122 cartes documentées pour cette passe. Comparer aux portes, voitures du décor, mobilier et rues ; ne pas assimiler le profil visuel existant à une validation. Revue explicite et preuves non enregistrées. |
| UNIT-ART — Identité et qualité de toutes les unités | NOT VERIFIED | 251 références source auditées, dont 231 entités éligibles aux animations ; l’audit technique ne vaut pas revue individuelle. Revue explicite et preuves non enregistrées. |
| FUNCTIONAL — Déplacement, ciblage, LOS, IA, PA, tours et fallback | NOT VERIFIED | Preuves historiques partielles disponibles ; aucune exécution exhaustive ni revue de toutes les interactions déduite des seuls tests de chargement. Revue explicite et preuves non enregistrées. |
| RESOLUTIONS — Lisibilité et interactions à 720p, 1080p et 1440p | NOT VERIFIED | Captures de cinq familles à trois résolutions disponibles ; revue exhaustive de contraste, occultation et ergonomie non enregistrée. Revue explicite et preuves non enregistrées. |
| PERFORMANCE — Performances et mémoire sur matériel joueur | NOT VERIFIED | Un parcours natif NVIDIA RTX 5070 Ti est archivé ; benchmark FPS/CPU/GPU/mémoire reproductible encore absent. Revue explicite et preuves non enregistrées. |
| ANIMATIONS — Actions multidirectionnelles complètes | FAIL | 0 / 231 ensembles complets selon le contrat actuel de neuf clips ; 6 partiels. Applicabilité par famille à documenter avant toute exemption. |
| REGISTER — Registre complet et preuves des tâches DONE | PASS | Statuts, portées, tests/contrôles, preuves et travail restant enregistrés. |
| TARGETED-TESTS — Tests exécutés dans la portée du lot | PASS | {'passed': 54, 'failed': 0, 'skipped': 0, 'not_executed': ['Calibration approuvée des 122 cartes', 'Revue artistique complète des 122 cartes', 'Actions de combat manquantes et autres unités', 'Benchmark GPU joueur', 'Suite intégrale du jeu'], 'scope': '54 cas ciblés réellement exécutés : acceptation globale, suivi artistique et résolution unifiée ; parcours natif Windows réel hors JUnit'} |
| TASK-COMPLETION — Toutes les tâches obligatoires du registre réalisées | FAIL | 29 / 40 tâches DONE ; les lots suivants ne disparaissent pas du bilan. |

## Tests réellement enregistrés

{"passed": 54, "failed": 0, "skipped": 0, "not_executed": ["Calibration approuvée des 122 cartes", "Revue artistique complète des 122 cartes", "Actions de combat manquantes et autres unités", "Benchmark GPU joueur", "Suite intégrale du jeu"], "scope": "54 cas ciblés réellement exécutés : acceptation globale, suivi artistique et résolution unifiée ; parcours natif Windows réel hors JUnit"}

## Critères encore ouverts

MAP-LOAD, MAP-ART, ART-OBJECTS, UNIT-SCALE, UNIT-ART, FUNCTIONAL, RESOLUTIONS, PERFORMANCE, ANIMATIONS, TASK-COMPLETION

## Prochaine action précise

UNIFIED : isoler les temps lancement → readiness et readiness → première frame, puis valider focus, Alt+Tab, réduction/restauration, redimensionnement et DPI multi-écrans sous Windows. Produire ensuite une défaite réelle et implémenter une commande de retraite réelle avant de vérifier la troisième issue. Validation auditive toujours NOT VERIFIED.
