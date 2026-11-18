# Combat Visual 2.5 — avancement de la tâche complète

Mis à jour : 18/11/2026.

**Tâche globale : EN COURS.** Le chargement réussi d’une carte ne signifie pas que sa refonte artistique est terminée.

## État mesuré dans le projet

| Indicateur | État |
|---|---|
| Catalogue | 122 cartes / 92 illustrations distinctes |
| Bibliothèque | 32 familles / 128 vues |
| Familles réellement placées | 24 / 32 |
| Placements actifs | 213 sur 109 cartes |
| Dont groupes partiellement remplacés | 5 |
| Entrées de relevé conservées en 2D | 3389 |
| Cartes déclarées artistiquement terminées | 0 / 122 |

Les entrées de relevé peuvent regrouper plusieurs objets ou des structures. Leur nombre ne permet pas de calculer honnêtement un pourcentage de finition artistique.

[Inventaire détaillé par carte](combat_visual_25_inventory.md).

## Ce qui est livré

- Placements et sprites séparés du sol ; pas d’extrusion du tapis ou des meubles à partir des seules collisions.
- Ombres de silhouettes pour agents, ennemis, power armors, robots et véhicules ; proportions, sélection et restrictions des véhicules en intérieur conservées.
- Portées et dégâts Godot rééquilibrés dans les livraisons précédentes ; aucune nouvelle modification des règles dans cette passe.
- PNG source, SHA-256, collisions, relevés de murs et lignes de vue préservés.
- Assemblages à quatre et six isolateurs, rangées de serveurs, bancs métalliques et végétation sèche ; masques de débordement visuel distincts des collisions.

## Passe en cours

| Travail | État | Résultat / reste à faire |
|---|---|---|
| Suivi global et examen des groupes restants | Terminé | Suivi généré depuis les catalogues ; 145 découpes supplémentaires examinées, soit 363 au total. |
| Ressources correspondant aux assemblages | Terminé | Six familles / 24 vues supplémentaires, dont variantes électriques à quatre et six isolateurs ; modèles Blender et trois planches finales. |
| Annotations et intégration | Terminé | Revue rapprochée des groupes, masques de débordement distincts des collisions et conservation des variantes incompatibles. |
| Validation native et comparaison | Terminé | 122 cartes contrôlées, 23 tests ciblés réussis, comparaisons à trois résolutions et contrôles des entités ; captures isolées des préférences partagées. |
| Inventaire et publication | Terminé | Preuves exportées, fichier d’avancement actualisé ; push et merge vérifiés sur main. |

## Validation

- Dernière livraison de référence : `3e06080ce73b4f0063eb62b0c605bee47aa1deea`.
- Preuves : [captures et inventaire](images/combat-25-assemblies/README.md).
- Concordance du code, des annotations et des sprites de décor : **oui**.
- 122 rendus natifs vérifiés, 23 tests ciblés réussis et cinq tests du suivi ; comparaisons à trois résolutions et contrôles des entités. Le catalogue 7244e46 est rejoué en mémoire pour la comparaison avant/après. Les captures dépendant de préférences partagées ont été refaites et leurs nombres de sprites vérifiés.

## Reste sur l’objectif complet

- Reconstruire davantage de murs, cloisons et structures hautes avec des silhouettes et matériaux adaptés ; conserver leur organisation tactique.
- Traiter les ensembles composés et les objets obliques sans les remplacer par un bloc unique ou un modèle générique agrandi.
- Compléter les accessoires, les variantes usées et les raccords au sol sur les familles encore en rendu source.
- Poursuivre la finition et les animations des entités par rapport à la maquette, en préservant les proportions et les données du jeu.
- Effectuer la revue artistique détaillée carte par carte ; aucune carte n’est cochée comme terminée par un simple test de chargement.
- Compléter les mesures de performances sur GPU joueur ; les contrôles disponibles utilisent le rendu logiciel llvmpipe.

## Historique des livraisons

| Référence | Avancée |
|---|---|
| `35f7b80` | 99 placements actifs sur 97 cartes ; bibliothèque de 16 familles / 64 vues ; validation native du catalogue. |
| `7244e46` | 187 placements sur 108 cartes ; 26 familles / 104 vues ; ombres des entités et correction du chargement des soutiens. |
| `3e06080` | 213 placements sur 109 cartes ; 32 familles / 128 vues ; assemblages adaptés, masques visuels séparés et suivi de la tâche complète. |

Ce fichier est régénéré par `python tools/art/update_environment_progress.py` à partir des catalogues, de la signature de validation et de `combat_visual_25_status.json`. Aucun indicateur de rendu ne coche automatiquement la finition artistique.
