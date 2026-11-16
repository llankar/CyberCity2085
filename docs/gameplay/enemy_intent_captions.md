# Enemy intentions in the shared caption layout

Enemy-intent plates now use the same bounded placement as unit names, hazards
and compact objectives. Complete plates reserve their space and avoid the
currently visible HUD rectangles. A connector leads from the enemy to the
displaced plate; target, destination and visible-coordinator links remain at
their actual world coordinates. No order, target selection or combat rule is
changed by the drawing pass.

Precision `LOCK` reserves a two-line plate containing both the target/action and
`2 AP / 30% CRIT - MOVE OR CUT SIGHT`. The former fixed-width cap could leave text
outside its plate; width now accounts for the actual caption and counterplay
line. Target names longer than 18 characters are shortened with an ellipsis,
while interruption and command-link markers remain. If no bounded space exists,
the plate is omitted under the existing explicit overflow policy; its world
links/marker may still render. Dense-overflow prioritisation remains open.

The draw adapter additionally filters dead and hidden enemies even when a caller
passes an old reserved-intent list. Their plate and links reveal no position.
The original intent list is returned unchanged; rendering does not mutate orders.

## Verification, November 16, 2026

Tests cover a precision plate beside another label, the full counterplay line,
plate height/visible bounds, unchanged enemy position and absence of links or
plates for stale hidden/dead intentions. Existing tests retain interruption,
mutant marking, swarm destinations and hidden command-coordinator checks.

Full regression: **862 tests and eight subtests passed**.

Actual hidden Arcade/OpenGL frames were visually inspected:

- `docs/qa/intent_captions_20261116/target_960.png`: target lock sidebar, ten bounded captions.
- `docs/qa/intent_captions_20261116/journal_960.png`: actual Escape cancellation restores journal, ten bounded captions.

Both have zero caption omissions. The contact-threat caption now sits above the
enemy nameplate rather than over allied names. The fixture explicitly positions
one enemy nearby, enters actual fire targeting and draws the engine's real
reserved intention. These frames show a breach intention, not a precision lock;
precision text/layout evidence comes from the regression tests.

Logical size 960 x 640 maps to a 1440 x 960 Windows framebuffer. The harness checks
bounded captions against panels/previous plates, unchanged allied coordinates
and drawing AP, and matching background/terrain dimensions. Window visibility
is explicitly false, audio mocked, with no desktop input or player saves.

This remains isolated fixture evidence, not a played mission or continuous
campaign. Sprite-body avoidance, pathological crowding, animation/input timing,
controller flows, Godot parity and the current Windows build remain unverified.
