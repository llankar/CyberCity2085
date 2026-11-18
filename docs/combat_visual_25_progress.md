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

## Animations des unités

| Indicateur | État |
|---|---|
| Références d’entités à couvrir (hors objets de mission) | 231 |
| Atlas produits | 4 |
| Marche et attente à huit directions vérifiées dans Godot | 4 |
| Unités avec les neuf actions animées complètes et validées | 0 |

Un cycle de marche ne termine pas les animations de combat. Les autres personnages gardent leurs ressources d’origine ; aucune famille n’est remplacée par un clone générique.

[Inventaire détaillé par carte](combat_visual_25_inventory.md).

## Ce qui est livré

- Placements et sprites séparés du sol ; pas d’extrusion du tapis ou des meubles à partir des seules collisions.
- Ombres de silhouettes pour agents, ennemis, power armors, robots et véhicules ; proportions, sélection et restrictions des véhicules en intérieur conservées.
- Portées et dégâts Godot rééquilibrés dans les livraisons précédentes ; aucune nouvelle modification des règles dans cette passe.
- PNG source, SHA-256, collisions, relevés de murs et lignes de vue préservés.
- Assemblages à quatre et six isolateurs, rangées de serveurs, bancs métalliques et végétation sèche ; masques de débordement visuel distincts des collisions.
- Couchages simples à un oreiller, lits de camp sur cadre ouvert et bancs métalliques à deux ou quatre places ; orientation du refuge corrigée et limites visuelles des cadres séparées des collisions.
- Profils de présentation des entités séparés des données tactiques ; robots de soutien à une échelle cohérente, détails des armures claires et ombres de véhicules différenciées.
- 192 frames dessinées pour quatre références : agent en manteau, ennemi standard, power armor et robot de combat. Attente et marche en huit directions ; autres actions et unités encore à produire.

## Passe en cours

| Travail | État | Résultat / reste à faire |
|---|---|---|
| Frames au style des sprites existants | Terminé | Quatre identités détaillées conservées ; planches sources et empreintes archivées. Le prototype procédural rejeté reste hors production. |
| Marche et attente dans huit directions | Terminé | 192 frames : 2 poses d’attente et 4 phases de marche × 8 directions pour chacune des quatre références. Les autres actions restent absentes. |
| Lecture et intégration | Terminé | Chargement contrôlé, ancrage aux pieds, ombre liée à la frame, orientation selon projection et phase de marche continue entre cases ; fallback statique préservé. |
| Validation native et artistique | Terminé | 34 tests réussis ; 128 sélections de frames natives. Clic réel avec 4 PA consommés, trois résolutions, cinq familles de cartes et contrôle du catalogue complet. |
| Couverture et publication | Terminé | Couverture, sources et preuves animées publiées ; passe fusionnée sur main. 4 / 231 références partiellement animées, zéro ensemble complet de neuf actions. |

## Validation

- Dernière livraison de référence : `d7ef8f7b3163d81fabaf58f19dfc373db16daa22`.
- Preuves : [captures et inventaire](images/combat-directional-animation/README.md).
- Concordance du code, des annotations et des sprites de décor : **oui**.
- 34 tests ciblés réussis ; 128 sélections de frames dans Godot. Clic natif : destination atteinte, 4 PA consommés, retour à l’attente ; captures aux trois résolutions et cinq environnements. Le contrôle des 122 cartes porte sur le rendu, la projection et le picking, pas sur une finition artistique complète.

## Reste sur l’objectif complet

- Étendre les animations aux 227 autres références éligibles et produire les sept actions manquantes sur les quatre premières ; revoir aussi les 46 silhouettes historiques qui touchent un bord de frame. Les véhicules ne disposent pas encore de nouveaux cycles.
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
| `6820eed` | Priorité aux entités : robots de soutien calibrés, détails des armures claires et ombres de véhicules différenciées. 26 tests, 122 cartes et comparaisons à trois résolutions ; audit de 251 références. |
| `d7ef8f7` | 192 frames dessinées pour un agent, un ennemi, une power armor et un robot : marche/attente × 8 directions. 34 tests, 128 sélections de frames natives, clic réel et PA vérifiés, 122 cartes contrôlées. Couverture partielle : 4 / 231 références, aucune unité complète pour les neuf actions. |

Ce fichier est régénéré par `python tools/art/update_environment_progress.py` à partir des catalogues, de la signature de validation et de `combat_visual_25_status.json`. Aucun indicateur de rendu ne coche automatiquement la finition artistique.
