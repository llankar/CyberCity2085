# Captures réelles Combat Visual 2.5

Les 11 planches sont des réductions des 122 captures natives en 1280×720. Les vues détaillées conservent exactement les pixels des captures PNG grâce à WebP sans perte. Les empreintes RGB originales et résultats natifs sont dans le manifeste.

| Environnement | Avant 1080p | Après 720p | Après 1080p | Après 1440p |
|---|---|---|---|---|
| city_interior_safehouse | [Voir](before-city_interior_safehouse-1920x1080.webp) | [Voir](after-city_interior_safehouse-1280x720.webp) | [Voir](after-city_interior_safehouse-1920x1080.webp) | [Voir](after-city_interior_safehouse-2560x1440.webp) |
| cybercity_inner_14_detention_block | [Voir](before-cybercity_inner_14_detention_block-1920x1080.webp) | [Voir](after-cybercity_inner_14_detention_block-1280x720.webp) | [Voir](after-cybercity_inner_14_detention_block-1920x1080.webp) | [Voir](after-cybercity_inner_14_detention_block-2560x1440.webp) |
| wasteland_inner_03_ruined_clinic | [Voir](before-wasteland_inner_03_ruined_clinic-1920x1080.webp) | [Voir](after-wasteland_inner_03_ruined_clinic-1280x720.webp) | [Voir](after-wasteland_inner_03_ruined_clinic-1920x1080.webp) | [Voir](after-wasteland_inner_03_ruined_clinic-2560x1440.webp) |
| city_transit_metro_interchange | [Voir](before-city_transit_metro_interchange-1920x1080.webp) | [Voir](after-city_transit_metro_interchange-1280x720.webp) | [Voir](after-city_transit_metro_interchange-1920x1080.webp) | [Voir](after-city_transit_metro_interchange-2560x1440.webp) |
| city_district_holo_square | [Voir](before-city_district_holo_square-1920x1080.webp) | [Voir](after-city_district_holo_square-1280x720.webp) | [Voir](after-city_district_holo_square-1920x1080.webp) | [Voir](after-city_district_holo_square-2560x1440.webp) |
| wasteland_inner_07_apartment_shelter | [Voir](before-wasteland_inner_07_apartment_shelter-1920x1080.webp) | [Voir](after-wasteland_inner_07_apartment_shelter-1280x720.webp) | [Voir](after-wasteland_inner_07_apartment_shelter-1920x1080.webp) | [Voir](after-wasteland_inner_07_apartment_shelter-2560x1440.webp) |

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


## Méthode et limites de cette passe

Les « avant » rejouent en mémoire le catalogue publié `13a4a1b` dans le même moteur ; les scripts de rendu du jeu sont inchangés. Le cadrage est celui des nouvelles annotations dans les deux versions. Ce ne sont pas des images conceptuelles.

Quatre familles / seize vues : lit simple à un oreiller, lit de camp à cadre ouvert et bancs métalliques deux ou quatre places. Vingt placements actifs utilisent ces ressources ; plusieurs remplacent déjà un ancien sprite et ne comptent pas comme de nouveaux objets traités. Le total passe de 213 à 221 placements actifs sur 109 cartes. Une table d’examen et deux variantes de couchages incompatibles reviennent au dessin source.

Après la revue native, les limites visuelles du lit de camp ont été élargies pour inclure l’ancien cadre débordant. Les captures détaillées, les comparaisons et les deux entrées du catalogue concernées ont été refaites ; les autres captures du parcours complet restent valides. Aucune limite tactique ni collision n’a été élargie. Les [différences d’annotations](changes.json) distinguent corrections, substitutions et fallbacks.

Le catalogue reste artistiquement incomplet : les variantes obliques, de nombreux murs, accessoires et objets restent issus des images d’origine. Les 122 chargements et interactions vérifiés ne signifient pas que les 122 cartes sont finalisées. Les mesures mémoire sont celles de Godot sur llvmpipe, pas une mesure complète de RAM/VRAM ni un benchmark GPU joueur.

## Revues source

- [Couchages : identité, oreillers et sens](reviews/narrow-furniture-sources.jpg).
- [Silhouettes des meubles et bancs](reviews/furniture-shapes-review.jpg).
- [Cadre débordant de l’ancienne image du lit de camp](reviews/cot-source-bounds.png) : le rouge indique l’ancienne annotation visuelle, pas une nouvelle collision.
- [Tests et validations natives](checks.txt).
- [Contrôles des entités](entity-native-report.json) : agents, ennemis, power armors, robots et véhicules, sans modification de leurs proportions ni autorisation de véhicules en intérieur.

Les modèles Blender sont les sources géométriques de production ; les sprites finis disposent de leurs planches artistiques et empreintes propres. Ils ne prétendent pas être la reproduction exacte des modèles.

## Captures des entités

- [entities-city_exterior_neon_market_alley-1920x1080](entities-city_exterior_neon_market_alley-1920x1080.webp).
- [entities-city_industrial_factory_floor-1920x1080](entities-city_industrial_factory_floor-1920x1080.webp).
- [entities-city_interior_blacksite_lab-1920x1080](entities-city_interior_blacksite_lab-1920x1080.webp).
- [entities-cybercity_inner_02_safehouse-1920x1080](entities-cybercity_inner_02_safehouse-1920x1080.webp).
- [entities-wasteland_outdoor_01_dust_road_ambush-1920x1080](entities-wasteland_outdoor_01_dust_road_ambush-1920x1080.webp).
- [Véhicule en extérieur](vehicle-review.webp).
