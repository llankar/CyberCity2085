# Combat Visual — bilan reproductible

**CHANTIER GLOBAL INCOMPLET**

Tâches DONE : 42 / 56. Ce ratio porte sur le registre, pas sur la finition artistique.
Cartes : 0 / 122 chargées ; 0 artistiquement vérifiées.
Animations complètes : 64 / 233 ; 0 partielles.
Objets artistiques complets / attendus : **inconnus**, ne pas calculer de pourcentage.

| Critère obligatoire | Résultat | Preuve / limite |
|---|---|---|
| MAP-SOURCE — Intégrité des cartes et relevés | PASS | 122 / 122 cartes relevées ; 0 empreintes invalides. |
| MAP-LOAD — Chargement natif et projection | NOT VERIFIED | 0 / 122 cartes dans les preuves natives compatibles avec la signature actuelle. Ne valide pas leur finition. |
| MAP-ART — Finition artistique de chaque carte | NOT VERIFIED | Revue périmée : le rendu ou les ressources ont changé. |
| ART-FILES — Présence des ressources de décor déclarées | PASS | 144 / 144 vues déclarées présentes ; 36 familles. Présence ≠ qualité artistique. |
| ART-OBJECTS — Silhouettes, matériaux et intégration des objets | NOT VERIFIED | 221 placements sur 109 cartes ; 3381 entrées source conservées. Nombre total d’objets artistiques attendus inconnu ; une entrée peut regrouper plusieurs objets. Revue périmée : le rendu ou les ressources ont changé. |
| UNIT-SCALE — Échelle PJ/PNJ/robots/armures/véhicules sur les 122 cartes | NOT VERIFIED | 122 / 122 cartes documentées pour cette passe. Comparer aux portes, voitures du décor, mobilier et rues ; ne pas assimiler le profil visuel existant à une validation. Revue périmée : le rendu ou les ressources ont changé. |
| UNIT-ART — Identité et qualité de toutes les unités | NOT VERIFIED | 253 références source auditées, dont 233 entités éligibles aux animations ; l’audit technique ne vaut pas revue individuelle. Revue explicite et preuves non enregistrées. |
| FUNCTIONAL — Déplacement, ciblage, LOS, IA, PA, tours et fallback | NOT VERIFIED | Preuves historiques partielles disponibles ; aucune exécution exhaustive ni revue de toutes les interactions déduite des seuls tests de chargement. Revue explicite et preuves non enregistrées. |
| RESOLUTIONS — Lisibilité et interactions à 720p, 1080p et 1440p | NOT VERIFIED | Captures de cinq familles à trois résolutions disponibles ; revue exhaustive de contraste, occultation et ergonomie non enregistrée. Revue explicite et preuves non enregistrées. |
| PERFORMANCE — Performances et mémoire sur matériel joueur | NOT VERIFIED | Benchmark natif Windows FPS/CPU/GPU/mémoire archivé ; sa portée matérielle reste celle de la machine mesurée. Revue périmée : le rendu ou les ressources ont changé. |
| ANIMATIONS — Actions multidirectionnelles complètes | FAIL | 64 / 233 ensembles complets pour toutes leurs actions applicables ; 0 partiels. Chaque exemption doit être justifiée par l’équipement ou le rôle. |
| REGISTER — Registre complet et preuves des tâches DONE | PASS | Statuts, portées, tests/contrôles, preuves et travail restant enregistrés. |
| TARGETED-TESTS — Tests exécutés dans la portée du lot | NOT VERIFIED | {'passed': None, 'failed': None, 'skipped': None, 'not_executed': 'UNKNOWN', 'scope': 'Aucun résultat JUnit enregistré.'} |
| TASK-COMPLETION — Toutes les tâches obligatoires du registre réalisées | FAIL | 42 / 56 tâches DONE ; les lots suivants ne disparaissent pas du bilan. |

## Tests réellement enregistrés

{"passed": null, "failed": null, "skipped": null, "not_executed": "UNKNOWN", "scope": "Aucun résultat JUnit enregistré."}

## Critères encore ouverts

MAP-LOAD, MAP-ART, ART-OBJECTS, UNIT-SCALE, UNIT-ART, FUNCTIONAL, RESOLUTIONS, PERFORMANCE, ANIMATIONS, TARGETED-TESTS, TASK-COMPLETION

## Prochaine action précise

ENV-FINAL : comparer la signature du dernier rendu Windows aux changements de rendu commun, dont l’ancrage des unités. Relancer la validation des 122 cartes pour les changements globaux. ANIM-COMPLETE : poursuivre les atlas authentiques avec des tests par unité.
