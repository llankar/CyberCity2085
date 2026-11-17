# Captures réelles Combat Visual 2.5

Les 11 planches sont des réductions des 122 captures natives en 1280×720. Les vues détaillées conservent exactement les pixels des captures PNG grâce à WebP sans perte. Les empreintes RGB originales et résultats natifs sont dans le manifeste.

| Environnement | Avant 1080p | Après 720p | Après 1080p | Après 1440p |
|---|---|---|---|---|
| cybercity_inner_02_safehouse | [Voir](before-cybercity_inner_02_safehouse-1920x1080.webp) | [Voir](after-cybercity_inner_02_safehouse-1280x720.webp) | [Voir](after-cybercity_inner_02_safehouse-1920x1080.webp) | [Voir](after-cybercity_inner_02_safehouse-2560x1440.webp) |
| city_industrial_factory_floor | [Voir](before-city_industrial_factory_floor-1920x1080.webp) | [Voir](after-city_industrial_factory_floor-1280x720.webp) | [Voir](after-city_industrial_factory_floor-1920x1080.webp) | [Voir](after-city_industrial_factory_floor-2560x1440.webp) |
| city_exterior_neon_market_alley | [Voir](before-city_exterior_neon_market_alley-1920x1080.webp) | [Voir](after-city_exterior_neon_market_alley-1280x720.webp) | [Voir](after-city_exterior_neon_market_alley-1920x1080.webp) | [Voir](after-city_exterior_neon_market_alley-2560x1440.webp) |
| city_interior_blacksite_lab | [Voir](before-city_interior_blacksite_lab-1920x1080.webp) | [Voir](after-city_interior_blacksite_lab-1280x720.webp) | [Voir](after-city_interior_blacksite_lab-1920x1080.webp) | [Voir](after-city_interior_blacksite_lab-2560x1440.webp) |
| wasteland_outdoor_01_dust_road_ambush | [Voir](before-wasteland_outdoor_01_dust_road_ambush-1920x1080.webp) | [Voir](after-wasteland_outdoor_01_dust_road_ambush-1280x720.webp) | [Voir](after-wasteland_outdoor_01_dust_road_ambush-1920x1080.webp) | [Voir](after-wasteland_outdoor_01_dust_road_ambush-2560x1440.webp) |

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


## Agents, ennemis, power armors et robots

Toutes les vues de contrôle existent en 720p, 1080p et 1440p ; les vues ci-dessous sont les captures natives 1080p. Les illustrations et proportions restent celles du jeu.
- [Unités — city_exterior_neon_market_alley](entities-city_exterior_neon_market_alley-1920x1080.webp)
- [Unités — city_industrial_factory_floor](entities-city_industrial_factory_floor-1920x1080.webp)
- [Unités — city_interior_blacksite_lab](entities-city_interior_blacksite_lab-1920x1080.webp)
- [Unités — cybercity_inner_02_safehouse](entities-cybercity_inner_02_safehouse-1920x1080.webp)
- [Unités — wasteland_outdoor_01_dust_road_ambush](entities-wasteland_outdoor_01_dust_road_ambush-1920x1080.webp)

## Véhicules extérieurs

- [Véhicule — city_exterior_neon_market_alley](entity-city_exterior_neon_market_alley-1920x1080-vehicle.webp)
- [Véhicule — city_industrial_factory_floor](entity-city_industrial_factory_floor-1920x1080-vehicle.webp)
- [Véhicule — wasteland_outdoor_01_dust_road_ambush](entity-wasteland_outdoor_01_dust_road_ambush-1920x1080-vehicle.webp)

## Contrôle des nouveaux objets

- [Détail — city_district_civic_center](detail-city_district_civic_center-1920x1080.webp)
- [Détail — city_industrial_power_substation](detail-city_industrial_power_substation-1920x1080.webp)
- [Détail — city_interior_medical_clinic](detail-city_interior_medical_clinic-1920x1080.webp)
- [Détail — city_interior_police_records](detail-city_interior_police_records-1920x1080.webp)
- [Détail — cybercity_inner_02_safehouse](detail-cybercity_inner_02_safehouse-1920x1080.webp)

Le transformateur générique a été rejeté après revue en gros plan : la sous-station conserve ses véritables ensembles d’isolateurs. La capture correspond au rendu corrigé.

## Décisions de revue et limites

218 découpes examinées : 88 décisions de substitution, les autres sont conservées et motivées dans le manifeste. Les 104 candidats issus de ces décisions incluent les illustrations identiques réutilisées ; 88 placements supplémentaires sont actifs après contrôle de proportions. Les groupes, meubles obliques et éléments spécialisés ne sont pas remplacés au hasard.

Les vues « avant » proviennent des captures réelles publiées dans `35f7b80`, au même cadrage et à la même résolution. Elles ne sont pas une maquette. La reconstruction artistique de tous les murs et accessoires reste incomplète.

### Planches de revue des objets

- [Découpes 0 à 23](reviews/review-00.jpg)
- [Découpes 24 à 47](reviews/review-01.jpg)
- [Découpes 48 à 71](reviews/review-02.jpg)
- [Découpes 72 à 95](reviews/review-03.jpg)
- [Découpes 96 à 119](reviews/review-04.jpg)
- [Découpes 120 à 143](reviews/review-05.jpg)
- [Découpes 144 à 167](reviews/review-06.jpg)
- [Découpes 168 à 191](reviews/review-07.jpg)
- [Découpes 192 à 215](reviews/review-08.jpg)
- [Découpes 216 à 217](reviews/review-09.jpg)

[Tests ciblés et contrôles natifs](checks.txt) · [Entités](entity-native-report.json) · [Détails](detail-native-report.json)
