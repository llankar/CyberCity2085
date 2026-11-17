# World Map Visual 2.0

The live Python/Arcade mission selector now renders every combat and narrative
mission as a holographic beacon: beveled icon diamond, vertical beam, luminous
footprint, concentric ground rings, neon halo and attached mission cartouche.
Main missions are orange, operations cyan, narratives violet and explicitly
urgent missions red. Risk alone does not change a mission's category.

Pulse, scanning highlights and hover enlargement animate without recalculating
layout. The selected mission gains a larger beacon, rotating ground accents,
a site cartouche and a moving luminous connection to its briefing. The same
mission objects and existing selection/launch/navigation handlers remain the
source of gameplay data; no tactical or campaign rules were changed.

## Layout and readability

The original artwork is unchanged, including its embedded title, city names,
legends, compass and information cards. Its SHA-256 remains
`9343b75e0b857f92c6edc185c0094c78b8e165105caf5e3c06a39afba89bd39f`.

The reference's floating briefing is adapted into a dedicated right HUD gutter
so its readable full details cannot cover the original map's legends or cities.
The map retains its aspect ratio. Marker and cartouche placement avoids measured
city/legend rectangles and every other marker/cartouche. Selected labels receive
priority; a visibility-grid route carries the briefing connection around these
obstacles. Layout is cached until resolution, selection or mission data changes.

Bundled OFL Rajdhani regular/bold fonts give the interface condensed, legible
cyberpunk typography without depending on workstation fonts. Cartouche titles
use measured ellipsis; the full title and all dynamic mission details remain
available in the scrollable briefing. Briefing text honors accessibility font
scaling. Marker and cartouche hit areas are separate, preventing links or empty
space between them from intercepting another mission's click.

Rendering is reusable (`game/ui/components/world_map_beacons.py`) and placement
is independent of Arcade (`game/ui/layouts/world_map_beacons.py`). Static beacon
geometry and panels are cached triangle meshes; glow textures, text and fitted
labels are cached too. Only lightweight animation details change each frame.

## Real captures and validation

These are actual OpenGL framebuffer captures of the Arcade view, not mockups:

- [1672 × 941 — story selection](images/world-map-visual-2/world-map-1672x941.png)
- [1280 × 720 — story selection](images/world-map-visual-2/world-map-1280x720.png)
- [1920 × 1080 — story selection](images/world-map-visual-2/world-map-1920x1080.png)
- [Narrative selection](images/world-map-visual-2/world-map-narrative.png)
- [Urgent selection](images/world-map-visual-2/world-map-urgent.png)
- [Machine-readable capture report](images/world-map-visual-2/report.json)

The isolated capture fixture uses the real mission catalog (six combat and six
narrative missions), two armed agents, and one explicit urgent flag. At all three
resolutions it clicks every mission, checks selection and non-overlap against
all city/legend rectangles, and verifies the selected briefing connection.
It also exercises hover, scroll-to-end, scroll isolation/reset, squad preparation,
back/Escape, narrative launch and combat launch/Enter. Only destination view
construction and campaign launch are mocked at that last navigation boundary;
rendering, hit regions, mission data and view handlers are real. The separate
native launch regression covers the actual Arcade → Godot → management round trip.

The reviewed captures corrected the font fallback, cartouche text overflow,
selected-label placement, connection crossing legends, decorative strokes over
site names and a stale Mesa capture buffer after resize. Warm rendering measured
24.6 ms/frame at 1920 × 1080 on software llvmpipe in this environment; this is
not a hardware GPU benchmark or an FPS guarantee.

```sh
DISPLAY=:102 ALSOFT_DRIVERS=null python -m tools.check_world_map_visual
DISPLAY=:102 ALSOFT_DRIVERS=null python -m pytest -q tests/test_world_map_ui.py tests/test_world_map_beacons.py tests/test_world_map_native.py tests/test_battle_maps.py tests/test_tactical_reference_runtime.py tests/test_godot_launch_routing.py tests/test_music_continuity.py tests/test_godot_combat_bridge.py tests/test_godot_file_exchange.py tests/test_ui_motion_audio.py
```

The focused integration command passed all 55 tests, including the native
capture and cross-process launch checks. The Godot reference capture also
reported `MARKET_RIGHTWARD_MOVE_PASSED`.

Use the available X11 display instead of `:102` on another workstation. The
native capture regression skips when no display is available. Its fixture does
not read or modify a player's campaign save.
