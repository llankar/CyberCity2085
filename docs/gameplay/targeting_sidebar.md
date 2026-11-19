# Targeting sidebar and shared HUD geometry

The offensive target-lock panel now temporarily replaces the combat journal and
initiative timeline. This prevents their overlap at 960 x 640, where the old
journal could draw over hit chance, damage and target HP. The journal preference
is preserved: leaving targeting restores the journal if enabled, otherwise the
initiative timeline. First-aid selection retains its existing sidebar behavior.

`battlefield_hud_regions` supplies a single set of rectangles to both pointer
occlusion and world-caption placement. These include the lower HUD, mission bar,
resources, phase, objective brief and the actually visible sidebar. Initiative
space is reserved before world captions are laid out, rather than using the
previous frame's slot count. Hidden journal/timeline areas no longer intercept
target clicks. The target panel's own area still blocks battlefield input.

Target HP is right-anchored inside its panel, correcting a visible overflow.
Long target names are capped at 22 characters in this compact panel; full agent
identity remains in the roster/dossier.

## Verification, November 16, 2026

Tests cover targeting, journal and timeline geometry at 960, 1280 and 1920 logical
widths; pointer dispatch confirms two-click targeting still works where the now
hidden journal used to intercept clicks, while the target panel itself blocks
clicks. A draw test checks the right-anchored HP text.

Full regression: **860 tests and eight subtests passed**.

Real Arcade/OpenGL fixtures at 960 x 640, all visually inspected:

- `docs/qa/target_sidebar_20261116/target_960.png`: nine captions, target panel only.
- `docs/qa/target_sidebar_20261116/initiative_960.png`: eight captions, initiative only.
- `docs/qa/target_sidebar_20261116/cancel_960.png`: nine captions, journal restored after actual Escape dispatch.

All report zero omitted captions. The render harness checks every bounded
caption against reserved panels and earlier captions, unchanged allied positions,
unchanged AP during drawing, and matching terrain/background coordinates.
Windows are explicitly hidden, audio mocked, no player save or desktop input.

Use `tools.render_tactical_snapshot` with `--width 960 --height 640 --deployment
--begin-battle --pan-x 64 --pan-y -32`. Add `--targeting`, `--hide-log`, or
`--targeting --cancel-targeting` respectively. The targeting fixture explicitly
places one enemy on nearby authored walkable ground, then enters through the
actual `_begin_target_action`; this is an isolated UI fixture, not a battle
playthrough. It does not demonstrate attack execution or a continuous campaign.

Enemy-intent captions, sprite-body collisions, extreme crowd overflow, controller
flows and multi-map live-input review remain open, along with broader release
and Godot validation gates.
