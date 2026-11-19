# Animations des unités — preuves réelles

**Livraison partielle : quatre références, attente et marche, huit directions.** Aucun ensemble complet d’actions de combat n’est déclaré terminé.

## Dans Godot

- [Boucle des huit directions](native-eight-directions.gif) : recadrage de 32 captures du véritable écran de combat. La fixture contrôle les phases et orientations ; les quatre poses de marche sont montrées dans chaque direction. Ce n’est pas un déplacement autonome.
- [Déplacement réel par clic](native-click-movement.gif) : sélection parmi 40 images successives du jeu, avec les intervalles réellement mesurés conservés. Le personnage atteint la destination, dépense 4 PA et revient à l’attente. La vitesse du GIF n’est pas accélérée pour simuler une marche.
- [Rapport d’interaction](animation-report.json) : temps, positions, clips, frames, PA et absence d’écriture de campagne.

### Comparaison à caméra identique

[Avant : ressources statiques d’origine](before-static-1920x1080.webp) · [Après : première phase de marche vers l’est](directions-00-00.webp).

L’avant est capturé dans la même fixture en activant le véritable fallback statique des quatre unités. Seules leurs ressources d’animation changent ; carte, caméra, profils de taille, données et rendu général restent identiques. Cette comparaison ne présente pas un ancien moteur reconstitué.

### Résolutions

[1280×720](scene-1280x720.webp) · [1920×1080](scene-1920x1080.webp) · [2560×1440](scene-2560x1440.webp).

Les WebP sont sans perte ; leurs [empreintes RGB](capture-rgb-sha256.json) sont celles des captures PNG originales.

## Aperçus des ressources

Ces quatre boucles montrent les véritables frames des atlas sur fond neutre ; ce ne sont pas des captures du jeu.

| Référence | Marche dans les huit orientations |
|---|---|
| Agent en manteau | [Animation](agent_diverse_04_trench_sniper.gif) |
| Ennemi standard | [Animation](enemy_grunt.gif) |
| Power armor | [Animation](enemy_corp_37_power_armor_grunt.gif) |
| Robot de combat | [Animation](robot_combat.gif) |

Les séquences comportent quatre phases de marche par direction et deux poses d’attente. Les sept autres clips restent à produire. Le canon du robot reste en pose de transport ; aucune animation de visée n’est livrée.

## Environnements et catalogue

Les cinq familles sont capturées avec les ressources dynamiques réellement choisies par la fixture standard ; elles ne prétendent pas montrer les quatre nouveaux atlas sur chaque carte.

| Environnement | 720p | 1080p | 1440p |
|---|---|---|---|
| Appartement | [Voir](family-cybercity_inner_02_safehouse-1280x720.webp) | [Voir](family-cybercity_inner_02_safehouse-1920x1080.webp) | [Voir](family-cybercity_inner_02_safehouse-2560x1440.webp) |
| Usine | [Voir](family-city_industrial_factory_floor-1280x720.webp) | [Voir](family-city_industrial_factory_floor-1920x1080.webp) | [Voir](family-city_industrial_factory_floor-2560x1440.webp) |
| Rue | [Voir](family-city_exterior_neon_market_alley-1280x720.webp) | [Voir](family-city_exterior_neon_market_alley-1920x1080.webp) | [Voir](family-city_exterior_neon_market_alley-2560x1440.webp) |
| Laboratoire | [Voir](family-city_interior_blacksite_lab-1280x720.webp) | [Voir](family-city_interior_blacksite_lab-1920x1080.webp) | [Voir](family-city_interior_blacksite_lab-2560x1440.webp) |
| Wasteland | [Voir](family-wasteland_outdoor_01_dust_road_ambush-1280x720.webp) | [Voir](family-wasteland_outdoor_01_dust_road_ambush-1920x1080.webp) | [Voir](family-wasteland_outdoor_01_dust_road_ambush-2560x1440.webp) |

[Rapport des familles](family-native-report.json) · [Contrôles natifs des 122 cartes](native-report.json).

Planches du catalogue : [1](catalogue-01.jpg), [2](catalogue-02.jpg), [3](catalogue-03.jpg), [4](catalogue-04.jpg), [5](catalogue-05.jpg), [6](catalogue-06.jpg), [7](catalogue-07.jpg), [8](catalogue-08.jpg), [9](catalogue-09.jpg), [10](catalogue-10.jpg), [11](catalogue-11.jpg).

## Limites et suite

34 tests ciblés réussis, dont 128 sélections natives de frames. Le catalogue conserve ses 221 placements de décor ; les PNG sources, leurs relevés et leurs empreintes restent inchangés. Les succès de chargement et de picking ne constituent pas une validation artistique complète des 122 cartes.

**4 / 231 références éligibles partiellement animées ; zéro unité entièrement animée pour les neuf actions.** Les autres agents, ennemis, robots, armures et véhicules conservent leurs ressources précédentes. Les effets de combat existants restent fonctionnels lorsque les clips manquent. Le rig procédural rejeté n’est pas utilisé.

Matériel de validation : Godot 4.6.3, OpenGL llvmpipe. Pas de mesure de performances sur GPU joueur.

[Couverture technique](../../combat_directional_animation.md) · [Avancement global](../../combat_visual_25_progress.md).
