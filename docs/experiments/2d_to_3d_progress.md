# Experimental 2D to 3D progress

This register is separate from the principal CyberCity 2085 GOAL.

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

