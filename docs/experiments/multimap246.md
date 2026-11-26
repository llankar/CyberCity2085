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
