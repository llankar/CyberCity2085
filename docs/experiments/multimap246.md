# Experimental six-map production

IN_PROGRESS — 2026-11-26. Latest attached multi-map brief supersedes the earlier
single-showcase limit. Production runtime, original maps and saves stay untouched.

Selected after direct visual inspection of a contact sheet of the originals:

| Original map | Interest | Survey objects |
|---|---|---:|
| city_exterior_neon_market_alley | Retained developed showcase | 24 |
| city_district_apartment_block | Dense roofs, entrances, narrow residential streets | 35 |
| city_interior_research_lab | Clinical partitions, pods, central workstations | 34 |
| city_industrial_factory_floor | Heavy machinery and production aisles | 32 |
| city_transit_subway_platform | Platforms, tracks, underground routes | 24 |
| wasteland_outdoor_02_ashfield_ruins | Open ash terrain, irregular rubble and ruins | 15 |

Inventory: 123 PNG files including `preview_control_center_edges`, hence 122
non-preview images. Inventory is not a claim that every image is a distinct map.

DONE: Existing importer now accepts a selected map, original project PNG fallback,
rectangles, polygons and width-bearing wall traces. Reimport preserves other maps,
existing reconstruction decisions and library assets. All five surveys imported:
140 new context crops, not isolated objects or finished 3D models. Source hashes
are checked against survey metadata. No tactical files are written.

Reproduce: `python experiments/2d_to_3d/prepare_multimap246.py`.
E: output `generated/phase2/multimap246/production_queue.json` contains originals,
source hashes, grid sizes, explicit existing associations, unmatched survey objects,
reuse candidates and unmeasured performance fields set to null.
Shared references/gallery: `environment-library/index.html`.

Tests actually run: six importer tests PASS, including cross-map retention,
reimport, changed-source rejection and polygon/stroked-wall crop bounds.

TODO: visually associate existing assets before inference; reconstruct lab first;
segment complex source objects and reuse working Hunyuan pipeline for textured
models; optimize and inspect actual Godot result. Do not infer artistic identity
from tactical object names alone. Complete other four maps, common metadata,
six-map selector, production-combat adapter, per-map visuals and tour video.
Production Battlefield is Node2D; earlier demo215 packages clinic214, a staged
showcase. Neither is evidence of a complete interactive 3D combat adapter.

Performance, six-map native loading and artistic acceptance: NOT VERIFIED.
New environments artistically finished: 0/5. No campaign tests or distribution.
CHANTIER GLOBAL INCOMPLET.

## Laboratory247 first assembly

IN_PROGRESS. `blender/laboratory247.py` reuses the real lab survey: traced
partitions, illustrated workstation footprints, source instrumentation surfaces,
original floor and two cylindrical three-pod banks. 239 meshes export to packed
BLEND/GLB on E:; Godot native art review actually loaded239 meshes and produced
`generated/phase2/lab247/godot_overview.png` at1920x1080. Screenshot inspected.
`res://laboratory247.tscn` is an art import review, not a combat demonstration.
One actual GLB pod export test PASS; Python compilation of changed scripts PASS.

Reusable pod bank registered by `register_lab247.py`: GLB, source BLEND/root,
dimensions, anchor, original reference, materials and footprint. Source-guided
rigid assembly replaces rejected Hunyuan pod trial; no AI texture success claimed.
This first assembly is visually below the retained showcase: plain wall surfaces,
source-image worktops and duplicate original floor equipment need improvement.
No claim that these are finished reconstructed scientific instruments.

Next: replace flat instrument details with reusable proper meshes, clean original
floor duplicates around replacements, improve wall materials, add retained cast
and integrate existing combat through an adapter. Other four environments remain
TODO; full six-map native and artistic acceptance still NOT VERIFIED.

## Laboratory248 and factory249

IN_PROGRESS. Lab248 adds separate angled displays, keyboards, specimen vials,
service conduits and existing blue-metal PBR maps; original instrument artwork
is retained on worktops after a visually rejected blank-steel variant. Native
Godot imported527 meshes and its FullHD screenshot was inspected. No cast or
interactive tactical adapter yet. Walls and instrument diversity remain unfinished.

`prepare_floor248.py` repairs inferred hidden floor only within selected surveyed
replacement rectangles. Original map bytes and unmasked corridor pixels remain
unchanged; one focused preservation test actually PASS. Inpainting is inferred
art, not authentic recovered hidden flooring. CLI accepts selected map/output and
explicit replacement identifiers; output is restricted to E: generated resources.

Factory249 reconstructs six survey groups using existing generator/crate assets;
crate rows use multiple proportion-preserving instances. Four compressor matches
were rejected after native visual inspection; original corner machinery remains.
Twenty-one other survey objects remain unmatched and retain original 2D art.
Do not count these drawings as 3D reconstruction. No new AI generation in this pass.
`blender/library_placement.py` shares imported mesh data and fits rigid models
uniformly inside placement envelopes instead of distorting their proportions.

Reproduce factory floor before Blender export:
`python experiments/2d_to_3d/prepare_floor248.py --map city_industrial_factory_floor --output E:/CyberCity2085-3d-lab/generated/phase2/factory249 --objects west_generator,north_crates_w,north_crates_m,north_crates_e,south_crates_w,south_crates_e`
Then run `blender/factory249.py` via existing Blender wrapper, and
`res://factory249.tscn` via existing Godot wrapper. Outputs stay on E:.

Next: source-specific industrial reactors/assembly lines and proper lab instrument
meshes, then metro/residential/wasteland using shared library. No new map has full
artistic acceptance; six-map selector, cast/real combat adapter and tour are TODO.

## Metro250 and environment selector251

IN_PROGRESS. Source subway art inspected, then24 survey groups assembled as
separate architectural parts: four recessed twin escalators,112 treads, two seat
banks, service columns, bins and ticket surfaces. Original floor retained outside
selected repair rectangles; stair openings use alpha in an E: copy. Existing PBR
metal and an actual source display crop used. Native Godot355 meshes loaded;
FullHD screenshot inspected. Plain wall/cabinet surfaces and terminal detail remain
below the retained showcase standard. This is not full artistic acceptance.

Reproduce: `python experiments/2d_to_3d/prepare_metro250.py`, existing Blender wrapper
with `blender/metro250.py`, then `python experiments/2d_to_3d/register_metro250.py`.
Four standalone transit modules are registered: escalator pair, seats, service
column and terminal. BLEND source/root, GLB, textures/materials, dimensions, source
reference and footprint recorded. Escalator anchor is the entry plane (stairs
extend below it), rather than incorrectly using the lowest tread as ground.
One actual GLB/floor-opening test PASS. Changed Python files compile.

`res://multimap251.tscn` provides independent selection of market, laboratory,
factory and subway art reviews; residential/wasteland remain explicitly disabled.
Shared reviews support Q/E rotation, wheel zoom and return to selector. These are
environment reviews, not four playable tactical battles. Market review preserves
the existing environment model; the original staged encounter remains untouched.
Native `--menu-smoke` actually emitted the subway button, loaded its GLB, emitted
the return button and exited0 with `ENVIRONMENT_MENU_ROUNDTRIP_PASS`.

Combat reuse inspected: existing `combat_mission_ui.gd` owns rules and exposes
`_visual_move_token`, `_visual_attack`, `_visual_self_effect`; production autoload
CombatSignals and res://scripts dependencies must be retained in an isolated
experimental project/adapter. No replacement combat rules were implemented.
Next: residential/wasteland, richer source-specific equipment, retained cast and
this visual adapter. New artistically accepted environments remain0/5.
