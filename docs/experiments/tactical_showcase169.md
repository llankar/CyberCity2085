# Neon Alley — démonstration de combat 3D indépendante

Livrables : `E:/CyberCity2085-3d-lab/generated/phase2/combat169/index.html`.
Vidéo `encounter_1080p30.mp4`, GIF extrait, captures `clean_*.png` sans diagnostic.

## Ce qui est effectivement exécuté

Deux agents, deux raiders et un robot conservent leurs positions après chaque
déplacement. Les cercles les suivent, les modèles s'orientent selon la trajectoire
ou la cible et la vitesse des cycles suit celle du déplacement. Les personnages,
leurs textures et leurs animations précédemment fonctionnelles sont réutilisés.

La rencontre est mise en scène dans un runtime expérimental : tirs depuis
l'arme avec tracés et flashs, impacts, réactions, perte de santé, mêlée, arcs
cyberpsychiques, destruction du robot et soins avec une vraie mallette PBR.
Le premier tir du robot est arrêté par le volume réel de la caisse. Les autres
obstacles utilisent les cellules de la carte. Le soigneur rejoint son patient
sans revenir à son point de départ, et la santé remonte pendant le soin.

La caméra tourne et zoome, puis descend ; les bâtiments masquant les agents
s'effacent progressivement. Les sons proviennent des WAV existants de CyberCity.
Le Movie Maker natif enregistre l'audio en même temps que les images ; le MP4
augmente le niveau audio de9dB, sans recréer les effets ni les décaler.

## Une seule carte vitrine

Les627cellules des obstacles sont conservées. Les neuf groupes de bâtiments
reçoivent brique/béton/métal PBR, fenêtres, portes, enseignes, cheminées,
réservoirs et panneaux de toiture. Des modèles existants de tuyaux, lampadaires,
compresseurs, câbles et rideaux métalliques complètent le décor.

Sources conservées sur E: : Poly Haven (`sources/environment169`),
Kenney City Kit Industrial, acteurs et notices déjà acquis. Le sol illustré et
les sons appartiennent aux ressources actuelles du projet. Aucun asset du jeu
de production n'est remplacé ; aucune des121autres cartes n'est convertie.

## Reproduire

```powershell
python experiments/2d_to_3d/acquire_environment169.py
& experiments/2d_to_3d/run_blender.ps1 -Script blender/showcase_environment169.py
& experiments/2d_to_3d/run_movie169.ps1
python experiments/2d_to_3d/package_combat169.py
```

Pour voir la scène sans capturer :
```powershell
& experiments/2d_to_3d/run_godot.ps1 -Scene res://combat169.tscn -RenderingMethod gl_compatibility
```

## Vérifications limitées à cette livraison

Capture native1920×1080,902images à30fps, soit30,07secondes de vidéo. Rendu
hors temps réel en environ60secondes, pas une mesure de capture temps réel.
Le journal Godot mesure environ7–10msGPU/image dans cette scène ; cela ne
garantit pas les performances d'une campagne. Le fichier possède une vraie
piste audio stéréo48kHz. Le contrôle ciblé confirme1tir bloqué,143occultations
de bâtiment/image et la santé finale cohérente. Les captures tir/PSI/soins ont
été inspectées. Aucun test de campagne ni ancien test de rig relancé.

## Limites restantes

La rencontre est scénarisée, sans IA de campagne ni modification des règles
tactiques de production. L'architecture et les transitions restent celles d'un
prototype ; certains volumes et panneaux sont encore simples. Les contacts du
soin et les fragments de destruction peuvent être améliorés. Le travail Hunyuan
couleur continue séparément et ne bloque pas la démonstration existante.

## Variante de façades du26novembre

Les composants architecturaux Poly Haven sont assemblés dans une variante
séparée, `showcase170` :204panneaux, fenêtres/vitres, portes et corniches,
avec conduits de toiture. Les neuf emprises de bâtiments et627cellules sont
conservées. Un premier aperçu natif a révélé les fenêtres absentes (composants
séparés des panneaux) ; les inserts ont été ajoutés et le nouvel aperçu inspecté.
La vidéo169 demeure conservée. Native170 delivery DONE: 902 frames,1920x1080/30fps, stereo audio,30.07s. Offline rendering72s; cover blocked1shot,144building/frame occlusions. Clean0254/0750 inspected. Repeated roofs, mixed prop styles and medical contact remain open.

```powershell
& experiments/2d_to_3d/run_blender.ps1 -Script blender/showcase_environment169.py -ScriptArguments @('--authored-facades')
& experiments/2d_to_3d/run_movie169.ps1 -Architectural
python experiments/2d_to_3d/package_combat169.py --folder E:/CyberCity2085-3d-lab/generated/phase2/combat170
```

CHANTIER GLOBAL INCOMPLET : cette livraison montre le combat, sans prétendre
que la migration3D ou la qualité artistique finale sont acceptées.

## Refined stage171

The optional `--refined-stage` Blender pass writes `showcase171`, preserving
169/170. It keeps authored PBR vents and compressors, removes the mismatched
white low-detail roof kit props, and mixes dark concrete with blue metal roofs.
The source PBR images remain intact; the derived roof colour image stays on E:.
`run_movie169.ps1 -Refined` selects that environment and writes `combat171`.
The patient turns toward the medic and the real medical case appears during
treatment. Hand-to-patient anatomical contact is still not artistically accepted.

Initial171 movie had no occlusion: removing the tall props reduced the building
bounds. The packaging check rejected it. A lower final camera demonstrates actual
building occlusion; failed and overbright roof takes are retained separately.
No campaign or production runtime is involved.

## Treatment contact173

`contact173.tscn` extends the retained encounter. A local arm IK adjustment follows
the patient's real left upper arm after treatment begins. The kneeling animation
and actual medical case remain in use; no full-body animation is replaced.
The close-up at `E:/CyberCity2085-3d-lab/generated/phase2/contact173/treatment.png`
was rendered natively and inspected, with visible hand contact and no major
deformation in that pose. Full-sequence transition acceptance remains separate.

```powershell
& experiments/2d_to_3d/run_godot.ps1 -Scene res://contact173.tscn -QuitAfter 200 -RenderingMethod gl_compatibility -SceneArguments @('--refined-stage','--contact-preview')
& experiments/2d_to_3d/run_movie169.ps1 -MedicalContact
python experiments/2d_to_3d/package_combat169.py --folder E:/CyberCity2085-3d-lab/generated/phase2/contact173_final
```

The final treatment variant also topples and grounds the destroyed robot body,
retaining the authored Death clip, fragments and sound. Earlier captures remain
in contact173; the final movie is written separately to contact173_final.

Native final capture executed:902frames1920x1080/30fps,69s offline rendering,
166building/frame occlusions and one shot blocked by cover. Packaging guards
PASS; clean0630 wreck and medical close-up inspected. Video/gallery on E: in
contact173_final. This is staged visual evidence, not production AI acceptance.

## Urban facade variant174

`--city-details` selects three real urban wall/window pairs alongside industrial
facades and mounts neon labels on fascia panels. Same627cells/9building groups.
Native902frame FullHD30 movie and package guards PASS; clean0254 inspected.
Reproduce with builder `--city-details`, `run_movie169.ps1 -CityDetails`, then
package_combat169.py --folder E:/CyberCity2085-3d-lab/generated/phase2/city174.
This preserves the treatment/contact/collapse variant and all previous outputs.

## VTOL finish178

The retained procedural aircraft now uses the existing local blue-metal PBR on
its main hull, rotor housings, fins and shoes.32inward lateral hull faces were
corrected. Eight cockpit panes follow actual fuselage faces; frames, fasteners,
louvres and aft turbine hardware add90components. Fins have physical thickness.
Front/rear neutral views were inspected; the original135 files remain intact.

Existing rotor/gear pivot transforms are preserved. Native Godot imports all
three clips, and Rotor_Spin loops in this variant. The first nonloop movie is
retained separately. Final native902frame1080p30 capture/package passed with
168building/frame occlusions and1blockedshot. Clean0254 was inspected in scene.
The69second capture is offline rendering, not a real-time FPS claim. Native gear
playback, landing clearance and final vehicle artistic acceptance remain open.

```powershell
& experiments/2d_to_3d/run_blender.ps1 -Script blender/finish_vtol178.py
& experiments/2d_to_3d/run_movie169.ps1 -VehicleFinish
python experiments/2d_to_3d/package_combat169.py --folder E:/CyberCity2085-3d-lab/generated/phase2/vehicle178
```

Vehicle sources/textures/views live in generated/phase2/vtol178; the full six-unit
movie, GIF and gallery live in vehicle178. No production/campaign/AI/download or
push work was performed. CHANTIER GLOBAL INCOMPLET.

## Impact finish 179 — 2026-11-26

Independent `-ImpactFinish` take retains the six-unit cast, city174 and VTOL178.
`combat_effects179.gd` adds short muzzle/impact/destruction lights, procedural
soft smoke, a wreck scorch and floor bounce for existing debris. Existing sounds,
tracers and encounter timing are reused. No production changes.

Executed two native takes; retained the first subtle take on E:. Final capture:
902 frames, 1920x1080 at fixed 30 fps, 71 seconds offline rendering. Encounter
records one cover-blocked shot, 168 building/frame occlusions and health
[100,0,0,100,76,100]. Inspected final impact_0603 and clean_0630: flash lighting
is visible; smoke remains too subtle at tactical zoom and is not artistically
accepted. Native capture is not a real-time performance measurement.

Outputs: E:/CyberCity2085-3d-lab/generated/phase2/impact179/.
Next: improve the encounter composition and visible destruction silhouette;
retain current characters and avoid further technical loading/rig proofs.
Global visual acceptance remains open.
`nPackaging executed successfully: MP4 with recorded audio, GIF, gallery and delivery.json.

## Wreck 180 — 2026-11-26

Added combat_effects180.gd and -WreckFinish; all previous takes retained.
Fragments now copy active source surface materials and remain eight seconds.
A denser elevated plume is visible above cover in inspected clean_0630.png.
The collapsed robot remains partly hidden and its silhouette is not yet clearly
identifiable; no complete destruction-art acceptance is claimed.
Executed native902frames1920x1080/30fps,71seconds offline. Existing encounter
retains one blocked shot,168occlusions and six-unit health state. No campaign,
production changes or push. Next: staging the robot's fall in a readable free
area without weakening the real cover demonstration. This is visual staging,
not a change to production tactical rules.

## Fall 181 — 2026-11-26 (IN_PROGRESS)

Previous turn progressed with native180 media. New -FallFinish staging moves
only the dying robot continuously1.25m toward the open alley over1.1seconds,
synchronized with its toppling. The earlier cover-blocked shot stays unchanged.
First0630 inspected: wreck moves out from cover, though close to the medic.
First native run exposed an error missed in180: source-material iteration also
matched spark CylinderMeshes. Corrected by matching fragment.mesh to an actual
source mesh before copying its surface materials. Previous180 material claim
was therefore not fully verified; first181 AVI retained as first_material_error.
Final native take in progress; no PASS until final log/media inspected.

Final181:902 native frames1920x1080/30fps,71seconds offline. Log confirms six
matched fragments and no surface-index/script errors; existing SDL gamepad
calibration warning persists. Final0630 inspected: wreck now outside crate,
but its bright material and proximity to medic still weaken readability.
Material-copy bug corrected, not a claim that all robot surfaces are dark.
Next substantial priority: presentation/composition and a shorter combat montage;
stop further tiny wreck iterations. Global artistic quality remains IN_PROGRESS.

## Presentation 182 — camera composition (IN_PROGRESS)

A separate presentation182 scene reuses the entire181 encounter and cast.
Extracted base update_camera hook preserves old camera behavior by default.
New camera smoothly frames gunfight, melee, PSI and treatment, with tactical
returns. Building fade uses actual updated camera. First native902frame take
finished and0460/0750 inspected: closer action/medical contact clearly visible.
Its zero occlusion events meant it did not demonstrate building fade, so the
first take is retained as first_no_occlusion. A final low orbit is now rendered
for that requirement; no acceptance claim until final output inspected.

Final182 executed902frames FullHD30,75seconds offline. One blocked shot,
61building/frame occlusion events, six-unit health state preserved. No script,
parse or surface-index errors in final log (existing SDL calibration warning).
Final low-orbit frame extracted at29.8s and inspected: foreground building
transparency reveals agents. First close melee/treatment captures inspected.
Camera composition delivered; scene still has repeated facade modules, bright
robot wreck and some close-up character/contact limitations. Global artistic
acceptance remains open; next focus is environment identity/material harmony,
not more isolated rig/loading checks.

## District 183 material pass (IN_PROGRESS)

Derives showcase174 without replacing it. Source district_finish183.py creates
18 material variants across114slots and three muted cool/warm palettes from
actual local diffuse textures; roughness/normal maps retained. Glass/signs/props
excluded by object scope. Two repeated industrial valves reduced to65percent.
No wall footprint changes. Source Blender/GLB/textures on E:showcase183.
Independent -DistrictFinish uses presentation182 camera with all retained cast
and encounter effects. Native capture in progress; material edits alone are
not proof of final artistic improvement. Repeated facade modules remain.

Final183 native902framesFullHD30 completed. One blocked shot,61occlusions,
health unchanged. No script/parse/surface-index errors found in native log.
Inspected0030/0254: smaller valves improve proportion; material variation is
modest, bright facade panels and repeated modules remain. Do not claim a major
architectural improvement from color changes alone. Packaging executed for
video/audio/GIF/gallery; environment GLB/packedBLEND and derived textures local.
Next: replace selected repeated facade bays with genuinely distinct assemblies
using existing authored kit parts; avoid another tint-only iteration.

## Facade assemblies 184 (IN_PROGRESS)

Actual local factory kit supplies three double-garage bays/shutters replacing
selected window bays. Existing fire-escape kit supplies eight rooftop platform/
railing parts. Source facade_assemblies184.py derives showcase183, preserving
all old assets. Independent -FacadeAssemblies scene uses existing182 camera.
First0030 inspected: a roof walkway overlapped HVAC, so first take retained.
Placement revised to require a3x3 roof patch and clearance from existing roof
prop origins. Final native capture in progress; bounds-origin clearance alone
is not artistic proof of no intersection. No production/campaign/download/push.

Final184:902FullHD30frames, one blocked shot,61occlusions, same six-unit health.
No script/parse/surface-index errors found in final native log. Final0030
inspected: visible foreground walkway separated from HVAC. Three garages are
exported but this front view does not provide sufficient artistic review of
those chosen bays; their appearance remains NOT VERIFIED. All eight walkway
parts are not individually artistically accepted from this single view.
Next: select facade bays visible to the encounter camera and review architectural
silhouettes from that camera; avoid claiming completion from export counts.

## Visible bays 185 (IN_PROGRESS)

Same184 generator adds --visible-bays185 and outputs a separate showcase185.
Bays selected by outward normal toward the main camera, with source-relative
insert offsets and shared frame/door scale. First0030 shows new foreground
bays, but retained solid wall backing occludes recessed shutters. First take
retained. Corrected depth placement keeps shutter back surface outward of the
opaque backing without cutting map walls. Final native render in progress.
No production/campaign changes. A visible facade replacement is the criterion,
not the number of exported objects.

Final185:0030 inspected, two shutter leaves clearly visible on foreground
facade, and another upper-edge assembly visible. Not all three bays fully
reviewed. Clear metal remains too bright and depth projection needs artistic
refinement; no final environment acceptance. Native902FullHD30frames, one
blockedshot/61occlusions, health unchanged. No script/parse/surface errors found
in final log. Separate sourceGLB/packedBLEND/textures in E:showcase185 and media
in E:visible185. Next substantial environment action: unify facade/roof material
response under scene lighting and compose building identities as a whole,
not more count-based minor additions.

## Material direction 186 (IN_PROGRESS)

Independent materials186 scene initially adjusts97 actual Godot surfaces:
charcoal garage shutters, less metallic roofs, calmer wall panels, preserved
textures/normals/emissive signs. First0030 inspected: doors noticeably darker.
Not satisfied with a runtime-only deliverable, added persist_materials186.py
(GLB chunk/material rewrite, unchanged geometry/binary textures) and Blender
import/pack script. E:showcase186 contains GLB and123MBpackedBLEND. First baked
capture was too light: runtime sRGB color factors differ from glTF linear
factors. Corrected sRGB/linear conversion; final native take in progress.
Both runtime-only and linear-mismatch AVI/PNG retained. Scene loads bakedGLB
directly with --baked186, avoiding duplicate material application. No production.

Final186 bakedGLB capture inspected0030: charcoal shutters match intended
scene direction after linear conversion, with textures retained. Native902frames
FullHD30, one blockedshot/61occlusions, health unchanged. Final log has no
script/parse/surface-index errors (existing SDL warning). Source geometry and
embedded binary textures preserved;97 primitive material copies edited. Blender
packed source123MB exists on E:. Final video uses baked source, not live tint.
Gallery includes same-camera185/186 comparison and corrected source links.
Architectural repetition and contrast against illustrated floor still prevent
final scene-art acceptance. Next: assess the whole combat sequence and sprite
comparison at real scale, prioritize substantial visible discrepancies over
more isolated material variants.

## Scale comparison 187 — 2026-11-26

New native scale187.gd/.tscn compares actual retained Rook, neural177, Raider166
and robot137 to actual first idle atlas tiles. Human21/41/62px nominal1.8m;
robot2.4m nominal/1.65sprite multiplier. Neutral light, fixed pose only. First
run used absent Raider alias; corrected to actual Rocketbox_Idle. Final native
capture executed and inspected: humans retain readable identity at62px, very
small at21px; robot markedly thinner than sprite and Raider dark. Not an
animation acceptance or exact skinned bounding-height audit. No campaign.
Next: robot silhouette using existing authored shell meshes and unchanged clips,
not new human recoloring or more facade microdetails.

## Robot shell trial 188 — NOT PROMOTED

Robot_shell188.py thickens18 authored shell meshes, preserving original binary
prefix, skins and animation JSON (five retained clips). Native fixed-pose187
comparison with --robot188 executed and inspected. Some purple panel identity
appears, but mass increase is modest and dark color worsens small-scale contrast.
Not promoted into the tactical scene; no full encounter/movie/animation review
was run for this rejected trial. Avoid iterating many tiny shell/tint changes.
Current retained full video stays materials186. Next viable direction is a
fundamentally broader authored/previously generated robot body, reusing known
rig/motions when practical; do not claim silhouette parity from mesh counts.
E:scale187/index.html joins native comparison, actual186 movie and rejected188
board/source. Prototype global art acceptance remains open, no production edits.

## Painted robot189 — first actual articulation, 2026-11-26

Reused existing paint168/robot_official painted_material.glb and its prior
neutral/scale evidence; no new generation, downloads or licence work. Added a
14-bone mechanical rig and spatial segment weights, reusing robot_gait.gait and
robot_shutdown.shutdown_pose. Five exported clips Idle/Walk/Melee/Hit/Death.
First rigid weighting produced visible elbow stretches; retained first_rigid
GLB/BLEND/AVI/stills. One joint-transition blend pass and reduced strike angle
made a second actual native movie. Significant elbow distortion persists: FAIL
for adoption, not a completed animation set. Plate separation/joint assignment
must be improved; no dozens of pose or engine proofs.

Executed: Blender export five actions; native Godot330frames1920x1080/30fps,
11seconds/22seconds offline; packaging checks exact frame/rate/dimensions and
encodes MP4/GIF. Native scale187 --robot189 and final comparison inspected.
Inspected Walk075/Melee135/Death285: broader silhouette, textured model intact,
but elbow stretches and gait/plate contacts need correction. Small-scale board
shows materially better body mass vs skinny137. Native logs contain no script
or parse errors (preexisting SDL calibration warning). No combat encounter
replacement or full campaign/motion acceptance was run. Preview has no audio.

Outputs E:phase2/robot189: real robot_actions.glb/.blend, actions_1080p30.mp4,
actions.gif, pose captures, native comparison, index.html. Source scripts
rig_painted_robot189.py, robot189.gd/.tscn, run_robot189_movie.ps1,
package_robot189.py; scale187 accepts separate --robot189. Retained full tactical
movie remains materials186. Next: rigid plate/joint separation at elbow and
only then trial this robot in the independent encounter. Global IN_PROGRESS.

## Robot190/191 and encounter192 — IN_PROGRESS

190 rigid face ownership plus four joint housings: first build failed because
mesh replacement removed vertex-group definitions; fixed. Actual native330frame
preview inspected135: severe holes/jagged seams, artistic FAIL, not adopted.
No production/campaign changes. Failed build/log and all190 outputs retained.

191 corrected189 anatomical classification: first spatial-priority attempt
fixed hand stretching but dragged thigh plates. Kept first_spatial sources/AVI.
Then used mesh connectivity below shoulder cut1.32m, welding UV-seam positions
only for graph matching. Two real forearm islands distinguish hands from legs:
819/929unique points,10491original UV-split vertices. Assigned these islands to
arm bones before leg classification. Native330frame preview executed; final
Walk075 and Melee135 inspected: prior long elbow ribbon/thigh wing absent.
Not a microscopic all-frame proof; remaining plate/gait quality open. Five
clips retained. E:robot191 GLB/BLEND/MP4/GIF/index, silent action study.

192 separate full encounter loads191 robot and baked186 environment, retained
cast/effects/sounds/camera. First902frame capture: one blockedshot,61occlusions,
health preserved;0254 inspected, broader robot visibly integrated.0630 exposed
old137 topple/grounding conflicting with new Death. First_double_fall take kept.
Old contact173 correction now explicitly skipped only for --painted192; travel
hook applies knockback before rendering, retaining new rig's falling animation.
Cannon firing returns to Idle with short recoil instead of inherited melee
swing; muzzle uses shoulder location. Final native capture in progress.

192 second capture still shows an incorrect elevated/disassembled-looking
settled body in0750, despite a correct isolated191Death285. Not adopted; do not
confuse preserved health/event counts with art acceptance. New source limits
cannon recoil rotation writes to before death and records one fall-state trace.
Third capture in progress; earlier second_rotation_conflict AVI/PNG retained.
191's final Walk075/Melee135 are materially improved; its standalone Death285
was also inspected. This contrast narrows the integration bug to scene control.

192 final visible correction: retained42 rest tracks did NOT by itself fix the
scene artifact. Targeted two-pose skin sampling then showed the actual causes:
old orientation put1135/7498sampled vertices inside the crate, and the falling
body went below the floor. Alternate caster-facing yaw had zero sampled crate
intersections (same pre-grounding body). Source191 now authors vertical floor
compensation into each Death frame in Blender, rather than using runtime AABB
correction. Existing faces/textures/rig/clips otherwise retained. Updated native
191Death285 inspected: whole body visible with floor contact. Saved pre-grounding
sources/movie/capture. No micrometre or all-pose gate is implied.

Final192 faces the robot toward the PSI caster before death, retains continuous
knockback, and lets its own grounded Death play. effects192 removes the whole-body
miniature fragment generated by the old multi-part robot effect; sparks, flash,
smoke, scorch and game sounds remain. Final0750 inspected: intact fallen robot,
clear of crate, no miniature. Earlier0254 established broad silhouette in scene.
Final native902frames FullHD30, one blockedshot/61occlusions, health unchanged.
No script/parse/surface errors found; existing SDL warning retained. Package
encodes actual audio/video and exposes191 GLB/BLEND and independent study.

Latest full visual prototype is E:painted192, older186 remains unchanged. This
is a staged encounter, not production tactical AI or campaign acceptance. Final
art still open: gait/armor contacts, precise cannon muzzle alignment, scene-wide
material/architecture quality and complete sequence review. Next: inspect the
whole encounter's action readability, fixing significant visible discrepancies
rather than another battery of old import/rig checks.
