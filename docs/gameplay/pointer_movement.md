# Previewed pointer movement

The reference Arcade MOVE action now enters pointer movement mode while keeping
arrow-key movement available. A first left-click snaps to the nearest 32-pixel
cell and previews the shortest legal cardinal path within remaining AP. Outlined
cells and a destination label show the cost. Clicking that destination again
confirms only if the recalculated path and actor still match the preview.
Escape/right-click cancels without spending AP.

Planning uses the existing bounded `path_to_cell` helper, extended with an
optional additional walkability callback. Terrain, living occupancy and the
view's cover/bounds restrictions therefore participate in the preview. A newly
blocked route is refused rather than blindly following a stale plan. A different
valid route requires another confirmation. Camera pan/shake use the same rendered
offset as target selection.

Committed movement calls the existing engine once per step, consumes its normal
one AP per cell and stops if movement fails, the actor cannot act or battle ends.
Normal active-unit advancement occurs afterward. No extra range, AP discount,
teleport command, sprint or new turn pacing rule is added. Other action buttons
clear movement mode; arrow movement clears any stale preview.

Tests run the actual view helper and engine: a two-step path costs nothing during
preview and exactly two AP on confirmation. A path blocked between clicks does
not move or spend AP. Existing movement regressions cover cardinal geometry and
terrain behavior. These checks do not certify rendered layout, animation timing
or a human pointer playthrough. Execution is immediate per step, using the
existing movement feedback, rather than a newly introduced animation queue.
No desktop control or visible window is used. The R2 archive predates this feature.

Validation: seven focused view/movement tests passed; the full suite passed
**820 tests and eight subtests**. These establish path/cost integration, not
the still-open graphical/input playthrough gate.
