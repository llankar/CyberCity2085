# Experimental 2D to 3D progress

This register is separate from the principal CyberCity 2085 GOAL.

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

