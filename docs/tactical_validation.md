# Tactical validation without desktop control

User constraint: do not take control of the user's PC for this project. Do not
use mouse/keyboard injection, activate game windows, or launch visible desktop
QA sessions. Use automated rules, scenario simulations, render-contract tests,
asset-backed terrain checks, and packaging. Report any unverified visual checks
separately instead of describing contract tests as a rendered playthrough.

## Current automated checks

- Godot launch correction (November 14, 2026): executable resolution keeps saved
  Settings, environment variables, and PATH priority, then checks bounded
  portable-install directories (including drive-root `Godot` folders on Windows).
  The mission briefing enters the handoff screen only after a process actually
  starts; an OS launch failure records its reason and uses the Arcade fallback.
  Regression tests cover portable discovery, console/GUI preference, failed
  process starts, and headless scene loading through the discovered executable.
  Restored fallback map loading and removed a duplicate terrain-connect block
  that used objective positions before initialization. Verified locally with
  578 tests plus 8 subtests; the discovered Godot 4.6.3 executable loads the
  combat scene in headless mode. No visible launch or desktop input was used.

- `python tools/render_tactical_offscreen.py`: renders production Arcade frames
  with EGL, silent audio, and an invisible window. Desktop fallback is disabled.
  Local Windows lacks EGL. The explicit `--backend hidden` uses an invisible
  native GL context and has successfully rendered deployment and combat locally
  without activation or input injection. Reviewed frames confirmed objective
  distance/readability and exposed excessive obstacle fill; map obstacles now
  use quiet contours. The locally
  added `Tactical off-screen QA` workflow provides Linux/Mesa rendering and frame
  artifacts; it has not been executed remotely.

- `python -m pytest tests/test_real_battlefield_routes.py -q`: representative
  shipped city/wasteland scenes through the production terrain pipeline;
  connected objective beats, preserved approach distance, safe spawn/objective
  anchors, and cover matched to blocked background cells.
- `python -m pytest tests/test_battlefield_language.py -q`: directional cover,
  sight blockers, peeking, friendly-line policy, hazard exposure, status ticks,
  disconnected terrain, and authored-mask preservation.
- `python -m pytest -q`: full campaign, save, engine, UI-contract regression gate.

## Geometry and remaining evidence

Image sampling and mask import flip image rows into world Y coordinates, and mask
export reverses the transform. The map texture uses the same world rectangle as
terrain sampling; camera pan no longer stretches only the background. An
asymmetric image/mask regression guards against vertically mirrored geometry.

Authored `.walkable.png` masks are authoritative. Without a mask, image-derived
walkability is a heuristic and may misclassify art. Terrain-bound obstacles now
come from blocked-region boundaries, rather than randomly placed high cover on
open ground. Inferred access lanes are explicitly marked and preserve mission
distance; they are a procedural gameplay fallback, not proof of precise art
alignment. Per-map authored masks and off-screen rendered review remain needed
before claiming pixel-accurate wall alignment across the map catalogue.

The earlier desktop check found collapsed extraction anchors and low objective
readability. Automated real-asset regressions cover the route correction; the
latest fixed objective card has now been verified in the invisible-context
production render (`runtime/tactical-qa/combat.png`). This is rendered evidence,
not a claim that an interactive playthrough of every mission has passed.
