# Animations directionnelles — livraison partielle

Cette passe introduit des poses réellement dessinées dans huit directions. Elle ne termine pas l’ensemble des animations de Combat Visual 2.5.

## Couverture livrée

| Ressource réelle | Attente | Marche | Autres actions |
|---|---|---|---|
| `agent_diverse_01_neon_blade` | 2 poses × 8 directions | 4 poses × 8 directions | À produire |
| `agent_diverse_03_magenta_pistol` | 2 poses × 8 directions | 4 poses × 8 directions | À produire |
| `agent_diverse_04_trench_sniper` | 2 poses × 8 directions | 4 poses × 8 directions | À produire |
| `enemy_grunt` | 2 poses × 8 directions | 4 poses × 8 directions | À produire |
| `enemy_corp_37_power_armor_grunt` | 2 poses × 8 directions | 4 poses × 8 directions | À produire |
| `robot_combat` | 2 poses × 8 directions | 4 poses × 8 directions | À produire |

Total : **288 frames**, six références partiellement animées parmi **231 références d’entités éligibles**. Les 20 pictogrammes d’objectifs de mission sont exclus de ce dernier nombre. Aucun personnage différent n’est remplacé par une copie de ces six unités.

Les tirs, mêlées, couvertures, impacts, morts, pouvoirs PSI et soins ne disposent pas encore de leurs clips. Le canon d’épaule du robot reste dans une pose de transport ; cette passe ne livre pas son animation de visée. Les véhicules conservent leurs ressources et ombres existantes. **Zéro unité possède encore les neuf actions complètes.**

## Production et intégration

Les planches dessinées sont conservées dans `assets/combat_visual/source_sheets/`, séparément des PNG historiques de `assets/units/`. Les manifestes enregistrent les empreintes des sources, le découpage, les clips disponibles et les actions manquantes. Le prototype Blender rejeté n’est pas utilisé.

`tools/art/import_directional_clips.py` nettoie les fonds résiduels, extrait les poses, applique une échelle commune par orientation et enregistre les atlas RGBA. Il ne fabrique pas une marche par translation, rotation ou miroir d’une image statique. L’audit rejette également des poses identiques simplement décalées ou redimensionnées.

La lecture utilise le véritable `unit_visual.gd` : ancrage aux pieds, ombre suivant la frame, hauteur de référence stable et phase de marche conservée entre deux cases. L’angle tient compte de la projection active. Les proportions générales des unités et les règles tactiques restent inchangées.

`unit_animation_contract.gd` contrôle les dimensions, les huit orientations, les indices des frames et l’identité de la source. Une ressource absente ou invalide conserve le rendu statique existant. Les actions manquantes gardent les effets de combat précédents ; elles ne sont pas comptabilisées comme animées.

## Validation

- 55 tests ciblés du rendu réussis, dont 192 sélections de frames dans Godot, continuité de marche, ancrage, fallback, lisibilité et régressions tactiques.
- Captures natives en 1280×720, 1920×1080 et 2560×1440.
- Déplacement déclenché par le véritable événement de clic : destination atteinte, coût réel de 4 PA par agente et retour à l’attente. La campagne n’est pas enregistrée par la fixture.
- La démonstration des orientations utilise des phases contrôlées dans la scène réelle ; elle est distincte du déplacement automatique enregistré.
- Les vérifications sont exécutées avec OpenGL llvmpipe ; elles ne remplacent pas un benchmark sur GPU joueur.

[Captures du lot 2, boucles animées et limites](images/roster-batch2/README.md) · [Avancement de la tâche complète](combat_visual_25_progress.md)

## Reproduction

```sh
DISPLAY=:107 godot --audio-driver Dummy --path godot/combat_missions_ui --script tests/directional_animation_regression.gd
DISPLAY=:107 godot --audio-driver Dummy --path godot/combat_missions_ui --script tests/capture_directional_animation.gd
DISPLAY=:107 godot --audio-driver Dummy --path godot/combat_missions_ui --script tests/capture_directional_animation.gd -- --static-only
python tools/art/build_directional_evidence.py
python tools/audit_combat_visuals.py --output work/directional-animation/audit.json
```

L’option `--require-complete` de l’audit doit encore échouer : la livraison complète de toutes les entités et actions reste ouverte.

## Échelles relatives aux décors

La demande `SCALE-CATALOGUE` impose une revue dédiée sur les 122 cartes, pour les PJ, PNJ, robots, armures et véhicules. Les ratios actuels sont estimés et ne valident pas les proportions par rapport aux voitures du décor, portes, mobilier et rues. Zéro carte n’est encore vérifiée pour ce critère ; aucune taille n’a été modifiée par ce lot d’animations.
