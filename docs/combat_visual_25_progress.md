# Combat Visual 2.5 — avancement de la tâche complète

Mis à jour : 18/11/2026.

**Tâche globale : EN COURS.** Le chargement réussi d’une carte ne signifie pas que sa refonte artistique est terminée.

## État mesuré dans le projet

| Indicateur | État |
|---|---|
| Catalogue | 122 cartes / 92 illustrations distinctes |
| Bibliothèque | 36 familles / 144 vues |
| Familles réellement placées | 28 / 36 |
| Placements actifs | 221 sur 109 cartes |
| Dont groupes partiellement remplacés | 5 |
| Entrées de relevé conservées en 2D | 3381 |
| Cartes déclarées artistiquement terminées | 0 / 122 |

Les entrées de relevé peuvent regrouper plusieurs objets ou des structures. Leur nombre ne permet pas de calculer honnêtement un pourcentage de finition artistique.

[Inventaire détaillé par carte](combat_visual_25_inventory.md).

## Ce qui est livré

- Placements et sprites séparés du sol ; pas d’extrusion du tapis ou des meubles à partir des seules collisions.
- Ombres de silhouettes pour agents, ennemis, power armors, robots et véhicules ; proportions, sélection et restrictions des véhicules en intérieur conservées.
- Portées et dégâts Godot rééquilibrés dans les livraisons précédentes ; aucune nouvelle modification des règles dans cette passe.
- PNG source, SHA-256, collisions, relevés de murs et lignes de vue préservés.
- Assemblages à quatre et six isolateurs, rangées de serveurs, bancs métalliques et végétation sèche ; masques de débordement visuel distincts des collisions.
- Couchages simples à un oreiller, lits de camp sur cadre ouvert et bancs métalliques à deux ou quatre places ; orientation du refuge corrigée et limites visuelles des cadres séparées des collisions.

## Passe en cours

| Travail | État | Résultat / reste à faire |
|---|---|---|
| Revue des couchages et bancs | Terminé | 26 découpes de couchages et 17 détails de mobilier examinés ; lits simples distingués des lits doubles, bancs comparés aux silhouettes source. |
| Production de mobilier adapté | Terminé | Quatre familles / 16 vues, modèles Blender et deux planches artistiques. Profondeur des sièges reprise après comparaison. |
| Intégration et contrôle des silhouettes | Terminé | 20 substitutions actives avec ces ressources, dont correction d’un lit tourné de 90° ; deux lits de camp incompatibles et la table d’examen conservent l’art source. |
| Contrôles Godot et comparaisons | Terminé | 122 cartes contrôlées, six comparaisons à trois résolutions, entités et interactions vérifiées ; 25 tests ciblés réussis et 12 tests de ressources réexécutés après correction des cadres. |
| Inventaire et publication | En cours | Préparation des captures, annotations de revue et inventaire global. |

## Validation

- Dernière livraison de référence : `mobilier — 18/11/2026 (publication en cours)`.
- Preuves : [captures et inventaire](images/combat-25-furniture/README.md).
- Concordance du code, des annotations et des sprites de décor : **oui**.
- 122 rendus natifs et leurs nombres de sprites vérifiés ; six cartes comparées à trois résolutions. 25 tests ciblés réussis, puis 12 tests des ressources et du suivi réexécutés après la correction des limites visuelles des lits de camp. Cinq familles d’environnements contrôlées avec agents, ennemis, power armors, robots et véhicules. Catalogue 13a4a1b rejoué en mémoire pour les avant ; captures concernées refaites après correction.

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
