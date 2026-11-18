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
- Profils de présentation des entités séparés des données tactiques ; robots de soutien à une échelle cohérente, détails des armures claires et ombres de véhicules différenciées.

## Passe en cours

| Travail | État | Résultat / reste à faire |
|---|---|---|
| Audit visuel des entités | Terminé | 251 références de sprites inventoriées, dont 231 entités et 20 objets de mission ; versions haute résolution présentes. 46 alphas atteignent un bord de frame, à revoir ; aucun manifeste d’animation livré. |
| Profils de présentation | Terminé | Profils visuels séparés : soutien robot non géant plafonné à 1,65× ; agents, power armors, véritables géants et véhicules préservés. Ombres aériennes et contact des châssis distincts. |
| Lisibilité et matériaux | Terminé | Compression des hautes lumières avant écrêtage ; contours cyan/rouge conservés. Vérifications pixel de l’opacité, des panneaux clairs et des frames réussies. |
| Validation native | Terminé | 26 tests réussis ; 122 cartes contrôlées, comparaisons avant/après et scènes militaires aux trois résolutions. Sélection, ciblage, déplacements, ombres et exclusion des véhicules en intérieur vérifiés. |
| Suivi et publication | En cours | Captures et audit des 251 références exportés ; préparation de l’inventaire global et de la publication. |

## Validation

- Dernière livraison de référence : `entités — 18/11/2026 (publication en cours)`.
- Preuves : [captures et inventaire](images/combat-25-entities/README.md).
- Concordance du code, des annotations et des sprites de décor : **oui**.
- 26 tests ciblés réussis ; 122 rendus natifs et nombres de ressources vérifiés. Avant réels capturés avec 7ea8323 ; cinq environnements aux trois résolutions et scènes militaires supplémentaires avec véhicules terrestres/aériens. Les deux intérieurs testés restent sans véhicules. Audit source de 251 références, distinct de la finition artistique.

## Reste sur l’objectif complet

- Poursuivre les ressources des entités : revoir visuellement les 46 silhouettes qui touchent un bord de frame et produire de véritables animations ; l’audit de 251 références de sprites ne constitue pas une validation artistique individuelle.
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
| `73c4ca1` | 221 placements sur 109 cartes ; 36 familles / 144 vues. Lits simples, lits de camp et bancs adaptés ; orientation et cadres débordants corrigés. |

Ce fichier est régénéré par `python tools/art/update_environment_progress.py` à partir des catalogues, de la signature de validation et de `combat_visual_25_status.json`. Aucun indicateur de rendu ne coche automatiquement la finition artistique.
