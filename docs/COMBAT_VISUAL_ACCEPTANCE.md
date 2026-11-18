# Combat Visual — critères d’acceptation globaux

**Une fin de lot ne termine jamais le chantier.** Le résultat calculé et les preuves se trouvent dans [le bilan reproductible](reports/combat_visual_acceptance.md) et [son JSON](reports/combat_visual_acceptance.json). Le [registre persistant](CODEX_PROGRESS.md) décrit chaque tâche et sa portée.

## Vérification reproductible

Depuis la racine du projet :

```sh
python -m tools.check_combat_visual_acceptance
python -m tools.check_combat_visual_acceptance --write
python -m pytest -q tests/test_combat_visual_acceptance.py tests/test_environment_progress.py --junitxml=docs/reports/work_governance_tests.xml
```

La première commande est en lecture seule. `--write` actualise uniquement les rapports et la version Markdown du registre, depuis `docs/CODEX_PROGRESS.json`. Aucune carte, unité, donnée tactique ou sauvegarde n’est modifiée. Ne pas lancer les captures ou modifier les ressources artistiques au cours d’une intervention limitée au suivi.

Codes de sortie : **0** tous les critères obligatoires PASS ; **1** au moins un critère FAIL ou NOT VERIFIED ; **2** contrôle non exécutable (donnée manquante/corrompue). Le code 1 est actuellement attendu et ne signifie pas que le chantier est terminé. Une erreur d’exécution n’est jamais convertie en PASS. Avec `--write`, elle remplace l’ancien rapport par NOT VERIFIED et conserve le registre, pour ne pas laisser visible un ancien résultat positif.

## Signification des résultats

- **PASS** : preuve disponible et contrôle réussi dans la portée décrite, sans extension implicite à une autre portée.
- **FAIL** : état mesuré qui ne satisfait pas le critère.
- **NOT VERIFIED** : contrôle, ressource, attente chiffrée ou preuve nécessaire absent, périmé ou non exécuté.

Les tests réussis prouvent uniquement leurs assertions. Un JUnit absent donne des nombres inconnus ; il ne devient pas « zéro échec ». Les suites non exécutées et les tests ignorés restent explicitement signalés. Les anciens 34 tests du rendu restent des preuves historiques distinctes des tests de ce lot de suivi.

## Critères obligatoires

| Identifiant | Attente réelle | Vérification et limite |
|---|---|---|
| MAP-SOURCE | 122 cartes relevées, PNG et SHA-256 préservés | Recalcul des empreintes depuis les sources et leurs relevés. Aucun changement tactique autorisé. |
| MAP-LOAD | 122 cartes rendues nativement, projection/picking contrôlés | Résultats natifs archivés et signature du rendu compatibles. Ce critère ne termine pas l’art. |
| MAP-ART | 122 cartes individuellement finalisées et revues | Drapeaux de finition **et** revue artistique explicite avec preuves. Le simple chargement ne suffit jamais. |
| ART-FILES | Toutes les vues déclarées dans la bibliothèque présentes | Décompte des familles, orientations et PNG. Un fichier présent n’est pas automatiquement beau ou finalisé. |
| ART-OBJECTS | Mobilier, murs, machines et objets crédibles, sans plateformes artificielles | Revue des silhouettes, faces, matériaux, ombres, raccords et occultation ; inventaire des objets attendus à préciser. Les entrées de relevé ne sont pas un nombre total d’objets. |
| UNIT-ART | Agents, ennemis, robots, armures et véhicules cohérents | Revue individuelle des identités, proportions, marges, ancrages et lisibilité ; aucun remplacement global par un clone. |
| ANIMATIONS | Véritables poses multidirectionnelles et actions complètes | Audit des atlas, huit directions et frames distinctes. Contrat actuel : idle, move, fire, melee, cover, hit, death, psi, heal. Documenter l’applicabilité réelle par famille avant toute exemption ; ne pas supprimer un critère pour gonfler la couverture. |
| FUNCTIONAL | Sélection, clics, déplacement, ciblage, LOS, IA, PA, tours et fallbacks préservés | Tests et captures des interactions réelles sur plusieurs familles ; pas de déduction depuis un test de chargement. |
| RESOLUTIONS | Présentation et interactions propres en 1280×720, 1920×1080 et 2560×1440 | Captures et revue de lisibilité, contraste, ancrage, HUD, occultation, zoom et coordonnées. |
| PERFORMANCE | Performance et mémoire acceptables sur matériel représentatif | Mesures à établir sur GPU joueur ; llvmpipe seul ne valide pas ce critère. |
| REGISTER | Suivi avec statuts, fichiers, contrôles, preuves, reste et blocages | DONE sans preuve ou avec travail restant dans sa portée échoue ; BLOCKED nécessite une raison. |
| TASK-COMPLETION | Toutes les tâches obligatoires du registre DONE | Les tâches des lots suivants restent dans le dénominateur. Un registre vide ne vaut pas terminé. |
| TARGETED-TESTS | Tests du lot exécutés et résultats traçables | Lecture du JUnit lié par SHA-256. La portée du lot est indépendante des critères artistiques et fonctionnels globaux. |

## Enregistrer une revue sans inventer de preuve

Dans `docs/CODEX_PROGRESS.json`, `reviews` peut contenir un enregistrement par identifiant de critère : `status` PASS/FAIL, `scope` décrivant toute la portée effectivement revue, `render_signature` du rapport courant et `evidence` avec des objets `{path, sha256}`. La revue doit être réellement effectuée ; ne pas écrire PASS pour faire passer le contrôle. Chaque fichier doit exister dans le dépôt et correspondre à son empreinte. Une modification du rendu ou des ressources rend la revue périmée.

Le script vérifie la traçabilité des preuves ; **il ne juge pas automatiquement la qualité artistique d’une image**. Une revue d’une seule carte ne peut pas être enregistrée comme une revue des 122 cartes.

`test_run` contient le chemin et SHA-256 du JUnit, la portée précise, `sources` liant les fichiers testés à leurs SHA-256, et `not_executed` listant les contrôles encore non exécutés. Le registre JSON est la source structurée ; régénérer le Markdown après toute modification.

## Bilan obligatoire avant toute déclaration finale

Relire les objectifs et le registre, puis rapporter : tâches DONE / total ; cartes chargées / 122 **séparément** des cartes artistiquement vérifiées ; ressources complètes / attendues (ou **inconnu**) ; animations complètes / attendues ; tests passés, échoués, ignorés et non exécutés ; critères encore ouverts.

Si un seul critère obligatoire reste ouvert : **CHANTIER GLOBAL INCOMPLET**. Indiquer la prochaine tâche précise. En cas d’arrêt ou de quota, conserver le registre et les preuves ; annoncer INCOMPLET ou BLOQUÉ avec la raison.
