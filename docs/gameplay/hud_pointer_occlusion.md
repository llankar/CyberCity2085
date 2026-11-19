# HUD pointer occlusion and fixed target information

Battlefield pointer selection/movement no longer receives clicks through
reserved HUD areas: the lower command/portrait band, mission/resource header,
visible objective brief, rendered initiative slots, target-lock panel and open
combat log. Action-button hit testing retains priority; right-click cancellation
still works before battlefield occlusion. Closing an optional panel releases its
screen region for battlefield clicks.

Target-lock and combat-log bounds are shared between their render functions and
pointer checks. Initiative count comes from the rendered timeline. The lower
HUD band is deliberately reserved across the viewport, including gaps between
cards, rather than allowing accidental movement there. Other panels use their
existing geometry. This is input routing, not a new movement/camera rule.

The target-lock information panel previously rendered while the battlefield
camera was active. It now renders after `gui_camera.use()`, while the target's
world-space outline remains in the battlefield pass. Camera pan/shake therefore
affects the target but not the fixed information panel.

Tests compare captured log drawing bounds with hit-test bounds at 960/1280/1920
widths and verify target-lock/lower-band occlusion. The actual view dispatcher
test double-clicks a target behind an open log and verifies that confirmation
is not invoked. Visual layout, all possible overlay overlaps and a human pointer
playthrough remain separate open gates. No desktop control or visible game
window was used. The R2 archive predates this correction.

Validation: **20 focused HUD/dispatcher tests passed** and the full suite passed
**821 tests and eight subtests** after correcting a test's rectangle-coordinate
ordering. Camera draw-order correctness is established from the source change;
actual rendered behavior remains unverified until graphical validation.
