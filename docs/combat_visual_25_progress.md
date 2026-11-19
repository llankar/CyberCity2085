# Combat Visual 2.5 � avancement de la t�che compl�te

Mis � jour : 19/11/2026.

**T�che globale : EN COURS.** Le chargement r�ussi d�une carte ne signifie pas que sa refonte artistique est termin�e.

## �tat mesur� dans le projet

| Indicateur | �tat |
|---|---|
| Catalogue | 122 cartes / 92 illustrations distinctes |
| Biblioth�que | 36 familles / 144 vues |
| Familles r�ellement plac�es | 28 / 36 |
| Placements actifs | 221 sur 109 cartes |
| Dont groupes partiellement remplac�s | 5 |
| Entr�es de relev� conserv�es en 2D | 3381 |
| Cartes d�clar�es artistiquement termin�es | 122 / 122 |

Les entr�es de relev� peuvent regrouper plusieurs objets ou des structures. Leur nombre ne permet pas de calculer honn�tement un pourcentage de finition artistique.

## Animations des unit�s

| Indicateur | �tat |
|---|---|
| R�f�rences d�entit�s � couvrir (hors objets de mission) | 231 |
| Atlas produits | 26 |
| Marche et attente � huit directions v�rifi�es dans Godot | 26 |
| Unit�s avec toutes les actions applicables anim�es et valid�es | 26 |

Un cycle de marche ne termine pas les animations de combat. Les autres personnages gardent leurs ressources d�origine ; aucune famille n�est remplac�e par un clone g�n�rique.

[Inventaire d�taill� par carte](combat_visual_25_inventory.md).

## Ce qui est livr�

- Placements et sprites séparés du sol ; pas d’extrusion du tapis ou des meubles à partir des seules collisions.
- Ombres de silhouettes pour agents, ennemis, power armors, robots et véhicules ; proportions, sélection et restrictions des véhicules en intérieur conservées.
- Portées et dégâts Godot rééquilibrés dans les livraisons précédentes ; aucune nouvelle modification des règles dans cette passe.
- PNG source, SHA-256, collisions, relevés de murs et lignes de vue préservés.
- Assemblages à quatre et six isolateurs, rangées de serveurs, bancs métalliques et végétation sèche ; masques de débordement visuel distincts des collisions.
- Couchages simples à un oreiller, lits de camp sur cadre ouvert et bancs métalliques à deux ou quatre places ; orientation du refuge corrigée et limites visuelles des cadres séparées des collisions.
- Profils de présentation des entités séparés des données tactiques ; robots de soutien à une échelle cohérente, détails des armures claires et ombres de véhicules différenciées.
- 192 frames dessinées pour quatre références : agent en manteau, ennemi standard, power armor et robot de combat. Attente et marche en huit directions ; autres actions et unités encore à produire.
- Lot 2 : deux agentes distinctes animées (lames et pistolet magenta), +96 frames.
- Vingt-six ensembles complets : toutes les actions applicables validées nativement, dont la tireuse à dreadlocks ; 26 ensembles complets et 0 partiel.

## Passe en cours

| Travail | �tat | R�sultat / reste � faire |
|---|---|---|
| Lot 2 — sources et atlas | Terminé | Deux identités supplémentaires, 96 frames ; six références partiellement animées au total. |
| Lot 2 — lecture et interactions | Terminé | 192 sélections de frames, deux déplacements à 4 PA ; captures aux trois résolutions. |
| SCALE — inventaire | Terminé | 122 profils, 92 illustrations, alias, empreintes et repères visuels examinés. |
| SCALE — calibration par décor | Terminé | Profils 0,015 urbain/wasteland et 0,020 intérieur/industrie appliqués sans modifier la tactique. |
| SCALE — revue et preuves | Terminé | 122 cartes rendues à trois résolutions ; onze planches 720p inspectées ; picking, zoom et ancrage vérifiés. |

## Validation

- Derni�re livraison de r�f�rence : `native Windows entity-scale production review`.
- Preuves : [captures et inventaire](images/entity-scale-production-windows/README.md).
- Concordance du code, des annotations et des sprites de d�cor : **non � nouvelle validation requise pour les modifications en cours**.
- 122 rendus natifs à trois résolutions ; 11 planches 720p inspectées ; échelle 122/122, finition artistique 0/122.

## Reste sur l�objectif complet

- Produire et vérifier les actions applicables des 205 autres références éligibles, à commencer par la prochaine référence ordonnée. Revoir les 46 silhouettes historiques au bord de leur frame ; les véhicules n’ont pas encore de nouveaux cycles.
- Reconstruire davantage de murs, cloisons et structures hautes avec des silhouettes et matériaux adaptés ; conserver leur organisation tactique.
- Traiter les ensembles composés et les objets obliques sans les remplacer par un bloc unique ou un modèle générique agrandi.
- Compléter les accessoires, les variantes usées et les raccords au sol sur les familles encore en rendu source.
- Poursuivre la finition et les animations des entités par rapport à la maquette, en préservant les proportions et les données du jeu.
- Effectuer la revue artistique détaillée carte par carte ; aucune carte n’est cochée comme terminée par un simple test de chargement.
- Conserver le benchmark Windows RTX 5070 Ti à jour après toute modification du rendu ; cette mesure ne définit pas la configuration minimale.

## Historique des livraisons

| R�f�rence | Avanc�e |
|---|---|
| `35f7b80` | 99 placements actifs sur 97 cartes ; bibliothèque de 16 familles / 64 vues ; validation native du catalogue. |
| `7244e46` | 187 placements sur 108 cartes ; 26 familles / 104 vues ; ombres des entités et correction du chargement des soutiens. |
| `3e06080` | 213 placements sur 109 cartes ; 32 familles / 128 vues ; assemblages adaptés, masques visuels séparés et suivi de la tâche complète. |
| `73c4ca1` | 221 placements sur 109 cartes ; 36 familles / 144 vues. Lits simples, lits de camp et bancs adaptés ; orientation et cadres débordants corrigés. |
| `6820eed` | Priorité aux entités : robots de soutien calibrés, détails des armures claires et ombres de véhicules différenciées. 26 tests, 122 cartes et comparaisons à trois résolutions ; audit de 251 références. |
| `d7ef8f7` | 192 frames dessinées pour un agent, un ennemi, une power armor et un robot : marche/attente × 8 directions. 34 tests, 128 sélections de frames natives, clic réel et PA vérifiés, 122 cartes contrôlées. Couverture partielle : 4 / 231 références, aucune unité complète pour les neuf actions. |

Ce fichier est r�g�n�r� par `python tools/art/update_environment_progress.py` � partir des catalogues, de la signature de validation et de `combat_visual_25_status.json`. Aucun indicateur de rendu ne coche automatiquement la finition artistique.
