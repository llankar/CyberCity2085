# UI Design System (CyberCity2085)

## Goal
Standardize visual hierarchy and reduce hardcoded styles to keep the UI modular and maintainable.

## Architecture
- `game/ui/theme/colors.py`: color tokens **semantic only** (`surface_primary`, `text_secondary`, `accent_warning`, `accent_danger`, etc.).
- `game/ui/theme/typography.py`: strict typography hierarchy.
- `game/ui/theme/spacing.py`: semantic spacing (`stack_tight`, `section_gap`, `screen_margin`).
- `game/ui/theme/motion.py`: animation durations/easings/pulse.
- `game/ui/theme/elevation.py`: layers (`base`, `surface`, `overlay`, `interactive`) + stroke tokens.
- `game/ui/theme/radii.py`: semantic radii (`control`, `panel`).
- `game/ui/components/foundation/`: primitives (`Panel`, `Button`, `Badge`, `Divider`, `ProgressBar`, `Tooltip`).

## Strict visual hierarchy
- **Screen title**: `typography.screen_title`
- **Panel title**: `typography.panel_title`
- **Secondary text**: `typography.body_secondary`
- **Meta text**: `typography.meta`
- The global `Text Size` setting applies through `game/ui/theme/typography.py`; `Large` should be a clear readability mode, not a subtle tint change.

## Progressive refactor rule (anti-hardcode)
1. New screens never use `palette.*` directly.
2. Color values flow through `theme/colors.py`.
3. Sizes/spacing/radii/strokes flow through dedicated tokens.
4. Legacy migration happens screen by screen (controlled scope, no big bang).

## Expected visual examples
- **Panel**: `surface_primary` background, subtle outline, title in `text_primary`.
- **Button**: `radii.control` radius, readable normal state, strong hover/focus contrast.
- **Badge**: compact size (`typography.meta`), brief informational role.
- **Divider**: thin separation line, never a dominant element.
- **ProgressBar**: discreet track background + accent fill based on status (`accent_success`, `accent_warning`, `accent_danger`).
- **Tooltip**: short text, consistent padding, high contrast.

## Conventions
1. No magic numbers for borders/strokes if a token exists (`stroke`, `spacing`, `radii`).
2. Use semantic colors from `theme/colors.py`.
3. Centralize shared drawing primitives in `game/ui/components/`.
4. Preserve scope: small iterative improvements, no architecture rewrite.

## Required screen grammar (management + tactical)
- Zone 1: global state.
- Zone 2: selected element.
- Zone 3: available actions.
- Zone 4: expected consequences.
- Reference templates: `OverviewLayout`, `DecisionLayout`, `RosterLayout`, `TacticalLayout` in `game/ui/layouts/screen_templates.py`.
