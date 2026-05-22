# UI Design System (CyberCity2085)

## Objectif
Standardiser la hiérarchie visuelle et réduire les styles hardcodés pour garder une UI modulaire et maintenable.

## Architecture
- `game/ui/theme/colors.py`: tokens de couleurs **sémantiques uniquement** (`surface_primary`, `text_secondary`, `accent_warning`, `accent_danger`, etc.).
- `game/ui/theme/typography.py`: hiérarchie stricte de typo.
- `game/ui/theme/spacing.py`: espacements sémantiques (`stack_tight`, `section_gap`, `screen_margin`).
- `game/ui/theme/motion.py`: durées/easings/pulse d'animation.
- `game/ui/theme/elevation.py`: couches (`base`, `surface`, `overlay`, `interactive`) + tokens de traits.
- `game/ui/theme/radii.py`: rayons sémantiques (`control`, `panel`).
- `game/ui/components/foundation/`: primitives (`Panel`, `Button`, `Badge`, `Divider`, `ProgressBar`, `Tooltip`).

## Hiérarchie visuelle stricte
- **Screen title**: `typography.screen_title`
- **Panel title**: `typography.panel_title`
- **Secondary text**: `typography.body_secondary`
- **Meta text**: `typography.meta`

## Règle de refactor progressive (anti-hardcode)
1. Les nouveaux écrans n'utilisent jamais `palette.*` directement.
2. Les valeurs de couleur passent par `theme/colors.py`.
3. Les tailles/espaces/rayons/traits passent par les tokens dédiés.
4. La migration legacy se fait écran par écran (scope contrôlé, sans big-bang).

## Exemples visuels attendus
- **Panel**: fond `surface_primary`, contour discret, titre en `text_primary`.
- **Button**: rayon `radii.control`, état normal lisible, contraste fort en hover/focus.
- **Badge**: taille compacte (`typography.meta`), rôle informatif bref.
- **Divider**: trait fin de séparation, jamais élément dominant.
- **ProgressBar**: fond de piste discret + remplissage accentué selon statut (`accent_success`, `accent_warning`, `accent_danger`).
- **Tooltip**: texte court, padding constant, contraste élevé.

## Conventions
1. Pas de nombres magiques pour bordures/traits si un token existe (`stroke`, `spacing`, `radii`).
2. Utiliser des couleurs sémantiques de `theme/colors.py`.
3. Centraliser les primitives de dessin partagées dans `game/ui/components/`.
4. Préserver le scope: petites améliorations itératives, sans refonte architecturale.
