# Combat Visual 2.5 — ressources et intégration, couverture artistique partielle

Le [fichier d’avancement de la tâche complète](combat_visual_25_progress.md) indique l’état courant, les validations, les livraisons et les travaux restants.

Cette passe ajoute une bibliothèque de véritables objets séparés et étend la séparation des plans aux 122 cartes. **L’objectif de reconstruction artistique complète n’est pas atteint** : une grande partie des murs, meubles et accessoires demeure issue des illustrations d’origine. Aucune carte n’est déclarée artistiquement terminée dans l’inventaire.

## Ce qui est implémenté

- Trente-deux familles d’objets et 128 orientations en PNG transparent : canapé, fauteuil, table, console, caisse, barrière, mur, machine, serveur, ventilation, banc, véhicule, épave rouillée, conteneur, étal de marché, barils, lit, bureau, casier, jardinières rectangulaire et compacte, transformateur, bac, établi, distributeur et lit médical.
- Modèles Blender éditables avec géométrie propre : pieds, assises, dossiers, poignées, panneaux, tuyaux, moniteurs, roues et ouvertures distincts. Aucun tapis ni sol n’est extrudé.
- Vingt-six familles ont une finition artistique générée à partir des planches de volumes Blender : cuir, métal, vitrages, bois, écrans, carrosseries et épaves. Les `.blend` correspondants sont des sources de blocage géométrique ; ils ne reproduisent pas exactement la finition générée. Les huit planches finales et les rendus de blocage sont conservés séparément.
- Raccord au sol non destructif : petit masque visuel séparé, texture de sol voisine et bords fondus pour effacer l’ancien objet et son ombre peinte. Les raccords complexes peuvent encore demander une retouche artistique dédiée.
- Placement uniforme sans déformation : l’objet est ajusté à son cadre visuel ; une incompatibilité de proportions fait conserver le dessin d’origine. Les contours alpha réels servent aux ombres et à l’occultation des sprites.
- Séparation des plans pour les éléments conservés : leurs régions de dessin source sont remises au premier plan selon la profondeur des unités, sans leur inventer une catégorie, une hauteur ou un modèle. Il s’agit d’un fallback 2D multicouche, pas d’une reconstruction 3D.
- Lumières localisées existantes conservées, adaptation de luminosité des sprites au matériau source, ombres de contact et atténuation des éléments masquant les unités.
- Cadrage initial plus proche de l’escouade, visant une silhouette de 96 pixels à 1080p lorsque la disposition permet de conserver les agents dans le cadre. Perspective de haut, proportions, zoom maximum et HUD préservés. F10 bascule les décors 2.5D ; F11 conserve l’ancienne projection.

Les fichiers `environment_catalog.gd`, `environment_depth.gd` et `visual_obstacle.gd` portent l’intégration. Les composants 2.4, matériaux et formes sont réutilisés ; aucun deuxième moteur de décor n’a été créé.

## Annotations et couverture

`art/environment/environment_art.json` contient les 122 cartes, leurs empreintes source, cadres visuels, références d’objets, ressources, orientations, éléments encore en 2D, problèmes et validations. Les familles proviennent de sélections explicites après inspection des planches des 92 illustrations distinctes. Les identifiants de relevé sont des liens aux objets examinés, jamais des règles de classification automatique.

La première livraison (`35f7b80`) activait 99 remplacements sur 97 cartes. L’extension du 17 novembre activait 187 remplacements sur 108 cartes ; 41 candidats sont conservés en rendu original pour incompatibilité de proportions. Les 3 411 entrées de relevé restantes (certaines regroupent plusieurs objets) restent en 2D. L’[inventaire par carte](combat_visual_25_inventory.md) détaille cette couverture. Les candidats rejetés restent listés : ils ne deviennent pas artificiellement des objets améliorés. Un groupe peut n’avoir qu’un élément remplacé ; le reliquat est alors conservé dans l’inventaire 2D.

L’extension examine 218 découpes d’objets. Les 88 décisions de substitution explicites produisent 104 candidats après réutilisation des seules illustrations de SHA identique ; 88 de ces candidats passent le contrôle de proportions. `expansion_reviews.json` conserve chaque décision, les cas rejetés et leur motif : groupes d’objets, matériel spécialisé, formes en L, vues obliques, végétation morte et écarts entre libellé et dessin. Deux placements de transformateurs sont révoqués après examen natif : le modèle à trois isolateurs remplaçait à tort un ensemble complexe. L’original est restauré et la carte est capturée de nouveau. Une orientation de lit imposée par la revue n’est pas retournée automatiquement pour améliorer artificiellement son score.

Les PNG des cartes, `.walls.json`, `.wall-traces.json`, SHA-256, cellules bloquées et relevés ne sont pas modifiés. Les contours sources servent à restituer leur profondeur visuelle ; les nouvelles annotations ne sont jamais injectées dans A*, les collisions ou la ligne de vue. Les données de campagne et sauvegardes ne sont pas réécrites.

## Agents, ennemis et soutiens

Chaque unité vivante reçoit une ombre projetée à partir du même sprite et de la même frame que son illustration : agents, ennemis, power armors, robots et véhicules. La projection est aplatie au sol, avec adoucissement et contact sous les pieds. Les marges transparentes ne deviennent pas une ombre rectangulaire. Le mode de qualité bas conserve l’ombre de contact simple et retire la projection. L’ombre disparaît avec l’unité morte et suit les animations.

Les illustrations, proportions, profils de taille par carte, équipes, PV et zones de clic restent ceux du jeu. Les vues de validation incluent réellement les deux types de soutien et les véhicules extérieurs, et vérifient leur opacité, leur cadrage de frame et leur sélection. Les cartes intérieures conservent leur exclusion de véhicules. Une erreur de typage Godot empêchant la création des soutiens sans liste d’actions explicite est corrigée par une copie dans le tableau typé, sans changement de la liste d’actions.

Cette passe ne prétend pas remplacer les sprites de personnages par de nouvelles animations ou des modèles 3D.

## Équilibrage des armes de la livraison précédente

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

Les 20 contrôles ciblés de l’extension passent, avec une reprise des neuf contrôles concernés après les dernières corrections de soutiens et d’ombres (ressources, intégrité des sources, régressions visuelles, projections, géométrie visuelle, tirs et règles tactiques).

La validation native comprend les 122 cartes, les rendus et leur picking/zoom, puis cinq familles en 1280×720, 1920×1080 et 2560×1440. Déplacement réel, ciblage, passage de tour/IA, qualité et F10/F11 sont contrôlés dans la scène complète. Les captures et mesures sont conservées dans le [rapport visuel de l’extension](images/combat-25-expansion/README.md).

La mémoire statique Godot relevée sur le catalogue reste autour de 246 à 312 Mio sur l’environnement de validation. Les fixtures masquent uniquement le bandeau transitoire de début de tour pour inspecter le décor ; le jeu normal le conserve.

L’extension ajoute des captures de cinq familles de nouveaux objets et de toutes les familles d’entités, aux trois résolutions. Le contrôle de catalogue écrit un résultat par carte, avec signature des ressources et du rendu, pour pouvoir reprendre une session interrompue sans réutiliser une capture d’une autre version.

Le rendu est contrôlé sur OpenGL logiciel llvmpipe : les mesures de mémoire statique Godot et durées de fixtures sont relevées, mais ne remplacent pas un benchmark GPU sur la machine du joueur. Les aperçus des 122 cartes sont inspectables en planches ; la vérification artistique détaillée se concentre sur les familles, et ne vaut pas validation exhaustive de chaque meuble.

Restent notamment : reconstruction du gros œuvre et de nombreux accessoires, annotations détaillées supplémentaires, raccords locaux complexes, variantes de matériaux et finitions de certains modèles. Les couches sources conservées ne résolvent pas tous les cas d’occultation d’un véritable environnement 3D. **La comparaison avec la maquette reste un objectif ouvert, pas un résultat déclaré atteint.**

## Production reproductible

La suite emploie `--only bed,desk,locker,planter,transformer,bin,workbench,vending,planter_square,medical_bed` pour préserver les ressources artistiques déjà livrées. Importer ensuite les planches avec leurs listes de familles, puis exécuter `apply_reviewed_environment_expansion.py` et `validate_environment_placements.py`. Le générateur ne lit jamais les noms de collisions pour inventer un objet. Les ressources disponibles sans placement suffisamment adapté restent signalées comme telles ; leur simple présence n’est pas une intégration artistique.


```sh
blender -b --threads 2 --python tools/art/render_environment_library.py -- godot/combat_missions_ui/art/environment/props25
python tools/art/finish_environment_renders.py godot/combat_missions_ui/art/environment/props25
python tools/art/import_artist_variants.py <planche-principale.png>
python tools/art/import_artist_variants.py <planche-secondaire.png> --families armchair,table,crate,bench --name artist_secondary_atlas.png
python tools/art/validate_environment_placements.py
python tools/art/build_environment_inventory.py
```

Blender n’offre pas OpenImageDenoise dans cette installation. Le débruitage de production repose donc sur un filtre médian léger des intérieurs opaques ; l’alpha original des rendus est préservé. L’import des planches nettoie les pixels parasites détachés, conserve les silhouettes complètes et refuse les images coupées. Les cartes source ne sont pas une cible autorisée de ces outils.

Les huit planches finales sont versionnées dans `props25/` et peuvent être réimportées directement. L’importeur reconnaît le cas où la planche est déjà à son emplacement final et recalcule les empreintes des 104 sprites. Pour les trois planches de la suite, employer respectivement les familles `bed,desk,locker,planter`, `transformer,bin,workbench,planter_square` et `medical_bed,server,hvac,barrier` avec leurs noms `artist_furniture_expansion.png`, `artist_industry_expansion.png` et `artist_facilities_expansion.png`.


## Passe du 18 novembre — assemblages et suivi global

Six familles supplémentaires (24 vues) complètent la bibliothèque : grilles électriques à quatre et six isolateurs, banc métallique à deux places, paire de bancs, rangée de six serveurs et jardinière sèche. Les modèles physiques sont décrits dans `tools/art/environment_assemblies.py`, réutilisés par le générateur Blender existant. Les nombres de composants sont issus de l’examen des images et conservés dans les annotations ; les noms des collisions ne servent pas de classification.

Les 145 nouvelles découpes portent la revue à 363 cas. Le contrôle de proportions conserve la paire de bancs d’origine lorsque la nouvelle vue ne correspond pas suffisamment au cadre : une ressource produite n’est pas automatiquement un placement validé.

Les isolateurs peints dépassent leur empreinte tactique. Des petits polygones d’effacement visuel sont tracés séparément pour retirer les anciens sommets, tout en conservant les équipements voisins. Aucune cellule, collision, ligne de vue ou texture source n’est modifiée. Les ensembles électriques sont signalés comme partiellement remplacés lorsque des éléments de contrôle restent issus du dessin source.

Le [suivi global](combat_visual_25_progress.md) est généré depuis les catalogues et le statut de la passe. Il compte séparément les ressources disponibles, familles réellement placées, placements actifs, groupes partiels, entrées conservées et cartes artistiquement terminées. Une signature du code, des shaders, des annotations et des sprites empêche d’afficher une ancienne validation comme actuelle après modification. La tâche reste explicitement en cours, sans pourcentage de finition inventé.


### 18 novembre 2026 — couchages et sièges aux proportions adaptées

Cette passe corrige des correspondances artistiques trop génériques, sans changer la vue de haut, le HUD ni les dimensions des unités. Les couchages étroits identifiés sur les sources utilisent désormais une variante à une place et un seul oreiller, distincte du lit double. Les lits de camp disposent d’un cadre tubulaire ouvert ; les bancs de transport ont deux ou quatre assises métalliques selon la source.

Quatre familles et seize vues ont été produites dans `environment_furniture.py`, avec des modèles Blender éditables et des finitions artistiques séparées. Une première comparaison a montré des sièges trop peu profonds : leur géométrie et leurs sprites ont été repris, sans abaisser le seuil de validation ni déformer les images. Le lit transversal du refuge wasteland reçoit une orientation explicite à 90°. La table d’examen segmentée n’est plus remplacée par un lit avec oreiller ; les variantes de lits de camp dont les proportions restent incompatibles conservent leur rendu source. La capture rapprochée de la clinique ruinée a également révélé des tubes de l’ancien cadre hors de l’empreinte tactique : les limites d’effacement et de placement ont été corrigées dans l’annotation visuelle uniquement.

Les PNG des cartes, leurs SHA-256, les relevés de murs et toutes les règles tactiques restent inchangés. Le suivi global distingue les remplacements de ressources existantes des nouveaux placements : la finition artistique des 122 cartes reste ouverte.

### 18 novembre 2026 — priorité aux agents, robots et véhicules

La présentation des unités est maintenant séparée de leurs données tactiques dans `unit_presentation.gd`. Le robot de soutien recevait une valeur d’échelle par défaut de 3,5, identique à celle d’un géant : son rendu non géant est limité à 1,65 fois la hauteur de référence. Les unités déclarées géantes et les véhicules conservent leur échelle visuelle précédente ; les agents ordinaires et power armors gardent leurs proportions. Aucun champ d’unité n’est réécrit.

Le shader comprime les hautes lumières avant l’écrêtage : deux panneaux d’armure presque blancs restent distincts au lieu de devenir un aplat blanc. Les corps restent opaques et les contours cyan/rouge restent visibles avant sélection. Les ombres de silhouettes suivent toujours le véritable sprite ou la frame d’animation. Leur projection distingue humanoïdes, châssis terrestres et aéronefs ; les châssis reçoivent un contact proportionné à leur largeur et les aéronefs ne portent plus de disque de contact de pieds.

Les captures « avant » de cette passe proviennent réellement du moteur publié `7ea8323`, avant toute modification des scripts, avec les mêmes fixtures et résolutions. Les comparaisons incluent les agents, ennemis, power armors, robots et VTOL ; une seconde série de missions militaires vérifie aussi le véhicule terrestre et l’exclusion des véhicules en intérieur. Les sources d’images, le HUD, le zoom et les données de combat sont conservés. Il ne s’agit pas d’une nouvelle bibliothèque complète d’animations ou de sprites : cette finition reste inscrite dans l’avancement global.

L’audit des ressources recense 251 références disposant d’une version haute résolution, dont 231 entités et 20 objets de mission. Pour 46 d’entre elles, l’alpha atteint au moins un bord de frame : cela signale une revue à effectuer, pas une preuve automatique de découpe du personnage. Aucun manifeste n’est présent dans `assets/combat_visual/animations` ; la capacité de lecture d’animations du moteur reste conservée, avec les sprites statiques en fallback. Le chantier des ressources animées n’est pas déclaré terminé.

## Passe suivante : animations directionnelles partielles

Les constats précédents sur l’absence d’atlas décrivent la passe historique. Quatre atlas réels sont maintenant intégrés : agent en manteau, ennemi standard, power armor et robot de combat ; 192 frames pour l’attente et la marche dans huit directions. Les autres actions, références et véhicules restent à compléter. Le prototype procédural rejeté n’est pas utilisé. Voir [couverture et preuves natives](combat_directional_animation.md).
