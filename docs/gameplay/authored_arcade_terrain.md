# Shared manual walls in reference Arcade combat

Arcade now consumes the same reviewed `.walls.json` surveys as Godot. Previously
its separate brightness inference could disagree with the manually authored
obstacles even though the Godot wall tests were green. All 122 playable maps have
valid reviewed manual surveys; no new image scan or wall edit was required.

## Coordinate and geometry rules

Stored surveys use a 40×28 grid in texture top-left coordinates. Arcade samples
those cells into its 32-pixel movement grid at the current window dimensions,
flipping texture Y into world Y. This is a rectangular background-space mapping;
it does not apply the Godot isometric projection to Arcade.

Manual data takes priority over inferred terrain and optional binary masks.
`TerrainProfile.source` identifies it as `manual_wall_traces_v1`. Forced spawn
anchors and inferred access-lane construction cannot erase these obstacles.
Unreviewed/missing/stale surveys retain the existing fallback pipeline. Existing
image-hash validation rejects stale data; cached profiles require cache clearing
or a process restart after authoring changes, as with the earlier terrain cache.

Movement blockers with `blocks_sight=false` (such as water) remain impassable
without being converted into high-cover LOS walls. Opaque blocked boundaries
feed the existing cover/sight rules. Those rules still permit adjacent cover
peeking; this change does not introduce a second shooting model.

## Connected encounter placement

The pure placement helper selects the largest cardinally connected walkable
region, with deterministic tie breaking. It assigns distinct cells to allies,
enemies and every objective stage without modifying terrain. Insufficient space
raises an explicit error instead of silently carving or stacking units.

Allies use the existing bottom band when it fits. Otherwise the band moves to
the region's lowest accessible floor and extends 96 pixels upward. This affects
eight maps for a six-unit squad at 1280×720; six of those have no main-region floor
below the old deployment ceiling. The HUD tints actual legal deployment cells,
and keyboard movement uses that set rather than clamping agents into walls.

Enemies start outside the deployment set. Defense markers exclude hostiles from
their initial breach radius. Containment keeps its configured line when possible,
advancing it beyond deployment if needed; enemies start above it. The same layout
is applied to units, sprites and objective state before cover/hazard generation.
Changing a map during deployment rebuilds those elements together. Changing it
after deployment is rejected so active combat cannot retain mismatched geometry.

## Evidence and limits

`tests/test_authored_encounter_placement.py` checks all 122 maps at 1280×720 and
960×640, across all eight objective families: **1,952 encounter placements**, each
with six allies and eight enemies. It uses the production objective prototypes,
terrain loader and placement helper. Checks cover connectedness, unique legal
cells, objective stages, deployment separation, pre-breach safety and unchanged
terrain. Landmark tests prove forced anchors do not punch through the holo
platform, and an opaque/non-opaque test checks LOS-cover handling.

Stubbed Arcade view tests verify actual setup, sprite synchronization, adaptive
deployment and the post-deployment map lock. HUD tests verify legal-cell tinting.
These checks require no desktop control.

Placement reachability is not a completed battle or balance result. Full authored
map fights, support-asset footprints, understrength squads, human visual review,
campaign aftermath and the Windows distribution gate remain open. Coarse 40×28
survey sampling and a single-floor model remain precision limits.
