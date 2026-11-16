# Combat Visual 2.0 — suivi réel

Mise à jour : 16 novembre 2026. Branche locale : `combat/visual-2`.
Base : `bb97e30671d683c12932a3ebe7ec18446c01c19f` (`llankar/CyberCity2085`).
Référence : maquette jointe par Laurent dans la conversation.

**Objectif global NON ATTEINT.** Le nouveau rendu est intégré et jouable ; il
ne possède pas encore la qualité artistique, les poses ni les animations de la
référence. Branche poussée sur `origin/combat/visual-2` à la demande de Laurent
le 16 novembre 2026, puis fusionnée dans `main` à sa demande explicite.
Aucun déploiement effectué. Les limitations artistiques restent ouvertes.

## Les cinq chantiers et leur état

1. **HUD — intégré, direction artistique encore partielle.** Nouveau composant
   `visual_hud.gd`, panneaux découpés cyan/ambre, portraits existants agrandis,
   PV/PA/stress, objectifs et progression, phase/tour, commandes basses avec
   icônes SVG, ciblage contextuel avec portrait et chance réelle du moteur,
   journal escamotable, paramètres de qualité. Disposition vérifiée à 960×540,
   1280×720 et 1920×1080. Les actions viennent toujours de l'unité active.
   F9 change uniquement l'interface, sans perdre le combat. Le lancement avec
   `--legacy-visuals` conserve aussi les anciens figurines, terrain et CRT.
2. **Unités — rendu statique intégré, animations bloquées par les ressources.**
   `unit_visual.gd` réutilise les silhouettes transparentes haute résolution sans
   étirement ni socle de figurine, avec ancrage au sol, ombre, sélection et tri
   en profondeur. Clic par alpha pour éviter de sélectionner le vide autour
   des silhouettes ; véhicules décoratifs non interactifs. Déplacements
   visuels suivent les points du chemin accepté. Tous les types partagent ce
   composant ; les véhicules combattants utilisent désormais leur art de
   véhicule et les armures leur silhouette adaptée. Aucune animation de corps
   créée à partir de copies/déformations d'une image.
3. **Cartes — compatibilité et relief intégrés, refonte artistique incomplète.**
   `visual_battlefield.gd` hérite du plateau existant, garde ses API tactiques,
   aligne les prévisualisations sur les vraies cases, dessine la grille en 70
   lignes environ, masque les relevés de débogage par défaut (F8 les montre).
   `visual_obstacle.gd` extrude les contours UV relevés, réutilise leur texture,
   trie les obstacles avec les unités et atténue ceux qui masquent l'agent
   actif. Ambiances pluie urbaine/poussière extérieure/particules intérieures.
   Les textures, les relevés et leurs SHA-256 sont inchangés.
4. **Effets — intégrés, rendu procédural simple.** Traceurs et flash de tir,
   arcs de mêlée, impacts, anneaux PSI et soins, explosions, particules et fumée.
   Effets déclenchés après validation d'une action ; maximum 64 effets actifs,
   expiration temporelle et arrêt du traitement quand la liste est vide.
   Trois niveaux persistants ; le niveau bas désactive relief et météo en
   conservant les règles de collision. Les reflets/néons des cartes restent
   ceux des images sources ; pas de nouveau système d'éclairage physique.
5. **Production et validation — outils livrés, export artistique non validé.**
   `tools/audit_combat_visuals.py` inventorie les ressources, vérifie les
   SHA-256 et rejette les animations à poses/directions identiques.
   `tools/render_combat_atlas.py` est une chaîne Blender pour modèles riggés
   AUTHENTIQUES, huit directions et neuf clips. Son refus de clips manquants
   a été vérifié. Aucun export complet de personnage n'a été possible : aucun
   modèle/rig/clip n'est fourni. La lecture de vrais atlas et leur qualité
   artistique restent donc à valider avec de véritables ressources.

## Vérifications exécutées

Environnement : Godot 4.6.3, Blender 4.3.2, Python dans `work/venv`, OpenGL
Compatibility Mesa/llvmpipe sous Xorg dummy. Pas de mesure de performances sur
une carte graphique de joueur ; ne pas interpréter ces résultats comme un
objectif de 60 FPS garanti.

- Suite Python complète : **886 tests réussis, 8 sous-tests réussis**.
- Après les derniers ajustements du rendu : **27 tests ciblés réussis**
  (`test_combat_visual_2.py` et les quatre suites Godot existantes).
- `tests/visual_regression.gd` : **537 vérifications, 122 cartes, zéro échec**,
  en mode headless ET avec rendu OpenGL réel. Clic de déplacement réel,
  raccourci F9 réel, conservation d'état, tir, mêlée, PSI, soins, missiles,
  défense/vigilance, phase ennemie, retour joueur, ciblage, nettoyage des
  effets, victoire, contrôle d'extraction et fichier résultat JSON vérifiés.
- `tests/render_all_maps.gd` : **122 cartes effectivement dessinées sous
  OpenGL**, sans erreur de script ni de triangulation ; 21,6 secondes pour le
  parcours comprenant le chargement des ressources et une image par carte.
  Ce temps ne constitue pas un benchmark de fluidité en combat.
- `tests/render_unit_catalog.gd` : **251 textures effectivement dessinées**
  (personnages, robots, véhicules et objectifs du catalogue), sans erreur.
- Audit : **122/122 empreintes de cartes valides ; 0/251 bibliothèques
  d'animations complètes**. Le nombre 251 désigne des images de ressources,
  pas 251 personnages animés.
- Captures réelles examinées : ville néon, laboratoire intérieur, wasteland,
  catalogue de silhouettes et HUD aux trois résolutions. Une collision des
  panneaux supérieurs à 960 px a été constatée puis corrigée.
- Ancien mode lancé avec `--legacy-visuals` : démarrage sans erreur de script.
- `git diff --check` et compilation Python des deux outils : réussis.

Des sorties courtes peuvent encore afficher un avertissement de nettoyage
AudioStream lors de l'arrêt pendant une musique. Le passage OpenGL complet
après libération de la scène ne présente pas d'erreur de script. Les tests
fonctionnels ne garantissent pas une campagne complète jouée manuellement.

## Blocages et travail restant — à ne pas déclarer livré

- **Art de personnages :** aucun `.blend`, `.glb`, `.gltf`, `.fbx`, `.obj`, rig
  ni bibliothèque de clips présents. Les PNG existants sont des images uniques.
  Il faut produire/acquérir des modèles riggés ou des planches dessinées pour
  toutes les familles et actions, avec proportions, pivots et huit orientations
  cohérents. Le rendu statique actuel ne satisfait pas ce critère.
- **Décors :** les cartes actuelles sont des images vues du dessus. Leur
  projection et l'extrusion de leurs relevés ne remplacent pas une vraie
  production de décors isométriques avec façades, accessoires, matériaux et
  éclairage conformes à la maquette. Les faces latérales actuelles restent
  simples ; certaines occultations et raccords réclament une revue artistique.
- **Animations :** valider l'export Blender complet, les pivots, le cadrage,
  l'orientation caméra/rig, les transitions marche→attaque, la couverture,
  les impacts et morts, les capacités propres aux classes et la mémoire des
  atlas. Le contrat et le chargeur sont préparés ; aucun clip authentique
  n'est annoncé comme livré. Une animation absente laisse l'art statique ;
  sans clip de mort, l'unité morte disparaît.
- **Qualité finale :** harmoniser portraits/silhouettes, remplacer les images
  de faible qualité, améliorer le cadrage près des bords des cartes (zones
  sombres hors du plateau), fabriquer les effets spécifiques aux capacités,
  revoir toutes les cartes artistiquement, tester la campagne Arcade→Godot→
  Arcade en interaction prolongée et profiler sur les configurations cibles.

## Reprise et commandes

Depuis la racine du dépôt, installer les dépendances du projet et pytest/Pillow
(déjà dans `work/venv` sur cette machine), puis :

```sh
python -m pytest -q
python tools/audit_combat_visuals.py --output work/visual-audit.json
# Porte de livraison artistique : échoue volontairement tant que l'art manque.
python tools/audit_combat_visuals.py --require-complete

godot --headless --path godot/combat_missions_ui --editor --import --quit
godot --path godot/combat_missions_ui -- --handoff /chemin/mission_handoff.json
# Interface et rendu historiques complets : ajouter --legacy-visuals.

godot --headless --audio-driver Dummy --path godot/combat_missions_ui \
  --script res://tests/visual_regression.gd -- \
  --handoff /chemin/mission_handoff.json --result-root /chemin/temporaire
```

Les scripts de capture nécessitent un vrai pilote de rendu (pas `--headless`).
`render_all_maps.gd` reçoit `--handoff`, `render_unit_catalog.gd` reçoit
`--asset-root /racine/du/depot`. Les captures de travail vont dans `work/`.

Pour chaque modèle riggé, après création des vrais clips :

```sh
blender -b personnage.blend --python-exit-code 1 \
  --python tools/render_combat_atlas.py -- \
  --key agent_diverse_01_neon_blade --root /racine/du/depot
python tools/audit_combat_visuals.py --require-complete
```

Les noms d'atlas utilisent le nom du PNG source **sans `_512`**. Le manifeste
est dans `assets/combat_visual/animations/<nom>.json`, la texture est référencée
relativement à la racine. Chaque clip contient huit listes de frames, une
fréquence et un indicateur de boucle. Les neuf clips communs requis sont
`idle`, `move`, `fire`, `melee`, `cover`, `hit`, `death`, `psi`, `heal` ; adapter
la porte artistique aux capacités propres à chaque famille avant production.
L'audit des pixels détecte les copies identiques mais ne remplace pas une
validation humaine des poses et des animations.
