## Current production workflow (owner correction,2026-11-26)
Create object families in sequence, reuse across compatible maps, then review the assembled lot together. Keep local IA pipelines loaded across entries. Skip per-object neutral render batteries and duplicate gray high BLEND files; retain high GLB, optimized/final Blender sources and original references. Run grouped map checks/captures after assembly and only repeat affected ensembles after an actual correction. Existing mandatory useful tests remain preserved. This supersedes earlier per-model review sequencing, not the final artistic criteria.

Current delivery: E:/CyberCity2085-3d-lab/generated/phase2/delivery279/index.html. One cargo model ->12 actual placements across factory/residential; artificial crate plinths removed. Wasteland wreck candidate rejected for source-footprint scale and not promoted. The next lot should tackle architecture/fixtures across further maps and a correctly scaled partial wreck, without restarting accepted machinery. Full final map art0/6.

# Current multicartes art priorities (attachment8c2be8de,2026-11-26)
IN_PROGRESS: existing industrial arm/conveyor/machine quality is now the minimum for complex objects. Prioritize source-matched modular architecture in all six environments, replace crude blue crates/artificial plinths, and rebuild significant remaining flat props. Reuse library resources before generation; preserve source PNGs, canonical tactics and production runtime. Build precise architectural structures in Blender and use Hunyuan for genuinely complex objects. Show real combat-scale multiple-actor captures, preserve cutaway, and measure significant reconstructions/reuse rather than map loading. No campaign tests or experimental asset publication. New maps only after main families become sufficiently rich.

LATEST CORRECTION: railway exits must stay open. Metro270 now splits both lateral walls across the rail band, clears only experimental boundary paint and extends rails to both map edges. Two actual exported-triangle/source tests PASS; corrected overview inspected.

# Experimental six-map production

PREVIOUS PRIORITY — Environment Detail Pass (attachment5f16d061,2026-11-26):
work by reusable object families across the existing six maps. Do not expand the
map count or treat flat art/rectangular extrusions as finished complex objects.
Prioritize industrial machines, then compatible lab/transport/residential/ruin
families; combat adapter work is deferred during this art pass. Preserve all six
baseline scenes, source PNGs, tactical data and production runtime.

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

## Residential253, ashfield254 and native tour255

IN_PROGRESS. Residential:13 original surveyed building/extension footprints,
including irregular outlines; original roof UVs; acquired door/window meshes;
inferred wall heights/elevations and existing concrete PBR. Dark albedo is prepared
explicitly for glTF because the initial multiply-node material exported too pale.
Native182 meshes loaded and screenshot inspected. Roof fans and street vegetation
still rely on original artwork; they are not claimed as reconstructed meshes.
Reproduce `prepare_residential253.py`, then `blender/residential253.py`.

Ashfield:12 source rubble/ruin/wall groups as tilted slab fragments, interrupted
wall remnants and exposed rods. Existing concrete PBR variant and projected original
slab art; original wrecks stay2D. Native192 meshes loaded; screenshot inspected.
Reproduce `prepare_wasteland254.py`, then `blender/wasteland254.py`.
The new wreck_e Hunyuan trial generated565656 triangles in69s, peak4.87GB allocated
and5.42GB reserved; optimized20k result was artistically rejected: near-planar,
0.024m thin versus~1.99m other axes. No paint run or textured AI success claimed.

Two actual outdoor export/source-hash tests PASS; two polygon/rectangle floor
preservation tests PASS. No campaign tests. Both new selector entries enabled;
native button-signal roundtrips for indices1 and5 exited0/PASS.

Tour255 records real native camera orbits through all six environment GLBs;
first export546frames at1920x1080/30FPS (18.2s), encoded H264 and contact sheet
inspected. Review found that market GLB omits the ground built by its encounter
script, so the independent viewer now restores that original visual floor.
The corrected native recording completed546frames/18.2s and was encoded/ffprobe
checked; its six-view contact sheet was inspected. The retained encounter is unchanged. No timing from offline capture is claimed as a live FPS benchmark.
`package_multimap255.py` makes six FullHD original/native comparisons and a local
HTML gallery. E: `generated/phase2/multimap255/`.

Native environment loading has now been observed for6/6 selected maps. This is
not6/6 artistically finished or playable tactical maps. Cast, actual combat adapter,
dynamic occlusion, detailed source-specific equipment, per-map memory/live performance
and close tactical comparisons remain open. Hunyuan input strategy for top-down
map props needs improvement or a different asset method; do not repeat failed
single-view crops unchanged. CHANTIER GLOBAL INCOMPLET.

## Detail pass256–258 — first reusable industrial family

DONE scoped prototype: one actual source-guided Hunyuan industrial arm and one
precise mechanical roller conveyor. Filename search of project/SourceAssets found
no isolated industrial arm match; the real west_assembly crop supplies the original
view. Built-in imagegen reconstructed one clean oblique reference, explicitly
inferred (one authentic top-down view, one generated view). Prompt:
`experiments/2d_to_3d/references/industrial_arm256.prompt.txt`.
Reference/provenance retained on E: `sources/arm256/`.

Hunyuan2mini:920440 raw triangles;57.4s;4.87GB allocated/5.42GB reserved. Blender
optimization39993 triangles. Hunyuan paint:1024² colour;86.3s;11.03GB allocated/
14.34GB reserved. No new weights downloaded. Native neutral geometry then coloured
GLB reviewed. Pedestal-ground anchor normalized; model height2.1m. Roughness/metal
masks and restrained enamel grading are artistic estimates, not measured scans.
High-definition shape, optimized/painted stages and final BLEND/GLB/maps retained.

Conveyor:22 distinct transverse rollers, bearings, structural rails, supports,
braces and drive motor;155 parts, existing PBR metal maps. This is real rigid
mechanical geometry, not a rectangular source projection. Both resources registered
with dimensions/anchors/source/provenance and actual use in factory257.

Factory257 preserves factory249 baseline and replaces three source assembly groups
with6 arms and5 conveyor modules. Eleven meaningful new instances from2 reusable
asset types; other important machine groups remain flat/unreconstructed. No final
map acceptance. Original floor drawings removed only in experimental replacement
regions; reviewed original clean floor sample replaces smeared inpainting beneath
assembly lines. Original outside-mask pixels asserted identical.

Native1014 environment meshes loaded. Wide/combat-scale/close screenshots inspected;
retained Rook plays Hard stand and sits on original free cell9,19 for scale only.
No new rules or combat engine. Two exported-resource/source-preservation tests PASS.
Native short orbit captured with this retained agent; H2641920x1080/30FPS/6.1s
verified by ffprobe. Offline capture is not a live performance benchmark.
E: `generated/phase2/factory257/detail258_1080p30.mp4`, `close_agent.png`,
`combat_scale_agent.png`; asset close view under environment-library/assets/industrial_arm256/.

Next: turbine/central-machine family from source references, then pipes/platforms,
lab wall panels/doors/consoles, metro rails, residential services and richer ruins.
Additional generated views must remain labelled inferred. Significant total object
coverage across six maps is not yet inventoried; final artistic acceptance0/6.

Current detail checkpoint259-262: factory260 and lab261 replace selector entries; baseline scenes preserved. Three industrial types/13 new instances, scientific service walls and local lights exported. Gallery on E: generated/phase2/detail262/index.html. Factory surveyed coverage5 detailed/11 coarse/16 flat, not full art inventory. All six final artistic acceptances remain TODO. Next: corner machines, flat factory props and metro track infrastructure.

Track263 IN_PROGRESS: standalone real-profile rails/sleepers and native scene exported on E:, two tests PASS. Artistic review NOT VERIFIED due image-output limit; selector intentionally retains metro250 until comparison. Ground-level only, recessed track/platform elevation remains TODO.

Station264: native overview and actor close reviewed; selector promoted from250 to264. Eight source-column service housings detailed and reusable normalized GLB registered. Rail263 previously pending visual review now inspected; no final station art acceptance. Generator265 source-art Hunyuan trial running, result not yet claimed.

Generator265/Factory266: direct original isolated illustration, textured40000triangle mesh, native standalone and actor-close inspected. West coarse generator upgraded without moving source root or changing tactical rules. Factory detailed families4/types14instances across6 surveyed groups; other26 surveyed groups still coarse/flat. Main selector now factory266. Final map art0/6.

Latest scoped architecture delivery281: physical wall UV/normal repair in residential280/wasteland280, reused acquired window/door variants in common library, two-map ensemble movie. This does not finish their simple architecture or replace flat wrecks. Next production lot: existing professional ventilation/cable resources in lab and subway; preserve rail exits.

- EXPERIMENTAL-FIXTURES-282 ? DONE for the prototype lot. Three shared duct, vent and cable meshes reused in 69 laboratory and 6 metro placements. Two export checks passed, including identical metro end-wall geometry. Godot ensemble captures reviewed, and fixtures282_1080p30.mp4 on E: contains 230 frames at 1920x1080 and 30 FPS. That recording predates the cutaway correction. The selector and detail tour use the updated maps. Next batch: replace flat laboratory benches and server banks with source-aligned 3D models. Artistic completion remains open across all six maps.

- EXPERIMENTAL-LAB-FURNITURE-285 ? IN_PROGRESS. Replaced 18 surveyed flat worktops with 16 solid workstations and two detailed server rack fronts. Existing screens, walls and map data retained. Blender export and one grouped native Godot capture ran, with 722 meshes and two agents. The first build stopped on an incorrect expected count (17 instead of 18); corrected build passed. Capture E:/CyberCity2085-3d-lab/generated/phase2/lab285/cast_close.png shows raised instruments but exposes old floor inpainting beneath a hidden table and overexposed cyan light. Keep lab282 as default. Next: replace the exposed footprint fill and tune light before promoting lab285.

- EXPERIMENTAL-LAB-FLOOR-285 ? DONE for the current prototype. Surveyed prop footprints now reveal a textured tiled substrate, with an automated pixel assertion preserving the floor outside the mask. Point lights reduced to 25% of prior energy. Blender export and Godot capture of both agents executed. Reviewed cast_close.png: inpaint blur removed, cyan less intense but still visible. Selector and detail tour now target lab285. Next art pass: diversify repeated apparatus and refine materials.

- EXPERIMENTAL-LAB-INSTRUMENTS-286 ? DONE for the prototype variation pass. Blender lab_furniture285.py now exports lab286, with four furniture families across 18 groups: analysis, control, preparation and servers. The floor and light correction are retained. Godot loaded 716 meshes and captured two agents. Close capture visually reviewed at E:/CyberCity2085-3d-lab/generated/phase2/lab286/cast_close.png. Selector and detailed tour updated. Materials and analyzer silhouettes remain simple. Next: reuse detailed instruments where available and extend the reconstruction to unreplaced map objects.

- EXPERIMENTAL-LAB-PROPS-287 ? DONE for this placement lot. Reused textured medical cases on preparation benches and three shared cargo crates in the surveyed south storage group, replacing its old projected top. Blender export and Godot ensemble capture succeeded (734 meshes, two agents). Wide capture reviewed at E:/CyberCity2085-3d-lab/generated/phase2/lab287/cast_wide.png. Selector and detail tour updated. Next: rebuild the flat greenhouse contents and remaining floor instruments.

- EXPERIMENTAL-LAB-GREENHOUSE-288 ? DONE for the greenhouse geometry pass. lab_furniture285.py replaces one projected worktop with two raised hydroponic beds and ten instances of one shared leaf mesh in the surveyed footprint. Blender export and Godot grouped capture executed (747 meshes, two agents). Wide render reviewed on E: at generated/phase2/lab288/cast_wide.png. Selector and detail tour updated. Foliage is stylized and remaining floor instrumentation is pending.

- EXPERIMENTAL-LAB-GROW-289 ? DONE for the greenhouse equipment pass. lab_furniture285.py adds two feed pipes and overhead emissive fixtures in the existing greenhouse group. Blender export and native Godot capture ran (757 meshes, two agents), and cast_wide.png under E: generated/phase2/lab289 was visually reviewed. Selector and tour updated. Remaining: survey untraced floor instruments and upgrade the other environments.

- EXPERIMENTAL-LAB-SURVEY-290 ? IN_PROGRESS. Six illustrated fixtures measured from the original map image and recorded with existing trace overlaps in lab_fixtures290.json. Bounds checked for all six. Three objects overlap an existing trace, including the south control bank. Next: assemble the three independent candidates and reconcile the three overlaps against the existing model layout.

- EXPERIMENTAL-LAB-FIXTURES-290 ? Three independent survey entries assembled as a control cabinet, sample cabinet and two cargo crates sharing the storage footprint. Their projected copies are masked; the pixel preservation assertion outside the masks passed. Blender export and native Godot capture executed (772 meshes, two agents) after correcting cabinet face depth from the initial overview. Selector and detail tour updated. Three overlapping traces remain IN_PROGRESS and need reconciliation.

- EXPERIMENTAL-LAB-RECONCILIATION-291 ? DONE for all six surveyed fixtures. Three overlapping proxy groups replaced in place using the corrected visual rectangles; source floor mask includes both previous and corrected footprints. Outside-mask assertion passed. Godot imported 714 meshes and captured two agents; wide render inspected at E:/CyberCity2085-3d-lab/generated/phase2/lab291/cast_wide.png. Selector and detail tour updated. Cabinet materials remain simple. Next: shift environment pass to subway platform furniture.

- EXPERIMENTAL-METRO-FURNITURE-292 ? DONE for this detail pass. platform_furniture292.py adds cushions and armrests to eight seats and lids, slots and labels to four bins. Blender export verified exact counts and native Godot captured three agents with 423 meshes. Existing track and end-wall objects are untouched by the furniture pass. Selector and detail tour updated. Next: review column and terminal finishes at close range.

- EXPERIMENTAL-METRO-DETAIL-293 ? DONE for the modeled detail lot. platform_furniture292.py adds grilles and service panels to eight columns and ticket slots and contactless readers to two terminals. Blender export counted all ten fixture groups; Godot imported 525 meshes and captured three agents. Selector and tour updated. Close view on E: generated/phase2/metro293/cast_close.png. Next: move to a different environment and keep the railway invariant in subsequent changes.

- EXPERIMENTAL-ASHFIELD-294 ? DONE for reinforcement geometry. ashfield_rebar294.py replaced 84 straight stubs in existing ruins with bent oxidized steel while retaining their attachment transforms. Blender export completed and Godot captured three actors with 192 meshes. Selector and detail tour updated. Visual refinement of the ruin shapes and compatible wreck fragments remains open.

- EXPERIMENTAL-ASHFIELD-RUBBLE-295 ? DONE for debris geometry. ashfield_rebar294.py now adds irregular concrete fragments to 12 existing ruin groups, with one combined mesh per group. Blender exported and Godot captured three agents and 204 meshes. Selector and detail tour updated. Next: fit vehicle fragments against the narrow original wreck footprint.

- EXPERIMENTAL-ASHFIELD-WRECK-296 ? IN_PROGRESS. ashfield_wreck296.py cuts a textured SUV section and fits it at 79.2% scale within wreck_e (1.415 ? 1.295 m footprint). Blender export and Godot capture with three units ran. The close view on E: generated/phase2/wasteland296/cast_close.png shows the recognizable fragment but also a blurred patch from the old floor fill. Keep the selector on wasteland295 until the patch is replaced with coherent terrain.

- EXPERIMENTAL-ASHFIELD-WRECK-FLOOR-296 ? DONE for the east wreck. prepare_ashfield_floor296.py uses nearby detailed terrain for the wreck footprint and asserts identical pixels outside that rectangle. Export and Godot capture repeated successfully with three agents. Close capture inspected: blurred patch removed. Selector and detail tour updated. Other flat wrecks remain open.

- EXPERIMENTAL-ASHFIELD-WRECKS-297 ? DONE for the three surveyed wreck footprints. West and northeast now reuse the east fragment mesh with separately fitted rotations and uniform scales. Adjacent terrain patches replace the drawings; pixel check outside the union passed. Blender export and Godot grouped capture executed (207 meshes, three units). Selector and detail tour updated. Native wide capture on E: generated/phase2/wasteland297/cast_wide.png. The wrecks share a silhouette, and the rest of the ruins still need artistic refinement.

- EXPERIMENTAL-VIDEO-298 — DONE for three-map delivery. Lab291, metro293 and Ashfield297 recorded in one pass with 2, 3 and 3 units. E: generated/phase2/current298_1080p30.mp4 contains 345 frames, 1920x1080 at 30 FPS, and decoded without errors. Deleted the intermediate AVI and reclaimed 113830520 bytes. This is an offline orbit preview. Next art batch: improve slab silhouettes and texture transitions.

- EXPERIMENTAL-ASHFIELD-FRACTURES-299 ? DONE for edge geometry. ashfield_fractures299.py recalculates face direction and bevels 107 fractured slabs and wall sections in place. Godot captured three units and 207 meshes. Selector and tour updated. Native preview E: generated/phase2/wasteland299/cast_close.png. Slab texture transitions remain open.

- EXPERIMENTAL-ASHFIELD-MATERIAL-300 ? DONE for fracture mapping. The 107 ruin meshes now use local weathered-concrete UVs on 4,630 cut and bevel faces. Broad upward faces retain the source material where applicable. Blender and native Godot capture ran (207 meshes, three agents); selector and tour updated. Next: evaluate the latest Ashfield art against its source and address remaining floor transitions.

- EXPERIMENTAL-ASHFIELD-TRANSITIONS-301 ? DONE for the three wreck seams. Feathered each terrain patch along its inner edge while keeping the detailed center. Exact outside-mask pixel assertion passed. Blender export and Godot capture ran (207 meshes, three agents), and selector and detail tour were updated. For a clean rebuild generate the intermediate floor with prepare_ashfield_floor296.py --version 297, then generate the current floor with the default argument before the corresponding Blender exports. Next art pass: compare Ashfield overall with the original art and move to the other environments.

- EXPERIMENTAL-ASHFIELD-LIGHT-302 ? DONE for lighting calibration. Compared the original overhead art to the native wide view, then replaced the cold bright preview lighting with a lower, warmer Ashfield-specific setting. Other preview defaults retained. Godot recaptured three actors and the resulting comparison was inspected at E:/CyberCity2085-3d-lab/generated/phase2/wasteland301/comparison.png. Roads read clearly; major ruined structures remain sparser than the original. Next environment pass should rebuild larger silhouettes.

- EXPERIMENTAL-ASHFIELD-ROOF-303 ? DONE for the collapsed roof geometry. Five corrugated metal sheets sit within existing slab footprints. Blender export and Godot capture ran with 212 meshes and three agents. Warmer Ashfield lighting retained. Selector and tour updated. Next: refine major ruin wall silhouettes with source-aligned structural framing.

- EXPERIMENTAL-ASHFIELD-FRAME-304 ? DONE for structural upright placement. Added 18 oxidized uprights aligned with the largest existing wall faces. Blender verified the export count and Godot captured three actors with 230 meshes. Selector and tour updated. Next: compare the enlarged structures in a grouped art review and resume detail work on the market and residential environments.

- EXPERIMENTAL-MARKET-SIGNS-305 ? DONE for the stall lighting pass. market_signs305.py adds seven color-coded illuminated stall markers within existing awning footprints. Blender exported seven groups and Godot loaded 1654 meshes. Selector updated. E: generated/phase2/market305/godot_overview.png. Next: differentiate trade symbols and inspect at tactical scale.

- EXPERIMENTAL-MARKET-ICONS-306 ? DONE for icon geometry. Seven stall markers now show three trade pictograms for food, supplies and electronics. Blender exported and Godot imported 1671 meshes. Selector and detail tour target market306. Next: frame the new signs near units and verify tactical-scale readability.

- EXPERIMENTAL-MARKET-CAST-307 ? DONE for close review. market306 now captures two humans and a robot at free tactical cells using the shared cast view. Restored the source ground in the derived market preview via an explicit scene flag. Godot loaded and captured all three. Close render E: generated/phase2/market306/cast_close.png inspected: signs visible, food icon readable, parcel and electronics remain too similar at this distance. Next: improve glyph silhouettes and replace remaining projected foreground stall.

- EXPERIMENTAL-MARKET-GLYPHS-308 ? Replaced two visually similar pictograms with an outlined parcel and lightning silhouette. Blender export and Godot capture with three units ran (1675 meshes). Selector and tour updated. Close capture on E: generated/phase2/market308/cast_close.png. The illustrated foreground stall remains the next geometry target.

- EXPERIMENTAL-MARKET-CUTAWAY-309 ? DONE for the foreground stall ghost. The stall already has a 3D group; the cutaway exposed its duplicate drawing in the ground. prepare_market_floor309.py replaces only market_se with nearby pavement, fading the inner edge and asserting identical pixels outside. Godot recaptured three agents; close view inspected and the duplicate canopy is gone. Next: address the remaining duplicated footprints as a group.

- EXPERIMENTAL-MARKET-FLOOR-310 ? DONE for seven traced rebuilt stalls. prepare_market_floor309.py now uses nearby pavement donors for all seven, with softened inner rims. Exact outside-mask pixel check passed. Godot loaded and captured the combined update with three units. Next: compare the wide capture and continue residential facade detailing.

- EXPERIMENTAL-RESIDENTIAL-VENTS-311 ? DONE for vent placement. Reused a shared vent mesh at 26 low facade anchors on 13 buildings through residential_vents311.py. Blender export and Godot capture ran with 238 meshes and three units. Selector and detail tour updated. Next: check the facade detail at street zoom and improve entrances and lighting.

- EXPERIMENTAL-RESIDENTIAL-ENTRY-312 ? DONE for entrance locator fixtures. Twelve entry meshes received warm emissive fittings. Blender export and Godot capture ran with 262 meshes and three units. Selector and detail tour updated. Remaining: visual review of entrance fittings at street distance and stronger facade differentiation.

- EXPERIMENTAL-RESIDENTIAL-LIGHTS-313 ? Close review of 312 showed underside lenses obscured by their housings. Added an exposed emissive band to all twelve entrance lamps. Blender and Godot capture ran (274 meshes, three agents), and selector and tour now use residential313. Next: add facade variation beyond small fixtures.

- EXPERIMENTAL-RESIDENTIAL-CLADDING-314 ? Added 26 low cladding strips in three finishes across 13 facades, with a center gap for entrances. Existing lamps and vents retained. Blender export and Godot capture ran (300 meshes, three units), selector and detail tour updated. Next: inspect wide and close ensemble and address roof equipment that remains illustrated.

- EXPERIMENTAL-RESIDENTIAL-ROOF-315 ? IN_PROGRESS. Placed 12 instances of the library twin-fan model on broad roof faces. First import failed due to filename mismatch; corrected to optimized.glb. Blender export and Godot capture passed with three units. Scene mesh count rose from 300 to 780, and original roof drawings remain. Keep residential314 on the selector pending merged fan geometry and selective roof-art cleanup. Preview: E:/CyberCity2085-3d-lab/generated/phase2/residential315/cast_close.png.
