# Échelles — premiers diagnostics, pas une calibration approuvée

**CHANTIER GLOBAL INCOMPLET — 0 / 122 cartes validées pour l’échelle.**

L’inventaire couvre 122 cartes et 92 illustrations. Les profils existants utilisent cinq ratios génériques : urbain 0,030 ; intérieur 0,043 ; petit intérieur 0,055 ; industriel 0,034 ; wasteland 0,026. Ce sont des estimations.

## Deux repères examinés dans les PNG source

Les [annotations de diagnostic](../../reports/entity_scale_anchor_samples.json) décrivent les extrémités approximatives de voitures réellement visibles, avec coordonnées source, SHA-256 et incertitude. Aucun type d’objet n’est déduit des seules collisions.

- `city_exterior_downtown_intersection` : axe visible de la voiture ≈ 309 px ; hauteur humaine actuelle équivalente 230 px, soit environ 0,75 de cet axe.
- `cybercity_street_01_downtown_intersection` : axe visible ≈ 261 px ; même hauteur humaine équivalente, soit environ 0,88 de cet axe.

La bande 0,32–0,45 utilisée pour préparer un essai est une **hypothèse de convention visuelle**, pas une mesure des mètres du monde. Une seule voiture par illustration ne suffit pas pour approuver la calibration ; ajouter des portes, meubles ou autres véhicules et vérifier la projection, les catégories et la lisibilité.

## Essais natifs, sans changer les profils de production

Le ratio 0,015 est injecté uniquement dans les handoffs de capture via l’override de présentation déjà existant. Les PNG, relevés, profils de production et mécaniques restent inchangés. Le cadrage des vues principales est fixé par la fixture à la même caméra pour les deux cas.

| Illustration | Actuel 1080p | Candidat 1080p |
|---|---|---|
| Intersection urbaine | [Voir](city-current-city_exterior_downtown_intersection-1920x1080.webp) | [Voir](city-candidate-city_exterior_downtown_intersection-1920x1080.webp) |
| Grande intersection | [Voir](street-current-cybercity_street_01_downtown_intersection-1920x1080.webp) | [Voir](street-candidate-cybercity_street_01_downtown_intersection-1920x1080.webp) |

Les captures en 720p et 1440p sont également présentes dans ce dossier. Les vues `vehicle` sont des gros plans à cadrage automatique ; ne pas les présenter comme des comparaisons à caméra identique. Les WebP sont sans perte et leurs empreintes RGB sont enregistrées dans [le rapport natif](native-diagnostics.json).

Les quatre cas ont passé les contrôles techniques de la fixture (rendu, projection, picking et ressources). Ils portent explicitement `scale_calibration_status: NOT VERIFIED`. Aucun succès de chargement n’approuve la taille d’un PJ, PNJ, robot, armure ou véhicule.

## Reproduire les captures

Depuis la racine, utiliser la fixture existante, avec `DISPLAY` configuré :

```sh
DISPLAY=:107 godot --audio-driver Dummy --path godot/combat_missions_ui --script tests/capture_combat_21.gd -- --all-maps --map city_exterior_downtown_intersection --art-review --entities --scale-comparison --output work/entity-scale/city-current
DISPLAY=:107 godot --audio-driver Dummy --path godot/combat_missions_ui --script tests/capture_combat_21.gd -- --all-maps --map city_exterior_downtown_intersection --art-review --entities --scale-comparison --human-ratio .015 --output work/entity-scale/city-candidate
```

Répéter avec `--map cybercity_street_01_downtown_intersection` dans des dossiers distincts. Les chemins absolus d’output sont conseillés pour la reproductibilité indépendante du répertoire de travail Godot.

## Suite

Poursuivre `SCALE-02` : mesurer plusieurs repères par illustration, traiter l’appartement et les autres familles, puis établir des profils candidats par carte et catégorie. Vérifier l’ancrage, la lecture au zoom utile et toutes les catégories avant application. Ne pas propager automatiquement un facteur 0,5 à l’ensemble des cartes.

[Inventaire complet](../../reports/entity_scale_baseline.md) · [Registre](../../CODEX_PROGRESS.md) · [Critères](../../COMBAT_VISUAL_ACCEPTANCE.md).
