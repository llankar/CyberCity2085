# Combat — vue de haut 2.5D et échelle des unités

La vue de haut devient le rendu Godot par défaut. Les cartes sont dessinées dans leur orientation source, avec une mise à l’échelle uniforme : aucune rotation en losange, aucune seconde compression verticale. Le relief peint dans les décors, les unités debout, leurs ombres et les éclairages locaux assurent la présentation 2.5D. Les assemblages extrudés de la version 2.4 sont désactivés dans cette vue : l’appartement retrouve ses meubles et son plan d’origine.

## Échelle et caméra

`art/environment/map_presentation.json` contient un réglage explicite pour chacune des 122 cartes. La hauteur de la silhouette humaine est exprimée relativement à la largeur du décor source, indépendamment de sa résolution en pixels et de la grille de combat. Les petits intérieurs utilisent un ratio supérieur aux grands espaces ouverts. Armures et véhicules conservent leurs multiplicateurs propres.

Ces ratios sont des calibrages artistiques estimés par famille d’environnement, pas des mesures métriques certifiées de chaque objet du catalogue. Ils peuvent être ajustés individuellement ; une mission peut aussi fournir `map.presentation.human_height_ratio`. Les proportions du sprite restent intactes et la taille relative au décor ne change ni au zoom ni au redimensionnement.

La caméra démarre sur une vue d’ensemble qui permet de reconnaître le plan. Le zoom rapproché atteint trois fois cette valeur ; panoramique et recentrage Home restent disponibles. F11 permet une comparaison immédiate avec l’ancien rendu isométrique ; `--isometric` le sélectionne dès le lancement. F9, les niveaux de qualité et l’option de relief F10 restent disponibles ; le relief extrudé concerne le mode isométrique uniquement.

## Obstacles et murs reconstruits

Les 122 fichiers `.walls.json` ont été reconstruits depuis les `.wall-traces.json`, puis vérifiés avant toute écriture. Les 3 597 obstacles obtenus sont strictement identiques aux relevés persistés : les traces sont déjà exprimées en `texture_top_left`, donc elles ne doivent subir ni rotation ni déplacement pour cette vue. Les fichiers régénérés sont volontairement identiques, y compris leur formatage. Les 122 PNG et leurs SHA-256 restent inchangés.

La projection des contours et des cases bloquées est maintenant rectangulaire, directement sur l’image source. Le même inverse sert aux clics, au survol et aux trajets ; le changement de vue ne modifie aucune cellule, collision, ligne de vue, portée, IA ou coût en PA.

Outil reproductible :

```sh
python tools/maps/rebuild_top_down_walls.py --write --report docs/images/combat-top-down/wall-alignment.json
```

Le [rapport de reconstruction](images/combat-top-down/wall-alignment.json) donne le nombre d’obstacles, de sommets et l’empreinte source de chaque carte. Le mode debug F8 affiche leurs contours dans le vrai renderer.

## Validation

20 tests réussis : projection et coordonnées de tous les centres de cellules sur les 122 cartes, trois résolutions, alignement des sommets des murs, échelle des silhouettes, collisions/LOS/chemins identiques, fallback et contrôles visuels existants.

Captures natives Godot sur cinq environnements (appartement, industriel, urbain, laboratoire et wasteland), en 1280×720, 1920×1080 et 2560×1440. Vérification du déplacement par le chemin réel d’entrée souris (pixels écran → coordonnées monde → cellule), dépense d’un PA, animation d’arrivée, sélection ennemie, tour IA, F10 et basculement F11 sans altération de l’état tactique. Les images ont été inspectées pour la reconnaissance du plan et la différence d’échelle intérieur/extérieur.

Commande principale :

```sh
DISPLAY=:103 python -m pytest tests/test_top_down_combat.py tests/test_natural_environment_geometry.py tests/test_combat_visual_2.py tests/test_tactical_reference_runtime.py tests/test_combat_visual_21.py tests/test_unit_readability_runtime.py tests/test_map_8k.py -q
```

[Captures réelles](images/combat-top-down/README.md). L’ancien cadrage reste consultable dans les [comparatifs 2.4](images/combat-24/README.md).

## Échap pendant un combat

Échap ne quitte plus Godot et ne termine jamais la mission. La touche ferme les paramètres et le journal lorsqu’ils sont affichés ; sans panneau ouvert, elle laisse le combat inchangé. Le comportement est partagé par les HUD moderne et classique. Le test `tests/test_combat_escape.py` envoie de véritables événements clavier répétés aux deux interfaces et vérifie que le combat, le tour et les données tactiques restent intacts.
