# CODEX — continuité du chantier Combat Visual 2.5

## État global

**EN COURS.** Une passe intermédiaire publiée ne termine pas l’objectif global. Reprendre en lisant ce fichier, puis vérifier `git status`, les manifestes et les preuves réelles. Les détails des cartes restent dans [combat_visual_25_progress.md](combat_visual_25_progress.md) et [l’inventaire](combat_visual_25_inventory.md).

Dernière référence publiée au début de ce lot : `47d593b`. Branche de travail : `codex/directional-agent-roster`.

## Critères d’acceptation

- [ ] Environnements : traiter les 122 cartes avec des objets crédibles, sans plateformes génériques ni altération des sources, SHA-256 ou géométries tactiques.
- [ ] Unités : couvrir les agents joueurs, ennemis, robots, power armors et véhicules avec des identités conservées et de véritables poses multidirectionnelles.
- [ ] Actions : produire et vérifier les clips applicables ; ne pas comptabiliser une attente ou un effet comme une animation de tir, d’impact ou de mort.
- [ ] Intégration : ancrage au sol, proportions, ombres, occultation, sélection et coordonnées de clic cohérents.
- [ ] Validation artistique : examiner les captures et boucles réelles, par famille et résolution ; ne pas déduire la finition d’un simple chargement réussi.
- [ ] Validation fonctionnelle : préserver règles, IA, PA, dégâts, portées, collisions et lignes de vue ; tests ciblés et preuves concrètes.
- [ ] Performance et publication : documenter les limites, conserver les fallbacks et publier uniquement avec autorisation. Publication autorisée par le message « publie à la fin stp ».

## Terminé et vérifié avant ce lot

- 221 placements de décor sur 109 cartes ; 36 familles / 144 vues ; zéro carte déclarée artistiquement complète.
- Quatre références disposent de marche/attente × huit directions : agent en manteau, ennemi standard, power armor et robot de combat.
- 192 frames ; 4 / 231 références éligibles partiellement animées ; zéro ensemble complet de neuf actions.
- 34 tests ciblés, 128 sélections natives de frames, déplacement par clic avec 4 PA, 122 cartes contrôlées et captures à trois résolutions.
- Le modèle procédural rejeté reste hors production. Les autres unités gardent leurs ressources d’origine.

## Lot actuel — cinq tâches maximum

1. **En cours :** produire des poses pour `agent_diverse_01_neon_blade` et `agent_diverse_03_magenta_pistol` depuis leurs véritables PNG ; conserver visage, tenue et équipement.
2. **À faire :** importer marche/attente en huit directions ; examiner silhouettes, marges, armes, cohérence des phases et transparence.
3. **À faire :** étendre les contrôles aux nouveaux atlas sans retirer ceux des robots, armures et ennemis déjà intégrés.
4. **À faire :** capturer et examiner les nouvelles unités dans le véritable combat, aux trois résolutions, avec déplacement et PA vérifiés.
5. **À faire :** actualiser couverture et preuves, sauvegarder le lot dans Git, puis prendre la première tâche restante tant que la session le permet.

## Restant sur l’objectif complet

- Étendre les ressources à toutes les identités, y compris véhicules, autres robots et armures.
- Produire tir, mêlée, couverture, impact, mort, PSI et soin lorsque applicables ; aucun de ces clips n’est livré par la seule marche.
- Poursuivre les murs, structures et meubles encore en rendu source ; revue artistique individuelle des cartes.
- Vérifier les 46 anciennes silhouettes au bord de leur frame ; distinguer audit automatique et validation artistique.
- Mesurer les performances sur GPU joueur : validation disponible sur llvmpipe uniquement.

## Problèmes rencontrés et garde-fous

- Le prototype Blender précédent a été rejeté pour qualité insuffisante ; ne pas le réintroduire.
- Les planches générées peuvent contenir des halos, cadrages ou directions incorrects : contrôler avant import et conserver un fallback propre en cas d’échec.
- Ne pas déformer une image statique ni la décaler pour prétendre produire un cycle ; l’audit rejette les copies simplement translatées/redimensionnées.
- Les fichiers de campagne, cartes et relevés tactiques ne doivent pas être modifiés pour une démonstration.

## Prochaine action précise

Récupérer les six planches de production actuellement demandées (front/rear/idle pour les deux agentes), contrôler visuellement les huit directions, puis les importer avec `tools/art/import_directional_clips.py`. En cas d’interruption, retrouver les originaux dans `/workspace/generated_images/` et lire les métadonnées de provenance des atlas avant de régénérer quoi que ce soit.
