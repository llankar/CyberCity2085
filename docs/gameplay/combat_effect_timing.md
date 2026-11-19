# Combat effects advance in elapsed time

The reference BattleView previously reduced particle life and shake intensity
partly once per frame. At high refresh rates effects vanished earlier; at low
rates they lasted longer. Flash decay used an integer decrement, so a sufficiently
small update step could stop its fade entirely. Delayed psi waves also discarded
the portion of a frame after their delay expired.

The update loop now uses elapsed seconds throughout these effects:

- Particle life decreases at 4.2 units/second, preserving the former 60 Hz lifetime.
- Particle ballistic positions integrate constant acceleration analytically.
- Shake decay uses the former 0.72 factor per 1/60 second, exponentiated by elapsed time.
- Flash fade retains fractional progress; attack timers clamp at zero.
- Psi waves consume the remaining active part of the frame after their delay.

These changes affect visual timing only. They do not advance tactical turns,
spend AP, change unit positions or add an animation input lock.

## Verification, November 16, 2026

`tests/test_combat_effect_timing.py` calls the actual BattleView update method
without a window. Five subdivisions of 0.1 seconds give the same particle
position/life, flash, attack timer, shake and delayed-wave radius/life. Complete
2.5-second lifecycles at 30, 60, 240 and 1000 updates/second clear every seeded
transient, including particles, popups, flashes, rings and waves.

Both existing actual hidden-window fire-input tests now run 150 real updates at
1/60 second after the shot. They assert that effects finish, allied sprites and
world coordinates remain fixed, the shot still costs one AP, and the next Fire
action can be opened and cancelled without another AP cost. The focused timing
and real-input selection passes all 11 tests.

Full regression: **875 tests and eight subtests passed**.

Actual settled renders and JSON reports, visually inspected:

- `docs/qa/effect_lifecycle_20261116/settled_960.png` / `.json`
- `docs/qa/effect_lifecycle_20261116/settled_1280.png` / `.json`

Both retain ten bounded captions with no omissions, no residual impact effects,
and the expected journal/initiative state. Run the previous fire fixture with
`--settle-effects` to reproduce. Window visibility is explicitly false, audio is
mocked and no desktop input or player save is involved.

These are deterministic simulation updates and real GL draws, not measured
render performance, live event-loop pacing or a human playthrough. Sprite-body
avoidance, dense labels, consecutive enemy attacks, end-turn transitions,
continuous campaign/controller/Godot and current release validation remain open.
