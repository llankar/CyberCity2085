# UI Design System (CyberCity2085)

## Objectif
Standardiser la hiérarchie visuelle et réduire les styles hardcodés pour garder une UI modulaire et maintenable.

## Architecture
- `game/ui/theme/tokens.py`: espacements, rayons, opacités, élévations, traits.
- `game/ui/theme/typography.py`: hiérarchie stricte de typo.
- `game/ui/theme/colors.py`: palette sémantique (`surface`, `accent`, `warning`, `danger`, `success`).
- `game/ui/components/`: primitives partagées (`panel`, `button`, `badge`, `progress`, `section_header`).

## Hiérarchie visuelle stricte
- **Screen title**: `typography.screen_title`
- **Panel title**: `typography.panel_title`
- **Secondary text**: `typography.body_secondary`
- **Meta text**: `typography.meta`

Aucune nouvelle taille de police ne doit être ajoutée hors de ces 4 niveaux pour les vues de commande.

## Conventions
1. Pas de nombres magiques pour bordures/traits si un token existe (`stroke`, `spacing`, `radius`).
2. Utiliser des couleurs sémantiques de `theme/colors.py` quand possible.
3. Centraliser les primitives de dessin partagées dans `game/ui/components/`.
4. Préserver le scope: petites améliorations itératives, sans refonte architecturale.
