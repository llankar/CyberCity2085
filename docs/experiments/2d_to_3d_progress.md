# Experimental 2D to 3D progress

This register is separate from the principal CyberCity 2085 GOAL.

- `IN_PROGRESS` EINAR-GAME-SKELETON-IDLE-79 — source rig/constraint audit and
  actual retained skin weights used to build222 baked game joints/one skin for
  76 textured meshes. Weighted bones sample source pose matrices; rigid parts
  sample complete authored object transforms, including mechanical constraints.
  Film controls are not shipped as runtime dependencies. Neutral Blender vertex
  error0.0000003825m. First glTF export included unrelated facial pose-library
  actions due exporter default export_anim_single_armature=True; inspected local
  official exporter option and disabled it. Real GLB now contains exactly one
  requested clip. Explicit mesh parenting also removed ambiguous armature lookup.

  FittingStressTest artifact: E: phase2/einar_rig01,39,223,776 bytes,222 joints,
  one diagnostic clip. Native skin sampling verifies head movement31.20mm and
  zero sampled leg drift; front screenshot inspected. This is not a game action.
  Source FK probes initially moved nothing: Properties bone IK switches were1.
  Explicit FK mode0 gives real arm/leg responses (~0.25m/~0.35m in the probes).
  New relaxed Idle lowers both arms through source controls/constraints and adds
  subtle cyclic head/arm motion. Not generalized into a fabricated action set.

  Latest Idle artifact E: phase2/einar_idle01/human_rig.blend/.glb,39,514,452 bytes,
 76 meshes/222 joints/one skin/one Idle clip. Eight normalized influences maximum
  exported explicitly; four vertices required truncation beyond8, worst discarded
  mass0.00889913. Real buffer verifier checks weight sums (max error1.44e-7),
  range/count, embedded images, skin/joint/clip coverage and neutral error. Native
  Godot CPU skin-transform sampling verifies3.008mm head motion,0 leg drift and
  0 head loop gap. It does not replace full deformation/artistic review.
  Current neutral Idle front screenshot inspected and coherent; hair omitted
  because previous strand derivative remains visually unaccepted.

  Independent comparison --charge --rigged-human --tactical --sprite-review
  --self-test loads five subjects, dispatches human Idle, explicitly reports
  unavailable robot/actions and measures62.208px projection. Native capture
  charge_idle_sprite_close.png inspected; source silhouette improved over T-pose,
  but final art/weapon/readability/performance remains NOT VERIFIED. Seven Python
  tests pass; native diagnostic/Idle skin checks and real-file rig checks pass.
  Main source controls/rig untouched on disk; no production/save changes or push.
  Files: audit_einar_rig.py, probe_einar_controls.py, rig_einar_game_study.py,
  verify_einar_rig.py, godot/skin_motion_check.gd/.tscn, comparison.gd.
  Next: author/validate actual walking with foot contacts using source IK/FK,
  then weapon grip/fire/melee/death; attach accepted hair and optimize rig/meshes.
  Robot glass/actions and full tactical/artistic acceptance remain open.
  Global objective remains incomplete; only this technical/Idle evidence advanced.

- `IN_PROGRESS` EINAR-AUTHORED-HAIR-78 — audited10 visible authored curve objects
  (beard21,970 guides, mustache5,965, eyebrows2,735, scalp10,299 plus secondary
  layers). First raw evaluated CURVES.data extraction put hair at the feet:
  visual FAIL, not accepted. Direct new_from_object(CURVES) then failed; a mesh
  carrier with ObjectInfo/CurveToMesh worked but revealed that the saved static
  derivative did not preserve source hair attachment evaluation. Corrected by
  evaluating the fresh original authoring scene, then loading only the76 game
  meshes into a new derivative scene. Camera-dependent helper drivers muted in
  memory; embedded scripts remain disabled. Corrected CLI exits0.

  Four main authored hair layers converted through deterministic strand thinning,
  six samples/strand and triangular profiles:123,810 extra triangles. Real GLB
  verifier passes80 meshes/359,536 triangles/38,829,820 bytes/embedded images,
  all hair bounds in source head region1.2<Z<2.1m. Native front capture inspected
  at E: phase2/einar_hair01/godot_front.png: beard now attached to face, but coarse
  bright/aliasing strands and approximate palette are NOT artistically accepted.
  No film hair shader fidelity, hair LOD, head skinning or actions. Keep original
  Einar source untouched and this derivative experimental. Seven Python tests pass.
  Files: audit_einar_hair.py, export_einar_hair.py, verify_einar_hair.py.
  Next: improve strand/card density and antialiasing with source palette, export
  game skeleton from audited25 weighted meshes plus51 rigid attachment chains,
  validate neutral/body poses and real actions. Robot glass still unresolved.
  Other global requirements remain open as listed above; no production/save
  modifications or push. Previous goal turn and this turn both made real progress.

- `IN_PROGRESS` EINAR-MATERIALS-TACTICAL-77 — authored dielectric bake expanded
  from the jacket to30 visible skin/cloth/boot/glove/satchel/eye meshes. First
  mechanical conversion added29 meshes, then explicit group-interface lifting
  and emission-strength multiplication raised coverage to76/76. Last five
  road-sign/finger surfaces completed with --resume; no entire-job restart.
  Native material tests pass:8 robot interfaces/refused glass; synthetic cable
  tests verify lifted color, emission strength3, cached outputs and changed-route
  refusal. Initial library restore failed because Blender mutated its requested
  object-name list; immutable tuple/copy fixed it before baking.

  E: phase2/einar_pbr01/human_pbr.blend/.glb,274 embedded images,235,726 triangles,
  35,302,928 GLB bytes. Real-file verify_einar_dielectrics.py --mechanics passes
  76 meshes/one scene/offline textures, zero unresolved adapters. This proves
  adapter coverage only: film refraction/cornea, subsurface, hair, emission HDR,
  detailed appearance and deformation are NOT accepted. Neutral native Godot
  front/side/back captures all executed/inspected: godot_front/side/back.png.
  Source beard/hair absent; source game skeleton/action clips not yet exported.
  Skinning audit confirms25 evaluated meshes retain vertex weights,51 are rigid;
  source rig/group names and constraint attachment mechanisms recorded on E:.

  Independent comparison.gd --charge loads these human/robot derivatives beside
  VTOL/crate/generator on the existing alley (5 subjects/627 obstacle cells).
  Native selection/camera/unavailable-action checks pass. Measured mesh heights
  are1.855504m human/1.949876m robot; no copied2.4m label. Actual1920x1080 sprite
  comparison matches62.208px and20.736px reference heights to<0.1px; captures
  charge_sprite_close.png/overview.png on E:. Close/tactical images inspected;
  overview capture generated, artistic review still pending. Existing sprites
  remain more immediately readable; T-pose and thin robot silhouette inadequate.
  Original animated-George comparison regression still dispatches Walk correctly.
  Frame-loop timing logs are CPU-loop samples, NOT a verified GPU/FPS benchmark.
  HUD overlap corrected and close capture rerun. Seven Python tests pass.

  Files: charge_dielectric.py, bake_einar_dielectrics.py, bake_einar_mechanics.py,
  charge_pbr.py, inspect_charge_materials.py, audit_einar_skinning.py,
  check_charge_group_channels.py, verify_einar_dielectrics.py, comparison.gd,
  preview.gd (--view=front/side/back). No production/source/save changes or push.
  Next: convert authored curve hair/beard, export a game skeleton preserving the
  audited weights/rigid attachments, validate deformations and real actions;
  fix robot glass/emission, optimize/batch stage geometry, redo tactical art review.
  Global scope remains incomplete; no humanoid artistic/animation criterion DONE.

- `IN_PROGRESS` CHARGE-GAME-CONVERSION-76 — whole static robot bake finished:
  120/124 meshes baked; four robot_glass meshes explicitly unresolved/purple.
  Real GLB verification:269,209 triangles,35,676,008 bytes,480 embedded images,
  one scene. Native Godot import/capture passed and screenshot inspected at
  E: phase2/security_pbr_robot01/godot_pbr.png. No rig/actions; glass coverage
  FAIL, full artistic fidelity NOT VERIFIED. Source-glass audit confirms layered
  Fresnel/refraction/mixed shaders, so a random Principled replacement was not
  presented as faithful. UV audit found15 meshes without UV and33 outside0..1;
  robot bake uses separate packed BakeUV and pinned SourceUV per part.
  Native adapters preflight:8 supported source materials, robot_glass refused.
  Emission image color-space handling corrected for FUTURE bakes after this run;
  existing whole-robot emission gamma/strength and decal alpha remain TODO.

  Human source audit:239 non-render-hidden meshes,64 used materials,414,526 base
  vertices including hidden variants. First geometry export included hidden proxy
  objects and Blender attribute errors (FAIL); fixed source visible_get filtering
  and excluded meshes without polygons. Corrected CLI run exits0;76 visible
  meshes,235,726 evaluated triangles reduced on copies to92,608. Real GLB verifier
  passes76 meshes/2,939,640 bytes/no proxies/no rig/actions, native Godot loads.
  E: phase2/einar_geometry01 retains original-material evaluated BLEND separately
  from diagnostic gray GLB. Capture inspected; this is NOT an accepted human.

  Authored jacket proof: actual Einar cloth geometry/material baked to1024px
  diffuse-color/roughness/tangent-normal maps, BLEND/embedded-texture GLB, native
  Godot screenshot and texture both inspected at E: phase2/einar_jacket01.
  Detailed fabric/wear retained without palette replacement. Diffuse-pass method
  is only a cloth study, not a valid metallic-albedo extraction. Seven existing
  Python tests pass; two real-file GLB verifiers and two native imports pass.
  No new animation, performance, VRAM-peak or full artistic acceptance evidence.
  Files: blender/charge_pbr.py, bake_charge_robot.py, check_charge_material_adapters.py,
  inspect_charge_materials.py, inspect_charge_glass.py, audit_charge_human.py,
  export_charge_human_geometry.py, bake_einar_jacket.py and two verify_charge_* files.
  Next: resolve robot glass/emission/alpha; convert remaining human materials and
  hair, preserve game rig/deformation, replace old candidates in tactical stage,
  compare source/sprites at20.736px and62.208px, then animate and review.
  Mandatory global criteria remain open: first convincing dressed/rigged human,
  Rook/Raider identities, full native animations, new-source tactical comparison,
  optimization/performance and final human/robot screenshots. Total artistic
  coverage expectation is not yet quantified; no global PASS or completion.
  All generated resources remain on E:. Production/save untouched; no push.

- `IN_PROGRESS` CHARGE-PBR-PIECE-75 — representative shin-shell source Worn
  Surface Color/Roughness/Metallic channels baked via emission and tangent-normal
  pass into four512px PNGs. Standard PBR GLB exports and loads in native Godot;
  capture inspected in E: security_pbr_piece01/godot_pbr.png. Real-file verifier
  passes1mesh/1scene/3 embedded images and connected base/metal-rough/normal maps.
  First export leaked selected objects from another stored scene and reentered
  the film-shader traversal; log proved wrong mesh was being processed. Stopped
  owned process, fixed explicit use_active_scene=True, rerun finished in0.034s
  export time. Added same scope flag to geometry bridge (that path not rerun).
  Seven Python tests pass. Scope strictly one shell, not whole robot/rig/actions;
  film layered dirt/paint fidelity remains NOT VERIFIED. Source materials retained
  in earlier derivative for broader baking. No production changes or push.
  Next: generalize validated material interfaces with safe UV packing per part/
  material, complete robot bake, optimize and preserve articulation, then human.


- `IN_PROGRESS` CHARGE-GEOMETRY-BRIDGE-74 — inspected23 source material
  interfaces/214 GEO objects, then created evaluated static security-bot derivative
  on E: security_geometry01. Original-material direct glTF export showed deep
  recursive shader traversal in exporter specular.py/search_node_tree.py; py-spy
  stack evidence saved on E: tmp/security_export_shader_stack.txt. Owned job
  intentionally stopped after this diagnosis (not merely observation timeout).
  Profiler installed on E: only. Retained original film materials in derived BLEND,
  exported separate simple-lit neutral GLB diagnostic. Native Godot import/capture
  inspected; real GLB verifier confirms124 meshes/269,209 triangles/8,319,684 bytes.
  No skins/actions exported; materials are explicitly diagnostic, not final PBR.
  Seven Python tests pass. Original source/rig preserved; no production changes.
  Next: bake source materials into game textures, optimize evaluated mesh and
  preserve articulated/deform structure in a new export; verify native actions,
  then human derivative. No artistic or global completion claimed.


- `IN_PROGRESS` CHARGE-PROFESSIONAL-SOURCES-73 — acquired official public Einar
  and Security Bot ZIPs under explicit CC BY4 (official cards plus embedded
  ReadMe.txt), stored on E: with hashes/provenance.579.8MB/76.2MB archives CRC
  tested, extraction containment checked, sources preserved. Einar inventory:
  main799-bone rig, garments/gloves/bag/boots/mechanical arm,64 image blocks;
  bot206-bone rig,13 image blocks. Neutral front/profile/back renders executed
  and all six inspected: E: phase2/einar_review and security_review. Authored
  detail is a stronger source candidate than generic MPFB/procedural human.
  Not Rook identity or final artistic acceptance; Godot/animation still TODO.
  First Einar review stopped intentionally after14.2GB OS working set. Lowered
  subdivision caused observed Surface Deform binding FAIL; corrected by keeping
  original topology and muting/disabling film displacement in review memory only.
  Corrected Einar review finished: Blender reported peak4771MB, observed OS9.5GB,
  sampled total GPU4531MiB/16303MiB (not per-process or peak VRAM). Bot review
  finished peak1104MB Blender, sampled OS3.4GB. Seven Python tests pass.
  Next: evaluated export derivative, bake film materials to game PBR textures,
  preserve rig controls/deform separation, optimize and verify native Godot
  lighting/scale/action playback. No source modification, production change/push.


- `IN_PROGRESS` INDUSTRIAL-GENERATOR-72 — modeled actual sources/
  industrial_machine.png reference into75 editable rigid parts: enamel vented
  housing, stacked finned rotary cores, bearings, cage, tubing, skid and control
  pod. Separate BLEND/GLB and neutral Blender/Godot captures on E: generator01,
  all inspected. GLB derivative merges copies after modifier baking into1mesh /
  6 material surfaces (asserted from real GLB); editable source parts preserved.
  Native standalone import passes. Added as5th subject to existing-map tactical
  stage; five-subject and actor-center-clear assertions/native controls pass.
  Stage capture E: phase2/tactical_generator.png inspected;120 frames2.000102s
  (~60fps) before merged-derivative optimization, not stress/uncapped evidence.
  Seven Python tests pass. Reference identity improved over rejected TripoSR;
  artistic acceptance still open: clean/simplified finish, no weathering/PBR maps,
  source proportions/detail require further review. Not production replacement.
  Next: qualified human acquisition, mechanical detail/materials and scene
  geometry; final human/robot screenshots and full acceptance remain TODO.


- `IN_PROGRESS` AUTHORED-HUMAN-SOURCE-71 — Vincent v1 public Blender Studio
  source acquired on E:,19,258,697-byte BLEND; official CC BY4 card, hash/credits
  recorded in3d_asset_selection.md. Neutral front/profile/back JPG renders executed
  and inspected in phase2/vincent_review. Full character rejected for exaggerated
  cartoon proportions despite professional authored geometry.2,263-bone old rig
  raises face-driver warnings in4.5; scripts disabled, animation NOT VERIFIED.
  PNG output format corrected in review script afterward; PNG rerun not executed.
  One hair-only integration study created separate BLEND/GLB in authored_hair01,
  with source credit/license/modification JSON. Native Godot import/capture passes,
  but initial floating/back-offset fit corrected only partly: scalp/base fit still
  artistically insufficient. No accepted hairstyle or final human claimed. Source
  and previous studies preserved. Seven Python tests pass; artistic gate FAIL for
  this fitting, not a completed human. No new generic armor recoloring performed.
  Next: coherent licensed tactical human/garment source; existing CC BY candidates
  need authenticated downloads; current Fajrul source still lacks rights grant.
  Continue independent rigid-asset/scene work without propagating this trial.


- `IN_PROGRESS` ROBOT-ATLAS-ALIGN-70 — all five actions rerendered separately
  in E: robot_unified_ACTION folders using common5m orthographic scale, camera
  target(0,0,.9),128px frames; prior experiments preserved. All160 frames pass
  nonempty/alpha-margin/packing checks. Cross-clip verifier confirms shared anchor
  (.5,.652639687), reference height .407039225UV and metadata equality within1e-6.
  Derived facing-to-orbit mapping [4,5,6,7,0,1,2,3] from camera projection of assumed
  Blender-Y-negative forward, not hand-written labels. Review supports projected
  E/SE/S/SW/W/NW/N/NE order via M and uses exported ground anchor. Native Death
  self-test passes frame indexing/timing/pause/view/mode/end behavior; screenshot
  inspected in robot_unified_Death/godot_review.png. Seven Python tests pass.
  Visual source-forward/facing acceptance NOT VERIFIED; sparse action sampling,
  style and final native3D fidelity remain open. Human acquisition/licensing
  questions remain pending, no integration of unlicensed candidate.
  Next: qualifying human source, more action samples only after art selection,
  improve scene/hardsurface identity, final acceptance screenshots. Global open.


- `IN_PROGRESS` ROBOT-ATLAS-ACTIONS-69 — independent Godot atlas_review scene
  added with timed playback, pause and eight-view selection. Native self-tests
  pass all32 frame indices, timed advance, pause, selection, loop/nonloop ending.
  Expanded Blender atlas proof to Idle/Walk/Shoot/HitRecieve_1/Death,160 frames
  across five32-frame sheets on E:. Four additional action sheets rendered and
  verified; Shoot/Hit legitimately return to initial pose (3 distinct samples
  per view), Idle/Walk/Death4 distinct. Initial Death cropping FAIL corrected by
  larger5m framing, rerendered and alpha-margin/packing checks passed. Shoot/Hit/
  Death sheets and Walk Godot review inspected. All five native review launches
  passed across this batch, screenshots saved in their E: atlas folders.
  Seven Python tests pass. Artistic approval NOT VERIFIED; four samples are sparse,
  Death has different scale/framing, production anchors/facing not yet calibrated.
  This proves five-action animated export/playback only, not production readiness.
  Next: unified clip framing/anchors, denser action samples as needed, qualified
  human acquisition, final 3D asset fidelity and scene screenshots. Global open.


- `IN_PROGRESS` AUTHORED-CANDIDATE-67 — official free Cyberpunk Samurai archive
  by Fajrul FN acquired on E: for license/technical inspection, 137,811,341 bytes,
  hash recorded in 3d_asset_selection.md. 36 files, modular jacket/head/hair/
  hands/bag/legs/weapons, 221-bone Blender rig,15 image blocks. Inspected with
  embedded scripts disabled. No license text found in archive/page/Blender;
  no adaptation/export/demo use. RIGHTS NOT VERIFIED. Existing Sketchfab CC BY
  candidates still require authentication (no configured API token). Optional
  user question pending for already-downloaded local candidate paths. This does
  not block robot/mechanical/atlas work. No outreach or purchase performed.

- `IN_PROGRESS` ANIMATED-ATLAS-68 — native Blender rendered Quaternius George
  Walk in8 orbit viewpoints x4 action samples (32 PNGs), transparent128px frames,
  packed1024x512 atlas and experimental metadata on E: phase2/robot_walk_atlas01.
  Atlas visually inspected; reproducible verifier passes32 nonempty uncropped
  frames,4 distinct poses/view and packing equality within1 channel value.
  Seven focused Python tests pass. This establishes animated3D-to2D production
  tooling, not artistic/facing acceptance. Production direction mapping, anchor,
  more samples/actions and native atlas playback remain TODO. Licensed source
  preserved; no game assets replaced. Next: qualified authored human acquisition,
  atlas playback/mapping, refine rigid assets and scene, final screenshots.


- `IN_PROGRESS` SPRITE-PIXEL-REVIEW-66 — added reproducible default-alley zoom
  calibration from current map presentation ratio .015 and wall image dimensions
  7680x4320, using production top-down overview/close formulas. At1920x1080,
  human reference is20.736px overview /62.208px close. Copied actual agent_samurai
  and enemy_corp_samurai_robot_heavy atlases to E:; source SHA256s verified.
  Native Godot projects 1.718m height to62.207947px /20.736023px (assert <0.1px).
  Both1920x1080 screenshots rendered and inspected: phase2/
  sprite_comparison_close.png, sprite_comparison_overview.png. Existing sprites
  remain more distinctive; no artistic pass for current human or robot.
  Seven focused tests pass (new formula contract included). Scope: default alley,
  no handoff overrides; selected robot sprite multiplier1.65 vs2.4m mesh retained.
  Sprite shaders/rim/shadows not reproduced, so not exact full-render equivalence.
  Next: acquire qualified authored human, compare again including production
  readability treatment and multiple views/actions. Global acceptance open.


- `IN_PROGRESS` TACTICAL-STAGE-64 — first existing-map composition now loads
  human, robot, crate and newly modeled reference-inspired VTOL in native Godot.
  Original alley PNG/walls copied to E: with SHA256 verification; 627 obstacle
  cells represented as prototype volumes over textured 2D floor. No production
  files modified. Actor-center clear-cell assertions and four-subject assertion
  pass; native selection/robot-animation/camera tests pass. Screenshot inspected:
  E: generated/phase2/tactical_first.png. 120 frames ~2.000161s (~60fps), limited
  four-subject scene only. Six Python tests pass. Not a finished 3D environment:
  block geometry, floor perspective, actor footprint margins and exact sprite
  zoom comparison remain TODO. Aircraft hovering because no clear landing-sized
  rectangle exists in this alley's blocked layout. Existing human remains only
  a technical comparison model; professional-human acquisition still open.

- `IN_PROGRESS` VTOL-MESH-65 — 48-part rigid mechanical study generated from
  actual project's sources/vehicle.png reference: tapered octagonal closed hull,
  cockpit facets, twin ducted rotors with individual blades, tail fins, landing
  struts and cabin windows. BLEND/GLB/neutral render saved on E: phase2/vtol01.
  Initial wing roots occluded fan disks; corrected and rerendered/inspected.
  Native Godot load in tactical stage verified. Shape still basic, not artistic
  acceptance; panel detail, real rotor animation and optimization remain TODO.
  Prior TripoSR vehicle was visually rejected and remains preserved, unused.
  Next: qualified authored human acquisition, production zoom/sprite comparison,
  improve map geometry and mechanical asset fidelity, final screenshots.


- `IN_PROGRESS` PROFESSIONAL-HUMAN-61 — user strategy correction adopted:
  stop generic MPFB recoloring, prioritize authored professional-quality humans,
  tactical modular gear and clear redistribution rights. Candidate/licensing
  register added in docs/experiments/3d_asset_selection.md. Two original cyberpunk
  candidates verified through public Sketchfab metadata API: CC BY4 commercial use,
  24,500/51,704 faces, 1/0 animations. Official downloads return HTTP401; files not
  acquired or artistically approved. Other gear/PBR candidates and exclusions
  documented. Existing-map tactical scene and exact sprite zoom comparison TODO.
  Continue other experimental tasks; do not substitute the scale stage for them.

- `DONE` COMPARISON-STAGE-62 — independent comparison.tscn/gd loads human+robot
  on 1m tiles, neutral lighting, shadows, isometric/orbit controls, selection and
  real robot action dispatch; human missing actions explicitly reported. Native
  self-test passed selection, Walk, camera mode and missing-human-action checks.
  120 frames after warmup: 2.000034s (~60fps), RTX5070Ti/OpenGL, two subjects only;
  not a stress test or uncapped GPU throughput measure. Screenshot inspected:
  E: generated/phase2/comparison_realtime.png. Current sprites not compared yet.

- `IN_PROGRESS` HUMAN-REALTIME-63 — preserved dense source; separate --realtime
  export reduces 827,976 to 61,998 triangles. Static and four-bone fitting-pose
  Godot captures inspected; silhouette broadly retained, no full deformation
  acceptance. Rendering counter in comparison: ~1.67M ->141,776 primitives
  including passes/scene (not unique triangle count). Six focused tests pass.
  Captures on E: authored_tactical01/human_realtime_neutral.png and
  human_realtime_pose.png. This optimization does not resolve insufficient art.
  Next: acquired authored human and real actions, complete tactical scene,
  production-resolution sprite comparison, final screenshots. Global IN_PROGRESS.


- `IN_PROGRESS` HUMAN-MATERIAL-60 — preserved authored_armor01 and generated
  authored_tactical01 BLEND/GLB on E:. Neutral Godot screenshot inspected:
  dark desaturated armor and copper hair now survive export. Blender MixRGB tint
  was initially lost by glTF exporter (observed white screenshot); corrected with
  explicit standard baseColorFactor in derived GLB JSON, preserving binary chunks.
  New in-memory roundtrip test verifies factors, chunk preservation and GLB length.
  Six focused tests pass. Screenshot: generated/phase2/authored_tactical01/
  human_neutral.png. This is a palette study, NOT final Rook geometry/art acceptance.
  Authored jacket, swept undercut, face identity and natural action clips remain TODO.
  Official MakeHuman system pose pack CC0 acquired (801 KiB), CRC validated and
  installed on E:. Manifest contains static poses, not locomotion animations;
  no animation coverage credit. Source: makehumancommunity/makehuman-static-website
  content/Assets/AssetPacks/makehuman_system_poses.md. Avoid destructive BVH pose
  importer on final rig: MPFB documents that it changes bone roll values.
  Next: authored tactical clothing/hairstyle acquisition and nondestructive
  animation retargeting; user-requested final screenshots remain TODO.


- `DONE` ANIMATED-FRAMING-59 — preview accepts Blender clip envelope JSON,
  converts Z-up bounds to Godot Y-up and uses a fixed conservative camera framing.
  Native Godot captures Walk at 0/50% and Death at 100%, all inspected: complete
  model visible, including fallen pose. Human authored_armor01 neutral screenshot
  regenerated and inspected. Five focused experiment tests pass. Captures on E:
  generated/phase2/george_tactical/review_*.png and authored_armor01/
  human_current_neutral.png. User requested final human/robot screenshots: current
  previews available, final artistic screenshots still TODO. Neither model meets
  final visual target; human identity/materials and robot style remain open.
  Next: improve licensed human outfit/identity and select less stylized robot
  candidate before final comparison. No full animation artistic approval claimed.


- `IN_PROGRESS` AUTHORED-MECH-SCALE-58 — Blender imported licensed George,
  measured evaluated rest geometry (7.437565 source units), created parent-only
  scale derivative at 2.4 m and exported BLEND/GLB with original 20 actions.
  Native Godot derivative Walk imports successfully; inspected screenshot exposes
  overly tight framing, still open. Added reproducible Blender clip checker:
  200 integer frames across Idle/Walk/Run/Shoot/Punch/HitRecieve_1/Death evaluated,
  all vertex coordinates finite. Walk envelope reaches 2.645 m; Death extends
  2.185 m behind origin. Evidence in E: generated/phase2/george_tactical JSONs.
  This does not prove foot contact, absence of intersections, or artistic quality.
  Five focused existing tests passed. Next: use animated bounds for preview framing,
  create multi-frame visual reviews and compare robot identity at tactical scale.


- `DONE` MECH-PREVIEW-57 — corrected camera placement relative to model bounds,
  rather than an absolute human-height camera position. Native Godot Idle,
  Walk, Shoot and Death midpoint captures generated and visually inspected on E:.
  The earlier apparent orientation failure was partly a camera framing problem;
  no source-axis correction is justified by that capture. Also fixed exact clip
  lookup: Walk previously matched Walk_Tall. Native rerun reports Walk exactly.
  Five focused experiment tests passed. These are sampled poses, not a verified
  full animation/deformation sequence. George is an authored textured animated
  candidate, but stylized silhouette/materials do not meet final CyberCity art.
  Next: normalize a derived copy to tactical scale, review complete clips and
  compare against the project robot reference; retain original licensed source.
  Global prototype acceptance remains IN_PROGRESS; no runtime changes or push.


- `IN_PROGRESS` MECH-ORIENTATION-56 — inspected George scene root (no explicit
  root rotation/scale). Added reversible preview root-X override; -90-degree
  Idle capture does not restore expected upright appearance (hypothesis fails).
  Downloaded and inspected pack Preview.jpg to compare intended silhouettes.
  Do not modify source or accept this converted mirror until animation/rest
  transforms are verified. Next: compare rest pose versus Idle and import the
  glTF in Blender; prefer official source if mirror conversion is faulty.

- `IN_PROGRESS` EXISTING-MECH-55 — official Quaternius Animated Mech page
  lists CC0. Acquired textured George glTF from agentkaerf/FreeModels mirror
  plus bundled License.txt (CC0 verified), on E: sources/quaternius_mech.
  Mirror provenance recorded; original author remains Quaternius. Inspected
  glTF animation inventory and sampled Idle in native Godot; capture inspected.
  Stylized existing animated asset is a comparison candidate, not accepted
  as source-faithful CyberCity robot. Next: evaluate Shoot/Walk/Death clips,
  normalize scale and compare quality against procedural robot under neutral light.

- `IN_PROGRESS` ROBOT-CONSTRAINT-BAKE-54 — separate script loads constrained
  source, keys knee fitting motion and bakes visual object transforms over
  49 frames, clearing constraints only in derived test source. Exports
  robot_baked_test BLEND/GLB on E:. First SCENE export split channels into
  separate clips; changed to ACTIVE_ACTIONS merged export and reran.
  Native Godot endpoint/clip verification remains NOT VERIFIED. Next: verify
  combined animation channels and sample knee/shaft endpoints in Godot.

- `DONE` HYDRAULIC-AXIS-53 — corrected shaft geometry to local Y to match
  STRETCH_TO and removed conflicting Z tracking. Native Blender endpoint
  assertions pass for both knee actuators in bent test (reported error 0 m,
  tolerance 0.1 mm). robot_mechanical08 generated; bent render inspected.
  This validates Blender endpoint constraints only. Next: bake constrained
  transforms into exported mechanical clips and verify endpoint continuity in
  Godot; complete piston sleeves and robot artistic work remain open.

- `IN_PROGRESS` ROBOT-HYDRAULIC-52 — added paired attachment empties and
  constrained knee actuator shafts using location/track/stretch constraints.
  robot_mechanical07 generated with rest/aim/pivot renders; pivot image
  inspected. Constraint endpoint accuracy and axis convention are NOT VERIFIED;
  GLB export does not prove live Blender constraints survive. Next: quantify
  shaft endpoints in bent pose, correct track/stretch axes, bake transforms for
  mechanical clips before Godot verification. No completed hydraulics claimed.

- `IN_PROGRESS` ROBOT-CONTOURS-51 — replaced chest/thigh/shin/forearm block
  plates with extruded eight-point contours, bevels and taper; added four leg
  actuator rods. robot_mechanical06 BLEND/GLB and three renders generated;
  neutral rest inspected. More defined shells but reference fidelity remains
  insufficient. Rods are rigid attached details, not telescoping constraints.
  Next: constrain hydraulic endpoints and design grounded leg motion; refine
  proportions/armor thickness against source before final material detailing.

- `IN_PROGRESS` ROBOT-HEAD-50 — native Godot head clip capture verifies corrected
  centered framing (full model visible). Reshaped helmet into lower angular
  housing with recessed split optics, jaw guards and four sensor masts.
  robot_mechanical05 BLEND/GLB and three renders generated; rest inspected.
  Closer sensor identity, but overall boxy silhouette still fails reference art.
  Next: reshape chest and leg shells using custom plate contours; add hydraulics
  and test grounded gait. Human fidelity and other prototype subjects remain open.

- `IN_PROGRESS` ROBOT-GODOT-49 — Godot native run samples TorsoYaw_AimTest
  at mid-clip, captures articulated rigid model; inspected capture confirms
  transport but old camera target clips head. Added mesh-bounds-centered target
  afterward (not rendered yet). Clip selection/fraction now configurable.
  Artistic robot still coarse; no finished attack or locomotion claimed.
  Next: rerender framing correction, sample head clip, then reshape silhouette.

- `IN_PROGRESS` ROBOT-AIM-48 — added three segmented fingers plus thumb per
  hand and 49-frame torso/head aiming test at 24 fps. robot_mechanical04
  BLEND/GLB and neutral aim render generated and inspected. GLB JSON confirms
  at least two animation clips and no skin: rigid-node animation, not human rig.
  Not accepted as final attack/idle; locomotion, impact/destruction and artistic
  fidelity remain open. Next: native Godot clip playback and source-faithful
  head/chest reshaping, then mechanical gait with grounded feet.

- `IN_PROGRESS` ROBOT-PLATES-47 — tapered ivory armor vertices and added
  inclined pectoral panels, shoulder caps, forearm shields, abdominal plates,
  vents and fasteners. robot_mechanical03 BLEND/GLB/rest and pivot renders
  generated on E:; rest image inspected. Mechanical layering improved, but
  silhouette remains too boxy versus reference and is NOT artistically accepted.
  Next: reshape head/chest and lower-leg armor, add fingers and hydraulics,
  then verify mechanical animation tracks in Godot.

- `IN_PROGRESS` ROBOT-JOINTS-46 — added eight cylindrical mechanical bearings
  and cannon barrel; regenerated robot_mechanical02 BLEND/GLB and neutral
  rest/pivot-test renders. Bent knee/elbow capture inspected: rigid components
  follow their pivots without mesh skinning. Still a coarse blockout, not
  source-faithful final art or a validated animation set. Next: taper/chamfer
  armor silhouette, add exposed mechanics and export real mechanical clips.

- `IN_PROGRESS` ROBOT-MECHANICAL-45 — built first rigid mechanical blockout
  from reference with independent torso/head/hip/knee/shoulder/elbow pivots,
  ivory armor, red visor/core and shoulder cannon. Blender generated BLEND/GLB
  and neutral render on E: robot_mechanical01; render inspected. This is only
  volume/hierarchy study: blocky geometry and sparse detailing fail final art
  target. No robot animation accepted. Next: verify pivot rotations, replace
  joint gaps with mechanical bearings and shape armor to the source silhouette.

- `DONE` IMPORTED-POSE-CLIP-44 — Blender exported separate authored_pose_test.glb
  with FittingStressTest (24 fps, frames 1–25). Godot finds AnimationPlayer,
  samples imported clip end and captures successfully; image inspected. This
  verifies animation transport for the fitting pose, not natural action quality
  or full retargeting. Static authored GLB/source remain preserved. Next: close
  joint-contact comparison and obtain suitable licensed natural action clips.

- `IN_PROGRESS` GODOT-POSE-43 — applied four-bone stress pose to imported
  authored rig and rendered. Initial absolute rotation replacement produced
  invalid limb orientation; changed to composition with imported pose rotation
  and rerendered. Captures inspected; direct local-axis correspondence with
  Blender still needs quantified verification, not accepted retargeting.
  Next: compare imported bone rest bases and export a Blender-authored pose
  clip to avoid assuming identical local axes between engines.

- `IN_PROGRESS` AUTHORED-POSE-42 — added reproducible Blender stress-pose
  renderer with both elbows bent and left thigh/calf flexed. Native execution
  succeeded; front/profile captures inspected on E:. Authored armor follows
  rig, but fitting under extreme joint bends still requires close review and
  comparison after GLB export. No natural animation acceptance inferred.
  Next: inspect elbow/knee armor contact at closer framing and verify same pose
  in Godot before authoring any action clips.

- `DONE` EXPERIMENT-TEXTURE-FILTER-41 — experimental GLB preview now generates
  missing mipmaps by default, caches shared images by texture/normal usage and
  renormalizes normal-map mip levels. --raw-textures retains diagnostic bypass.
  Native Godot run passes with seven generated image chains; filtered 12 m
  capture saved on E: and inspected. This addresses texture aliasing only;
  materials/artistic quality and production-scale equivalence remain open.
  Next: compare matched neutral Blender/Godot materials and pose authored armor.

- `IN_PROGRESS` TEXTURE-FILTER-40 — inspected GLB sampler (linear/mipmap
  requested) and images. Added runtime mipmap/anisotropic diagnostic for
  GLTFDocument-loaded textures. Native Godot capture with generated mipmaps
  inspected: bodysuit/hair speckle substantially reduced versus prior capture.
  This isolates missing runtime mip levels as a contributor, not geometry fix.
  Armor contrast and material fidelity remain open. Next: make texture setup
  reusable/cached, verify map channels and compare matched Blender exposure.

- `IN_PROGRESS` MATERIAL-ISOLATION-39 — no-shadow capture still shows speckle.
  Added unlit diagnostic; first run hit GDScript type inference error, corrected
  with explicit Material type. Native rerun generated unlit capture, inspected.
  Diagnostic switches are not artistic fixes. Next: compare source texture
  maps and direct PBR export against these controlled captures.

- `IN_PROGRESS` MATERIAL-DIAGNOSIS-38 — inspected GLB JSON: every material
  exported alphaMode BLEND, including opaque skin/armor. Export copies now
  disconnect alpha for non-hair surfaces and disable clearcoat. Regenerated
  GLB and Godot neutral capture; speckle persists (hypothesis insufficient).
  Do not claim material fix. Original authored materials remain untouched.
  Next: inspect exported normal/roughness textures and isolate direct-light
  specular versus shadow artifacts with controlled material/shadow diagnostics.

- `IN_PROGRESS` AUTHORED-GODOT-37 — native Godot 4.7.2 OpenGL loaded authored
  armor GLB and captured neutral 12 m and 3 m orthographic views on E:.
  Both inspected: silhouette readable, but materials show excessive bright
  contrast/speckle versus Blender; not accepted. 12 m view is a controlled
  tactical-size study, NOT verified equivalence to production combat camera.
  Next: simplify/bake authored material nodes to glTF PBR and compare with
  Blender under matched neutral exposure; validate actual combat display scale.

- `IN_PROGRESS` AUTHORED-EXPORT-36 — reviewed armor01 back/profile: coherent
  authored fit; checked Helios MHCLO CC0 (author field unknown) and bodysuit
  CC0/MatCreator headers. Added disposable-copy exporter and successfully
  generated authored_outfit.glb with five mesh objects, skinning and textures.
  Export warnings: multiple image samplers and >4 skin influences. Godot
  material/deformation review NOT VERIFIED. Next: native Godot capture and
  tactical-scale framing, then posed comparison before accepting materials.

- `IN_PROGRESS` AUTHORED-ARMOR-35 — suits02 download complete (192,511,027
  bytes), CRC/install passed. Inspected cyborg/Guardian/Helios thumbnails;
  Guardian header explicitly says MatCreator/CC0. Fitted MC-BodySuit-2021 plus
  Helios armor via MPFB to preserved body. authored_armor01 BLEND and four
  neutral renders generated on E:, front inspected. Authored modular armor
  baseline exists, but is not Rook's reference outfit or artistically accepted.
  Next: inspect back/profile, per-file licenses/materials and deformation,
  then assess tactical-scale export and more appropriate jacket candidates.

- `IN_PROGRESS` LICENSED-TACTICAL-CANDIDATES-34 — recovered official asset-pack
  manifests through GitHub API (makehuman-static-website/content/Assets/AssetPacks).
  suits02 explicitly lists CC0 joachip_cyborg_suit and MatCreator Guardian,
  Helios and Jupiter7 armor. Started only that targeted 183 MB pack on E:
  downloads/suits02_cc0.zip via curl. No acceptance inferred from manifest;
  individual files and appearance still need inspection. Hair01 is described
  as low-poly/stylized and hair02 as higher-poly; further selection remains open.
  Next: poll curl, CRC/install suits02, inspect armor thumbnails and fit chosen
  pieces under neutral light. Preserve existing authored outfit comparisons.

- `IN_PROGRESS` AUTHORED-REVIEW-33 — inspected outfit02 neutral back/profile:
  coat and trousers fit coherently, but short04 hair shows scalp holes at the
  crown/back. Not accepted. Official MakeHuman November 2026 notice confirms
  legacy asset browsing is offline while metadata/files and packs remain.
  Queried Makehuman-2 CC0 repository via GitHub API: community_index.json is
  literally [] (not a usable inventory). No unsupported third-party asset was
  downloaded. Next: use official pack manifests or legacy master metadata to
  find licensed leather/tactical jacket and swept hair; fix hair fit/alpha.
  Source: https://wwww.makehumancommunity.org/news/2026-11-08-moving-to-discord.html

- `IN_PROGRESS` AUTHORED-COMPARISON-32 — inspected thumbnails of male suits
  01/02/03/05/06, work suit and short hair 01/03/04. Selected suit05 + shoes03
  + short04 for second authored fitting. Blender produced authored_outfit02
  BLEND and four neutral views on E:; front inspected: coherent jacket folds,
  pockets, cuffs and footwear, but civilian padded coat/jeans and cropped hair
  do not reproduce Rook's tactical jacket/undercut. Next: inspect back/profile,
  find licensed tactical/leather jacket and swept undercut assets, keeping
  this outfit as authored pipeline comparison rather than accepting it as Rook.

- `IN_PROGRESS` AUTHORED-OUTFIT-31 — inspected male_casualsuit04 MHCLO header:
  explicit CC0 release, supplied diffuse/normal/AO maps. Executed MPFB loader
  with casualsuit04, shoes01, short02 hair, high-poly eyes and middle-aged
  Caucasian male skin. Blender generated authored_outfit01 BLEND plus neutral
  front/back/profile and perspective renders on E:. Front inspected: genuine
  textured authored garment geometry now provides a materially better baseline,
  but civilian outfit is not Rook's final identity. Next: inspect remaining
  views and compare other official male outfits/short hair before adaptation.

- `DONE` MPFB-SYSTEM-INSTALL-30 — original downloader completed; ZIP CRC and
  containment checks passed, official MPFB installation/metadata refresh ran
  successfully on E:. Catalog includes male casual suits 01–06, work suit,
  shoes 01–06, short hair 01–04, eyes, eyebrows, lashes, teeth and tongue.
  No asset fitting or artistic quality inferred from installation. Next:
  inspect pack licenses/thumbnails, choose outfit and short hair, run authored
  loader and review neutral views. Previous download waits are now historical.

- `IN_PROGRESS` NEUTRAL-ASSET-REVIEW-29 — same downloader PID 25556 verified
  active at 182,620,160 bytes; helper 40263 ended its timed wait, not the
  download. New wait helper 89513 follows the same process. Outfit loader now
  accepts authored eye assets and emits neutral orthographic front/back/side
  views at fixed 2.05 m framing. Syntax compilation passed; rendering awaits
  pack completion. Next: poll downloader and verify/install completed archive.

- `IN_PROGRESS` ASSET-DOWNLOAD-WAIT-28 — verified live downloader PID 25556;
  file grew from 137,650,176 to 155,131,904 bytes. Wait helper session 40263
  observes the same process; no restart. Inspected MPFB's official Load Pack
  operator and aligned installer with update_all_asset_lists after extraction.
  Robot source reviewed: biped mechanical frame, shoulder cannon, red visor,
  rigid segmented armor; appropriate for independent mechanical pivots.
  Next: finish CRC/installation and inspect authored human assets; robot work
  remains TODO. No completed artistic asset is claimed from this wait.

- `IN_PROGRESS` AUTHORED-OUTFIT-27 — downloader PID 25556 remains active;
  archive grew to 116,535,296 bytes. Added configurable MPFB outfit loader
  using add_mhclo_asset for clothes/hair and set_character_skin for materials,
  retaining rig fitting and neutral review lighting. Python syntax compilation
  passed for installer and loader; actual fitting NOT EXECUTED until verified
  asset pack exists. Next: finish download, validate/install, select real assets
  and run loader. No additional download was started.

- `IN_PROGRESS` MPFB-PACK-INSTALL-26 — downloader PID 25556 verified alive;
  archive grew from 39,239,680 to 67,817,472 bytes during this turn. Added
  Blender installer using official MPFB API with ZIP CRC, path containment and
  E:-only data/temp checks. Script not executed while archive is locked.
  Next: poll PID 25556/file completion, execute installer in E: MPFB profile,
  inspect pack metadata and choose authored outfit/hair/eyes/skin.

- `IN_PROGRESS` MPFB-SYSTEM-ASSETS-25 — found direct official files host after
  download.makehumancommunity.org DNS failure. Started 267 MB CC0 system pack
  download from https://files.makehumancommunity.org/asset_packs/makehuman_system_assets/makehuman_system_assets_cc0.zip
  into E:/CyberCity2085-3d-lab/downloads/makehuman_system_assets_cc0.zip.
  File is actively written/locked by downloader; ZIP integrity not yet verified.
  Do not restart while process is alive. Next: inspect process/file completion,
  verify ZIP integrity and asset license metadata, then install using MPFB API.

- `IN_PROGRESS` HUMAN-ASSET-PIVOT-24 — user rejects procedural human garments
  as sufficient production method; target is modern tactical character quality.
  v20 shoulder-cap attempt generated and inspected front/back: rejected as
  pointed, disconnected geometry. Preserve as pipeline study only. Priority
  shifts to authored MPFB-compatible clothes/hair, meshes and detailed PBR
  materials; procedural work remains appropriate for rigid assets.
  Official MakeHuman asset-pack index and MPFB license identify core assets
  as CC0; third-party asset licenses must be checked individually. Sources:
  https://static.makehumancommunity.org/assets/assetpacks.html and
  https://github.com/makehumancommunity/mpfb2/blob/master/LICENSE.md .
  Asset download pages returned timeout/502; no pack downloaded yet. Added
  neutral white-light review settings (not rendered yet). Next: acquire official
  system asset pack on E:, inspect authored clothes/hair/skin, integrate one
  outfit and render neutral front/profile/back plus Godot combat-scale views.

- `IN_PROGRESS` ROOK-BACK-FIT-23 — jacket ring vertices now use evaluated body
  samples at matching X/Z to place front/back panels outside the surface with
  25 mm clearance. v19 BLEND/GLB/five renders generated on E:. Back inspected:
  the large exposed back patches seen in v18 are covered. Shoulder seams remain
  open/uneven; no all-pose collision guarantee. Next: build shoulder yoke joins
  and check front/side and elbow pose for new fitting defects.

- `IN_PROGRESS` ROOK-REVIEW-22 — regenerated v18 with scalp boundary smoothing
  and inspected front/back/side. Hairline remains stepped: smoothing alone is
  insufficient. Back view reveals substantial torso/undershirt penetration
  through jacket and open shoulder joins (FAIL artistic). Blender GLB body
  bounds/53-bone roundtrip passes at 0.00000060 m error; five lightweight tests
  pass. These checks do not validate garment quality. Next: measure evaluated
  back surface and expand/rebuild jacket yoke, then rebuild scalp edge topology.

- `IN_PROGRESS` ROOK-SCALP-21 — separate short-hair scalp derived from evaluated
  body, offset 2.5 mm and weighted to head. v17 BLEND/GLB and renders generated;
  side inspected: improved coverage but visibly jagged hairline and cap-like
  silhouette. Added boundary smoothing afterward (NOT EXECUTED yet).
  Next: regenerate smoothed scalp, verify hairline from all angles, then refine
  face/eyes and jacket details. Overall character remains below artistic target.

- `DONE` PHENOTYPE-ROUNDTRIP-20 — reproducible Blender script compares the
  evaluated authoring body bounds to reimported GLB world bounds and checks
  the 53-bone armature modifier. v16 passes with 0.00000060 m max bound error.
  Godot native render/rig/toggle gates pass: 31 meshes, 31 skins, six boot parts.
  Capture inspected; this proves body extent preservation, not vertex-level
  deformation equivalence. Hair and garment artistic acceptance remain open.
  Next: short-side scalp geometry, face identity and complete multi-angle review.

- `IN_PROGRESS` PHENOTYPE-EXPORT-19 — identified raw/evaluated scalp mismatch:
  1.6674 versus 1.7182 m. Hair now projects onto evaluated scalp samples.
  Export copies preserve mixed shape-key coordinates before removing keys,
  fixing phenotype loss in the previous helper-mask export path. v16 generation
  succeeded; front inspected with hair now above scalp. Hairstyle still too
  regular and silhouette not accepted. Next: Godot comparison of v16 morphology,
  varied lock direction and short-side hair geometry.

- `IN_PROGRESS` ROOK-HAIR-18 — inspected v14 front/side: locks mostly buried
  in scalp after uniform lowering. Measured actual scalp top at 1.6674 m,
  Y extent -0.1473..0.0361 m; rebuilt paths with curved height variation and
  swept tips around these dimensions. v15 generated; front inspected. Hair
  is visible on scalp, but remains stylized parallel locks, not accepted Rook
  resemblance. Next: add short shaved-side scalp and vary lock width/direction.

- `IN_PROGRESS` ROOK-HAIR-17 — generated 16 mesh locks with copper material
  and head weights. v13 front inspected: hair floated above scalp and looked
  comb-like (FAIL artistic). Lowered lock coordinates 55 mm and regenerated
  v14 BLEND/GLB/renders on E:. v14 artistic inspection remains NOT VERIFIED;
  needs scalp fitting, varied lock directions and silhouette matching portrait.
  Next: measure scalp bounds, inspect v14 side/front and reshape the hairstyle.

- `DONE` GLB-HELPER-FIX-16 — export uses disposable mesh copies, clears
  authoring shape keys on copies, applies non-armature modifiers, retains skin
  and deletes copies afterward. First attempt failed on shape keys; corrected
  run generated v12 GLB. Native Godot rig/toggle/capture gates pass; inspected
  capture confirms skirt-like helpers and facial helper artifacts removed.
  Authoring BLEND retains original keys/modifiers. Remaining visible defects:
  feet protrude at boot edges, coarse garment fit, missing hair/identity.
  Next: hide covered body faces safely and add the referenced hairstyle.

- `IN_PROGRESS` GODOT-RENDER-15 — Godot 4.7.2 OpenGL Compatibility rendered v11
  on RTX 5070 Ti and saved godot_preview.png on E: through frame_post_draw.
  Native rig gate passed (53 bones/15 skins); injected B key handler test
  verified six boot parts hide then restore. Capture inspected; lighting and
  camera still need refinement. FAIL: body helper geometry appears in GLB
  (skirt-like surface and facial artifacts); clothing modifiers are also not
  faithfully exported. Structural PASS does not imply usable rendering. Next
  priority: bake helper masks on export copies while retaining skin modifiers.
  Model not artistically accepted. SDL reported
  a gamepad calibration error unrelated to model import. No desktop automation.
  Next: improve framing/lighting and compare posed imported skin against Blender.

- `DONE` GLB-STRUCTURE-14 — native Godot 4.7.2 validation of v11 confirms
  exactly one 53-bone skeleton and 15 distinct mesh instances, all with skin
  resources resolving to a Skeleton3D. Added --validate-rig CLI gate (exit 3
  on mismatch) and B key to toggle boot components in the experimental preview.
  Structural gate passed; interactive B key and deformation appearance remain
  NOT VERIFIED. Next: visible comparison and equipment interaction test.

- `IN_PROGRESS` ROOK-GLB-13 — repositioned lapels toward the measured front
  surface and exported visible body/garment components plus rig as GLB.
  v11 BLEND, GLB and five renders generated on E:. Godot 4.7.2 headless loads
  the dressed GLB with exit 0. Export warns that weights beyond four influences
  are truncated/normalized; posed Blender/Godot comparison remains required.
  This is technical import evidence only, not visual or animation acceptance.
  Next: inspect v11 all angles and compare skin deformation after GLB import.

- `IN_PROGRESS` ROOK-FIT-12 — measured actual body sections with bpy; torso
  is offset toward negative Y (front reaches -0.162 m at z=1.12). Corrected
  jacket center, depth and chest width instead of assuming a centered ellipse.
  v10 BLEND/five renders generated on E:; front inspected: panels now cover
  the torso more consistently. Shoulder joins, collar/lapel placement and
  undershirt boundary remain below acceptance. Next: tailor shoulder yoke and
  reposition lapels onto the measured front surface, then inspect all angles.

- `IN_PROGRESS` ROOK-TORSO-11 — replaced rendered body-cut jacket with a
  separate open quad torso (five rings, 24 segments) using transferred body
  weights and leather thickness. v9 BLEND and five previews generated on E:;
  front inspected. Boundary is regular, but upper torso/shoulder fitting and
  undershirt still require refinement. No artistic acceptance claimed.
  Next: shape armholes and shoulder yoke, replace undershirt cut boundary.

- `IN_PROGRESS` ROOK-DEFORMATION-10 — increased each sleeve from four to seven
  rings; explicit upper/lower-arm weight progression 0/0/0.15/0.5/0.85/1/1.
  v8 Blender generation completed with five renders; bent-arm preview inspected.
  Elbow transition is less abrupt, but shoulder joining and underlying torso
  remain visibly rough. Full animation and resemblance are not accepted.
  Next: replace the torso cutout with authored jacket panels and shoulder joins.

- `IN_PROGRESS` ROOK-DEFORMATION-09 — inspected v6 back/side views: open
  shoulders confirmed. Extended sleeve roots inward and increased shoulder
  radii; generated v7 views plus a 0.9-radian lower-arm pose. Pose render
  inspected: sleeves follow the arms but show angular elbows and remaining
  shoulder fit defects. This proves movement only, not accepted animation.
  Next: add elbow support loops and smooth bone-weight transitions; garment
  body topology still requires replacement rather than further cut masks.

- `IN_PROGRESS` ROOK-SLEEVES-08 — replaced jagged arm cutouts with separate
  four-ring sleeves aligned to upper/lower arm bones and transferred weights.
  v6 Blender generation and front/back/side detail renders succeeded on E:.
  Front detail inspected; shoulder joins and garment silhouette still need
  artistic refinement. Back/side review and posed elbow tests NOT VERIFIED.
  Next: inspect remaining views, fix shoulder intersections and test elbow bend.

- `IN_PROGRESS` ROOK-JACKET-07 — added separate thickened lapels and raised
  collar with body-derived skin weights. Blender CLI successfully generated
  rook_dressed_v5 BLEND and preview on E:. Front three-quarter preview inspected;
  overall garment identity remains below the reference, with sleeve fitting,
  hair and face work still open. Deformation NOT VERIFIED. Next: replace sleeve
  cuts with coherent rings and produce close-up/multi-angle views.

- `IN_PROGRESS` ROOK-BOOTS-06 — replaced cube primitives with four rounded
  cross-section rings per component. v4 BLEND and preview generated on E: and
  inspected: toe silhouette is rounder, but ankle fitting and garment overlap
  still need correction. Native bpy assertions passed: six parts, 384 vertices,
  armature modifiers and normalized single-bone weights on every vertex.
  Animation deformation and all-angle artistic acceptance remain NOT VERIFIED.
  Next: correct ankle/pant overlap and author the jacket collar and sleeves.

- `IN_PROGRESS` ROOK-BOOTS-05 — replaced anatomical foot shells with six
  separate beveled components (sole, upper, shaft on each foot), weighted to
  the actual MPFB foot bones. Blender generation succeeded; v3 preview was
  inspected. Toe anatomy is covered, but the blocky silhouette, shaft fit and
  articulation remain below acceptance. Output: rook_dressed_v3 on E:.
  Next: shape rounded toe/ankle loops and verify foot rotations and intersections.

- `IN_PROGRESS` ROOK-GARMENTS-04 — rendered and inspected the first garment
  study. Rejected its jagged jacket cut and unwanted hand geometry. Added
  boundary relaxation, restricted garment extents and separate boot shells.
  Blender execution and preview generation succeeded in rook_dressed_v2 on E:.
  Second visual inspection still rejects the result: sleeve openings remain
  irregular, boot shells retain toe anatomy, and fit is too tight. No artistic
  acceptance or animation readiness claimed. Next: replace derived sleeve and
  boot shells with authored garment topology and soles; add collar/lapels.

- `IN_PROGRESS` ROOK-GARMENTS-03 — portrait inspected; separate trousers,
  undershirt and open jacket shell derived from the preserved MPFB body with
  inherited skin weights and real thickness. Blender CLI generated
  generated/phase2/rook_dressed/rook_dressed.blend and preview on E:.
  These are fitting studies: silhouette, seams, collar, hair, boots and
  deformation remain NOT VERIFIED. Next: inspect the preview and refine the
  jacket geometry against the portrait before exporting or animating.

Continuation objective accepted: modular Rook and Raider, ten human actions,
articulated robot with five actions, industrial machine, VTOL, interactive
Godot demonstration, animated eight-direction atlases and measured performance.
All remain TODO or IN_PROGRESS until visual acceptance; optional gated AI
access does not block procedural work. Next action: inspect Rook references
and build modular clothing on the preserved MPFB body.

- `DONE` ATLAS-MULTIPART-02 — renderer now supports a multipart subject through
  camera orbit without removing its separate components. Eight 256 px frames
  and a 2048 x 256 RGBA atlas generated successfully from the procedural crate
  under E:/CyberCity2085-3d-lab/generated/phase2/crate_procedural/atlas.
  Artistic framing review remains NOT VERIFIED.

- `DONE` ENV-01 — RTX 5070 Ti, WSL2, E: capacity and ComfyUI audited.
- `DONE` BLENDER-01 — portable Blender 4.5.17 LTS downloaded to E:, checksum
  verified, CLI and bpy executed successfully.
- `DONE` LICENSE-01 — TripoSR/TRELLIS/TripoSG compatibility and license gate
  recorded; TripoSG rejected for EU use.
- `DONE` GPU-01 — isolated Python 3.11/PyTorch CUDA environment on E: and real
  Blackwell GPU computation verified.
- `DONE` PROTOTYPE-CRATE-01 — true textured mesh generated, optimized, exported
  to Blender/GLB and loaded by Godot. Artistic quality remains NOT VERIFIED.
- `DONE` PROTOTYPE-SET-01 — all six true meshes generated, Blender/GLB exports
  created and Godot-loaded. Visual review rejects all six as final art; Rook and
  Raider are not anatomically riggable.
- `BLOCKED` SPAR3D-01 — SPAR3D and Stable Fast 3D are compatible with the GPU,
  but their Stability AI Community License must be accepted on Hugging Face and
  no authenticated token is available. No gated weight was downloaded.
- `TODO` TRELLIS-01 — requires Linux, compilation and at least 16 GB VRAM; the
  RTX 5070 Ti is exactly at the documented minimum. Deferred until the lighter
  alternatives can be compared fairly.
- `DONE` MPFB-BASE-01 — MPFB 2.0.18 installed in the E: Blender profile. A
  complete 1.718 m humanoid (19,158 vertices, 18,486 faces) with the built-in
  53-bone game-engine rig and skin weights was exported to Blender/GLB, rendered
  and loaded by Godot 4.7.2. Anatomy is visually coherent.
- `DONE` HARD-SURFACE-CRATE-02 — a clean 20-part cyberpunk cargo crate was built
  procedurally from real beveled geometry and PBR/emissive materials. BLEND,
  GLB and preview are on E:; the GLB loads in Godot 4.7.2. This is materially
  cleaner and more controllable than the rejected TripoSR crate.
- `IN_PROGRESS` HUMANOID-ROOK-01 — the valid MPFB body still needs Rook's hair,
  clothing, equipment, materials and attachment points before animation work.
- `TODO` HUMANOID-ANIM-01 — idle, walk, fire, melee and death start only after
  the dressed model passes the anatomy/deformation review.
- `TODO` GODOT-VISUAL-01 — visible isometric comparison, lighting, shadows and
  performance evidence.
- `IN_PROGRESS` ATLAS-01 — eight static orientations and PNG atlas verified on
  the crate; animation strips wait for a valid rig.

Phase 1 evidence is stored under `E:\CyberCity2085-3d-lab\outputs`; Phase 2
evidence is under `E:\CyberCity2085-3d-lab\generated\phase2`. These generated
resources must not be pushed without explicit authorization.

