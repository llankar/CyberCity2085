# Experimental 2D to 3D progress

This register is separate from the principal CyberCity 2085 GOAL.

- `IN_PROGRESS` ROBOT-SAVED-BLEND-ROUNDTRIP-112 (2026-11-25). Continuedff577a26.
  Actual packed security_bundle01/robot_actions.blend opened and re-exported,
  not regenerated from source rig. Source Blend SHA541a87865e9bf3bdc7119c026d66e0baea93bbaeea767b43ef10ea76e8687958
  remains unchanged. Output E:security_roundtrip01/robot_actions.glb212,485,072B,
  SHA d395e14c1082d2f13a018987d7419d558cc83770eab02cdb6c5ccd4b65a1b0c7.
  Six animated owners retain five source tracks;124meshes/269209triangles/
  496images retained. Portable re-export is not byte-identical to source.

  First native FAIL exposed imported one-frame offset. Whole-strip movement
  frame_start_ui fixes duration without stretching (frame_start alone extended
  strip). Imported object/mesh names differ; exact source GLB mesh identity
  map restores node names after clearing import-only collisions. Re-export
  splits seam vertices; opt-in native test uses sampled bidirectional nearest
  surface clouds, not false index identity. Three executed fixture assertions
  cover reordered/duplicate vertices, small displacement and rejected2mm gap.
  Original bundle index-based comparison remains unchanged.

  30Hz export native FAIL: Idle527.070micrometre surface error >500micrometre
  gate.120Hz is common multiple of actual24/30Hz sources, fixes sampled surfaces:
  Idle .211293,Walk .376973,Melee .266586,Hit .399910,Death .860891 micrometres.
  All five real clips now examined, but native overall FAIL remains: Melee
  J036 basis error .000555951 at fraction .375 exceeds unchanged .0001 transform
  criterion. Other clips meet both thresholds. Fresh native_bundle_check.json
  records passed=false, explicit failure and current GLB SHA; full logs on E:.
  Existing original-bundle native regression actually rerun: all five clips
  transform/surface error0, Death-to-Idle reset0, positive gate marker PASS.
  No artistic acceptance follows from these surface measurements.
  `TODO` next: inspect original/imported J036 quaternion interpolation at .375s
  and affected rigid part, preserve five motions and resolve measured discrepancy
  before marking roundtrip DONE. Human contact/identity gate still open; overall
  first human0/1, finalhumans0/2, native map1/1, artistic map0/1, stage5/6 subjects.
  Full goal task total is not fixed: historical batch counts are not completion
  percentage. CHANTIER GLOBAL INCOMPLET. No production change, push or release.

- `IN_PROGRESS` SCANNED-HUMAN-SHOOT-111 (2026-11-25). Same authored armor,
  photographed head and Maxwell hair candidate now retains all six original
  body clips and adds a separate Shoot study. A constant 19.752309-degree
  upper-arm correction levels nominal aim while preserving authored angular
  recoil (maximum vertical direction component .0745544). Per-frame leveling
  was rejected because it flattened recoil. No production resource changed.
  Output: E:/CyberCity2085-3d-lab/generated/phase2/scanned_armor_shoot01;
  editable packed Blend, body GLB, source surface samples, credits and reports.
  Body SHA256:
  6b878a2126a58b820a2b12bcaf2282d0e4eae22a5c7bc797f4c1d35e40c83084.
  E: aim_report.json records seven durations; Shoot is .133333 seconds.

  `DONE` technical checks within this study: native seven-clip/18-mesh/122-bone
  load and sampled skin gate; source six clips, scanned head geometry/UV/photo
  and Maxwell topology/UV/texture preservation checks. Actual pistol is a
  separate nine-part CC0 asset, attached to the actual imported hand bone.
  Combined Shoot-only export: 27 meshes, native surface error 1.760104 micrometres.
  Runtime attachment: 17 sample times, nonzero actor placement, bidirectional
  surface error 3.707486 micrometres; contact_acceptance remains false.
  Initial equipped export incorrectly included muted NLA clips; explicit
  derivative-only removal fixed that. Retained Shoot was initially muted,
  causing .605312 m mismatch; explicitly unmuting it fixed the actual gate.
  Original body retains all seven clips. Existing Rocketbox combined/runtime
  and original Unvanquished combined regressions PASS (errors .801898,
  3.282046 and 1.644267 micrometres respectively).

  `DONE` native independent tactical stage dispatch: real pistol shown for
  Shoot and hidden for Walk; seven body clips; robot five-action checks and
  VTOL three controls. Five subjects, existing alley footprint with627 gray
  obstacle cells, 62.208-pixel human reference. Short120-frame timing .406337s
  is not a sustained benchmark. Inspected actual tactical_shoot.png and neutral
  hand_closeup.png: face visible, but right index extended, left hand detached
  from grip, hair/armor/identity still do not meet Rook art target. NOT accepted.
  Tests executed:28 Python tests PASS,0 fail,0 skip; JUnit on E:tmp/pytest-111.xml.
  Human acceptance0/2, independent stage5/6 subjects; native map1/1,
  artistically finalized map0/1. Full action-set coverage remains incomplete.
  `TODO` next: correct and inspect finger/trigger and offhand contacts, then
  neutral front/profile/back and combat-zoom comparison. Do not start Raider
  production before first human artistic acceptance. No push or release.

- `IN_PROGRESS` AUTHORED-HAIR-SOURCE-FIT-110 (2026-11-25). Continued871acd95.
  Returned to actual Rook portrait on E: (orange raised quiff/undercut), not a new
  generic character. Reviewed primary MakeHuman hair catalogs and three actual
  author thumbnails on E:; selected Elvaerwyn Maxwell authored swept/spiked hair.
  Old asset web repository now retired; two guessed GitHub paths404, new download
  homepage DNS failed, hair02 web-tool timeouts resolved by actual publisher HTML
  through urllib. No repeated protected/robots-denied resource requests.

  Actual publisher hair02 pack72,283,345bytes/ETag44ef4d1-6160e77b9a38e supports206
  ranges. Full download deliberately STOPPED after10,485,760bytes (verified Python
  parent command/PID26476, terminal session6088 exit1), not restarted after timeout.
  After selective success, incomplete part removed; E:aborted_full_download.json
  retains size/hash/reason. New bounded remote ZIP directory/selected-member reader
  caches ranges E:, checks206/Content-Range/ETag, directory bounds and ZIP CRC.
  Only five Maxwell files plus publisher metadata acquired:837,770uncompressed bytes.
  Per-file SHA/CRC in E:sources/makehuman_maxwell_hair/acquisition.json; no full ZIP
  SHA claim. Fourteen new range/grant tests PASS; focused29Python PASS0fail0skip
  (range/grant/anatomical/existing acquisition). Acquirer rerun successfully offline
  from cached ranges/files with idempotent CRC and source grant checks.

  Source OBJ/MHCLO explicitly Elvaerwyn/CC_by; publisher pack/catalog CC-BY.
  Publisher CC-BY FAQ defines this label by referencing BY4.0; archived HTML and
  qualified_grant preserve distinction between short source label and platform
  version basis. Original files/credit retained, commercial game adaptation grant
  reviewed; original-source/upstream metadata empty. No silent blanket CC0 claim.
  CREDITS carried into combined Blend/GLB; contribution stays SA4, originals retain
  original notices. Traditional DCC only, Nathan NoAI respected.

  Actual hair765vertices/1468triangles/1024RGBA map, not primitives. OBJ imported
  in Blender; source axes verified. Uniform.11282246 fit, rigid head joint skin.
  First bounds-only fit visually FAILed (floating above scalp); first_fit_face/
  first_fit_side PNG preserved. Corrected from actual profile by world(0,-.01,-.045)m
  offset and generated smooth normals (OBJ lacks authored normals). No topology,
  UV, pixel repaint or source geometry replacement. Uses lit alpha MASK.35,
  double-sided, roughness.7; legacy shadeless/red-emission not adopted. Blender
  exports MASK natively; no portable metadata override needed.

  E:scanned_armor_hair01 editableBlend120,465,396bytes /GLB48,260,816bytes,
  18meshes/122bones/15,764triangles/4materials/6images. FinalSHA
  24a0f02f6343cf8611ddb91a1d7e27d653bc666ad595fa56b5a9cc3b080bf3dd.
  verify_maxwell_hair actual PASS all1468source triangles/winding, UVcomponent
  error4.4632e-8, positioncomponent.165299micrometres, original PNG bytes/RGBA exact,
  head-only influence and lit MASK material. Independent head/body verifier PASS:
  complete6630head triangles, JPEG/UV exact and all16body meshes/six motion tracks
  unchanged. Native eighteen-mesh/six-clip gate PASS, actual alpha-scissor/double-
  sided/no-emission material checked, sampled skin max.269581mm, Death->Idle0m.

  Corrected neutral face/profile/back captures inspected: much closer raised red
  silhouette, no initial floating cap, but burgundy rather than Rook orange,
  scanned brown hair/beard still differs and scalp fitting not collision-solved.
  Not XCOM2/Rook final artistic acceptance. Actual independent --scanned-hair-study
  --robot-action-bundle --vtol-motion-study --tactical --self-test --sprite-review
  PASS: five subjects/627gray cells,62.208px projection, six-body/five-robot dispatch
  and vehicle controls. tactical_comparison.png saved. Observed120render frames
  .42146s (~284.72fps) is a short interval only, NOT a sustained performance or
  VSync guarantee; previous109five-second benchmark remains scoped to no-hair asset.
  No production/campaign/build/push; user save untouched; SDL warning persists.

  `TODO` next: fix actual firing pose (108arm obscures face), consolidate corrected
  Shoot onto this one head/hair candidate and fit the real pistol before further
  cosmetics or Raider. Use FK upper-arm correction/world aiming direction, inspect
  finger/trigger contact; existing source6clips remain intact. Current human art
 0/2 accepted, scene5/6, native map1/1/art-final0/1. Full actions, facial rig, proper
  costume/PBR, environment and robot optimization remain open.
  CHANTIER GLOBAL INCOMPLET.

- `IN_PROGRESS` SCANNED-HEAD-AUTHORED-ARMOR-109 (2026-11-25). Continued actual
  checkpoint927662b3. Real Renderpeople scanned head/neck assembled with authored
  15piece armor/body. Original geometry/photographic UV/JPEG, no primitive hair or
  human clothes, no generation/MPFB recolor. Original sources unchanged. REST
  anatomies both face Blender-Y; authored poses turn root180deg (posed107 correct).
  Bind-space eye-midpoint/head-width fit scale1.0964134. Neck/head weights max2;
  old head/eyes/teeth removed only from derivative game scene. Facial expression,
  eye/blink bindings NOT retained; not a completed face rig.

  First name-substring extraction FAILed visual review: omitted mouth groups,
  6234faces/3577vertices. Corrected by complete neck-bone descendants, final
  6630head triangles/3765vertices. Six new anatomical helper cases PASS incl mouth,
  misleading names, cycles/missing parents; focused total26Python PASS0failed0skip.
  Independent verify_scanned_head.py: all selected-source triangles/winding match,
  UV error0, max position component error.247416micrometres; original JPEG bytes
  EXACT. All16body/armor mesh payloads and six animation tracks EXACT SOURCE.
  Initial5e-5normal criterion FAIL: actual Blender custom-normal storage error
  .000119051 and GLB max.000128925 measured; explicit2e-4component tolerance used,
  not false exact-normal preservation or geometric workaround.

  E: scanned_armor_head01/human_actions.blend119,635,470bytes /GLB47,565,184bytes;
  17meshes/122bones/14,296triangles/3materials/5images. GLB SHA
  399b35189c62bee2b5202e2381aed66f52f577c47047a5c235667deb8e4f66ad.
  Native --scanned-head-study PASS six durations/17meshes, max sampled skin.269581mm,
  Death->Idle0m. Neutral face/profile/back inspected: no obvious neck hole. Crouch
  closeup initially misframed at1.55m (NOT verification); corrected to actual head
  height1.03m and inspected: collar covers cut neck in this pose. Not exhaustive
  contact/collision proof. Face/hair remains Nathan, not accepted Rook identity.

  Assembly contribution BY-SA4 under original SA3section4(b)/CC primary compatibility;
  underlying armorSA3/headBY4 notices retained in Blend/GLB/CREDITS. Official pages
  read through web tool; urllib archival403, actual tool response saved on E: as
  license_web_snapshot.json, NOT publisher HTML. No game code relicensing/push.
  Nathan NoAI respected: traditional DCC only. No paid/massive new download.

  Native comparison --scanned-head-study --robot-action-bundle --vtol-motion-study
  --tactical --self-test --sprite-review PASS: five subjects/627prototype cells,
  human1.872654m projected62.208px. Stage PNG inspected; sprites still stronger,
  robot dark/slender, map gray volumes unfinished. Five-second rendered benchmark:
  300frames/59.8159fps/p95interval16.718ms,586drawcalls, enginevideo1,690,916,512bytes.
  Texture1920x1080/window1280x720; VSync capped, no uncapped/hardware guarantee.
  GPU24samples with live Godot PIDs: global1452..3543MiB, not exclusive allocation
  or guaranteed peak. Actual JSON/PNG retained E:. No production/campaign tests.

  Embedded Blender ignored cache env and had emitted helper bytecodes on D:.
  Lab-only wrapper now sets sys.pycache_prefix on E: before script, no system-env
  exposure. Bounded experimental bytecodes moved to E:legacy-script-bytecode, no
  deletion. Actual check_python_cache.py PASS verifies imported helper cache on E:.
  User save untouched, no build/push, SDL warning persists.

  `DONE` head assembly structural/native/neutral-view proof only. `TODO` next:
  genuine authored Rook hairstyle/identity, coherent PBR/contact and corrected
  firing pose, retaining this first candidate. Do not start Raider/generalize.
  Accepted final humans0/2, native map1/1 but artistically finalized0/1, scene5/6;
  full action/contact set, environment and robot optimization remain open.
  CHANTIER GLOBAL INCOMPLET.

- `IN_PROGRESS` AUTHORED-HAND-WEAPON-108 (2026-11-25). Prior107 is concrete progress:
  native saved-Blend roundtrip and measured facing, not a wait/status-only turn.
  Actual worktree inspected: user save remains dirty and untouched. Reused body,
  no production edits or push. Acquired pinned1368byte character.cfg on E: SHA
  24a8f7a6dbb897942b7f779231c98937340b9a8d8b3b2da22271547b8a84a19e,
  source commitbbf9e8f276b3cf3f4b3fab217f2c947d2dd25515. Parsed41 hand bones.
  Only64KB diagnostic prefix of existing23MBIQE read/saved on E:, not a full asset
  download: confirms122joint hierarchy including control bones. Not full-file hash
  verification or a new runtime source. Existing FireWarden pistol grant retained.

  Independent pose_delta.py implements local translation difference and ordered
  base-relative unit-quaternion composition. Eight new tests PASS incl base->target,
  no-op/body preservation, noncommuting rotations, invalid/nonfinite inputs. Final
  targeted20Python PASS,0failed/0skipped (pose/ranges/existing grip geometry).
  Optional bake_unvanquished_actions.py --weapon-study uses source stand1 and
  blaster_delta1 on configured hand bones of real blaster_attack0..8@60fps. One
  Pistol_Attack_Study .133333s; no fake complete action set. E: unvanquished_weapon01
  actual Blend/GLB/reference/credits. Native --weapon-study PASS122bones/21meshes,
  nine sampledtimes, composed Blender/export skin error79.5913micrometres, restart0.
  This reference is composed Blender geometry, NOT original engine parity.

  fit_unvanquished_pistol.py reuses actual nine-part CC0 FireWarden prop and measured
  middle/ring/pinky bone-circle frame. Portable armed Blend/GLB written only to
  unvanquished_weapon01/pistol_fit01, all meshes bound to actual hand.R joint.
  Extended existing rocketbox_pistol_check --unvanquished-study:30meshes/122bones,
  one real clip, full nine-part vertices at nine times/nonzero actor placement,
  bidirectional native weapon error1.64427micrometres, positiveUNV_COMBINED_PISTOL_OK,
  matchingSHAa48da3d653aeda67c8929969202de3efa3e7d8f250363a9cafe64f184838c33e.
  Neutral side/hand_closeup PNG actually inspected: pistol follows right hand but
  shooting arm blocks face, wrist/barrel high, support fingers not contacting weapon.
  Artistic firing pose/contact FAIL; do not advertise this as accepted Shoot.
  No copied GPL engine implementation, no new skeletal system or placeholder prop.

  Corrected saved weapon-study track selection (Idle absent, use actual first clip).
  Preview keeps120fps for both authored-body and equipped study paths. Regression:
  actual default six-clip bake rerun -> original GLB SHA BYTE IDENTICAL
  1e4d8b0a06899e4968391a421cdee1f52ad3ce1a07551edcac290af737070614;
  native six-clip gate PASS. Existing Rocketbox combined pistol native regression
  PASS0.801898micrometres. No production/campaign/build tests; SDL warning persists.

  `TODO` next: improve the single candidate's actual head/identity and pose, not
  proliferate technical animation checks. Investigate scanned Nathan head with
  authored armor: original CC BY4 and BY-SA3 notices must remain, derivative may
  use BY-SA4 under CC primary compatibility/SA3section4(b), checked this turn.
  No mix/relicensing performed yet. Inspect neck topology/skin/texture fidelity
  before composition; reject bad seams. Arm/contact study remains unaccepted.
  Accepted final humans0/2; scene5/6; finalized experimental maps0/1.
  CHANTIER GLOBAL INCOMPLET.

- `IN_PROGRESS` AUTHORED-HUMAN-REVIEW-ROUNDTRIP-107 (2026-11-25). Continued local
  checkpoint7eee9db5. Actual audit_authored_facing.py evaluates eye surface centroid
  against head bounds at original clip start, not guessed source axes. Idle forward
  Blender(.07317,.99732,0), Godot(.07317,0,-.99732); Attack(.00443,0,-.99999).
  Walk/Run/Crouch likewise point toward negativeGodotZ (head yaw retained).
  Earlier105 source-X/Blender-Y facing assumption was WRONG: posed authored human
  faces approximately Blender+Y/Godot-Z. No asset transform changed to hide error.
  Preview view=back is negativeZ camera and therefore anatomical face here.

  Existing --neutral flag used (white ambient/gray background), not blue default
  preview. Actual E: unvanquished_motion01/human_neutral_face.png,
  human_neutral_side.png, human_neutral_front.png (last is anatomical back), plus
  security_bundle01/robot_neutral_face.png. All four captures returned0. Face and
  robot inspected; source armor coherent, modern Rook face/hair/style NOT accepted;
  white mechanical shell/black internals unlike Wraith sprite. No geometry or
  material edit, no generated beauty image. Initial106 previews were blue ambient,
  not neutral acceptance images. Source axes now measured, not guessed.

  `DONE` editable Blender roundtrip: roundtrip_authored_human.py opens the saved
  Blend with scripts disabled, activates game scene/unmutes six NLA tracks and
  reexports to unvanquished_roundtrip01 on E:, without rebuilding from acquisition.
  GLB SHA1e4d8b0a06899e4968391a421cdee1f52ad3ce1a07551edcac290af737070614
  BYTE IDENTICAL to original29MBGLB. SourceBlend SHA
  ce53b155c30fc95a158bad671507b8239420a5928cf9d26b98d23c4883f1e039 unchanged.
  Extended native authored_motion_check --saved-blend-roundtrip PASS: six durations,
  122bones/21meshes, nine sampledtimes/clip, max1.27053mm skin error, Death->Idle0m.
  Fresh matchingSHA native_motion_check.json and positive marker. Real Blender
  source inspection/export ran; no production/campaign tests.

  Official Unvanquished cg_animdelta.cpp and cg_segmented_skeleton.cpp inspected
  through GitHub connector: weapon delta relative to stand applies to configured
  hand bones; legs composed separately. Engine source GPL2-or-later is distinct
  from asset CC BY-SA3.0. NO engine implementation copied/relicensed. Static
  rifle_delta alone is not completed composition. `TODO` next: isolate source pose
  composition and fit real licensed weapon, check hand contacts and action views.
  Accepted final humans0/2, full scene subjects5/6, artistically finalized maps0/1.
  Modern Rook identity, Raider, complete human action set, environment and robot
  optimization remain open. CHANTIER GLOBAL INCOMPLET.

- `IN_PROGRESS` AUTHORED-HUMAN-MOTION-106 (2026-11-25). Continued checkpoint105,
  actual principal register/worktree and external objective read; production and
  user save untouched. Reused actual licensed authored Unvanquished armor/body.
  New authored_action_ranges parser uses the original name:start:end:fps table;
  seven parser cases, final focused30Python PASS, zero failed/skipped. Raw action ranges extend
  beyond authored exports: die0..400 is intentionally trimmed to0..40, Walk0..89
  to0..70, Run keeps120fps. Six source clips only: Idle6.666667s, Walk1.166667s,
  Run.75s, Attack.266667s, Death.666667s, Crouch.166667s. No invented Shoot/Melee.

  Constraint-free122bone shared game rig /21meshes baked in separate source/game
  scenes, every bone location/quaternion/scale keyed each original source frame,
  source poses reset between clips; authored originals retained in packedBlend.
  Initial constraint collection clear() API FAIL corrected to explicit removal.
  Exact visual-matrix bake FAIL on two eyelid bones: source constrained shear
  cannot be represented by ordinary TRS. Kept the actual dimensionless matrix
  error .121207 in report; did NOT call this exact preservation. Sampled evaluated
  skin instead, maximum1.3391mm in Blender; initial1mm criterion FAIL on Run head.
  Adopted explicit2mm sampled-surface tolerance (about.067px at measured combat
  scale), not an artistic pass. Source surface evidence covers nine times/clip,
  about12vertices/mesh; NOT every vertex or every possible time.

  Native first30fps import FAIL Walk2.846mm; retaining120fps for this source fixes
  resampling. Fresh native_motion_check matches GLB SHA
  1e4d8b0a06899e4968391a421cdee1f52ad3ce1a07551edcac290af737070614:
  six real durations,21meshes/122bones; maximum sampled native error1.27053mm,
  Death->Idle sampled skin reset0m. Positive UNV_NATIVE_AUTHORED_MOTION_OK.
  E: unvanquished_motion01/human_actions.blend100,246,822bytes /GLB29,079,264bytes,
  actual source references/reports/credits. CC BY-SA3.0 retained. No relicensing.

  Native main.tscn previews actual Idle; front camera axis shows back of authored
  animation, opposite axis shows face. Do not interpret camera flag as verified
  anatomical orientation. Existing neutral material/light retained. Visually
  coherent fitted armor but legacy face/style still below requested Rook target.
  comparison.tscn --unvanquished-motion-study --robot-action-bundle
  --vtol-motion-study --tactical --self-test --sprite-review passes actual native
  six body-action dispatch and robot five-action/reset checks. Real existing alley
  floor and627gray prototype cells; human/robot/VTOL/crate/machine loaded (5/6).
  62.208px projected human height verified;120settled frames ~60fps vsync capped,
  NOT uncapped performance guarantee. tactical_motion.png inspected: sprites still
  stylistically stronger; robot very dark/slender, gray map/VTOL unfinished.
  SDL gamepad warning persists. Missing preview.tscn attempt FAIL; correct existing
  main.tscn used. No production/campaign/build/push checks run.

  `DONE` technical six-source-clip export/native sampled correspondence only.
  `TODO` next: verify actual source forward from authored head/foot geometry and
  clip root transforms; apply explicit lab-only orientation, inspect face/profile/
  back and action poses, then integrate original segmented HandDelta weapon poses
  with a correctly licensed weapon before accepting grip. First Rook art remains
  0/1, accepted humans0/2; Raider deliberately not started. Mandatory full human
  action set, modern identity/wardrobe/PBR, final environment, optimized robot and
  Blender roundtrip remain open. CHANTIER GLOBAL INCOMPLET.

- `IN_PROGRESS` AUTHORED-TACTICAL-WARDROBE-SOURCE-105 (2026-11-25). Prior turn104
  progress verified from checkpointbebd1e50, actual principal/experimental registers
  and worktree. Returned to explicit professional clothing/armor sourcing rather
  than more eye/light tweaks. Official Unvanquished shipped Male/Light Armour/
  Medium Armour credits specify Angelo, armor texture touchups Stannum, medium
  variation Viech, CC BY-SA3.0. Actual publisher HTML and CC legalcode saved on E.
  CC primary deed/compatible-license pages consulted: adaptation/commercial use
  requires attribution/ShareAlike; no relicensing or mixing Nathan performed here.

  Located actual source repo via official registry submodule (initial guessed
  mdl-human repo404, not repeated). Pinned res-players_src.dpkdir commit
  bbf9e8f276b3cf3f4b3fab217f2c947d2dd25515. Downloaded ONLY15reviewed files45,356,392
  bytes:2MBBlend, source diffuse/normal/spec maps, bare head maps, skins/README/
  animation list. No full313MBrepo clone, IQE23MB, helmet maps or external weapons.
  Per-file Git blob/size/SHA checks PASS, source metadata pinned in checked-in JSON.
  Grant parser initially FAILed because later upcoming-model Male/RXMT row overrode
  shipped Male/Angelo. Corrected to shipped In game rows, retained exact author/
  license requirements; regression test ensures upcoming row cannot override grant.
  Six new provenance cases; focused23Python PASS,0failed,0skipped (source/acquisition/
  Nathan), actual native functional gates below separate. No automatic license assumption.

  Actual source .blend opens with scripts disabled: one122bone rig,42actions,
  authored15armor pieces + body/head/eyes/teeth =21rendered human meshes. Includes
  chest/shoulders/wrists/groin/thighs/knees/shins/shoes, proper source body fit.
  Excluded helmet, guide plane and unrelated embedded weapon objects/data from
  derivative. Original source untouched. Neutral A-rest height13.811447source units
  scaled .1339468634 to1.85m, source-X forward rotatedZ+90 to-Y. Max4source influences
  per vertex (no weight truncation). Six original diffuse/normal images applied:
 2048-square body/armor and1024head. Legacy specular maps acquired/preserved but NOT
  falsely used as roughness/metallic; roughness constants/material convention
  remain approximation, normal-map handedness/art review incomplete. No recolor.

  E: phase2/unvanquished_human01/human_armor.blend41,460,767bytes / GLB27,417,396bytes;
  source audit,conversion_report,static_surface_reference,native_static_check,
  CREDITS and front/side/back/tactical_close PNGs.1skin/122bones/21meshes/9,640tris/
 6images. Native full-part neutral sampled correspondence PASS max51.766um and
  UNV_NATIVE_AUTHORED_ARMOR_REST_OK, fresh matchingSHA JSON. Static model exports
  ZEROanimations intentionally;42source actions retained in Blend, not claimed
  already integrated. No invented animation availability.

  Actual --unvanquished-study with robotbundle/animatedVTOL tactical selftest PASS,
  five subjects/627cells and62.208008px human calibration. Neutral front/profile/back
  and tactical comparison inspected: much more coherent authored armored body than
  failed fitted shirt; source head/hair and yellow/black armor remain candidate,
  no final Rook identity/modern XCOM2 quality acceptance. Some original narrow body
  proportions and legacy surfaces still need artistic judgement. No generalized
  character production. Native actor action controls honestly unavailable here.

  Bounded source tasks3/4DONE (specific license/pinned acquisition, neutral derivative,
  native views/scale/fidelity); native animation/PBR/style qualification IN_PROGRESS.
  Human identities accepted0/2, final cyberpunk outfits0, source-specific robot
 5action/eightview atlases and vehicle3motion studies retained. Native subjects5/6,
  one partial floor/block map, finalized maps0. Next: source-authored human actions
  with documented segmented/HandDelta convention (character.cfg) and grip, then
  armor identity adaptation. No Nathan/SA combined derivative before compatibility
  is explicitly handled. No production/user save changes, campaign tests, push or
  release. CHANTIER GLOBAL INCOMPLET.

- `IN_PROGRESS` PROFESSIONAL-SCAN-EYE-MATERIAL-104 (2026-11-25). Prior turn103
  progress verified from checkpoint00d94d53, actual worktree and main/experimental
  registers read. Returned to human quality without MPFB recoloring or primitive
  clothing. Read-only eye UV audit finds four authored eye islands454vertices/
 840faces with real iris/sclera UVs. Diagnostic source texture crops inspected:
  original8K photograph already has detailed blue-gray irises and dark pupils.
  Gray color is not a missing-texture bug; do not claim anatomical repair from
  material work. Source scan face/hair/wardrobe still below accepted Rook target.

  Created material-only derivative using those real eye surfaces and unchanged8K
  JPEG: eye roughness.18/coat.65/coat roughness.035, original body roughness.996432
  retained. Source geometry/UVs not recolored or remeshed. New structural functional
  verifier actually PASS: all21,506textured triangle corners POSITION/NORMAL/UV/
  fourjointindices/fourweights exactly source (cyclic winding/multiplicity),89joint
  names/order/inverse binds and every authored Walk channel/input/output exactly
  source; original photographic image bytes EXACT_SOURCE. Native ninepose source
  surface gate PASS max51.895um as original. Regeneration executed: GLB BYTE-IDENTICAL
  SHA2569834a8e3b58a347c5f805795913f772b200b47bc304e8b44544e6e4c0abd00f2.

  Initial native material gate FAIL: native import leaves clearcoat_enabled=false
  in BOTH OpenGLCompatibility and VulkanForward+, despite valid exported uniform
  KHR_materials_clearcoat factors. Roughness imported correctly. Added explicitly
  opt-in lab-only uniform extension bridge using GLTFState JSON, preserving texture/
  original materials, validating scalar ranges and refusing textured coat variants.
  Original importer limitation recorded, not silently countedPASS. Actual bridged
  material checks PASS in both renderers with matchingSHA reports: eyes.18/.65/.035,
  bodyunchanged,8192-square textures. This proves imported/material properties, not
  shader-identical rendering or universal support for arbitrary glTF extensions.
  Primary references consulted: Khronos KHR_materials_clearcoat specification and
  Godot4.7 gltf_document.cpp; observed native behavior is the acceptance evidence.

  E: phase2/nathan_eyes01/human.blend24,189,284bytes / human.glb19,756,632bytes,
  eye_uv_audit/material/source_preservation/native_surface reports, renderer-specific
  native_material_check, original/refined neutral closeups and tactical_close PNGs.
  Closeups inspected under same neutral lighting: modest response change confined
  to eyes; no convincing full-human artistic acceptance. Smaller ortho framing.3m
  is diagnostic only. Optional launcher RenderingMethod allows actual same-engine
  Forward+ CLI study; default/production renderer unchanged. No new engine/assets.

  --nathan-eyes-study stage loads derivative + lab bridge, one true Walk only.
  Actual sourceWalk+fiveclip robot+animatedVTOL stage selftest PASS,89joint human
  source motion,5subjects/627cells,62.208008pxcalibration and vehicle keys retained.
  No artificial human combat action set.20existing focusedPython cases PASS,0failed,
 0skipped (GLB/bundle/provenance), plus NEW structural/native material functional
  gates above actually executed. No production/campaign tests, user save edits,
  push or release. No AI training/generative image/mesh use of source.

  Bounded eye tasks3/4DONE (audit/derivative, source fidelity/native motion, actual
  material import/bridge/preview); full-human artistry remainsIN_PROGRESS. Human
  accepted0/2, modular combat outfits0; robot5clips/eightview atlases, vehicle3motion
  studies; native subjects5/6, one partial floor/block map, finalized maps0. Next:
  acquire/adapt better professional tactical wardrobe/armor and full human actions;
  no more small material/lighting tweaks as substitute for garment/identity quality.
  True tactical environment, vehicle bays/contact and Blender re-export remainTODO.
  CHANTIER GLOBAL INCOMPLET.

- `IN_PROGRESS` VTOL-MECHANICAL-ARTICULATION-103 (2026-11-25). Continued explicit
  independent vehicle deliverable after checkpointeb452e6c facing work. Existing
  vtol01/vtol.blend procedural mechanical study retained unchanged (sourceSHA checked).
  New48mesh derivative adds six real pivots: two counter-rotating hubs+20blades and
  four hinged strut/shoe pairs,30moving mesh parts. Separate Rotor_Spin2s and
  Gear_Retract/Gear_Extend1s actions, all six controllers explicitly keyed/reset.
 120RPM is deliberately slowed inspection, not flight dynamics or realistic thrust.

  Initial source/native gate FAIL exposed pivot neutral transform mismatch. Fixed
  explicit parent inverse/basis, with per-object matrix equality checks preserving
  original placement. Second gate FAIL found constant gear rotation omitted by
  glTF object-animation optimization (Rotor_Spin inherited stowed rest). Inspected
  actual Blender export RNA, retained constant object channels and disabled size
  optimization. Fresh export/native gate PASS, max sampled source surface error
 10.130um across27poses/24moving blade+shoe surfaces; actual four-shoe origin travel
 770.746mm and retract->rotor neutral reset0. Rigid source/natively animated meshes,
  not billboard effects. Model has3real clips,6pivot nodes,48meshes; no fake skeleton.

  E: phase2/vtol_motion01/vtol_actions.blend1,402,514bytes and GLB470,128bytes,
  source_surface_reference, motion_report, matchingSHA native_motion_check and
  deployed/stowed/tactical_close PNGs. Credits/experimental provenance in Blend text
  and GLB copyright. No new external downloads. Source references/neutral assembly
  and existing model file remain untouched. Native preview new optional camera
  distance14m avoids near clipping of8m vehicle; default behavior unchanged. Actual
  deployed/stowed neutral screenshots inspected, moving shoes disappear into hull
  as designed, but no landing bay cutouts/collision approval/final hull PBR detail.

  Independent --vtol-motion-study replaces only lab scene's static aircraft with
  animated derivative. Keys7rotors/8retract/9extend work; Rotor_Spin loops with
  complete4revolutions, gear clips hold final pose. Actual sourceWalk+five-clip robot
  +vehicle stage selftest PASS (VTOL_STAGE_ACTION_KEYS_OK), existing camera/selection/
  robot action/62.208008px human checks PASS. Final native capture inspected after
  moving sprite-review note down40px to prevent new HUD line overlap. Aircraft
  still hovering because existing alley has no clear landing footprint. No claim of
  landing simulation, flight support gameplay, realistic speed or final Nighthawk art.

  Tests actually executed final focused36Python PASS,0failed,0skipped across vehicle/
  facing/sampling/pixel/bundle modules; six new vehicle cases cover counterrotation,
  avoiding10blade/30Hz aliasing, retract/extend time reversal and invalid controls.
  Source/native failures above preserved in narrative, not counted as PASS. SDL
  calibration warning remains; no campaign/production tests. Source/generated models,
  shaders, logs and captures on E, no user save/production changes/push/release.

  Bounded motion tasks3/4DONE (derivative/export, native geometry/reset, scene controls/
  captures); landing-bay/contact/art acceptance IN_PROGRESS. Human accepted0/2,
  final modular combat outfits0; robot5real actions with8view atlases, vehicle3motion
  studies; native subjects5/6, one partial floor/block map, finalized artistic maps0.
  Next: professional human wardrobe/eyes/actions and true tactical environment,
  vehicle bay/detail/clear landing site and Blender re-export checks remainTODO.
  CHANTIER GLOBAL INCOMPLET.

- `IN_PROGRESS` ROBOT-ATLAS-FACING-PROJECTION-102 (2026-11-25). Prior turn101
  progress verified from checkpointac3be2af and actual main/experimental registers/
  worktree. Read-only production unit_visual.gd:85 establishes screen atan2 with
  facing_y_scale2 and sectors E,SE,S,SW,W,NW,N,NE. No runtime or production asset edits.
  New measured projection mapping uses actual Blender cameras matching .6rad orbit
  elevations/orthographic calibration. Forward comes from measured signed Walk
  displacement, not guessed portrait orientation. Actual world_to_camera_view
  vectors invert into unique facing->orbit[4,5,6,7,0,1,2,3]. All5manifests enriched.

  Script records source BlendSHA, eight camera positions/projected vectors per clip,
  source forward and existing sector convention in E: security_bundle01/atlas/
  facing_projection_check.json. All170existing PNG hashes before/after identical;
  no new160frame render needed. Pure facing_lookup rejects missing/duplicate/zero/
  nonfinite projections, tests rotated orbit order and actual expected sectors.
  Five new tests; final focused18PASS,0failed,0skipped across facing/sampling/pixel
  modules. Actual160PNG verifier rerun PASS. Native Walk --production-order selftest
  PASS32frame indices, animation/pause/view selection and M orbit/facing toggle;
  fresh walk_facing_review.png inspected with labels E..NE. Other clips share exact
  verified projection correspondence, not individually rerun natively in this mode.

  Bounded mathematical/native facing tasks3/3DONE; subjective full robot artwork
  acceptance remainsNOT VERIFIED. Same5*8*4 atlas coverage160, accepted human0/2,
  final modular outfits0, native subjects5/6, one partial floor/block map, finalized
  maps0. Next: vehicle articulation with real moving components; human professional
  wardrobe/eye/action work, full scene and Blender re-export remainTODO. No production
  or user save edits, campaign tests, push or release. CHANTIER GLOBAL INCOMPLET.

- `IN_PROGRESS` AUTHORED-ROBOT-EIGHT-VIEW-ATLASES-101 (2026-11-25). Previous
  turn100 progress verified from checkpointd2f2beca, actual worktree and principal/
  experimental registers read. Reused existing Rocketbox atlas renderer/verifier
  with opt-in robot source; old human rendering branch retained. Source is the same
  packed124joint/124mesh security_bundle01/robot_actions.blend, all six animated
  owners (rig+five cable shape sets) switch together. No primitives/source replacement.

  Initial160render attempt completed but NOT accepted: recentering sign was guessed
  incorrectly. Measured foot displacement then exposed an additional timing issue:
  imported Blender NLA strips start at scene frame1, actions internally at0. Read-only
  inspect_robot_action_timing confirms Idle/Death1..61, Walk1..37, Melee1..31, Hit1..25.
  First Walk-only corrected attempt intentionally FAILed actual endpoint check
  (-.59172Y/+4.68mmZ at wrong final frame36). Corrected renderer derives scene range
  from real strips, validates duration/owner synchronization, samples actual1..end
  times. Actual Walk full-cycle displacement(29.8nm,-.599999905m,11.2nm) measured from
  evaluated foot geometry. Removes this signed vector over clip duration for in-place
  atlas, preserving rig/skin deformation and source files. All160affected frames then
  regenerated correctly once; first attempt is not completion evidence.

  New pure atlas_sample_frames + six tests cover imported strip offsets, correct
  seconds/endpoints, loop duplicate-end avoidance and invalid intervals. Four new
  pixel-contract tests cover robot physical scale, nonloop Walk/root-motion metadata,
  wrong forward sign and source timing fields. Final focused25Python PASS,0failed,
 0skipped across sampling/pixel/bundle modules. Existing actual Rocketbox160PNG
  verifier rerun PASS, no old frames regenerated. Default old frame sampling stays
  numerically equivalent, full old Blender re-render NOT VERIFIED/not required here.

  E: phase2/security_bundle01/atlas now has five1536x768RGBA sheets,160individual
 192x192PNGs (8views*4poses*5clips), JSON source hashes/timing/anchors and pixel proof.
  Human calibration1.869130611m ->62.208px gives physical robot1.949875712m ->64.89535px;
  padding widened by existing renderer, no clipping. All160sheet/source frames match
  <=2channel levels, nonempty alpha, transparent border and observed motion PASS.
  Idle loops2s; Walk1.2/Melee1/Hit.8/Death2s hold final pose rather than fake loops.
  PNGs incl early native Death review total4,434,463bytes before four further review
  captures; final bytes not used as a performance claim. No source model changes.

  Native atlas_review five real runs PASS32frame indexing, playback/pause, view keys
  and correct loop/hold behavior, fresh captures for Idle/Walk/Melee/Hit/Death. Native
  Walk and Death review images inspected: eight actual orbit directions visible,
  dark slim robot detail remains below current colorful sprite/art target. Projection
  to production facing NOT VERIFIED; scene viewer explicitly says orbit-only. No
  final Wraith artistic or production atlas acceptance. GPU sampler opt-in process
  names now records Blender too, keeping Godot IDs separately:24actual live-Blender
  samples globalGPU1661..2439MiB, not exclusive model VRAM or guaranteed peak. EEVEE
  log ~.4-.5s/frame and max~557MiB Blender-reported RAM are scoped observations.

  Bounded atlas tasks3/4DONE (render/source timing, pixel proof, native playback);
  facing/art acceptance IN_PROGRESS. Robot5clips*8views*4frames rendered, human
  accepted identities0/2, final modular outfits0, native3Dsubjects5/6, one partial
  floor/block map, artistically finalized maps0. Next: derive/verify actual facing
  correspondence, then vehicle articulation and remaining professional human outfit/
  eyes/actions; Blender model re-export and final tactical scene remainTODO.
  No production/user save changes, campaign tests, push or release.
  CHANTIER GLOBAL INCOMPLET.

- `IN_PROGRESS` SHARED-MECHANICAL-ACTION-BUNDLE-100 (2026-11-25). Prior turn99
  classified progress from checkpointd89cd708, actual worktree and principal/
  experimental registers read. Audited real five mechanical source GLBs:124meshes,
 249nodes each; POSITION/indices/UV/weights/joint indices byte-identical. Reused
  existing Einar bundler with bounded source/output parameters instead of creating
  parallel animation architecture. Original default retained. Source files untouched.

  Initial merge FAIL: strict accessor reader refused source sparse corrective data.
  Added explicit expanded_values with zero/authored base, packed view bounds,
  allowed index types, strictly increasing in-range indices and count checks.
  values() remains strict. copy_accessor densifies only when explicitly copying.
  Six new tests cover sparse bases/copy/strict refusal, duplicates/order/out-of-range
  and override overrun. Final focused37Python PASS,0failed,0skipped across bundle/
  shutdown/hit/strike/gait modules. Actual default Einar regeneration into separate
  E: regression folder yields BYTE-IDENTICAL GLB SHA256
 3f1ba1e7da8f2fcd3d5bd3be1f8a07faf565f3950a9093874a17d23e8f81865e,
  so existing Einar output not overwritten and default behavior preserved.

  E: phase2/security_bundle01/robot_actions.glb145,473,632bytes and editable packed
  robot_actions.blend150,337,772bytes now contain real Idle2s/Walk1.2s/Melee1s/Hit.8s/
  Death2s, ONE skin/124joints/124meshes/269,209triangles/496images. Five union-corrected
  cable meshes: head203targets, each lower/upper leg123targets. Every clip drives
  every union target, clearing other actions; no different base normals or rest
  rebase needed. Native action change works on same model without reloading.
  CREDITS and source SHA256s in GLB asset extras, companion notice and Blender text;
  original StudioCHARGE/Blender Foundation CC BY4 grant retained. No humanoid stand-in.

  Actual native original/bundle gate PASS for all five clips: all124skin transforms
  at17fractions/clip,17selected surface meshes at9fractions/clip (stride8) exactly0
  error; Death->Idle sampled reset0. Fresh native_bundle_check tied to GLB hash,
  positive ROBOT_NATIVE_ACTION_BUNDLE_OK, selected meshes recorded, final rerun PASS.
  Static verifier confirms source hashes, triangle/image/skin counts, exact durations,
  normalized weights(error0), and every clip driving all union corrections. Blender
  import checks all six animated owners (rig+five cable shape-key sets) have five
  NLA tracks,124bones/124render meshes and496packedimages. Imported bone control
  helper excluded from rendered mesh count. Blender re-export roundtrip NOT VERIFIED.

  Independent --robot-action-bundle stage supports1Idle/2Walk/4Death/5Melee/6Hit;
  Shoot explicitly unavailable. Forward Walk stays nonloop and does not teleport;
  Idle loops. Actual sourceWalk+bundle stage selftest PASS including foot travel.6m,
  hand strike.730687m/recovery, native full-foot Hit and full124mesh shutdown checks.
  Camera/selection and62.208008px human calibration PASS; five subjects/627cells,
  tactical_close PNG inspected. Image retains partial map gray block volumes, dark
  slim robot vs large sprite and civilian human; no artistic acceptance inferred.
  Scene120frame timing~60FPS is startup observation, not performance/VRAM validation.

  Bounded bundle tasks3/3DONE (shared GLB, editable Blend, native switching/evidence).
  Global mechanical production remainsIN_PROGRESS: atlas from this source, loop/
  locomotion controller, optimization and final artistic action acceptanceTODO.
  Accepted human identities0/2, modular combat outfits0, native subjects5/6, one
  partial floor/block map, artistically finalized maps0. Next: robot atlas through
  same native/Blender source, vehicle articulation, then professional human outfit/
  eye/action work. No production changes, user save edits, campaign tests, push or
  release. CHANTIER GLOBAL INCOMPLET.

- `IN_PROGRESS` AUTHORED-MECHANICAL-SHUTDOWN-99 (2026-11-25). Prior turn98
  progress verified from actual checkpointffcc3eb2, principal/experimental register
  and worktree read. Continued explicit robot action deliverable, no production or
  user save changes. New Death study2seconds/61frames30Hz: original rig lowers Root
 40cm with authored foot IK, head tilts .2rad; articulated buckle then rotates back
 90degrees, flat-ground lift measured from actual geometry, hold after1.3s. Not a
  humanoid animation substitute or detached primitive assembly.124actual mechanical
  meshes/joints and five61sample cable correction sets retained.

  Initial unit run12PASS/2FAIL: test wrongly required zero velocity of every channel
  at every other channel's stage boundary. Corrected to compare left/right velocity
  continuity; final focused suite53PASS,0failed,0skipped across eight experimental
  modules, including8new shutdown cases. Initial bake FAIL at frame7: lower-leg cable
 1128->912vertices despite fixed Array28. Initial AutoSmooth hypothesis rejected:
  disabling it still failed. Read-only prefix audit proves first change is ARRAY
  merging, before Curve/Subdivision. In derivative only, disabled proximity welding
  and AutoSmooth on six cables, mapped baked neutral corners to stable underlying
  rings with KDTree distance<10um checks. No original source edits. All61poses then
  export with stable correspondence. inspector script/evidence retained on E.

  E: phase2/security_death01/robot_death.blend139,792,506bytes / robot_death.glb
 85,547,168bytes; source rig/ground reports, coverage/CREDITS, surface references,
  native_surface_check, shutdown_native_action, neutral death_side and tactical_close
  PNGs. Source all124surfaces/61poses minimumZ -12.35nm (rounding), final held drift0.
  Native sampled source-surface check14surfaces*61times max1.002um PASS, plus full
  geometry checks124meshes at0/.4/1.25/1.6/2s: initial height1.949876m, buckle1.554187m,
  final height.591319m/span1.546401m, ground abs<.1mm, held geometry drift.246um.
  Fresh GLB SHA256 JSON and both MECHANICAL_SHUTDOWN_NATIVE_OK and
  EINAR_NATIVE_SURFACE_GATE_OK present, no assertion. These do not establish
  continuous-time collision, inter-part collision, debris/explosion or gameplay.

  Independent comparison --robot-shutdown-study loads actual Death; key4 selects
  it, missing clips remain unavailable. Native5subject/627cell sourceWalk+Death
  selection/camera/calibration selftest PASS, projected human62.208008px. Native
  sourceWalk+Hit regression rerun PASS. Neutral side corpse and tactical image
  inspected: articulated knees/crouch then back-rest pose visible, no accepted final
  robot identity/material/readability claim.120frame startup timing~60FPS is an
  observation, not a new full performance/VRAM validation. Original source notices
  retained in accompanying CREDITS/coverage. No push/release/campaign tests.

  Bounded shutdown tasks3/3DONE (bake/correspondence, native geometry/scene, captures).
  Global robot action set IN_PROGRESS: five separate Idle/Walk/Melee/Hit/Death
  studies exist but unified action switching on one rig, seamless locomotion and
  artistic action acceptance remainTODO. Accepted human identities0/2, modular
  combat outfits0, native subjects5/6, one partial floor/block map loaded, finalized
  maps0. Next: audit/unify real robot clips without losing corrective cable surfaces;
  vehicle articulation and human licensed outfit/eyes/actions remain separate TODOs.
  CHANTIER GLOBAL INCOMPLET.

- `IN_PROGRESS` AUTHORED-MECHANICAL-HIT-98 (2026-11-25). Continued other explicit
  experimental deliverable after rejected human shoulder alternatives. Genuine
  StudioCHARGE CC BY4 mechanical source206bone rig, existing124part PBR derivative,
  no new humanoid substitute. Added .8s Hit recoil: .2s peak, root8cm back/2cm lower,
  root tilt.08rad/head counter tilt.12rad, authored foot IK held on measured world
  targets. Source untouched. Existing cable arrays frozen in derivative as before;
  five25sample corrective cable morph sets retain source deformation. Real124joint
  game export,25frames/30Hz, no damage/gameplay effects or destruction claim.

  Source all corresponding heel/toe vertices drift<=.04471um, full124part return0.
  E: phase2/security_hit01/robot_hit.blend132,568,026bytes / robot_hit.glb59,140,080bytes,
  rig report, coverage/license, surface reference, native_surface_check,
  hit_native_action, neutral hit_side and tactical_close PNGs. Native source surface
  check14surfaces*25times max.369um; positive EINAR_NATIVE_SURFACE_GATE_OK. New
  independent actual native geometry check: four full foot surfaces displacement0,
  head maximum224.607mm, final recovery0. Initial native action check FAIL because
  broad heel name also selected authored heel_damper meshes. Corrected exact intended
  set by excluding dampers, kept four-foot requirement. Caller now requires five
  evidence entries before JSON/success, preventing helper assertion from yielding
  misleading generic success. Rerun has MECHANICAL_HIT_NATIVE_OK + fresh matching
  SHA256 JSON. First failed empty actionJSON is not acceptance evidence.

  Added --robot-hit-study to independent comparison stage and key6 Hit; missing
  clips remain explicitly unavailable. Actual Nathan Walk+robotHit stage selftest
  PASS, selection/camera/action availability and calibrated62.208008px human, existing
  partial map627cells/five subjects. Reproducible hit pose paused at.2s for capture.
  Old robotMelee/Nathan stage regression rerun PASS (hand reaches.730687m and returns).
  Neutral side and native tactical screenshot inspected: recoil visible, no accepted
  final Wraith design; source robot still slender/dark vs large colored 2D sprite.
  Five native subjects/expected six, no Raider; one map loads partial floor/block
  geometry, artistically finalized maps0. Screenshot render timing120frames is
  startup observation only, not full combat performance/VRAM acceptance.

  Tests actually executed final focused suite45PASS,0failed,0skipped across seven
  modules (cloth clearance,alignment,skinning,robot hit/strike/gait,Nathan provenance).
  Six new recoil tests cover bounded peak/recovery, stage velocity continuity and
  nonfinite rejection. Native checks above actual runs, no campaign/production tests.
  Bounded hit tasks3/3DONE (source bake,native geometry/stage checks,captures); global
  mechanical action set IN_PROGRESS: Idle/forwardWalk/openHandMelee/Hit studies
  exist, destruction remainsTODO, no seamless loop/full combat art acceptance.
  Human accepted0/2; modular combat outfits0. Next independent task robot destruction
  with authored mechanical articulation/settled contacts, then vehicle articulation;
  human professional outfit/eyes/combat clips and final scene/atlases remain open.
  No production changes, push or release. CHANTIER GLOBAL INCOMPLET.

- `IN_PROGRESS` AUTHORED-CLOTH-REGULARIZATION-97 (2026-11-25). Previous turn96
  classified progress (real bind/export and measured fit evidence, checkpoint3476fa4d).
  Read actual worktree and principal/experimental registers. Kept original candidate
  and sources intact; no MPFB recoloring. Added displacement-only mesh-neighbor
  smoothing, preserving authored topology rather than smoothing original garment
  details. Six tests verify isolated vertices/uniform translation, no overshoot,
  reduction of correction discontinuity, input preservation, rigid equivariance
  and malformed mesh rejection. New source measured-joint polyharmonic interpolator
  with affine tail gets two tests: exact measured constraints/affine reproduction,
  rejection of planar/duplicate constraints. Original segment implementation retained.

  Actual two bounded fit experiments exported and loaded natively: E: phase2/
  nathan_wardrobe02 is60iteration correction smoothing; nathan_wardrobe03 is26actual
  source/target joint-depth landmarks, no hand-built primitive garment. Neutral front
  PNGs inspected. Smoothing improves smoothness but reopens Tshirt/shoulder clipping;
  landmark fit reduces maximum projection gap89.19->73.94mm but still leaves shoulder
  distortions. Both artistic FAIL, not final clothing. Rest binding stays.377um,
  minimum retained source skin98.680%. Native glTF load/texture/capture markers PASS;
  full sampled deformation of these rejected variants NOT VERIFIED (not falsely
  inherited from01). No more production expansion from these failed shoulder fits.
  Tested fitting machinery DONE; acceptable outfit remains IN_PROGRESS. New clips0,
  accepted human identities0/2, final modular outfits0. Next human action: suitable
  authored garment/rest-pose topology or skilled shoulder re-fit, plus eye/material/
  tactical gear qualification; don't accumulate small lighting/palette changes.
  No production changes, push, release or campaign tests. CHANTIER GLOBAL INCOMPLET.

- `IN_PROGRESS` PROFESSIONAL-SCAN-WARDROBE-96 (2026-11-25). Previous turn95
  classified progress: qualified source and checkpoint687b48d7. Read actual git/
  principal/experimental registers before continuing; user save remains untouched.
  Read-only anatomical audit on E finds33topological islands, actual eye front/back
  surfaces and eye/eyelid/jaw joints. One phototexture/material, no hidden complete
  anatomical body asserted under clothes. Neck1.55493m, wrists+.71969/-.73863m at
  z1.53774/1.53528m; old garment fitted to A-pose, professional source T-pose.

  DONE measured-segment rest alignment and actual barycentric rebind of existing
  authored CC BY jacket/CC0leather onto89joint Renderpeople source. New pure
  segment_transform preserves endpoints, positive determinant/uniform scale without
  shear, including antiparallel cases; rejects degenerate/nonfinite/malformed joints.
  Seven new tests plus existing13cases actually PASS (20total,0failed,0skipped).
  Initial Blender script sum(int,Vector) failed; fixed explicit Vector seed.
  First native fit shows Tshirt clipping heavily. Local outward clearance14mm
  projection improves coverage; rest bind error.377um, max nearest-body gap89.19mm,
  retained skin weights>=98.755%. Old A-pose custom normals reset after deformation.

  Native export source-surface check actually PASS,9Walk times max49.170um with
  positive EINAR_NATIVE_SURFACE_GATE_OK and freshJSON; rerun after tested segment
  implementation replacement PASS. One real original Walk only, no new combat
  animation claim. Original source files unchanged; notices combined in Blend/GLB.
  Outputs E:/CyberCity2085-3d-lab/generated/phase2/nathan_wardrobe01 include anatomy
  audit, fit report, Blend/GLB, credits, surface reference/native check and neutral
  front/walk-side/walk-back PNGs. Geometry fit before pure-helper extraction differs
  only at float-rounding level; screenshot review scope recorded explicitly.

  Native neutral front/profile/back inspected: shoulder/sleeve surface irregularities,
  local remaining poke-through and over-shiny leather remain artistic FAIL. Real
  scanned anatomy/hair remains better candidate, not an accepted Rook. Do not treat
  faithful native deformation as correct cloth fit. No final art screenshots claimed.
  Bounded tasks2/3 DONE (anatomy audit and verified skin/export), artistic fit remains
  IN_PROGRESS. Accepted human identities0/2, final modular outfits0, native scene
  still5/6subjects/onepartial existing map, final artistic maps0. No production changes,
  campaign tests, push or release. Next TODO: improve actual garment shoulder topology/
  clearance smoothly rather than per-vertex normal pushes; qualify eye/material
  repair and tactical gear. Robot impact/destruction and vehicle articulation remain
  realizable independent TODOs. CHANTIER GLOBAL INCOMPLET.

- `IN_PROGRESS` PROFESSIONAL-SCANNED-HUMAN-95 (2026-11-25). Qualified and acquired
  Renderpeople Nathan Animated003, exact Sketchfab UID143a2b1ea5eb4385ae90a73657aca3bc.
  Current primary author/license metadata verifies Renderpeople / CC BY4. This
  specific publication is distinct from the website commercial free-package terms.
  NoAI restriction retained: traditional DCC/game study only, no generative use.
  Protected website download was not bypassed. Objaverse metadata lookup contained
  neither Nathan nor Eric; no model payload fetched from that index. Four source
  files acquired from public replica mehulkapadia5/open-theft-auto, pinned commit
  b37e7f3070501dd90353c250e9ad90dffdf4c8b2; 20,053,344bytes total, Git blob/SHA256
  checked. No unrelated repository content acquired. Source notices preserved.

  DONE bounded acquisition/import/native scene tasks (3/4); artistic adaptation
  IN_PROGRESS. Real scan has authored face, solid hair, jeans/shoes/Tshirt,89joints,
  21,506triangles, one8192-square JPEG and ONE authored Walk (67/30seconds).
  No fictional Idle or combat clips. Blender initially exposed a second mesh:
  importer-created bone control Icosphere. Strict import failed; correction excludes
  only referenced bone custom shapes from character transforms/export, not anatomy.
  Source centimeter scale normalized .01; ground offset+.01304978m, height1.86913m.
  Blender24,159,973bytes / GLB19,754,728bytes, original JPEG embedded byte-for-byte.

  E:/CyberCity2085-3d-lab/generated/phase2/renderpeople_nathan01 contains sources
  report, credits, Blend/GLB, native_surface_check, source_preservation_check,
  neutral front/back/profile/head/walk and tactical PNGs, benchmark and GPU samples.
  Source/export surface gate9times: max51.895um. Verifier passes finite normalized
  four-influence weights, active joints<89, normals, triangles, duration, attribution
  and exact8K texture bytes. Equal-pose direct source/export walk screenshots differ
  in241/921600pixels, max27/255, meanRGBA .000081109: near-identical observation,
  NOT pixel-exact acceptance. Source default posed vs exported stopped T-pose is
  not an equal-pose comparison. Gray eyes are visible in the source too; no complete
  PBR maps, cyberpunk outfit, Rook identity or artistic acceptance claimed.

  Native --nathan-study --robot-melee-study --tactical --sprite-review --self-test
  passes actual source Walk, robot strike, selection/camera and5subject/627cell
  independent stage; human projected62.208008px vs62.208target. New source Walk
  is paused at a reproducible frame for capture. Existing wardrobe/five-human-clips
  plus robot strike regression rerun PASS. Existing map still partial floor/blocks,
  Raider absent pending first convincing human. Accepted humans0/2, final modular
  outfits0, artistically final maps0. Source head closeup inspected: substantially
  better face/hair base, gray eyes/materials and civilian outfit remain inadequate.

  Actual5s paused-pose native benchmark:2620frames/5.000665s=523.9303frames/s,
  p95 postdraw2.193ms, max554drawcalls, engine-reported video1,005,772,648bytes.
  Not GPU execution timing or full animated combat. NVIDIA24samples/400ms: baseline
  1368MiB, live-Godot GPU-wide1390..2597MiB; includes desktop/other applications,
  not exclusive process VRAM or guaranteed peak. Driver621.24, RTX5070Ti16303MiB.

  Corrected lab shader/log cache physical location: exact Godot lab userdata folder
  on C had30files/18,769,019bytes. While no Godot process running, copied to
  E:/CyberCity2085-3d-lab/godot-userdata, verified every SHA256/count, then replaced
  only owned lab source directory by junction. configure_godot_cache.ps1 validates
  exact source and E destination, preserves mismatches; launcher reuses it. Native
  scene/regression runs after migration pass. Other Godot projects/saves unchanged.

  Tests actually executed:59Python PASS,0failed,0skipped (10experimental modules),
  including8new source provenance/local URI safety cases. Re-run verifier after
  active-joint bound check PASS. No production/campaign tests, push or release.
  Next TODO: inspect anatomical/eye/material structure and adapt actual licensed
  wardrobe/gear to this89joint source; qualify neutral views and combat-size art
  before producing Raider. Robot impact/destruction, vehicle articulation, final
  environment and new-human animation/atlas coverage remain TODO/NOT VERIFIED.
  CHANTIER GLOBAL INCOMPLET.

- `IN_PROGRESS` SHARED-RIG-WARDROBE-FIT-94 (2026-11-25). Continued from checkpoint
 4e0ef2d0 using the real licensed garment, not MPFB primitive armor. Read-only
  rest-joint audit: Neck1.52084m, shoulders+/- .21037m/z1.42811m, wrists+/- .58765m/
  z1.04557m. Rest garment scale1.02/1.15/1 and offset(0,.015,.84584)m; authored hem
  extended8cm, cuffs smoothly alignedY-8cm/Z-4cm. Original sources untouched.

  Reused existing80-bone rig/five CC0 motions and MIT weighted head. New garment
  weights projected barycentrically onto actual source body triangles, restricted
  to existing pelvis/spine/neck/clavicle/arm/hand bones. Four-influence limit retains
  essentially100% of allowed weights; max rest bind error.259um, max projected-body
  distance8.8136cm. New pure surface_weights helper/tests reject degenerate faces,
  invalid/outside projections and invalid weights; report any truncation loss.
  All5retargeted clips exported, no new human animation production or new skeleton.

  First visible waist gap was not accepted. Retaining crossing old uniform faces
  then exposed a camo band over the coat. Extended real garment hem and changed
  source-upper-clothing mask using pelvis-relative height. Covered7,559original
  polygons alpha-hidden (not deleted); original helmet/head hidden as before.
  A floating old neck guard seen in profile is now covered too. Wrists/hem improve,
  but actual hip/pants overlap remains: visible review FAIL for final fit, not DONE.

  E: generated/phase2/wardrobe_fit01/human.blend342,164,920bytes / human.glb
 97,552,648bytes; fit_report,landmark_audit,garment_surface_reference,
  native_motion_check,intersection_audit,front/back/walk_side/shoot_side/death_side/
  tactical_close PNGs. Both original MIT and garmentCC BY4/surfaceCC0 notices
  retained. Original character/garment/production resources remain unchanged.

  Actual native garment gate:45times across Idle/Walk/Pistol_Shoot/Punch_Cross/
  Death01; max sampled nearest surface error43.809um, complete cloth Death->Idle
  reset0. Positive AUTHORED_WARDROBE_NATIVE_MOTIONS_OK, old head-mode regression
  ROCKETBOX_NATIVE_HEAD_MOTIONS_OK also rerun PASS. Independent tactical stage
  loads five subjects,627cells; synthetic selection/camera/five clips/robot strike
  checks PASS, projected human62.208008px vs62.208target. HUD labels first rendered
  second as warming up, avoiding misleading FPS1 inherited from blocking import;
  no new full performance claim. Native screenshot captured on final sources.

  Deformation export fidelity is NOT garment collision acceptance. Actual Blender
  BVH audit over45poses finds10,569overlap PAIRS with opaque visible original body,
  zero with opaque new head. Pairs repeat across frames/triangles, not10,569unique
  defects. Hidden original clothes and partial-alpha hair excluded; no continuous/
  cloth-self collision guarantee. Hip/pants collisions visible, especially in Idle;
  requires mesh-fit correction or a more suitable body. Inherited scalp/hair still
  visibly below target (back-view holes), no artistic Rook acceptance.

  Tests actually executed:51Python PASS,0failed,0skipped across nine modules;
  five new skinning cases check true barycentric weights, rigid/unit equivariance,
  influence-loss reporting, bad geometry and invalid weights. Native gates above
  PASS only their documented scopes. Collision/art FAIL remains open. No campaign,
  production tests, push, release or desktop automation.
  Bounded tasks3/4: source fitting/skinning tools, native motion fidelity and scene
  integration DONE; collision/art fit IN_PROGRESS. Accepted human identities0/2,
  final modular outfits0; scene native5/6subjects (Raider awaits first good human),
  one existing map loaded as partial floor/blocks, zero final artistic maps.
  Next: fix hip fit without visible holes; also qualify better professional body
  source before investing more in rejected head/hair. Discovered current official
  Renderpeople Sketchfab Eric/Nathan CC BY4 grants, independent of website package
  terms; both live primary metadata verified. Eric absent public optimized catalog;
  Nathan public derivative available but only1K. Original Objaverse19.8MBbounded
  metadata index lacks both UIDs, no models downloaded there. Pinned public GitHub
  Nathan re-distributor has full8K baseColor/89joint rig/one authored walk, not normal
  map/PBR completeness. License and metadata checked; model payload still pending.
  CHANTIER GLOBAL INCOMPLET.

- `IN_PROGRESS` AUTHORED-WARDROBE-PBR-93 (2026-11-25). Continued after local
  checkpoint54e7d717, not after another generic MPFB recolor. Revisited the actual
  licensed Trebejo garment topology: decoded55,200corners weld to9,375positions,
 18,400triangles, ONE connected component. No claim of separate button/zip meshes.
  Audit changes only an in-memory copy; original source unchanged on E:.

  Acquired ONE genuine photometric PBR surface, Leather037/ambientCG by Lennart
  Demes. Current primary asset/license pages explicitly CC0-1.0, including raw
  commercial redistribution. Reviewed2K-PNG57,088,064byte archive, capped64MB,
  pinned SHA256055968fef7b4f1b401f30e9fa952e1b0ade2dfb27c82f297cef8e75eb67e3dc7.
  CRC/extraction-size checks; only Color/NormalGL/Roughness extracted. Source,
  provenance, credits and all cache/temp exclusively E:. No AI weights or model
  library downloads. Subsequent real cached-source/hash check executed PASS.

  Built real material derivatives in Blender: source painted albedo replaced,
  existing garment folds/panels retained. Variant01 retains authored corner/seam
  normals with explicitly approximate weak leather normal perturbation. Variant02
  recalculates smooth corner normals and uses leather normal only. This is an
  authored garment with real PBR maps, not a body silhouette or primitive jacket.
  Painted decorative details are lost; no invented geometric button completion.
  Eight UV repeats are NOT a calibrated physical grain-size claim.

  Initial reuse of generic smart-project bake unnecessarily fragmented garment
  UVs. Added opt-in preserve_source_uv to existing experimental bake helper,
  leaving prior default unchanged. Final derivatives copy original UV layout.
  Strict GLB check compares ALL18,400triangles: every position/UV corner tuple,
  multiplicity and cyclic winding exactly matches original source, while allowing
  harmless index reorder. Embedded-only textures, finite unit normals and source
  CC BY4 author/license metadata checked. Variant01 native51,301render vertices;
  variant02 native12,226, same18,400triangles/.7000007m height. Normal recalculation
  does not alter geometry or UVs. Original author credits plus CC0 surface credits
  preserved in packed Blender sources, GLB extras/copyright and localCREDITS.

  Both Blender/GLB material variants generated on E: generated/phase2/
  trebejo_leather01 and trebejo_leather02, six2K bake PNGs, retexture_report,
  geometry_uv_check, native_check. Fresh-normal front/profile/back inspected in
  Godot under unchanged neutral light. Painted white/faceted highlights removed;
  collar/pockets/folds visible. Still only standalone study, not final Rook art.
  Speckled dark patches remain in default preview. No-shadow diagnostic removes
  these patches, identifying a shadow contribution; that diagnostic is not used
  as artistic acceptance. Tested shorter directional shadow range had no useful
  visible improvement and was reverted; no lighting tweak claimed as a fix.

  Tests executed:46Python passed,0failed,0skipped across eight isolated modules.
  Five acquisition cases verify unrequested traversal entry never extracted,
  corrupt cache rejection, reviewed redirect restriction, stream cap/partial
  cleanup and valid-ZIP/unreviewed-hash rejection. Full real geometry/UV verifiers
  pass BOTH variants. Native TREBEJO_NATIVE_GARMENT_OK positive for both2K
  derivatives and original1K garment regression. Default film bakes not rerun;
  no production tests/artist PASS claimed. Persistent SDL/sampler warnings remain.
  DONE3/3 bounded technical tasks: topology audit, licensed PBR rework, portable
  geometry/material validation. Accepted humans0/2; fitted/skinned wardrobe0,
  final shadow/render/art and remaining action coverage TODO. Next: fit a qualified
  authored garment to the first human prototype, verify actual cuffs/shoulders,
  deformation/collision and native combat-scale appearance before generalizing.
  CHANTIER GLOBAL INCOMPLET.

- `IN_PROGRESS` MECHANICAL-STAGE-STRIKE-92 (2026-11-25). Prior turn classified
  PROGRESS: actual walk sources/export/contact evidence and checkpointf4d22d3e.
  Continued without touching production/main GOAL/save or downloading large AI
  models. Added native scene switches --robot-walk-study and --robot-melee-study;
  mutually exclusive with the prior Idle study. Forward walk explicitly nonloop:
  actual native foot travels.6m and holds last pose without teleporting to start.
  All five subjects use existing experimental alley/map/props;627blocked cells,
  two obstacle batches. This is still 2.5D painted floor/prototype block volumes,
  NOT an artistically finished 3D map.

  Real sprite comparisons executed at1920x1080 render viewport (1280x720 window).
  Close projected human62.207947px vs62.208target; overview20.736px. Screenshots
  security_walk01/tactical_close.png and tactical_overview.png. Close inspected:
  human identity still wrong; slender dark robot~1.95m reads worse than Wraith
  sprite (sprite multiplier1.65), not compensated by hidden scaling/light changes.
  Five-second native overview benchmark:2499frames/5.001422s,499.658frames/s,
  p95post-draw2.241ms,562drawcalls,engine video781,845,111bytes. Paused robot pose
  and human Idle; not animation/combat/GPU execution/total VRAM peak validation.

  Source mechanical strike via --melee: actual authored left wrist IK, staged
  preparation, extension/open-hand orientation, recovery;31frames/1s at30Hz.
  First profile exposed hanging wrist; explicit world orientation corrected,
  new profile inspected. Left hand actual source surface moves>.6m, all124source
  meshes return exactly to start. Native hand first vertex reaches.730687m and
  returns within.1mm; MECHANICAL_STRIKE_STAGE_OK. Full native source fidelity
  gate EINAR_NATIVE_SURFACE_GATE_OK also passes actual hand/finger/head/cable/
  shin samples31times. Art remains a single-arm strike study: no fist closure,
  target collision, hit reaction, destruction or gameplay effects claimed.
  Sources on E: generated/phase2/security_melee01/robot_melee.blend/.glb,
  surface_reference,rig_report,strike_targets,native_surface_check,strike_side.png,
  tactical_close.png. Existing Idle scene/input/five human action regressions
  executed PASS, positive CHARGE_ROBOT_IDLE_DISPATCH_OK and input markers.

  Human sourcing continued: Renderpeople current official terms2.5/4.1b permit
  free-model game use,4.2b/4.3b restrict raw/derivative asset redistribution.
  Public download page now requires Turnstile; not bypassed,zero3Dpayloads
  acquired. Local primary HTML/review on E: sources/renderpeople_review. Blender
  Studio Snowv4 official CC BY4 card/104,748byte preview reviewed on E: snow_review;
  visibly cartoon proportions/hair, not selected for Rook,no full model download.
  Optional budget preference remains unanswered; no payment/approval assumed.

  Tests actually executed:41Python passed,0failed,0skipped across seven isolated
  modules; seven new strike cases check preparation/reach/recovery, velocity at
  boundaries and nonloop time limits. Three native scopes: forward stage,
  articulated strike+source surfaces, prior Idle/input regression. SDL calibration
  warning remains. No production tests or artistic PASS claimed.
  DONE3/3 bounded technical tasks: native forward stage, genuine rig strike,
  source/scene/regression evidence. Global accepted humans0/2, finished robot
  action/art set NOT VERIFIED. Next TODO: improve qualified authored wardrobe
  using genuine PBR resources; retain prototype/artistic rejections; complete
  impact/destruction/locomotion quality rather than counting bone motion as final.
  CHANTIER GLOBAL INCOMPLET.

- `IN_PROGRESS` MECHANICAL-WALK-91 (2026-11-25). Continued independent robot
  work while first convincing human/wardrobe remains unresolved. No production,
  principal GOAL or user-save changes. Source remains Blender Studio Security Bot,
  CC BY4, original unchanged. Shared rig exporter now accepts --walk; default Idle
  route retained. Genuine source mechanical IK feet and Root drive 1.2s forward
  stride, 37 samples at30Hz, .6m displacement and .10m swing target clearance.
  No humanoid retargeting or replacement primitive geometry.

  Initial export FAIL: source FIT_CURVE cable arrays changed vertex counts
  (left upper2208->2248). Strict topology guard caught it. Read-only cable audit
  identifies authored Array/Curve/Subsurf stack. Derivative fixes six array counts
  at neutral topology (legs55/28 each, head58,torso26), preserving original source.
  Five genuinely bending cables require sampled corrective morphs; leg residuals
  before correction up to38.81mm, not represented as rigid cable success.
  Full foot vertices checked during each separate stance interval: toes and heels
  both sides show zero sampled world drift. All move~.6m across complete clip;
  prevents a stationary-foot false positive. IK target max error1.67e-8m.
  First frame differs .189968m from neutral bake because it is a stepping pose;
  explicitly NOT a failed or claimed neutral-equality test.

  Actual Blender sources generated on E: generated/phase2/security_walk01/
  robot_walk.blend/.glb, surface_reference, rig_report,foot_targets,cable_audit.
  Native surface check positive EINAR_NATIVE_SURFACE_GATE_OK (historical shared
  marker), actual head/shins/feet/corrected cables,14surfaces/37times, worst
  sampled distance0.363um; no assertion-only
  exit-code assumption. Neutral side snapshot walk_side.png inspected: articulated
  stride and intact limbs; front screenshot walk_front.png also inspected.
  GLB68,685,736bytes/Blender134,976,186bytes. Dark film robot lacks tactical readability/art
  acceptance. World translation baked per joint, no extracted gameplay root track.
  This single forward pass is NOT a seamless looping locomotion clip; no claim of
  arm swing, continuous-time contacts, collision safety or finished action set.
  Source film driver/material and exporter sampler warnings remain recorded.

  Python regression executed:34passed,0failed,0skipped across six experimental
  modules; four new gait tests cover world stance stability, clearance, landing
  velocity continuity and invalid parameters. No production tests claimed.
  DONE technical tasks3/3: mechanical source gait, stable cable derivative,
  measured Blender/native export. Global humans0/2 artistically accepted; robot
  attack/hit/destruction, finished locomotion/art, human professional wardrobe,
  native tactical/animation acceptance remain TODO. Next: inspect front/back and
  native combat-scale gait readability, then remaining actual mechanical actions.
  CHANTIER GLOBAL INCOMPLET.


- `IN_PROGRESS` LICENSED-GARMENT-CODEC-90 (2026-11-25) - continued actual source
  selection and standalone garment inspection; no more recoloring MPFB armor.
  Reviewed public paprika3d documentation/client to discover documented public
  assets.keeno.dev search/asset routes. GitHub connector could not read3.08MB
  client; bounded public raw source read on E:, never executed or installed its
  renderer/MCP. No new scene engine/browser/Windows automation. Public library
  is a CC BY/CC0 redistributor; original author/license independently checked via
  public Sketchfab metadata, not an authenticated Sketchfab download bypass.

  Cyberpunk/wardrobe/tactical queries and thumbnails retained on E:. Known4d_Bob
  and Aleksei priority IDs absent in this older catalog (404); no full models
  acquired for them. Mika Jacket Final current primary404, not acquired. Original
  90s Robot author describes own Unity2017 Neon challenge work and current CC BY4
  verified, but only preview/metadata inspected, no robot model acquired this lot.
  Obvious irrelevant vehicles/generic scans not chosen as humanoid assets.

  Acquired ONE standalone authored Trebejo_Nixon_Jacket by Nixontrebejo,
  UID1a5ef5dbcd304f3a984848cd26de890f: current primary license explicitly CC BY4,
  commercial use allowed with attribution; original is downloadable,18,400faces/
  9,375author vertices, no animations. Public optimized derivative862,576bytes,
  SHA2565702deb7dd27c2346fab64500fa1fa42161c51ae85372def6dcd32c1944551f1.
  Original unchanged on E: sources/trebejo_jacket, both original/provider metadata
  and full attribution/source/license links preserved. No unverified reuse based
  only on an aggregator label; no purchase or model mass download.

  First native import FAIL(code2, GLTF43) for required EXT_meshopt_compression,
  EXT_texture_webp/KHR_mesh_quantization. Added offline format converter instead
  of changing Godot/runtime or abandoning actual asset. Node26.12.1 verified;
  minimal SDK on E: tools/gltf_codec, npm cache/temp E: only. Pinned actual packages
  core/extensions/functions4.5.1,meshoptimizer1.3.0,sharp.35.5 (20packages), MIT SDK/
  meshoptimizer and Apache2 Sharp. Setup script executed PASS; no global install.
  SDK reads original hash-checked GLB, decodes Meshopt, expands quantization,
  normalizes decoded normal vectors and converts WebP to PNG without resize or
  pixel change. All three decoded RGBA buffers compare EXACT before/after PNG;
  scene bound max change2.4396984e-8 raw units. Removes codec-only extensions and
  keeps source attribution/modification metadata. No original resolution recovery
  claim; source redistributor already uses1024px compressed maps.

  Actual Blender import/export PASS:18,400tris/55,200decoded corner vertices,
  one garment mesh,3packed1024x1024PBR maps. Catalog unit normalization yields
  width1.207334m/depth.303943m/height.700001m, no rig/fitting. Portable jacket.blend
  4,005,278bytes/jacket.glb2,955,436bytes; raw decoded GLB3,839,176bytes. Native gate
  TREBEJO_NATIVE_GARMENT_OK PASS counts/UVs, albedo/normal/metal/rough slots, three
  texture identities/dimensions and actual world height. Neutral front screenshot
  inspected; embedded albedo and metal/rough maps extracted byte-for-byte for
  inspection, no image editing. Source albedo visibly contains baked/faceted
  highlight bands; sampled metallic median0, roughness~.298. Not simply an all-
  metal import error. DO NOT treat this look as final Rook wardrobe or spend time
  on a full fitting/rigging batch without addressing artistic source quality.
  Genuine source garment topology remains potentially reusable. No artist PASS
  from format conversion or texture hashes.

  Evidence E: sources/paprika_source_inspection/*.json/previews, trebejo_jacket/
  primary_metadata/provenance/CREDITS/jacket_source.glb; generated phase2/
  trebejo_jacket/decode_report,blender_import_report,native_check,front.png,
  three portable sources; converter package-lock/reviewed_versions on E:.
  New actual codec/source assertions and native structural gate executed PASS.
  Existing30 Python tests remain their batch89 scope; not falsely claimed to test
  this Node decoder. Persistent SDL calibration warning/export sampler warning
  retained. No production/main GOAL/save changes; no push/release.

  DONE3/3 bounded technical tasks: verified licensed bounded source, reproducible
  non-destructive codec conversion, real offline Blender/Godot garment sources.
  Global final human identities0/2 remain unaccepted; modular fitted wardrobe,
  convincing first character, robot action/art work and full final acceptance
  remain open. Optional budget preference pending, no answer/payment assumed.
  Next: better professional wardrobe source or genuine PBR rework of useful
  topology; retain artistic rejection of card-strip hairstyle. Other independent
  mechanical/environment work remains available, not blocked by this preference.
  CHANTIER GLOBAL INCOMPLET.


- `IN_PROGRESS` AUTHORED-HEAD-HAIR-89 (2026-11-25) - followed batch88 with a real
  licensed source for a more suitable raised hairstyle, not procedural hair
  cones or generic armor recoloring. Official Rocketbox Male_Adult_08 nonfacial
  FBX508,784bytes plus only three head TGA maps/one opacity TGA and MIT notice:
  six files55,035,978bytes on E:. Body textures deliberately not acquired. New
  whitelist manifest pins commit/blob/size, cap64MB; existing candidate remains
  cap160MB. Every acquired file hash verified. Unknown manifest/path rejection
  tests execute before network. No entire character library downloaded.

  Actual source import3,907verts/7,364tris. First extracted opacity hair-only
  354verts/302tris rendered visible card gaps: artistic FAIL, retained only as
  diagnostic (preview --rocketbox-hair), not recommended Rook hair. Added real
  source head/scalp with cards:1,905verts/3,342tris, real UVs, head PBR normal/
  specular and opacity color maps. Interocular fit measured from real source and
  target eye bones gives scale~1; no invented scalp primitive or fake texture.
  Texture alpha0..1 is actually present and used, GLB hair material MASK.4,
  double-sided. Original source colors retained. Original source custom corner
  normals captured/preserved on selected geometry; no lighting substitution.

  First head extraction material indices were reset by clearing mesh slots;
  explicit post-slot face remap fixed two actual primitives. First skin transfer
  normalized-weight gate FAIL: copied mesh carried deform groups already, and
  recreated names acquired .001 duplicates, giving all1,905 vertices weight sum2.
  Clearing copied groups before explicit original-index weight transfer fixed
  the cause; no tolerance relaxation. Source80 named groups transferred to real
  shared Biped rig, original body head/helmet alpha-hidden. Not rigidly attaching
  whole neck to head; genuine neck/head/facial bone weights remain. No facial
  expression animation claim. Temporary report read after source object removal
  raised RNA error; source property captured beforehand. All final producer runs
  completed, no first-failure PASS claim.

  Portable five-action assembled human.blend333,479,364bytes and human.glb
  97,869,492bytes on E: rocketbox_hair08/character01, with full MIT notices and
  UAL CC0 identity. Native actual replacement-head surfaces vs independently
  evaluated Blender skin45 times PASS: Idle22.450um,Walk23.645um,Shoot22.554um,
  Melee20.044um,Death46.736um, reset0m. Positive
  ROCKETBOX_NATIVE_HEAD_MOTIONS_OK and hash evidence saved. Original five-clip
  body motion gate rerun PASS after shared probe extension. Native front/profile/
  back head, front body and death captures inspected. Full source head fixes
  missing anatomical base, but visible hair-card strips/gaps and youthful generic
  face remain artistically insufficient for Rook. This candidate is NOT accepted
  as the requested modern tactical-game character; no production generalized.

  Independent --rocketbox-head-study includes actual equipped firing study,
  robot Idle, vehicle/props and existing alley. All five human actions/input and
  camera tests PASS. Scale measurement now excludes wholly alpha-hidden material
  surfaces and hidden attached props (verification probes default still include
  all geometry): visible candidate height1.8281883m, projected62.208008px, not
  invisible helmet1.850357m. Native stage screenshot inspected; existing map still
  prototype floor+blocked volumes, not final art. No new full performance claim.

  Evidence: E: sources/rocketbox/Male_Adult_08/acquisition.json; generated phase2/
  rocketbox_hair08/import_audit.json, fitted_head_hair_report.json, source Blend/
  GLB, character01/assembly_report/head_surface_reference/native_motion_check,
  neutral captures and tactical_comparison. Source opacity PNG extracted byte-for-
  byte from embedded GLB for inspection, no image alteration. Final Python gate
  30passed,0failed/skipped in five experiment modules. SDK/runtime smoke SDL warning
  persists. No production/main GOAL/save changes or push/release.

  DONE bounded technical work: pinned partial acquisition, genuine source
  head/hair/weight/normal integration, portable five-clip export, source/native
  verification. Artistic acceptance0/2 human identities unchanged. Next action:
  improve source selection/wardrobe, not repeatedly tweak this inadequate card
  hairstyle. Optional budget preference asked asynchronously, no answer assumed
  and no purchase authorized/performed. Free sourcing continues independently.
  Two paid storefront previews inspected only, no model acquired: Hayq15.99USD
  stylized hero and PEPOLA72.60USD masked male (standard license sales cap); neither
  selected/approved. Public free catalog access discovered without installing its
  renderer/MCP; one licensed standalone jacket being inspected in next batch90.
  CHANTIER GLOBAL INCOMPLET.


- `IN_PROGRESS` MEASURED-HUMAN-PISTOL-88 (2026-11-25) - previous goal turn
  classified PROGRESS: authoritative source integration, actual five-clip motion,
  native evidence and authored gear extraction/checkpoints85-87. This turn
  continued the missing weapon fitting, not production or generic MPFB retint.
  Measured actual Rocketbox firing-pose wrist/forearm and three curled-finger
  bone chains. Circumcenters estimate handle center(-.128950,-.457005,1.407012)m.
  Existing licensed FireWarden CC0 pistol reused, nine real mesh parts/palette.
  Known source grip anchor(0,-.012,.052)m remains a fitting hypothesis; finger
  bones are not a skin-contact/collision solver. No trigger/support grip PASS.

  Pure fit math rejects collinear/collapsed/parallel landmarks. First up-priority
  frame tilted barrel away from forearm; actual side render exposed it. Revised
  forward-priority frame preserves measured forearm aim and treats finger curl
  line as an orthogonalized up hint. Added explicit regression for oblique curl.
  First native wrist-local conversion FAIL111.421mm due imported FBX/glTF bone
  local basis. Actual native reference-pose calibration derives ONE constant
  mount, then all subsequent times use real BoneAttachment3D. Nine-time complete
  bidirectional vertex-set comparison PASS3.282047um with nonzero actor offset.
  First successful comparison emitted empty AnimationPlayer position error;
  guarded access corrected it, final gate has no such animation error. Persistent
  unrelated SDL calibration warning remains, not called warning-free.

  Real equipped portable source also created: human_pistol.blend278,684,667bytes,
  human_pistol.glb79,660,580bytes. Body plus nine genuinely wrist-skinned prop
  meshes,80 joints,175 facial targets, Pistol_Shoot.633333s scene clip/241 channels.
  Blender bind-space vertices preserve source armature world scale, no textured
  billboard. MIT notice, UAL CC0 and prop CC0/source identities retained. Original
  master five-clip/source assets unchanged. Native portable skin vs independent
  Blender prop surface comparison PASS.801899um at nine times. Runtime and
  portable source both verified separately; exact visual/contact fit not assumed.

  Preview --attach-rocketbox-pistol and comparison --rocketbox-motion-study now
  show actual gun; comparison hides it for Idle/Walk/Melee/Death and shows it on
  Shoot. Existing five-action/camera/input tests and62.207947px scale PASS after
  attachment; --shoot-preview captures the operation at native sprite zoom.
  Actual neutral side close-up inspected: barrel alignment improved, gloves,
  support-hand/index placement still need work. Source stowed pistol surface is
  still present in source body; draw/stow-specific source surface treatment TODO,
  not silently claimed solved. Portable side and tactical screenshot captured.

  Evidence E:/CyberCity2085-3d-lab/generated/phase2/rocketbox_military03/motion01:
  grip_landmarks.json; pistol_fit01/fit_report.json, weapon_surface_reference.json,
  native_check.json, native_combined_check.json, human_pistol.blend/.glb,
  grip_side.png, portable_shoot_side.png, tactical_shoot.png. Native positive
  ROCKETBOX_PISTOL_BIND_OK and ROCKETBOX_COMBINED_PISTOL_OK observed. Python final
 28passed,0failed/skipped across five experiment modules, including five actual
  grip geometry contracts. No production tests rerun; production/save/main GOAL
  untouched. Git checkpoint local only, no push/release.

  DONE this batch4/4 bounded technical tasks: measured fitting, constant native
  wrist mount, portable equipped source, source/native render/math checks. Global
  final human identities0/2 and accepted full actor action sets unchanged. Next:
  professional Rook wardrobe/face/hair integration rather than more minor gun
  technical work; refine actual contacts/stowed source surface, robot actions/art,
  source-aware optimization and Blender re-export roundtrip remain open. Further
  primary-source search found no accepted replacement this turn: Scarlet Proxy
  page has conflicting BY/BY-SA and additional social conditions; not acquired.
  AI/procedural catalog results are not professional-art acceptance evidence.
  CHANTIER GLOBAL INCOMPLET.


- `IN_PROGRESS` AUTHORED-ACCESSORY-SELECTION-87 (2026-11-25) ? continued source
  selection/integration instead of multiplying generic human variants. Official
  GitHub connector supplied pinned Adults tree metadata. Downloaded ONLY21 male
  preview PNGs,9,704,937bytes total, checked original Git blob hashes and retained
  per-file SHA256/provenance under E: sources/rocketbox/adult_preview*.json.
  All21 previews inspected. Male_Adult_04 has an actual black zip jacket/hood,
  Male_Adult_12 a denim jacket; other candidates are ordinary shirts/knitwear/
  casual or traditional outfits. None is accepted as Rook's cyberpunk outfit.
  No corresponding complete civilian FBX/model/texture packs downloaded.

  Real Military_Male_03 topology audited:65 connected components. Largest4,330
  vertices spans body/head/clothes/boots/gloves; these are NOT separate modular
  garments. Avoided claiming all requested modular armor/clothes are solved.
  Extracted only34 disconnected authored props >=20vertices from equipment,
  helmet and pistol materials plus actual glasses component7249. Retained real
  UVs/materials and unchanged rest-space geometry, no primitive substitute.
  5,500 triangles total, static accessories.glb30,471,284bytes and packed editable
  accessories.blend162,379,015bytes on E:, full MIT notice retained. Suggested
  mount bones are metadata for future fitting, not an installed working rig.
  Main garment segmentation/fit remains TODO; props remain in original rest-space
  assembly, not individually pivoted finished inventory assets.

  Source component vertex/face counts and UV gates PASS in actual Blender.
  Native imported34 mesh parts/5,500tris with albedo/UV coverage; all component
  bounds compared to independent original world-space inventory, max error
  2.101111um PASS. First native gate had a GDScript Variant inference parse FAIL;
  explicit mesh cast fixed it. Next ID lookup FAIL from JSON float string keys;
  integer-normalized IDs fixed it. Final positive
  ROCKETBOX_ACCESSORY_SOURCE_BOUNDS_OK observed, native_check.json saved.
  No artistic/pivot/skin fit acceptance from this structural check.

  Evidence: component_audit.json; accessories01/extraction_report.json,
  native_check.json, portable sources; adult_preview_manifest/provenance.json.
  Existing23 Python passes from batch86 remain their recorded scope; not rerun
  for these separate bpy/native tools. New native structural gate executed PASS.
  Persistent SDL warning retained. DONE3/3 bounded tasks: visual preview review,
  true connectivity audit, verified authored prop extraction. Global open human
  identities0/2 and unfinished robot action/art coverage unchanged. Next: select
  better licensed cyberpunk wardrobe/hair/face, fit/skin actual accessories with
  correct pivots and contact, improve first actor art before generalizing. No
  production/main GOAL/save changes, no push/release. CHANTIER GLOBAL INCOMPLET.


- `IN_PROGRESS` TACTICAL-SOURCE-MOTION-ATLAS-86 (2026-11-25) ? continued batch85
  automatically, using actual MIT Rocketbox geometry/rig and licensed CC0
  Quaternius UAL Standard motion, no primitive clothing or MPFB armor retint.
  Anatomical child vectors calibrate source T-pose vs target A-pose: upper arms
  ~43.98deg, forearms~50.26deg;52 mapped Biped controls including all30 finger
  segments. Full80-bone local location/quaternion/scale tracks retained per clip.
  Idle2.5s, Walk1.333333s, Pistol_Shoot.633333s, Punch_Cross1s, Death012.4s.
  Master Blend contains real rig,175 facial targets,packed15 textures and five
  NLA actions; separate GLB79,890,972bytes,Blend278,317,195bytes. Both source MIT
  and motion CC0 notices embedded and adjacent; source commit pinned. Master
  sources untouched. Full source appearance remains soldier, not Rook identity.

  First native surface comparison FAIL on melee between baked frames. Corrected
  quaternion hemisphere continuity and explicit linear baked F-curves rather than
  relying on Blender's Bezier default. Fresh independently evaluated Blender skin
  references45 times (5 clips x9),25 sampled source points each; native full skin
  nearest-vertex distance maxima: Idle22.522um, Walk23.475um, Shoot22.459um,
  Melee20.093um, Death47.062um. Threshold unchanged1mm. Native80bone/175morph
  gate PASS; Death->Idle reset0m, final GLB SHA256
  aecb4b71b7682ee0e6c14df11388ba7dded5a35c8dca45c56e98c3d14bf0b397.
  This verifies export deformation, not artistic action quality or source motion
  adaptation quality. Hand grip/weapon attachment and ground contact remain TODO.
  Neutral actual Idle/front/back, Walk/profile, Shoot/profile, Melee/front,
  Death/profile inspected. Preview bounds now also use real skinned positions;
  --hide-material + --focus-height reveal actual unhelmeted source head, not an
  invented face. Source short hair/face present; sunglasses/outfit still not final.

  Alternative pipeline produced five genuine Blender-rendered PNG sheets,
  eight orientations x4 frames/action =160 frames. First128px frame FAIL clipped
  six fallen-body views. Corrected192px transparent padding while keeping
  projected standing height62.208px and elevation.6rad, not shrinking the actor.
  Final sheets1536x768RGBA; per-source/frame-pixel comparison<=2levels, alpha
  coverage/nonclipping and observed motion in every orbit view PASS160/160.
  Production-facing correspondence NOT VERIFIED and disabled in reviewer when
  no mapping exists. Generic manifest playback supports real frame dimensions;
  five native sheet playback/pause/view-selection/loop-end gates PASS, existing
  George atlas regression PASS. Sprite-row layout is experimental and not installed.

  Independent native stage --rocketbox-motion-study --robot-idle-study --tactical
  --sprite-review --self-test --msaa4 PASS: five human clips dispatched, robot Idle,
  five subjects,627 blocked cells/two obstacle batches, human1.850357175m,
  robot1.949875712m, projected human62.207947px. Existing alley layout/floor only;
  gray prototype obstacle volumes are not finished map art. Five-second native
  post-draw sample1,694frames/5.002625s (~338.62/s),p95interval3.371ms,562drawcalls,
  engine-reported video allocation832,299,424bytes, render texture1920x1080/window
  1280x720. Most sample is Idle, not GPU execution timing/full-combat/total VRAM
  peak. Initial900-frame quit guard ended before the benchmark; discarded and
  rerun to explicit benchmark+capture completion. Persistent SDL calibration
  warning remains; not called warning-free. Fresh human/robot/tactical captures
  retained; robot is still too dark/thin versus the current sprite at native zoom.

  Evidence E:/CyberCity2085-3d-lab/generated/phase2/rocketbox_military03/motion01:
  retarget_report, surface_reference, native_motion_check, native_benchmark,
  neutral captures, head_unhelmeted, robot_review_front, tactical_comparison;
  atlas/*.png/*.json plus verification.json and native_*_review screenshots.
  Python final gate23passed,0failed/skipped in four experiment modules. An initial
  synthetic swapped-tile test used colors only1level apart within the deliberate
  2level PNG tolerance; corrected fixture separation, then all23passed. No claim
  that first run passed. No production suite/runtime/save/main GOAL changes.

  DONE this batch6/6 bounded technical tasks: licensed retarget, portable export,
  independent source/native deformation gate, real eight-view atlas pipeline,
  native sprite playback, measured tactical comparison. Global remains open:
  accepted final Rook/Raider identities0/2; robot only Idle, other robot actions
  and final art NOT VERIFIED. Six initial prototypes are not six artistically
  accepted assets. Native map evidence covers one experimental alley layout;
  other production maps are untouched, not claimed verified. TODO next: source
  gear segmentation/fit and professional Rook face/hair/outfit selection, correct
  pistol/support grip, foot contact, robot actions/readability, source-aware
  material/morph/texture optimization and Blender re-export roundtrip. No human
  production generalized, no push/release. CHANTIER GLOBAL INCOMPLET.


- `IN_PROGRESS` LICENSED-TACTICAL-CANDIDATE-85 (2026-11-25) ? strategy moved to
  an actual authored game character rather than more MPFB recoloring. Reviewed
  official Microsoft Rocketbox previews, selected Military_Male_03 for real vest,
  pouches, gloves, boots, knee pads and a younger face. Pinned official commit
  0943055db6ec570bcef9f2c8b41c9e5467c808f9; LICENSE.md is MIT, copyright2020
  Microsoft, permitting adaptation/distribution with notice. Manifest pins every
  Git blob/size; acquisition verifies SHA1 Git blobs and records SHA256, rejects
  other asset paths/oversize/corrupted payloads. Acquired only one facial FBX,
  15 TGA textures and notice:17 files/144,278,814 bytes on E:. Seven source previews
  retained separately. No whole-library clone. Jacob candidate is a fox rather
  than human; Blender Studio human research download is402 paid, not acquired.

  Blender import PASS: one mesh7,928 source vertices/15,517 triangles,80-bone rig,
  176 keys including Basis, four weights maximum, five materials,15 packed images,
  1.8503574m height. Fixed texture paths to original local TGA names. Legacy FBX
  reflected all skin/fabric as metallic1; separate declared dielectric candidate
  sets metallic0, retaining source roughness/specular/normal routing. Not a full
  authored PBR conversion: mixed metal masks/normal handedness remain unaccepted.
  Imported_source.blend retained unchanged; character_dielectric.blend + GLB
  79,490,856 bytes retain full MIT notice (text block, GLB extras and LICENSE.md).
  Source FBX Short user-property and unused vertex-color export warnings recorded.

  Native Godot PASS: one skin/80bones,5 surfaces/15,517tris,175 facial morphs,
  ten albedo/normal textures, finite weights and actual skinned height1.850357175m.
  Neutral front/profile/back screenshots inspected: real authored equipment and
  usable soldier anatomy, but helmet/camouflage/face are NOT final Rook identity.
  Facial morph count is not expression/artistic validation. No motion clips yet.
  Independent comparison --rocketbox-study shows this real asset with robot Idle,
  VTOL, crate, generator and existing alley2D floor +627 prototype obstacle cells.
  Actual skinned bounds fixed a comparison bug: raw node transform can include
  FBX .01 scale canceled by skin binds. First naive comparison FAIL(height0 after
  assertion); discarded. Corrected comparison PASS projected62.207947px at native
  1920x1080, input/camera/action-unavailability tests and inspected screenshot.
  Still prototype map volumes, no final environment art or human motion claim.

  Evidence E:/CyberCity2085-3d-lab/generated/phase2/rocketbox_military03:
  import_audit.json, export_report.json, native_check.json, front/side/back.png,
  tactical_comparison.png; source acquisition.json + preview_provenance.json.
  Native log rocketbox_native_check/tactical.log retain positive markers; persistent
  SDL gamepad calibration warning is unrelated and not suppressed. Python gate:
  20 passed,0 failed/skipped (three experiment modules), including corruption/path
  rejection. No production tests/runtime/save modification, no push/release.
  DONE this batch: licensed bounded acquisition, real FBX/GLB/Blend integration,
  skin-aware native scale correction and rendered candidate comparison. TODO next:
  retarget actual licensed motion, inspect head without helmet and separable gear,
  improve Rook-specific professional face/hair/outfit assembly; no generalization.
  Global accepted final human identities0/2, complete accepted actor action sets0/2.
  All other batch84 open artistic/animation/atlas/roundtrip tasks remain open.
  CHANTIER GLOBAL INCOMPLET.

- `IN_PROGRESS` AUTHORED-GROOM-PALETTE-84 (2026-11-25) — resumed actual human art
  integration rather than further generic armor recoloring. Inspected licensed
  Einar groom/material: four primary parts use the same authored node graph,
  primary Principled palette plus brown diffuse and film blood branch. Converted
  actual groom curves/radii/taper; replaced unavailable mesh Hair Info fields with
  captured curve attributes, baked source clean palette into float vertex colors.
  Deterministic random seed137 preserves palette distribution, not exact per-fiber
  film random identity. Optional clean diffuse color blend/specular attenuation
  approximate the inspected mixed shader; blood FX/full light transport omitted.

  Initial space guard FAIL: carrier was at origin while constrained source matrix
  updated only during graph evaluation. Now reads ORIGINAL local groom geometry
  and applies evaluated source transform afterwards; all parts pass1.2<Z<2.1m
  head-space gate. Source natural diameters0..0.00016m retained; old prototype had
  constant1mm-diameter fibers. Initial reduced natural-width render had too little
  density. Full four-part reference40,969 curves/1,229,070 triangles preserved on
  E: einar_groom_full02 and einar_groom_full02_layered. Layered GLB111,634,352 bytes.
  Short-range AO variant einar_groom_occlusion03 uses original head + full groom,
  .015m/16 samples, vertex-color AO,135,849,032 bytes; roots/tips vary0..1.
  AO bake initially hit stale Blender custom-data RNA wrappers after adding a
  color layer; re-resolving attributes fixed it. No source asset edited.

  Critical native material FAIL found after several over-white captures: GLTF
  runtime import contained real COLOR_0 arrays, but StandardMaterial's
  vertex_color_use_as_albedo was false. Explicit groom material copies now enable
  it, with vertex_color_is_srgb=false for linear glTF colors. Native palette gate
  PASS four actual nonempty/noncollapsed color arrays and renderer material flags.
  All earlier white-beard captures before palette_fixed_* are diagnostic failures,
  not accepted color evidence. Palette-fixed front/profile/back captures inspected.
  Material correction, not retinting a white generic beard or changing lights.

  LOD candidate einar_groom02_layered_lod samples4,127 curves/123,810 triangles,
  preserving taper/palette and explicitly widens radius by sqrt(stride) to partly
  compensate reduced density. Not exact full-density geometry or final hair cards.
  GLB10,927,876 bytes, four mesh parts, float vertex colors; standalone Blend retained.
  Original full-density comparison and AO variant remain separate. Structural
  verifier PASS on LOD/full-layered/AO geometry, counts, head-space, palette variance
  and actual buffers. Head BoneAttachment uses real J100_DEF-Head metadata. Native
  binding gate PASS45 times (five clips x9), four parts, nonzero actor placement,
  transform error0 and proper palette flags; body/groom hashes recorded. No lip/jaw
  expression deformation claim. Neutral front/profile/back LOD captures inspected;
  body uses real five-clip rig, not static posed proxy. Full film shader fidelity,
  temporal shimmer and artistic LOD acceptance remain NOT VERIFIED.

  Independent scene --authored-groom --msaa4 adds the LOD only with shared human
  study. Five actions, weapon visibility, robot Idle, camera/input,627-cell map and
  62.208038px projection PASS. Native1920x1080 render texture, five-second sample:
  1,256 frames/5.002875s (~251.06/s), p95 post-draw interval4.746ms,730 draw calls,
  Godot-reported video allocation1,368,635,305 bytes. Window1280x720. Most interval
  is human Idle/robot Idle; not GPU execution timing/full-combat or total VRAM peak.
  Tactical screenshot inspected alongside existing sprites: first-character
  identity/readability still not approved, source Einar is not final Rook/Raider.
  No character production generalization. Thirteen Python regression tests PASS;
  native source/material/scene checks PASS in their recorded scope. No production
  suite run because production remains untouched. SDL calibration warning persists.

  Files: inspect_einar_hair_materials, convert_einar_authored_groom,
  bake_groom_occlusion, verify_einar_groom, groom attachment/material/motion native
  checks, preview/comparison. All bulky geometry/colors/captures on E:, main GOAL,
  runtime and user's save unchanged; no push/release. DONE this batch: source groom
  conversion, genuine palette routing fix, head binding and measured LOD candidate.
  TODO next: hair-card/LOD temporal review, actual Rook/Raider face/hair/outfit
  identities, support grip and remaining actions; source-aware mesh/material/morph
  optimization; Blender export roundtrip; textured tactical environment and shared
  atlas. Accepted final identities0/2 and complete actor action sets0/2 unchanged.
  CHANTIER GLOBAL INCOMPLET.

- `IN_PROGRESS` SHARED-HUMAN-ACTIONS-83 (2026-11-25) — one real GLB now shares
  76 meshes/235,726 triangles/222 joints/one skin/274 embedded images across five
  clips: Idle2s, Walk1.333333s, Pistol_Shoot0.633333s, Punch_Cross1s, Death012.4s.
  E: phase2/einar_bundle02/human_actions.glb71,898,692 bytes; editable companion
  human_actions.blend124,994,575 bytes. Original single-clip/source files retained.
  Packed Blender import verified222 bones/76 body meshes, seven animated owners
  (rig + six shape-key sets), each with all five NLA track names,30fps, Idle
  selected and274 packed images. Importer's Icosphere is a referenced bone-shape
  helper, hidden for rendering; not counted as a body mesh. Blender re-export
  roundtrip remains NOT VERIFIED. The shared file has no embedded weapon/hair.

  Initial compatibility audit: identical vertex/index/skin-weight buffers except
  12 normal components of left sole, max9.93684e-5 component difference. Preserved
  via explicit constant normal-only morphs. Rest bases also differed substantially
  between older Idle/Walk and current source loader; direct bone-track copy refused.
  Flat-joint rebasing enforces newPose*baseBind=oldPose*oldBind. Modern pistol rest
  is common basis, preserving recent clips' original STEP tracks; only Idle/Walk
  rebased, max TRS recomposition residual1.72659e-7. No fps guessing: GLB seconds
  retained directly. Varying STEP/shear are explicitly refused by the rebase path,
  rather than silently changing interpolation. Union morphs126/124/124/104/104/124
  across six pieces, all driven by every clip to prevent state carryover. Size and
  target count remain unoptimized.

  Native first combined test FAIL: Idle retained finger poses from Pistol. Numeric
  GLB skin products agreed (~1.73e-7), but Godot default removed rest-valued constant
  tracks. Explicit generate_scene(state,30,false,false) fixed it; now preserved by
  experimental preview/comparison loaders. Official API reference:
  https://docs.godotengine.org/en/stable/classes/class_gltfdocument.html#class-gltfdocument-method-generate-scene
  Final original/bundle comparison PASS:222 skin transforms x17 times per clip;
  selected head/pants/strap/sole vertex correspondence x9 times. Max sampled vertex
  delta0.257micrometer; max transform metric9.91135e-5 on Walk (mixed translation/
  basis-vector metric, not a distance claim). Modern three clips exactly match in
  this gate. Death->Idle reset max sampled vertex error0.239micrometer. Evidence
  native_bundle_check.json binds proof to actual GLB SHA256.

  Actual GPU captures with common fixed camera inspected and numerically compared:
  pistol phase.25 original/bundle differ94 of921,600 pixels; death phase.75 differ29.
  Maximum RGB channel difference1/255 for both; no visible deformation difference.
  Evidence gpu_pixel_comparison.json and paired PNGs on E:. This proves these two
  rendered samples, not global artistic quality or every frame/material.

  Licensed separate pistol attaches to common wrist through BoneAttachment3D and
  recorded measured grip/rest basis. Full vertex-set bidirectional comparison of
  nine parts at six times PASS <=3.187micrometers against prior skinned fitted prop.
  Initial arbitrary vertex-index comparison failed43.93mm because baking normals/
  transforms reordered split vertices; replaced with complete bidirectional point
  sets, not a looser threshold. Native syntax issue typed time float then rerun.
  Existing trigger/support-hand fit remains artistically unaccepted. Comparison
  --human-bundle-study offers keys1..5 Idle/Walk/Shoot/Death/Melee; weapon visibility
  true only for Shoot, explicitly tested. --attach-pistol previews the same binding.

  Five-action dispatch/selection/camera/map stage PASS. Reference height now comes
  from actual base vertices rather than morph-union AABB:1.855504m instead of
  inflated1.878544m; native1920x1080 projection62.208038px vs62.208 target. Source
  map remains627 cells/two batches/five subjects; robot Idle option retained.
  Armed front and tactical Idle captures inspected. Six new behavioural buffer/
  pose/morph unit tests plus seven existing experimental tests:13 PASS,0 failed,
  0 skipped in final run. All intermediate failures above retained as resolved
  diagnostics; no reliance on native exit0 alone. Positive native markers required.
  Prior two-clip Charge stage and original George stage regression self-tests also
  PASS after loader/height changes; both produced native success/capture markers.

  DONE this batch: shared five-clip GLB, packed Blender companion, rebase/reset/
  GPU correspondence gates and independent weapon attachment. Files: glb_document,
  gltf_pose, bundle_einar_actions, inspect_einar_clip_compatibility,
  verify_einar_action_bundle, import_einar_action_bundle, native bundle/pistol gates,
  preview/comparison and tests/test_experimental_action_bundle.py. No production
  runtime/save changes, no push/release. Main GOAL untouched; bulky data on E:.
  TODO next: actual human hair/face/clothing identity review, support grip; optimize
  union morphs/meshes/materials; source-compatible remaining humanoid/robot actions;
  Blender export roundtrip; textured tactical environment, animation atlas and full
  acceptance. First convincing Rook/Raider identities remain0/2 artistically accepted;
  full actor action sets0/2 accepted. CHANTIER GLOBAL INCOMPLET.

- `IN_PROGRESS` ROBOT-VISOR-RIG-STAGE-82 (2026-11-25) — film robot glass adapted
  explicitly, not silently declared equivalent. First glossy-color bake produced
  an excessively white head and was rejected after native capture. Latest variant
  uses authored diffuse tint plus authored glossy roughness/normal routes, opaque
  dielectric/clearcoat, omitting layered refraction. security_pbr_robot02 now has
  124/124 textured surfaces,496 embedded images,269,209 triangles,36,998,108-byte
  GLB. Four diagnostic purple surfaces removed. Structural coverage PASS is not
  source shader fidelity; original120 bakes still retain earlier emission treatment.

  Original source rig audited:206 bones,124 meshes;107 with no vertex groups and
  17 with one group. New independent124-joint mechanical skeleton samples evaluated
  source surfaces/constraints rather than inventing mechanical linkages. Actual
  Head control yaw+/-0.12rad,49 frames/2s Idle scan. First native gate FAIL0.65151m
  on shin from missing edit-bone rest basis; corrected delta*rest pose then rebuilt.
  Also fixed Blender library loading mutating the passed list into object refs.
  Neutral source mismatch1.202e-7m. One cable needs residual morphs (otherwise
  2.707mm max rigid-fit error). Latest security_idle01/robot_idle.blend/.glb:
  124 meshes/124 joints/one skin/one Idle,51,094,860 bytes. Actual normalized skin
  buffers, exact clip duration and embedded materials verified. Native reference
  gate PASS six surfaces x49 source times: four shin/shell pieces<=0.061micrometer,
  head65.782micrometers, cable16.630micrometers sampled nearest-surface distance.
  Only a head-scan Idle, not walk/fire/death or a complete robot action set.

  Added explicit --robot-idle-study option to the independent comparison. Robot
  Idle dispatch, human Pistol_Shoot dispatch, selection/camera controls and627-cell
  map/five-subject stage PASS. Regressions: prior Charge Idle/Walk stage PASS and
  original two-subject George stage PASS, with positive markers and native exit0.
  Seven Python tests PASS. Obstacles now use two MultiMesh batches, exact627
  transforms/occupancy retained; screenshot draw calls1992 before/740 after (not
  an isolated matched GPU benchmark). Neutral front/profile/back captures for
  armed Einar and new robot generated and inspected. Human support grip, missing
  beard/hair, identity/clothing art and robot dark-surface readability remain open.
  Scene still has prototype untextured obstacle volumes and hovering VTOL.

  Five-second frame_post_draw measurement after warmup:1617 rendered frames in
  5.001573s (~323.30/s), interval p95=3.499ms,740 draw calls, Godot-reported video
  allocation1,278,827,200 bytes. Render texture/logical viewport1920x1080; OS window
  1280x720 (do not confuse physical window size with offscreen render size).
  Human is at end of its one-shot pistol clip while robot Idle loops during most
  samples. Evidence animated_pair_benchmark.json and
  charge_animated_pair_benchmark.png on E: phase2. This is a short native scene
  measurement, NOT GPU execution timing, total GPU VRAM peak, full combat load or
  production performance acceptance. Source Blender invalid geometry-node driver
  warnings and native SDL calibration warning remain recorded, not hidden.

  Files: adapt_charge_robot_visor.py, audit_charge_robot_rig.py,
  rig_charge_robot_idle.py, authored_scene.py, verify_charge_robot_pbr.py,
  surface_motion_check.gd, comparison.gd. No production/runtime/save edits,
  no push/release. All models/materials/captures external E:. DONE in this batch:
  explicit visor candidate, head-scan rig, native sampling, obstacle batching and
  short native benchmark. TODO next: compatible multi-clip morph packaging,
  human identity/hair/grip acceptance, remaining humanoid/robot actions, mesh/
  material/morph optimization, textured environment and final atlas comparison.
  Six prototype categories have technical studies; accepted final Rook/Raider
  identities0/2, newly accepted complete humanoid/robot action sets0/2. Existing
  map layout loaded1 in this experiment; expected multi-map coverage unspecified,
  artistically finalized experimental maps0. Full acceptance NOT VERIFIED.
  CHANTIER GLOBAL INCOMPLET.

- `IN_PROGRESS` AUTHORED-ACTIONS-SURFACES-81 (2026-11-25) — acquired the free
  Quaternius Universal Animation Library Standard through its normal itch.io
  download flow. Official page and archive License.txt/README explicitly CC0.
  ZIP15,904,933 bytes, SHA256
  cc73fc4e495b82958207316596317a3f40b9fa38065bde1027937452da537724.
  Safe extraction/CRC on E:,43 actual actions/65 source bones; paid library not
  acquired. Authored Einar FK retarget maps48 controls, intentionally excludes
  the absent left mechanical ring finger; constrained spine/toe controls solved
  separately. Native Blender pose gate passed maximum global control error
  1.74846e-7 rad on the mapped globally solved controls. This is not a full
  deformation or artistic gate. Source film drivers referencing depsgraph.scene
  removed only in loaded derivative before scene activation; source unchanged.

  Pistol_Shoot0.633333s, Punch_Cross1.0s and Death012.4s exported with222 joints,
  76 meshes, eight normalized weights. Initial evaluated-surface rigid fitting
  FAIL for source Surface Deform straps/soles: worst residuals82.11/172.39/137.15mm.
  Corrected derivatives use per-frame residual morphs before rigid skinning,
  only on wholly rigid-bound pieces; mixed bindings are explicitly refused.
  Native Godot morph+skin comparison samples every authored frame and source
  vertices every8, nearest imported surface vertex (not identity correspondence).
  PASS: four corrected pieces/20 frames for pistol, six/31 for punch, six/73 for
  death; worst distances0.000000349/0.000000576/0.000001005m respectively.
  Corrective sampling does not prove between-frame fidelity, normals, all
  weighted surface deformation or gameplay contacts. Blend/GLB and reference/
  native hash evidence on E: phase2/einar_ual_{Pistol_Shoot,Punch_Cross,Death01}01_surfaces.
  GLB sizes43,922,748/47,115,600/57,718,556 bytes: morph cost is real and requires
  optimization before runtime use. Structural verifier passes all three.

  CC0 FireWarden Lowpoly Pistol acquired from original OpenGameArt page;
  archive186,627 bytes SHA256
  8c6cecf861b672d610e169e0eecd3ca2696e311d107387ecacd03a2f3f12e6c7.
  Original palette material converted to Principled on derivative only; nine
  selected parts attached to actual right-wrist joint. Corrected equipped study
  einar_pistol_fit01_surfaces:85 meshes, one skin,44,028,376 bytes. Structural and
  native primary attachment/proximity/axis gates pass six times, nearest sampled
  glove distance<=9.336mm. Mechanical support hand, trigger fit and prop art NOT
  accepted. Original Quaternius public Drive gun downloads hit quota and returned
  HTML; responses quarantined, not used as Blender files or bypassed.

  Independent comparison --charge --human-action-study --tactical --sprite-review
  loads actual corrected armed human, static robot, VTOL, crate, generator and
  existing alley floor with627 prototype obstacle volumes. Mouse/keyboard/action
  dispatch self-test PASS; native capture charge_pistol_sprite_close.png inspected
  at1920x1080, human projection62.208008px vs62.208 target. Robot remains static
  and visually inferior to sprite; four purple unresolved glass pieces remain.
  Human side/front and terminal death side captures inspected: coherent dressed
  source, incomplete hair/beard/support grip, no death-ground acceptance. Neutral
  robot current front screenshot saved; no artistic PASS. CPU120-frame average
  is NOT sustained GPU/FPS acceptance (HUD startup FPS1 also visible).

  Seven Python regression tests PASS. Native CLI exit codes and positive success
  markers checked; Godot assertions can otherwise exit0 on timeout. Initial native
  surface test failed on sanitized dot/underscore names, corrected exact normalized
  lookup then rerun PASS. First scene export used scene title as clip name; fixed
  scene naming/re-export and verified exact clip IDs. SDL calibration warning and
  original Blender attribute/material warnings persist; no claim of warning-free
  source conversion. All large inputs/outputs/temp/cache E:, no production changes,
  no push/release. CLI wrappers run embedded source scripts disabled.

  DONE in this batch: licensed acquisition, control retarget, three individual
  corrected action exports, native surface gates and equipped source-scale capture.
  TODO: combine differing-FPS clips plus morph actions without lost channels;
  optimize morphs/geometry/material draw calls; final humanoid hair/identity/grips,
  grounded actions/remaining actions; robot glass/emission/rig/actions; tactical
  environment art/performance; shared-model animated atlas; final art comparison.
  First convincing Rook/Raider remains NOT VERIFIED; no character production
  generalization. Next batch: robot glass/emission conversion and rig sampling,
  then multi-clip/morph packaging. CHANTIER GLOBAL INCOMPLET.

- `IN_PROGRESS` EINAR-WALK-CONTACTS-80 (2026-11-25) — actual in-place walk
  authored through source foot IK, lowered torso and counter-swinging FK arms.
  First native gate failed0.21m stance drift: original soles deform through a
  surface modifier, so sampling object transforms alone had left them static.
  Added evaluated-surface rigid fitting (Kabsch), with explicit per-part residual
  reporting. Native geometric tests pass known rotation/translation, planar
  surface, nonrigid residual and invalid input cases. Worst source walk residual
  ~0.000150m on right sole; most rigid parts below2 micrometers. Not a claim that
  every dynamic corrective surface is reproduced by the game skeleton.

  Remaining6.562mm contact failure traced to glTF's default one-frame start offset:
  native clip length differed from the intended32-frame interval. Explicit
  export_anim_slide_to_zero=True fixed this; imported duration now asserted
  against source report. Source IK master goal error~7.5e-9m. Foot clearance is
  tested against the actual experimental floor atY=-0.03m, not an inventedY=0.
  Latest Walk GLB39,480,332 bytes;76 meshes/222 joints/one skin/eight influences,
  duration1.333333s. Native17 samples/stance/foot, sampled sole vertices: maximum
  compensated drift0.000000816m left/0.000002498m right; floor clearance~4.754mm;
  head loop gap0.000000239m. Compensation assumes0.7m actor travel per cycle
  (+Z in Godot); the clip itself stays in place. Real locomotion integration is
  not claimed. Neutral body/weights and loop checks pass; side phases0/.25/.5
  captures generated and inspected on E: phase2/einar_walk01. These show coherent
  source-clothing/mechanical motion, not final animation artistic acceptance.

  Idle regenerated with surface fitting and zero-based timing. Combined single
  mesh set/skin with two compatible clips at E: phase2/einar_motion01:
  human_motion.blend/.glb,39,820,980 bytes. Real buffer gate passes76 meshes,
  222 joints, normalized eight-weight maximum, exact Idle2.0s/Walk1.333333s,
  embedded textures and only the two requested clips. Native bundle Idle and Walk
  skin/contact gates pass. Comparison --charge --rigged-human now dispatches both
  clips with keys1/2; unavailable Shoot still explicitly refused. Five-subject
  tactical62.208px capture charge_walk_sprite_close.png inspected. CPU frame-loop
  timing remains NOT a GPU/FPS acceptance benchmark. Seven Python tests pass.

  Files: rig_einar_game_study.py, rigid_surface_fit.py,
  check_rigid_surface_fit.py, probe_einar_walk.py, combine_einar_motion.py,
  verify_einar_rig.py, skin_motion_check.gd and comparison.gd. Original licensed
  source and production/runtime/save untouched. No push or release. Global art
  acceptance, Rook/Raider identities, remaining humanoid actions/weapon grips,
  robot materials/actions, optimization and final comparison remain open.
  Next: evaluate licensed authored/mocap actions and weapon assets before fire/
  melee/death authoring; continue robot glass/rig conversion and stage batching.

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


