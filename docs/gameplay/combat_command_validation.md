# Authoritative tactical command validation

`CombatEngine.perform_action` now requires the exact living allied unit object
to belong to the current battle. A forged equivalent unit or hostile cannot
issue player commands. Offensive actions require an exact living enemy target;
corpses, allies and external targets are rejected before spending AP/resources.

In tactical-grid mode, one movement command is exactly one 32-pixel cardinal
step. Zero-length, diagonal, off-grid and multi-cell commands cannot teleport
through terrain for one AP. The shared movement helper checks the terrain and
living occupancy even if no view-specific `can_enter` callback was provided.
Impassable cover is also checked; an optional callback can impose additional
restrictions. Invalid movement preserves position and AP.

This reuses existing grid/occupancy rules rather than adding a second movement
system. The explicitly selected legacy fluid mode retains its existing delta
and occupancy semantics. Enemy activation still uses its dedicated AI path.
Normal keyboard/pointer commands continue through the same engine boundary.
This does not implement click-to-move, sprinting or new path costs.

Seven regressions failed before the correction and pass afterward. They cover
invalid deltas, occupancy without a callback, nonmember actors, invalid attack
targets, terrain and impassable cover. The full suite passed **818 tests and
eight subtests**; after the final cover assertion, **13 focused command/flow
tests passed**. No visible game window or desktop control was used. The earlier
R2 executable does not contain this fix.

The source entry-point smoke also passed: 122 surveys, seven MP3 files, fifteen
preserved story objectives, temporary save/load and a legal dockside victory
on turn 25. This does not certify graphical startup or audio playback.
