# Combat Visual 2.4 — Natural Geometry & Materials

Le rendu par défaut abandonne l’extrusion des polygones de collision. Un obstacle possède désormais soit un assemblage visuel explicitement décrit et vérifié sur son illustration source, soit le rendu 2D original, sans plateforme ajoutée. Les identifiants des relevés servent seulement à joindre les annotations : ils ne permettent pas de deviner la nature d’un objet.

## Géométrie et couverture

`art/environment/natural_geometry.json` décrit 28 objets sur quatre cartes : safehouse (8), usine (7), laboratoire (10), ruelle urbaine (3). Chaque entrée est liée aux dimensions et au SHA-256 du PNG original. Une source absente, modifiée ou non annotée déclenche le fallback 2D. Cette politique s’applique aux 122 cartes du catalogue ; elle ne constitue pas une reconstruction 3D complète de ces 122 cartes. Le wasteland conserve volontairement ses objets peints, faute de silhouettes suffisamment identifiées.

Les neuf familles réutilisables sont canapé, fauteuil, table, banc, console, caisse, machine, mur et cloison. Les sièges séparent pieds, châssis, coussins, dossier et accoudoirs. Les tables séparent plateau et quatre pieds. Les machines emploient des corps chanfreinés ; les murs et cloisons utilisent des empreintes étroites revues dans l’image. Les hauteurs et axes locaux appartiennent aux annotations visuelles, jamais aux cellules bloquées.

Le sol et les tapis ne deviennent pas des meshes. Des complétions locales du fond, découpées selon les silhouettes annotées, évitent de conserver simultanément l’ancien objet peint et son nouveau volume. Ces textures sont calculées en mémoire : aucun PNG source n’est réécrit.

## Matériaux et intégration

Les coussins et dossiers réutilisent des panneaux de revêtement de l’objet source ; leurs épaules sont légèrement arrondies par une géométrie mise en cache. Les côtés utilisent des matériaux fins et des teintes échantillonnées, sans étirer une photographie complète sur une face verticale. La réponse métallique locale provient des pixels émissifs de l’objet annoté.

Les ombres suivent les silhouettes visuelles et les contacts réels au sol. L’occultation utilise les faces de l’assemblage ; les objets bas s’atténuent lorsqu’ils cachent une unité. Les obstacles inconnus ne dessinent plus une seconde copie de la texture par-dessus les personnages. Le tri repose sur l’ancrage visuel, tandis que la projection des relevés tactiques reste identique.

Les faces latérales restent des matériaux simplifiés : il ne s’agit pas de modèles photoréalistes ni de ressources originales entièrement remodélisées. Les objets sans annotation restent volontairement dans leur rendu d’origine.

## Conservation et fallback

Aucune modification des PNG, relevés de murs, empreintes source, cellules bloquées, règles, IA, PA, portée, ligne de vue, HUD, taille des unités ou perspective. F10 conserve le basculement vers le fond original. La qualité basse évite les volumes. `--legacy-environment` permet de retrouver explicitement le renderer 2.3, conservé dans `environment_depth_legacy.gd`.

Composants : `environment_catalog.gd` (validation), `natural_prop_shapes.gd` (assemblages), `natural_materials.gd` (réponse des matériaux), `environment_depth.gd` (composition) et `visual_obstacle.gd` (dessin/occultation).

## Validation réelle

- 18 tests Python/Godot réussis, incluant les 122 relevés, les 28 assemblages liés aux sources, le fallback, les projections, le ciblage et la lisibilité des unités.
- Captures natives Godot 4.6.3/OpenGL : intérieur safehouse, industriel, urbain, laboratoire et wasteland, en 1280×720, 1920×1080 et 2560×1440, avant/après, plus ciblage et effets.
- Contrôle réel de déplacement, dépense d’un PA, arrivée de l’unité animée, sélection ennemie et résolution du tour IA ; caméra et données tactiques conservées lors des changements de qualité et F10.
- Ancien renderer lancé séparément avec la même séquence de validation.
- Captures inspectées pour les assises, pieds de table, consoles, machines, cloisons, contours d’unités et raccords au sol. Les performances ont été vérifiées sur le renderer logiciel disponible ; ce contrôle ne remplace pas un benchmark GPU sur la machine du joueur.

Commande de tests :

```sh
DISPLAY=:103 python -m pytest tests/test_natural_environment_geometry.py tests/test_combat_visual_2.py tests/test_tactical_reference_runtime.py tests/test_combat_visual_21.py tests/test_unit_readability_runtime.py tests/test_map_8k.py -q
```

Les [captures réelles et leur index](images/combat-24/README.md) sont enregistrées en WebP sans perte, avec comparaison pixel par pixel contre les PNG de capture. Le manifeste contient les dimensions et empreintes des pixels RGB.

### Mobilier : ancien renderer puis assemblage naturel

![Renderer 2.3](images/combat-24/furniture-legacy.webp)

![Assemblage 2.4](images/combat-24/furniture-natural.webp)
