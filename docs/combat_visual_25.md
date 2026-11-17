# Combat Visual 2.5 — ressources et intégration, couverture artistique partielle

Cette passe ajoute une bibliothèque de véritables objets séparés et étend la séparation des plans aux 122 cartes. **L’objectif de reconstruction artistique complète n’est pas atteint** : une grande partie des murs, meubles et accessoires demeure issue des illustrations d’origine. Aucune carte n’est déclarée artistiquement terminée dans l’inventaire.

## Ce qui est implémenté

- Seize familles d’objets et 64 orientations en PNG transparent : canapé, fauteuil, table, console, caisse, barrière, mur, machine, serveur, ventilation, banc, véhicule, épave rouillée, conteneur, étal de marché et barils.
- Modèles Blender éditables avec géométrie propre : pieds, assises, dossiers, poignées, panneaux, tuyaux, moniteurs, roues et ouvertures distincts. Aucun tapis ni sol n’est extrudé.
- Huit familles ont une finition artistique générée à partir des planches de volumes Blender : cuir, métal, vitrages, bois, écrans, carrosseries et épaves. Les `.blend` correspondants sont des sources de blocage géométrique ; ils ne reproduisent pas exactement la finition générée. Les deux planches finales et les rendus de blocage sont conservés séparément.
- Raccord au sol non destructif : petit masque visuel séparé, texture de sol voisine et bords fondus pour effacer l’ancien objet et son ombre peinte. Les raccords complexes peuvent encore demander une retouche artistique dédiée.
- Placement uniforme sans déformation : l’objet est ajusté à son cadre visuel ; une incompatibilité de proportions fait conserver le dessin d’origine. Les contours alpha réels servent aux ombres et à l’occultation des sprites.
- Séparation des plans pour les éléments conservés : leurs régions de dessin source sont remises au premier plan selon la profondeur des unités, sans leur inventer une catégorie, une hauteur ou un modèle. Il s’agit d’un fallback 2D multicouche, pas d’une reconstruction 3D.
- Lumières localisées existantes conservées, adaptation de luminosité des sprites au matériau source, ombres de contact et atténuation des éléments masquant les unités.
- Cadrage initial plus proche de l’escouade, visant une silhouette de 96 pixels à 1080p lorsque la disposition permet de conserver les agents dans le cadre. Perspective de haut, proportions, zoom maximum et HUD préservés. F10 bascule les décors 2.5D ; F11 conserve l’ancienne projection.

Les fichiers `environment_catalog.gd`, `environment_depth.gd` et `visual_obstacle.gd` portent l’intégration. Les composants 2.4, matériaux et formes sont réutilisés ; aucun deuxième moteur de décor n’a été créé.

## Annotations et couverture

`art/environment/environment_art.json` contient les 122 cartes, leurs empreintes source, cadres visuels, références d’objets, ressources, orientations, éléments encore en 2D, problèmes et validations. Les familles proviennent de sélections explicites après inspection des planches des 92 illustrations distinctes. Les identifiants de relevé sont des liens aux objets examinés, jamais des règles de classification automatique.

La passe active 99 remplacements sur 97 cartes ; 25 candidats sont conservés en rendu original pour incompatibilité de proportions. Les 3 499 entrées de relevé restantes (certaines regroupent plusieurs objets) restent en 2D. L’[inventaire par carte](combat_visual_25_inventory.md) détaille cette couverture. Les candidats rejetés restent listés : ils ne deviennent pas artificiellement des objets améliorés. Un groupe peut n’avoir qu’un élément remplacé ; le reliquat est alors conservé dans l’inventaire 2D.

Les PNG des cartes, `.walls.json`, `.wall-traces.json`, SHA-256, cellules bloquées et relevés ne sont pas modifiés. Les contours sources servent à restituer leur profondeur visuelle ; les nouvelles annotations ne sont jamais injectées dans A*, les collisions ou la ligne de vue. Les données de campagne et sauvegardes ne sont pas réécrites.

## Équilibrage des armes demandé pendant cette passe

Le changement de règles autorisé concerne les portées et dégâts du combat Godot. La hiérarchie s’inspire des rôles tactiques de XCOM et Shadowrun — arme courte, fusil polyvalent, précision, puissance à courte portée — sans prétendre recopier leurs valeurs ni convertir les cases en mètres.

| Action | Portée avant Godot | Portée actuelle | Dégâts de base | PA |
|---|---:|---:|---:|---:|
| Pistol Shot | 3 | 10 | 4 | 1 |
| Rifle Burst | 6 | 24 | 7 | 1 |
| Precision Shot | Action non définie | 36 | 11 | 2 |
| Shotgun Blast | Action non définie | 8 | 9 | 1 |
| Plasma Burst | 5 | 18 | 9 | 2 |
| Missile Salvo | 8 dans les données | 24 effectives | 10 avant réduction radiale | 2 |

Les armes existantes augmentent donc d’au moins ×2. Les fusils dépassent les pistolets ; les tirs de précision portent plus loin. Les noms d’actions déjà transmis par l’équipement (PM, fusil à pompe, précision, armes lourdes, etc.) disposent maintenant de définitions effectives au lieu de tomber dans une action système inconnue. Les profils ennemis suivent la même hiérarchie de portées et dégâts, sans réécrire leur algorithme de décision.

Cet équilibrage concerne le moteur tactique Godot ; le catalogue de simulation Python/Arcade n’est pas rééquilibré par cette passe.

Les tirs de zone utilisent désormais les statistiques de l’arme sélectionnée et vérifient effectivement leur portée avant de consommer des PA. La ligne de vue des tirs directs, les probabilités existantes, déplacements, coûts des actions déjà définies, armes de mêlée et pouvoirs PSI restent inchangés. Le catalogue de campagne/Arcade n’est pas rééquilibré par cette passe Godot.

## Validation et limites

Les tests couvrent les sources des 122 cartes, leurs coordonnées à trois résolutions, l’intégrité des relevés, les contours, les fallbacks, les ressources transparentes, les interactions, les menus et le bridge. Les tests de tir exécutent réellement un tir de fusil à 18 cases, un refus de pistolet sans dépense de PA, les nouveaux dégâts et les statistiques des tirs de zone.

Les 21 contrôles ciblés finaux passent (ressources, intégrité des sources, régressions visuelles, projections, géométrie visuelle, tirs et règles tactiques).

La validation native comprend les 122 cartes, les rendus et leur picking/zoom, puis cinq familles en 1280×720, 1920×1080 et 2560×1440. Déplacement réel, ciblage, passage de tour/IA, qualité et F10/F11 sont contrôlés dans la scène complète. Les captures et mesures sont conservées dans le [rapport visuel](images/combat-25/README.md).

La mémoire statique Godot relevée sur le catalogue s’étend de 246 à 312 Mio. Les fixtures masquent uniquement le bandeau transitoire de début de tour pour inspecter le décor ; le jeu normal le conserve.

Le rendu est contrôlé sur OpenGL logiciel llvmpipe : les mesures de mémoire statique Godot et durées de fixtures sont relevées, mais ne remplacent pas un benchmark GPU sur la machine du joueur. Les aperçus des 122 cartes sont inspectables en planches ; la vérification artistique détaillée se concentre sur les familles, et ne vaut pas validation exhaustive de chaque meuble.

Restent notamment : reconstruction du gros œuvre et de nombreux accessoires, annotations détaillées supplémentaires, raccords locaux complexes, variantes de matériaux et finitions de certains modèles. Les couches sources conservées ne résolvent pas tous les cas d’occultation d’un véritable environnement 3D. **La comparaison avec la maquette reste un objectif ouvert, pas un résultat déclaré atteint.**

## Production reproductible

```sh
blender -b --threads 2 --python tools/art/render_environment_library.py -- godot/combat_missions_ui/art/environment/props25
python tools/art/finish_environment_renders.py godot/combat_missions_ui/art/environment/props25
python tools/art/import_artist_variants.py <planche-principale.png>
python tools/art/import_artist_variants.py <planche-secondaire.png> --families armchair,table,crate,bench --name artist_secondary_atlas.png
python tools/art/validate_environment_placements.py
python tools/art/build_environment_inventory.py
```

Blender n’offre pas OpenImageDenoise dans cette installation. Le débruitage de production repose donc sur un filtre médian léger des intérieurs opaques ; l’alpha original des rendus est préservé. L’import des planches nettoie les pixels parasites détachés, conserve les silhouettes complètes et refuse les images coupées. Les cartes source ne sont pas une cible autorisée de ces outils.
