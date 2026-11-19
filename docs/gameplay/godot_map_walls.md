# Stored manual walls for every Godot background

## Coverage — November 14, 2026

All **122 playable backgrounds** have an adjacent `.wall-traces.json` source and
a compiled `.walls.json` survey. **92 distinct images were visually examined**;
30 additional filenames contain byte-identical art and reuse the corresponding
manual source, with `same_pixels_as` recording its origin. Reuse requires an
exact SHA-256 match, not a similar name, palette or layout.

The complete per-file checklist is [manual_wall_inventory.md](../manual_wall_inventory.md).
No playable map retains an automatic dark-region candidate. The black-and-white
`preview_control_center_edges.png` is a diagnostic image and is explicitly
excluded from the playable catalogue. Existing `walkable` masks are also excluded.

The pass covers district, exterior, industrial, interior, rooftop, transit,
Cybercity street/interior, ruined city, shelter and wasteland outdoor families.
Source images and translucent footprint overlays were inspected in batches with
`tools/review_wall_batch.py`, without desktop activation, input or audible playback.

## Manual authoring

Each named object uses a filled polygon, an axis-aligned `rect: [x0,y0,x1,y1]`,
or a `points` polyline with `width`. Coordinates refer to the source's declared
`canvas_size`; canvases can be scaled down versions of the original image.
Polyline strokes compile to thickness-preserving polygons. Sources are editable
object by object; there is no runtime visual detection or random wall pattern.

Footprints represent buildings, surviving walls, machinery, vehicles, containers,
furniture, planters, deep water and off-floor voids. Floor grates, road markings,
cracks and shallow puddles remain passable. A source record with `collision:false`
can document a floor-only detail. Water/void records use `blocks_sight:false` where
they block movement without hiding targets.

## Coordinates and gameplay limits

Compiled surveys use texture coordinates: top-left is (0,0), with 40 columns and
28 rows. Do not apply Arcade's bottom-origin Y flip. The survey is tied to the
image SHA-256. Godot's local sidecar takes precedence over geometry embedded in an
older handoff; JSON grid dimensions are converted to integers before validation.

Godot renders the exact authored outlines over its diamond. Collisions sample
those footprints onto the coarser tactical grid: a cell is blocked at roughly
18% coverage. Thin walls or narrow doors can therefore differ from the visible
polygon by part of a cell. These are manually interpreted 2D footprints, not a
multi-level navigation mesh; overpasses do not support separate simultaneous
upper/lower walkable floors. Small debris is grouped into meaningful obstacles.

Solids govern AStar movement, reachable cells, route AP costs and direct LOS for
players and enemies. Encounter placement uses a connected free-floor region
without erasing walls. Water blocks movement but can remain transparent to LOS.

## Visible QA and commands

The temporary high-visibility overlay remains enabled by default. Solid contours
are magenta/yellow with identifiers; water is distinguished. F8 changes only the
display, not collisions or LOS. The status reports the loaded wall-cell count.

```powershell
python tools/manual_map_inventory.py
python tools/manual_map_inventory.py --propagate-identical
python tools/scan_map_walls.py --compile-traces
python tools/manual_map_inventory.py
python tools/review_wall_batch.py city_district_holo_square.png city_industrial_service_tunnel.png --output runtime/review.png
python tools/review_map_walls.py assets/maps/city_industrial_dockside_terminal.png
python -m pytest tests/test_map_geometry.py tests/test_battle_maps.py -q
```

The default scanner preserves existing files. `--refresh-unreviewed` skips
reviewed surveys; explicit compilation rebuilds authored sources. Refresh the
inventory after compilation. The automated scanner remains available for future
images, but its candidates are not considered manually validated.

Tests verify catalogue-wide manual coverage, source/compiled equality, exact-art
reuse, image hashes and cell bounds, obstacle/open-floor landmarks, stale-data
rejection and headless Godot path/LOS/projection/placement behavior. Full-scene
Godot validation still has the previously documented result-script parse errors;
the isolated headless wall test does not load that unrelated script.
