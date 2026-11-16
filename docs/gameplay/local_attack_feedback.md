# Local attack feedback without washing out the HUD

Outgoing attacks and overwatch shots now rely on their actual impact particles,
unit flashes, muzzle flash, floating text and aftermath rather than a green
screen-edge overlay. Enemy attacks only trigger the red edge cue when they cause
positive damage. A zero-damage incoming attack adds no new edge cue.

The remaining incoming-damage cue is eight pixels wide with alpha capped at 60,
instead of six percent of screen width at alpha 140–200. It is drawn immediately
after switching to GUI space and before HUD panels, so it cannot wash over HUD
text and buttons. The legacy draw helper's outgoing `hit=True` case draws
nothing. Existing timing/decay and mechanical attack resolution are unchanged.

Floating damage, critical, healing, status and XP text now reserve rectangles in
the shared bounded caption layout. Their positions account for the actual camera
pan/shake and avoid HUD panels and other reserved captions. Payload world
coordinates and lifetimes are not mutated. Expired popups draw nothing. The
existing explicit no-space policy applies under extreme crowding; a popup can be
omitted if no rectangle fits. This is not a complete crowd-overflow solution.

## Verification, November 16, 2026

Draw tests verify outgoing-cue absence, incoming edge thickness/alpha, popup
bounds at both sides of the camera, expired-popup suppression and unchanged
popup payloads. Both actual hidden-window input tests now additionally assert
that a real outgoing shot leaves screen-edge flash alpha at zero.

Full regression: **866 tests and eight subtests passed**, including both hidden
GL input flows.

Real post-shot frames and JSON reports, both visually inspected:

- `docs/qa/local_attack_feedback_20261116/fire_960.png` / `.json`
- `docs/qa/local_attack_feedback_20261116/fire_1280.png` / `.json`

Both retain the real input loop (Fire button, cancellation and two-click shot),
one-AP expenditure, a surviving target changing from 100 to 98 HP, restored
journal/initiative preference and no changed allied positions. Forced hit/crit
rolls are deterministic test setup, not balance evidence. Eleven bounded captions
include the critical popup, with zero omissions. Actual post-shot rendering shows
no green veil and the critical text remains within the visible battlefield.

The windows are explicitly hidden, audio mocked, no desktop input or player save.
These fixtures do not execute a full enemy phase or validate incoming damage in
a played mission. Sprite-body avoidance and animation timing remain open: popup
placement can still cross a character sprite despite avoiding captions/HUD.
Continuous campaign, controller, Godot and current Windows release gates remain
outstanding.
