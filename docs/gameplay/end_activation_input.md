# End-activation confirmation and enemy-phase return

The mouse dispatcher used to clear `pending_end_turn_confirmation` before
processing every click. Consequently each click on End Turn started a new
confirmation and the second click could never confirm it. The dispatcher now
preserves confirmation for that button. Another action or a battlefield click
clears it; keyboard actions other than confirm/cancel also invalidate it.

The confirmation identifies the agent and remaining AP being forfeited. Existing
semantics remain: End Turn ends the current agent's activation, advances to the
next available ally, and starts the enemy phase after all allies finish. It does
not immediately discard the entire squad's AP. Escape cancels without opening
pause or spending AP.

## Verification, November 16, 2026

Two new hidden-window integration tests use the actual rendered action buttons,
mouse/keyboard handlers and CombatEngine. At both 960 x 640 and 1280 x 720 they:

1. Click End Turn once, preserving AP; Escape cancels without pause.
2. Start confirmation again, choose Move, then cancel Move; no AP is spent and
   end confirmation is no longer pending.
3. End each of four agents with two clicks on its rendered button.
4. Run one actual enemy phase, return from turn 1 to player turn 2, restore 2 AP
   per ally and select the first ally, without changing allied world positions.

The enemy phase and callbacks are not mocked. This initial defense fixture
primarily exercises distant enemy approaches, not damage/casualty handling or
mission completion. It does not prove an extended engagement or continuous
campaign. The input harness still verifies caption bounds/collisions and terrain
alignment; both frames retain eight captions with no omission.

Real frames and JSON sidecars, visually inspected:

- `docs/qa/turn_input_20261116/next_turn_960.png` / `.json`
- `docs/qa/turn_input_20261116/next_turn_1280.png` / `.json`

Reproduce through `tools.render_tactical_snapshot` with `--deployment
--begin-battle --exercise-turn --pan-x 64 --pan-y -32` and the respective size.
Fresh agents, mocked audio, explicitly hidden windows; no desktop input or player
save. Existing two fire-loop tests remain alongside the new two turn-loop tests.

Full regression: **877 tests and eight subtests passed**.

Remaining gates include consecutive enemy attacks and feedback sequencing,
casualties/debrief, continuous mission/campaign flows, controller and Godot
coverage, and current Windows release validation.
