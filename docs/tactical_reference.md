# Tactical reference presentation, deployment and music continuity

## Deployment fix

Encounter placement now selects the largest connected region of surveyed floor,
with proximity to the requested deployment as a tie-breaker. All agents, enemies
and the objective get distinct cells in that region. Temporary unit occupancy is
excluded from this topology calculation. Collision cells and wall surveys are
unchanged.

The underground market and its duplicate previously deployed everyone into an
isolated 68-cell perimeter instead of the main 421-cell interior. The regression
driver checks all 122 maps for unique spawns and routes to the objective.

## Reference presentation

The default visual interface draws a cyan route with luminous waypoints, an
arrow ending at the destination diamond, and a beveled badge showing the real
movement AP cost. Grid cells and movement costs are unchanged. The active unit
uses a matching ground diamond. Unreachable or cleared paths show no badge.

Health bars are segmented and beveled, cyan for allies and red for enemies. They
stay six screen pixels thick, eight pixels above visible sprite pixels, with
transparent portrait margins removed. Animated atlas bounds are measured once
and cached as small normalized rectangles. Segment fills use the actual HP
fraction, clamped to valid bounds; segment count follows max HP (3–10 segments).

![Actual underground market capture](images/tactical-reference.png)

## Music transport

`MusicTransitionMixin` pauses music before `show_view` loads another interface
and resumes only when the destination is ready. Nested view changes are handled.
Aliases using the same physical audio file reuse the same player and timestamp;
different tracks retain independent bookmarks for later visits.

The Godot handoff carries `audio.start_position`. Arcade stays paused while the
child owns playback. Mission results include a track/time bookmark and capture
timestamp, allowing the returning interface to account for child playback before
resuming the matching file. Disabled audio remains disabled. The bridge passes
bookmarks for MP3 and WAV soundtracks without resetting an already playing track.

## Validation

37 focused tests pass, including a real Linux/X11 Arcade → Godot → management
round trip, music alias/bookmark tests, and Godot runtime checks over all 122 maps.
The capture driver also executes a rightward move on the underground market,
checks the AP deduction and waits for the rendered agent to reach the target.
The existing FX lifetime test now waits for the real remaining TTL, including
smoke, rather than assuming all explosion effects expire after 2.1 seconds.

```sh
python -m pytest -q tests/test_music_continuity.py tests/test_godot_combat_bridge.py tests/test_godot_launch_routing.py tests/test_godot_file_exchange.py tests/test_godot_move_highlights.py tests/test_ui_motion_audio.py tests/test_tactical_reference_runtime.py
```

To capture the reference scenario with a real display:

```sh
godot --path godot/combat_missions_ui --rendering-method gl_compatibility --audio-driver Dummy --script tests/capture_reference.gd
```

The driver creates its own isolated handoff and screenshot under `work/`.

## Reference zoom and ten-percent token enlargement

The supplied zoom reference corresponds to a full isometric tile approximately
280 screen pixels wide (the smaller destination diamond is 46% of that width).
The initial camera zoom is now also its maximum:
`clamp(280 / (2 * iso_tw), 0.25, 3.0)`. It adapts to the board's terrain scale;
zooming out remains available. Runtime checks verify the framing at 1280 × 720,
1920 × 1080 and 2560 × 1440.

All token presentation dimensions increase by exactly 10%: Godot visual bodies,
legacy standees and shadows, and Arcade fallback sprite scales (1.5 → 1.65;
human/power-armor half-scale 0.75 → 0.825). Grid geometry, collision cells,
pathfinding, AP costs and logical unit size remain unchanged. HP bars continue
to anchor above the enlarged visible body.

[Actual capture at the new zoom with enlarged tokens](images/tactical-zoom-tokens.png).
The capture driver uses the same adaptive zoom and executes a real rightward
move on the underground market, including AP deduction and rendered arrival.

## Agent visibility on detailed terrain

Living tactical sprites now have a dedicated unshaded readability material.
It restores solid body interiors from partially transparent source pixels,
retains antialiased silhouette edges and empty margins, lifts dark artwork and
adds a subtle 1.25 screen-pixel silhouette contour (cool for allies, warm for
enemies). The atlas frame bounds constrain outline sampling, preventing adjacent
animation frames from bleeding into the contour. Static and animated art share
the same material; fallen sprites retain their existing subdued rendering.

The art is drawn by a separate child sprite so the correction does not brighten
health bars, terrain, selection diamonds or combat text. Token scale, collision,
input hit testing and movement geometry are unchanged.

Actual market captures: [before](images/agent-visibility/before.png) and
[after](images/agent-visibility/after.png). The capture also executes a rightward
move and verifies its AP cost and rendered destination. The native readability
regression checks rendered RGB pixels from semitransparent source art, untouched
background pixels, atlas/static parity, and dead-token hiding.

```sh
DISPLAY=:103 ALSOFT_DRIVERS=null python -m pytest -q tests/test_unit_readability_runtime.py tests/test_tactical_reference_runtime.py tests/test_godot_launch_routing.py
```

Replace `:103` with the available X11 display. The pixel test requires the real
compatibility renderer and skips without a display; headless geometry tests
remain independent of it.

## Reference-based ally and enemy presentation

The supplied infiltration reference now guides unit presentation with the existing
character artwork and current token scale. Living bodies stay solid and brighter
than the terrain. The active ally gets a narrow cyan silhouette and ground
selection diamond; targeted enemies get a red silhouette, ground diamond and
luminous corner brackets fitted to the visible body. Every living ally has a cyan contour and every living enemy a red contour,
including unselected units. Selection adds a thicker, brighter contour, so it
retains clear visual priority. Silhouette and bracket
thickness use screen pixels across camera zooms; source images, atlas animation,
collision cells and tactical scale are preserved.

The red enemy card now connects to the actual rendered enemy, follows camera
panning/zooming and unit motion, and flips sides near the viewport edge. It stays
above the squad/action area, shows the real portrait, name, segmented HP,
defense, hit chance, distance, range and AP cost. Offscreen targets dock the card
without drawing a misleading connector. It is hidden outside the player's
attack context and consumes mouse clicks to prevent attacks through the card.

The reference's example “coverage 50%” is not fabricated: this client resolves
shots using the target's defense, so the card displays that real defense value.
The displayed hit probability uses the same aim/defense formula as shot resolution;
blocked line of sight and out-of-range warnings remain explicit.

Real in-game captures on the neon-market map:
[ally selection and movement](images/unit-reference/movement.png),
[targeted enemy and linked card](images/unit-reference/target.png).
These use an isolated live handoff; they do not alter a player's campaign.
The screenshot contains the existing art rather than replacement character models.

Native tests cover solid body rendering, selected-ally and targeted-enemy
materials, exact atlas framing, body-fit brackets, card projection after camera
pan, card click consumption, and edge/footer placement at 1280×720, 1672×941 and
2560×1440. Existing movement/AP and Arcade→Godot→management checks also pass.

```sh
DISPLAY=:103 ALSOFT_DRIVERS=null python -m pytest -q tests/test_unit_readability_runtime.py tests/test_tactical_reference_runtime.py tests/test_godot_launch_routing.py tests/test_godot_move_highlights.py
```

Use an available X11 display. The reference capture can also be reproduced with
`godot --path godot/combat_missions_ui --rendering-method gl_compatibility --audio-driver Dummy --script tests/capture_reference.gd -- --target-reference`.


### Always-visible faction contours

Cyan/red silhouette outlines are enabled for all living units, independently of
selection, targeting or active turn. The ordinary outline is approximately
1.35 screen pixels; selected/targeted outlines are 1.8 pixels and slightly
brighter. Empty margins and dead-unit handling remain unchanged. Native pixel
checks explicitly render an unselected ally and an untargeted enemy and verify
their cyan/red edges.

[Real capture with all living units outlined](images/unit-reference/all-outlined.png).
