# Captions within the visible battlefield

The reference Arcade view gives hazard, compact objective and unit-name captions
the actual camera-visible rectangle. It excludes the top mission bar and the
lower controls/HUD, with an eight-pixel inset. Bounds include the rendered camera
pan and shake, so moving the camera does not change the coordinate system used
by the layout.

The layout clamps candidate rectangles to these bounds and explores nearby free
positions around occupied rectangles. Resources, phase indicator, objective brief
and the open combat log reserve their actual screen rectangles translated into
world coordinates. Existing captions reserve their complete plates. Marker
positions and sprite coordinates remain unchanged, with connectors indicating
displaced captions.

When a rectangle cannot fit, placement explicitly returns `None` without changing
the occupied list. The caller omits that caption rather than drawing outside the
viewport or over another plate. World icons/rings and the persistent objective
brief remain; full crowd-overflow inspection is still needed before release.
No omission occurs in the two measured four-agent fixtures below.

## Verification, November 16, 2026

Tests cover nine combinations of viewport size and camera pan, captions beyond
all four edges, a resource-panel obstacle, adjacent labels, deterministic
placement, a fully blocked viewport and an oversized plate. HUD integration
tests remain in the suite. The portrait-name test now mocks texture drawing
explicitly, so it also runs independently without an active window.

Full regression: **858 tests and eight subtests passed**; the independent
caption/HUD selection also passes all 39 tests.

Actual hidden Arcade/OpenGL frames, visually inspected:

- `docs/qa/bounded_captions_20261116/combat_960.png`: 960 x 640 logical / 1440 x 960 framebuffer.
- `docs/qa/bounded_captions_20261116/combat_1280.png`: 1280 x 720 logical / 1920 x 1080 framebuffer.

Both render eight bounded captions with zero omissions, after the real deployment
Enter handler and a pan of (64, -146). The render harness checks every placed
caption against visible bounds, previously placed captions and reserved panels.
It also checks unchanged unit coordinates and matching terrain/background size.
Audio is mocked, windows are explicitly hidden and no desktop input/player save
is used. Reproduce with `tools.render_tactical_snapshot`, `--deployment
--begin-battle --pan-x 64 --pan-y -32`, adding the respective size/output flags.

Remaining work includes the closed-log initiative panel, targeting panels,
enemy-intent captions, sprite-body avoidance, dense overflow priorities and
continuous input/playthrough checks. A single-map fixture does not establish
every-map fidelity, Godot parity or current Windows distribution readiness.
