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


## Priorité aux agents, ennemis, power armors, robots et véhicules

Les vues « avant » ont été capturées avec le moteur publié `7ea8323`, avant modification des scripts de présentation. Les vues « après » utilisent les mêmes fixtures et cadrages. Les scènes militaires supplémentaires exercent les deux véhicules, terrestre et aérien, aux trois résolutions ; les deux intérieurs testés n’affichent aucun véhicule.

Corrections livrées : robot de soutien non géant plafonné visuellement à 1,65× ; échelles des agents, power armors, véritables géants et véhicules conservées. Compression des hautes lumières avant écrêtage, corps opaques et contours d’équipe conservés. Ombres de silhouette différenciées pour aéronefs, véhicules terrestres et humanoïdes ; contact des châssis proportionné à leur largeur. Les tests couvrent aussi la sélection, les déplacements, le ciblage, les changements de tour et le fallback graphique.

Le profil ne modifie jamais les dictionnaires d’unités. Aucune règle, PA, statistique, collision, portée ou ligne de vue n’a été modifiée. Les fichiers des cartes et les PNG des unités sont inchangés.

### Véhicules en gros plan

| Carte | VTOL avant | VTOL après | Véhicule terrestre après |
|---|---|---|---|
| city_exterior_neon_market_alley | [Voir](before-city_exterior_neon_market_alley-vtol.webp) | [Voir](after-city_exterior_neon_market_alley-vtol.webp) | [Voir](military-city_exterior_neon_market_alley-1920x1080-vehicle-1.webp) |
| city_industrial_factory_floor | [Voir](before-city_industrial_factory_floor-vtol.webp) | [Voir](after-city_industrial_factory_floor-vtol.webp) | [Voir](military-city_industrial_factory_floor-1920x1080-vehicle-1.webp) |
| wasteland_outdoor_01_dust_road_ambush | [Voir](before-wasteland_outdoor_01_dust_road_ambush-vtol.webp) | [Voir](after-wasteland_outdoor_01_dust_road_ambush-vtol.webp) | [Voir](military-wasteland_outdoor_01_dust_road_ambush-1920x1080-vehicle-1.webp) |

### Audit des ressources et limites

[Inventaire source avec dimensions, alpha et SHA-256](resource-audit.json) : 251 références en haute résolution, dont 231 entités et 20 objets de mission. Les groupes par préfixe comprennent 27 références d’agents, 140 d’ennemis (y compris robots et armures), 60 de véhicules, deux power armors et deux robots de soutien. Il s’agit d’un audit des fichiers, pas de 251 personnages artistiquement finalisés ni de 251 tests individuels sous Godot.

Quarante-six alphas atteignent un bord de frame ; cela justifie une revue rapprochée mais ne prouve pas automatiquement que l’anatomie est coupée. Certaines variantes endommagées comportent volontairement des fragments séparés : aucun nettoyage automatique n’a effacé ces détails. Aucun manifeste n’est livré dans `assets/combat_visual/animations` ; le moteur conserve son fallback statique. La production des animations et la finition de certaines silhouettes restent ouvertes.

Les neuf planches suivantes présentent les ressources d’origine, réduites pour la revue, et ne sont pas des captures de jeu :

- [Ressources 1](reviews/units-01.jpg).
- [Ressources 2](reviews/units-02.jpg).
- [Ressources 3](reviews/units-03.jpg).
- [Ressources 4](reviews/units-04.jpg).
- [Ressources 5](reviews/units-05.jpg).
- [Ressources 6](reviews/units-06.jpg).
- [Ressources 7](reviews/units-07.jpg).
- [Ressources 8](reviews/units-08.jpg).
- [Ressources 9](reviews/units-09.jpg).

[Tests](checks.txt) · [Contrôle militaire et absence de véhicules en intérieur](showcase-final-native-report.json). Les mesures llvmpipe ne constituent pas un benchmark sur GPU joueur.
