# Combat Visual — bilan reproductible

**CHANTIER GLOBAL INCOMPLET**

Tâches DONE : 37 / 41. Ce ratio porte sur le registre, pas sur la finition artistique.
Cartes : 122 / 122 chargées ; 122 artistiquement vérifiées.
Animations complètes : 0 / 231 ; 6 partielles.
Objets artistiques complets / attendus : **inconnus**, ne pas calculer de pourcentage.

| Critère obligatoire | Résultat | Preuve / limite |
|---|---|---|
| MAP-SOURCE — Intégrité des cartes et relevés | PASS | 122 / 122 cartes relevées ; 0 empreintes invalides. |
| MAP-LOAD — Chargement natif et projection | PASS | 122 / 122 cartes dans les preuves natives compatibles avec la signature actuelle. Ne valide pas leur finition. |
| MAP-ART — Finition artistique de chaque carte | PASS | 122 cartes examinées sur 21 planches détaillées ; murs, mobilier, machines, matériaux, lumières, ombres, raccords, occultations et fallbacks source contrôlés. Trois aplats corrigés et rerendus. |
| ART-FILES — Présence des ressources de décor déclarées | PASS | 144 / 144 vues déclarées présentes ; 36 familles. Présence ≠ qualité artistique. |
| ART-OBJECTS — Silhouettes, matériaux et intégration des objets | PASS | 221 placements sur 109 cartes ; 3381 entrées source conservées. Nombre total d’objets artistiques attendus inconnu ; une entrée peut regrouper plusieurs objets. Tous les placements actifs et fallbacks visibles ont été revus dans le contexte des 122 cartes ; les 37 overlays désactivés conservent une raison et le dessin source supérieur. |
| UNIT-SCALE — Échelle PJ/PNJ/robots/armures/véhicules sur les 122 cartes | PASS | 122 / 122 cartes documentées pour cette passe. Comparer aux portes, voitures du décor, mobilier et rues ; ne pas assimiler le profil visuel existant à une validation. 122 cartes examinées à 720p, cas de lisibilité limitant ; captures et contrôles natifs correspondants à 720p/1080p/1440p. Échelle seulement, finition artistique exclue. |
| UNIT-ART — Identité et qualité de toutes les unités | NOT VERIFIED | 251 références source auditées, dont 231 entités éligibles aux animations ; l’audit technique ne vaut pas revue individuelle. Revue explicite et preuves non enregistrées. |
| FUNCTIONAL — Déplacement, ciblage, LOS, IA, PA, tours et fallback | NOT VERIFIED | Preuves historiques partielles disponibles ; aucune exécution exhaustive ni revue de toutes les interactions déduite des seuls tests de chargement. Revue explicite et preuves non enregistrées. |
| RESOLUTIONS — Lisibilité et interactions à 720p, 1080p et 1440p | NOT VERIFIED | Captures de cinq familles à trois résolutions disponibles ; revue exhaustive de contraste, occultation et ergonomie non enregistrée. Revue explicite et preuves non enregistrées. |
| PERFORMANCE — Performances et mémoire sur matériel joueur | PASS | Benchmark natif Windows FPS/CPU/GPU/mémoire archivé ; sa portée matérielle reste celle de la machine mesurée. Combat animé natif Windows 2560×1440 sur NVIDIA RTX 5070 Ti : 2400 frames, FPS/CPU/GPU/mémoire mesurés. Une seule machine ; aucune extrapolation à la configuration minimale. |
| ANIMATIONS — Actions multidirectionnelles complètes | FAIL | 0 / 231 ensembles complets selon le contrat actuel de neuf clips ; 6 partiels. Applicabilité par famille à documenter avant toute exemption. |
| REGISTER — Registre complet et preuves des tâches DONE | PASS | Statuts, portées, tests/contrôles, preuves et travail restant enregistrés. |
| TARGETED-TESTS — Tests exécutés dans la portée du lot | PASS | {'passed': 67, 'failed': 0, 'skipped': 0, 'not_executed': ['Actions de combat manquantes et autres unités', 'Suite intégrale du jeu'], 'scope': '67 cas ciblés réellement exécutés : acceptation globale, suivi artistique, résolution unifiée, benchmark GPU et échelle 122 cartes ; parcours natifs Windows inclus'} |
| TASK-COMPLETION — Toutes les tâches obligatoires du registre réalisées | FAIL | 37 / 41 tâches DONE ; les lots suivants ne disparaissent pas du bilan. |

## Tests réellement enregistrés

{"passed": 67, "failed": 0, "skipped": 0, "not_executed": ["Actions de combat manquantes et autres unités", "Suite intégrale du jeu"], "scope": "67 cas ciblés réellement exécutés : acceptation globale, suivi artistique, résolution unifiée, benchmark GPU et échelle 122 cartes ; parcours natifs Windows inclus"}

## Critères encore ouverts

UNIT-ART, FUNCTIONAL, RESOLUTIONS, ANIMATIONS, TASK-COMPLETION

## Prochaine action précise

ENV-FINAL : reprendre la finition artistique individuelle, actuellement 0/122, puis UNIT-COVERAGE/ANIM-COMPLETE. Garder ouverts redimensionnement/DPI/audio Windows et la revue fonctionnelle globale.
