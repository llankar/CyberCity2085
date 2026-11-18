# Captures réelles Combat Visual 2.5

Les 11 planches sont des réductions des 122 captures natives en 1280×720. Les vues détaillées conservent exactement les pixels des captures PNG grâce à WebP sans perte. Les empreintes RGB originales et résultats natifs sont dans le manifeste.

| Environnement | Avant 1080p | Après 720p | Après 1080p | Après 1440p |
|---|---|---|---|---|
| city_industrial_power_substation | [Voir](before-city_industrial_power_substation-1920x1080.webp) | [Voir](after-city_industrial_power_substation-1280x720.webp) | [Voir](after-city_industrial_power_substation-1920x1080.webp) | [Voir](after-city_industrial_power_substation-2560x1440.webp) |
| city_industrial_data_vault | [Voir](before-city_industrial_data_vault-1920x1080.webp) | [Voir](after-city_industrial_data_vault-1280x720.webp) | [Voir](after-city_industrial_data_vault-1920x1080.webp) | [Voir](after-city_industrial_data_vault-2560x1440.webp) |
| city_transit_metro_interchange | [Voir](before-city_transit_metro_interchange-1920x1080.webp) | [Voir](after-city_transit_metro_interchange-1280x720.webp) | [Voir](after-city_transit_metro_interchange-1920x1080.webp) | [Voir](after-city_transit_metro_interchange-2560x1440.webp) |
| city_district_holo_square | [Voir](before-city_district_holo_square-1920x1080.webp) | [Voir](after-city_district_holo_square-1280x720.webp) | [Voir](after-city_district_holo_square-1920x1080.webp) | [Voir](after-city_district_holo_square-2560x1440.webp) |
| wasteland_city_11_ruined_transit_plaza | [Voir](before-wasteland_city_11_ruined_transit_plaza-1920x1080.webp) | [Voir](after-wasteland_city_11_ruined_transit_plaza-1280x720.webp) | [Voir](after-wasteland_city_11_ruined_transit_plaza-1920x1080.webp) | [Voir](after-wasteland_city_11_ruined_transit_plaza-2560x1440.webp) |

## Catalogue complet

- [Planche 1](catalogue-01.jpg)
- [Planche 2](catalogue-02.jpg)
- [Planche 3](catalogue-03.jpg)
- [Planche 4](catalogue-04.jpg)
- [Planche 5](catalogue-05.jpg)
- [Planche 6](catalogue-06.jpg)
- [Planche 7](catalogue-07.jpg)
- [Planche 8](catalogue-08.jpg)
- [Planche 9](catalogue-09.jpg)
- [Planche 10](catalogue-10.jpg)
- [Planche 11](catalogue-11.jpg)

[Inventaire détaillé](../../combat_visual_25_inventory.md) · [Données et empreintes des captures](inventory.json) · [Mesures natives](native-report.json)

Le matériel de validation utilise OpenGL llvmpipe. Les mesures incluent les fixtures et captures et ne constituent pas un benchmark GPU joueur.


## Entités et soutiens

Les agents, ennemis, power armors, robots et véhicules sont conservés et contrôlés. Les vues ci-dessous sont les captures natives en 1080p ; les contrôles couvrent aussi 720p et 1440p.
- [Unités — city_exterior_neon_market_alley](entities-city_exterior_neon_market_alley-1920x1080.webp)
- [Unités — city_industrial_factory_floor](entities-city_industrial_factory_floor-1920x1080.webp)
- [Unités — city_interior_blacksite_lab](entities-city_interior_blacksite_lab-1920x1080.webp)
- [Unités — cybercity_inner_02_safehouse](entities-cybercity_inner_02_safehouse-1920x1080.webp)
- [Unités — wasteland_outdoor_01_dust_road_ambush](entities-wasteland_outdoor_01_dust_road_ambush-1920x1080.webp)

[Véhicule extérieur](vehicle-review.webp). Aucun véhicule n’est ajouté aux cartes intérieures.

## Assemblages complémentaires

- [Vue de contrôle — nw_transformer](detail-nw_transformer.webp)
- [Vue de contrôle — se_transformer](detail-se_transformer.webp)

## Méthode et limites

Les vues « avant » rejouent en mémoire le catalogue versionné dans `7244e46`, avec les mêmes sources, unités, caméra et résolution. Les fichiers source et les sauvegardes ne sont jamais réécrits. Les vues « après » utilisent les nouveaux assemblages et leurs masques visuels distincts des collisions.

Les modes graphiques sont imposés aux fixtures pour éviter qu’un autre test modifiant les préférences n’influence une capture. Les reprises ciblées du fret et du wasteland sont incluses dans les rapports finaux ; le nombre de sprites effectivement rendus est comparé au catalogue attendu.

Les variantes à quatre et six isolateurs sont séparées. Les pointes qui débordent des empreintes tactiques sont effacées par des petits polygones tracés sur l’illustration, sans changer la géométrie tactique. La paire de bancs est disponible comme ressource mais reste désactivée lorsque son cadre ne convient pas.

La tâche artistique complète reste **en cours** : les essais natifs ne valent pas une validation artistique exhaustive de chaque carte. Voir le [suivi complet](../../combat_visual_25_progress.md).

## Revue des sources

[Comparaison rapprochée des assemblages d’origine](reviews/assembly-sources.jpg).
- [Découpes de la passe, planche 1](reviews/assemblies-review-00.jpg)
- [Découpes de la passe, planche 2](reviews/assemblies-review-01.jpg)
- [Découpes de la passe, planche 3](reviews/assemblies-review-02.jpg)
- [Découpes de la passe, planche 4](reviews/assemblies-review-03.jpg)
- [Découpes de la passe, planche 5](reviews/assemblies-review-04.jpg)
- [Découpes de la passe, planche 6](reviews/assemblies-review-05.jpg)
- [Découpes de la passe, planche 7](reviews/assemblies-review-06.jpg)

[Tests et contrôles](checks.txt) · [Rapport des entités](entity-native-report.json) · [Rapport de détail](detail-native-report.json)
