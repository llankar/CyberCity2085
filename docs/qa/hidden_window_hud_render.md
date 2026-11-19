# Real HUD rendering without desktop control

`python -m tools.render_tactical_snapshot --output runtime/tactical_snapshot.png`

This opt-in tool creates an Arcade window with `visible=False`, constructs a
temporary four-role defense fixture, draws the actual BattleView once and saves
its OpenGL framebuffer. It never shows/activates a window, dispatches desktop
input or reads a player save. Audio is mocked. The owned hidden window closes
in a `finally` block. It is a rendered fixture, not a played battle.

The first real frame failed with `UnboundLocalError` in the psi role indicator:
`num_points` existed only inside the samurai branch. Initializing shared ring
geometry before role branches fixes actual drawing. A new independent psi
regression and samurai/psi card-bounds assertions protect it.

Visual inspection then found huge role rings and enum-qualified stance labels
overflowing portrait cards. Indicators now fit inside their cards, labels use
actual enum values, and mode colors resolve those values correctly. When the
combat journal is open it replaces the initiative panel rather than overlapping
it; closing the journal restores initiative and pointer-region ownership.

Both corrected frames were rendered and inspected:

- [1280x720 logical viewport](rendered_hud_20261116/tactical_snapshot_1280_fixed.png)
- [960x640 logical viewport](rendered_hud_20261116/tactical_snapshot_960_fixed.png)
- [Framebuffer sizes and hashes](rendered_hud_20261116/report.json)

Windows DPI scaling produced 1920x1080 and 1440x960 framebuffer images respectively.
No screenshot of the user's desktop was taken. Captures expose remaining layout
work: status/action panels overlap at the bottom; header information is crowded,
especially at 960 width; deployment/fog/HUD can obscure units. These remain open,
along with target/movement/other-objective frames and actual input/audio playthrough.
The rendered fixture manually bypasses deployment/intro, so it is not proof of
those transition flows. No full visual release gate is closed.

Validation: real OpenGL draws completed at both viewport sizes; **827 tests and
eight subtests passed** in the full suite. This rendering tool requires a usable
local graphics context; it is separate from the pure/headless build smoke. R2
predates the crash/layout fixes and remains an older immutable archive.
