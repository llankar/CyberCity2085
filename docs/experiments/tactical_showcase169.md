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

## Cannon193 — geometry sockets and visible aim, 2026-11-26

New cannon_sockets193.py derives robot191: cap vertices of actual barrel identify
muzzle/axis, two sockets attached to upper_arm.R; barrel cap section made rigid
on that carrying bone. Source robot193 GLB/packedBLEND and muzzle.json on E:.
No new geometry generated or AI run. Native cannon193 scene drives heading and
bone aim from sockets, re-applies aim after animation advancement during the
shot window, and uses the exact socket origin (no generic22cm clearance).
Base hooks default to prior behavior; only experimental sources edited.

Executed one native902frame1920x1080/30fps take,74seconds offline. Actual shot
at4.8s reports3.73degree residual axis error after two aim iterations: not a
micrometre gate or full-motion accuracy claim. Inspected cannon0146: trace starts
at barrel and hits real crate while Rook crouches behind it. One blockedshot,
61occlusions, same six-unit health. Final0750 inspected: grounded wreck and
medical scene retained. No script/parse/surface errors found, existing SDL
warning remains. Package actual recorded audio to MP4/GIF/gallery with193 sources.
Previous192 and earlier media retained.

Next significant visible discrepancy: robot's new gait uses authored stride.28,
duty.6,period1.2, while inherited travel assumes generic nominal speed.85m/s.
Derive cycle speed from that gait before further visual polish; do not rerun
old import/rig gates. Global scene art/contacts and whole-sequence acceptance
remain IN_PROGRESS, not completion.

## Gait194 — authored cadence and actual path

Independent gait194 scene derives cannon193. Existing .28m stance displacement,
.6duty/1.2s period imply .388889m/s nominal stance speed. Actual2.8m/5s path is
.56m/s; cycle scale1.44 replaces inherited human-oriented.6588. Other paths,
events and clips unchanged. Constants refer to the existing baked191/193 gait;
regenerating that gait requires updating this explicit prototype calibration.

Executed one native902frame1920x1080/30fps capture,74s offline. gait.json records
actual1.4399999speed_scale and.56path speed. One blockedshot/61occlusions, same
six-unit health, no script/parse/surface errors found (existing SDL warning).
Package MP4/audio/GIF and eight-frame8.2s walk board, which was inspected: more
frequent steps, no major new tearing in these samples. Not proof of planted
feet across the full clip; supports cadence correction, not complete contact art.
E:gait194/index.html includes prior193 walk comparison. No new model export.

Next substantive priority: whole-map composition and visual identity/readability,
not more tiny foot poses. Remaining contact/architecture/complete artistic review
criteria stay open. No production/campaign/download/push or old rig/engine gates.


## Market195 ? carte vitrine, 26 novembre 2026

Livraison courante : `E:/CyberCity2085-3d-lab/generated/phase2/market195/index.html`.
Vid?o Full HD30 avec sons existants, GIF, captures propres et liens vers les
sources `showcase195/environment.blend` et `.glb`. Reproduction :
`python experiments/2d_to_3d/prepare_market195.py`, puis
`run_blender.ps1 -Script blender/market_identity195.py`,
`run_movie169.ps1 -Market195`, puis `package_combat169.py --folder
E:/CyberCity2085-3d-lab/generated/phase2/market195`.

Sept auvents sur les comptoirs existants, cadres m?talliques, bordures lumineuses
et enseigne m?dicale diff?rencient march?/clinique sans changer les volumes
fonctionnels. Premi?re palette trop vive conserv?e sous `first_bright_*`.
Final : 902 images,1920?1080,30fps,74s de rendu hors ligne ; ce chiffre ne mesure
pas les performances interactives. Assertions du packaging ex?cut?es avec
succ?s : un tir bloqu?,693 images avec occultation, ?tat final conserv?.
Captures0030/0750 inspect?es. Contr?le exhaustif des intersections non effectu?.

CHANTIER GLOBAL INCOMPLET : architecture encore r?p?titive, contacts de soins
et validation artistique de toute la s?quence restent ouverts. La sc?ne est
une rencontre locale mise en sc?ne, pas une validation de l'IA de production.
Aucun test de campagne ni push. Prochaine action : d?tailler les surfaces
r?p?titives sans nouvelle carte, puis corriger les contacts visibles des soins.


## Treatment196 ? soins lat?raux

Livraison : `E:/CyberCity2085-3d-lab/generated/phase2/treatment196/index.html`.
Commande de capture : `run_movie169.ps1 -Treatment196`, puis packaging avec
`--folder E:/CyberCity2085-3d-lab/generated/phase2/treatment196`.
Le trajet continu du soignant aboutit au c?t? du patient, qui regarde d?sormais
lat?ralement ; la mallette est rapproch?e. Animations et IK existantes conserv?es.
La capture0750 et la planche21..26s montrent des silhouettes s?par?es sans
chevauchement des visages. Cela ne prouve pas chaque contact de main ? chaque
image. Capture finale902images1920?1080/30fps,74s hors ligne, packaging r?ussi,
un tir bloqu?,702images d'occultation et sant? finale inchang?e. Premi?re
ouverture de film ?chou?e faute de dossier ; ordre du wrapper corrig?.
Aucun changement de production ni test de campagne ni push.
Prochaine action : d?tailler les devantures du march?, encore trop uniformes.
CHANTIER GLOBAL INCOMPLET.


## Storefront197 - furnished market

Current gallery: `E:/CyberCity2085-3d-lab/generated/phase2/storefront197/index.html`.
Real sources: `showcase197/environment.blend` / `environment.glb`.
Reproduce with `run_blender.ps1 -Script blender/storefront197.py`, then
`run_movie169.ps1 -Storefront197`, then `package_combat169.py --folder
E:/CyberCity2085-3d-lab/generated/phase2/storefront197`.

Seven existing counters receive worktops, metal fascias, local PBR medical
boxes, existing authored crates, terminals and geometric shop signs. The
functional map cells and paths remain unchanged. This is cosmetic furnishing,
not a market gameplay system. Captured902frames1920x1080/30fps in79s offline;
package assertions pass: one blocked shot,702occlusion frames, unchanged health.
0030/0750 inspected: merchandise visible, foreground stall fades, treatment
staging retained. No script/parse errors found. Existing SDL calibration error
and Blender shared-texture-sampler warnings remain documented.

Artistic limitations: stock still repeats, counter finishes are flat, existing
pipe valve competes with medical shop sign, architecture remains too uniform.
Whole-scene final artistic acceptance NOT VERIFIED. Next action is a cohesive
art pass and full encounter review, not repeated engine/rig validation.
No production edits, campaign tests, downloads or push.
CHANTIER GLOBAL INCOMPLET.


## Art198 - material/composition pass and useful final orbit

Gallery: `E:/CyberCity2085-3d-lab/generated/phase2/art198/index.html`.
Source: `showcase198/environment.blend` and `.glb`. Reproduce:
`run_blender.ps1 -Script blender/art_finish198.py`,
`run_movie169.ps1 -Art198`, `package_combat169.py --folder
E:/CyberCity2085-3d-lab/generated/phase2/art198`.

Two old decorative valves removed because they obstructed the medical shop
sign and overlapped the staged casualty. Existing metal roughness/normal maps
added to four stall materials;49merchandise units receive small deterministic
placement offsets. Functional map volumes/paths untouched. This is a modest
art pass, not proof of professional final environment quality.

The first full-story contact sheet exposed a poor low final camera angle with
large void below the finite map. Its media are retained as first_low_orbit_*.
Final198 camera keeps the27..30s rotation above the floor and frames the map.
Final29.5s orbit image actually inspected: tactical scene fills the frame,
units/wreck remain visible. Initial contact sheet samples the whole encounter;
this does not constitute continuous-motion artistic acceptance.

Final native902frames1920x1080/30fps,81s offline; packaging assertions pass,
actual audio/MP4/GIF/storyboard/final orbit PNG produced.1blockedshot,
602occlusion frames, final health [100,0,0,100,76,100]. No campaign test,
production edit, new download or push. No real-time FPS claim.
Still open: repetitive stall/facade appearance, character identity, full-motion
contact/impact quality. Next: stronger cyberpunk silhouettes/materials using
retained assets, with camera and working encounter preserved.
CHANTIER GLOBAL INCOMPLET.


## Roof199 - three distinct building identities

Gallery: `E:/CyberCity2085-3d-lab/generated/phase2/roof199/index.html`.
Sources: `showcase199/environment.blend` / `.glb`. Reproduce with
`run_blender.ps1 -Script blender/roof_identity199.py`, `run_movie169.ps1 -Roof199`,
then `package_combat169.py --folder
E:/CyberCity2085-3d-lab/generated/phase2/roof199`.

Utility reservoir has a real round shell, bands, cap and mounts. Repair shop
receives four tilted solar panels with frames/cell divisions. Clinic gets a
supported backlit rooftop sign. Existing free roof patches selected from
actual roof polygons; original tactical cells and paths preserved. Models are
cosmetic hard-surface objects, not new cover/movement systems.

Final native capture902frames1920x1080/30fps,81s offline; packaging assertions
pass:1blockedshot/602occlusion frames, health unchanged.0030 inspected: panels
and clinic sign visible. Tank outside main framing, so a single native overview
was captured with --roof-review on the same scene/flags (quit after90frames).
Actual roof_overview.png inspected: all three assemblies visible, tank separate
from the existing equipment. Not exhaustive geometric/all-frame acceptance.
No campaign tests, production edits, downloads or pushes.

Remaining artistic scope: repeated facade kit and human/cast distinction,
full-motion contacts/impact readability. Next work should focus retained human
candidates at combat scale rather than more small decorative roof pieces.
CHANTIER GLOBAL INCOMPLET.


## Cast200 - alternate reinforcement with actual retaliation

Gallery: `E:/CyberCity2085-3d-lab/generated/phase2/cast200/index.html`.
Reproduce: `run_movie169.ps1 -Cast200`, then `package_combat169.py --folder
E:/CyberCity2085-3d-lab/generated/phase2/cast200`.

Enemy4 now uses existing `modularity166/body_0_helmet_restfixed.glb` with its
real textures/helmet and shared five actions, rather than duplicating enemy1.
Existing Blender source linked in gallery. No new body generation or repaint.
Added retaliation at11.7s reuses actual pistol, effects and WAV. First take
crossed teammate; new endpoint(6,0,.45) gives a measured.763855m clearance on
this shot. `retaliation.json` proves76->64HP. Runtime/package assertions check
clearance>.35 and damage12 for this one event. This is not a new general
friendly-fire system. Flash starts from actual wrist at the existing.3s firing
pose. Idle guard allows the shoot animation to progress. Four-frame visual
board inspected: distinct body/helmet, unobstructed trace and progressing pose.
Treatment starts from actual remaining HP and uses the retained5HP/s cap100.

Final902frames1920x1080/30fps/81s offline, packaging assertions pass;1blockedshot,
602occlusion frames, final health unchanged. Earlier crossed/chest/wrist takes
preserved. One sparse trace typing error caused a parse failure, corrected
before final capture; no final script/parse error found. No campaign test,
production edit, new download or push. Exact barrel alignment/full-motion fit
not claimed. Global art remains incomplete, especially duplicate green main/
medic identity and architectural repetition. Next: genuine retained medical
accessory/role distinction, without rebuilding humans from primitives.
CHANTIER GLOBAL INCOMPLET.


## Medic201 / Scale202 - role equipment and actual-scale comparison

Current encounter: `E:/CyberCity2085-3d-lab/generated/phase2/medic201/index.html`.
Comparison: `E:/CyberCity2085-3d-lab/generated/phase2/scale202/index.html`.
Reproduce equipment with `run_blender.ps1 -Script blender/medical_pack201.py`;
then `run_movie169.ps1 -Medic201` and `package_combat169.py --folder
E:/CyberCity2085-3d-lab/generated/phase2/medic201`. Real module sources are
`medic201/medical_pack.blend` and `.glb`, using the existing local medical case
PBR textures. Rigid upper-spine attachment is calibrated in retained idle pose;
body, wardrobe and motion clips remain unchanged. Actual0750 inspected: medical
cross visible and case follows bent back. All-motion clipping NOT VERIFIED.
Native902frames1920x1080/30fps/81s offline, packaging assertions pass; one blocked
shot,602occlusion frames, retaliation76->64HP and.763855m teammate clearance,
final health unchanged. No campaign/production changes or new model downloads.

`run_godot.ps1 -Scene res://scale202.tscn -RenderingMethod gl_compatibility
-QuitAfter 300` produces a native1920x720 comparison of retained main human,
Hunyuan177, alternate helmeted Raider and painted193robot against actual idle
atlas tiles at nominal41/62px human projection (robot1.65multiplier). Existing
comparator reused as a current artistic deliverable, not another engine gate.
Board actually inspected: painted robot has a legible broad silhouette; humans
remain stylistically distant, especially civilian-shirt reinforcement. Sprite
and model idle views/poses differ; no exact pose/skin-bound match claimed.
The medic module helps role recognition but does not solve duplicate face/outfit.
Next: select from existing armored/scanned human candidates for a stronger Raider
identity, retaining working robot and staged encounter. No push.
CHANTIER GLOBAL INCOMPLET.


## Armored203 - retained authored Raider armor, portable model

Gallery: `E:/CyberCity2085-3d-lab/generated/phase2/armored203/index.html`.
Actual reusable sources: `armored203/armored_actions.blend` and `.glb`.
Reproduce model with `run_blender.ps1 -Script blender/assemble_armored203.py`,
then `run_movie169.ps1 -Armored203`, then `package_combat169.py --folder
E:/CyberCity2085-3d-lab/generated/phase2/armored203`. Current comparison:
`run_godot.ps1 -Scene res://scale202.tscn -RenderingMethod gl_compatibility
-QuitAfter 300 -SceneArguments @('--armored203')`.

Inspected existing scanned candidate and Unvanquished authored armor. Selected
latter for its detailed yellow/black plates and stronger tactical identity.
Original body, actual bound pistol and six source motions plus existing pistol
study combined into one portable model; no new AI generation/recolor/download.
Native import retains static channels, -Z anatomical forward is corrected using
existing audit, firing seeks source reference1/15s. No new rig or retarget pass.
First runtime-composed take retained before self-contained export.

Final902frames1920x1080/30fps,82s offline. Packaging assertions pass, seven clips
present; encounter exercises Idle/Walk/Pistol_Attack_Study, not all seven clips.
One blocked shot,602occlusion frames; retaliation76->64HP and.750454m teammate
clearance, final health unchanged. Actual0750, fire extraction and current41/62px
comparison inspected: stronger Raider likeness and cast separation; no major
new deformation in these samples. All-motion grip/foot/contact quality remains
NOT VERIFIED. Prior source legacy-PBR, grip and source-game-parity limitations
are preserved; technical import does not close them. No campaign test,
production edit or push. Global scene art remains incomplete: main/medic face
reuse, repeated facade kit and full-motion contact/impact quality. Next: review
whole-sequence visible motion defects rather than additional small props.
CHANTIER GLOBAL INCOMPLET.


## Contact204 - visible hits and contact-driven melee

Gallery: `E:/CyberCity2085-3d-lab/generated/phase2/contact204/index.html`.
Reproduce: `run_movie169.ps1 -Contact204`, then `package_combat169.py --folder
E:/CyberCity2085-3d-lab/generated/phase2/contact204`.

Actual203 hit/melee strips inspected before edits. Nonlethal shots no longer
queue Death on the first Raider. Short torso recoil on both enemies restores
its prior offset before animation advancement, preventing cumulative lean even
when a source clip has no bone key. One nonlooping melee gesture, attacker.15m
closer, resolves on an advancing wrist reaching an approximate torso volume.
Death, contact effect and existing melee WAV share that event. Robot out of
reach now waits instead of swinging. Existing169 scene preserves its original
15.2s behavior via a virtual hook; new behavior is confined to204 prototype.

Actual melee_contact.json:14.725s, right wrist distance.281415m, advancing speed
5.81987m/s. Package asserts distance<=.35, speed>.12 and target dead. These test
one staged contact volume, not general production/triangle collisions. Final
902frames1920x1080/30fps,82s offline, packaging successful:1blockedshot,
602occlusion frames, same final health. Hit strip, melee strip and0750 inspected:
legs do not collapse on nonlethal hit, punch precedes fall, medical staging kept.
No all-motion foot/grip/art acceptance claimed. First indentation parse failure
corrected and targeted script check exited0; initial valid take preserved and
second interrupted before final overlay-reset capture. No campaign tests,
production edits, downloads or pushes.

Next: coherent local delivery of selected scene, reusable sources/assets and
media with a short honest remaining-art list; avoid more small prop variants.
Global art acceptance remains open (facade repetition, main/medic face reuse,
full-motion contacts/identity). CHANTIER GLOBAL INCOMPLET.


## Delivery205 - one usable local delivery

Folder: `E:/CyberCity2085-3d-lab/deliveries/tactical_demo205`.
Open `index.html` for media/models or double-click `Run.cmd` for the30second
staged encounter. Included engine: Godot4.7.2Windows. No Python or separately
installed Godot is required to run this local folder. Keep it on E: as requested.
Allow about35seconds for scene loading on the measured machine. It closes after
30seconds of sequence; relaunch to replay. This is not production tactical AI.

Builder: `python experiments/2d_to_3d/build_delivery205.py`.
Native run: `& E:/CyberCity2085-3d-lab/deliveries/tactical_demo205/Run.ps1 -Verify`.
Verification: `python experiments/2d_to_3d/verify_delivery205.py`.
Recorded assets:93unique files/2,003,457,707bytes, including editable packed Blender
sources and two bundled engine binaries. AI weights, caches and intermediate
takes excluded. Runtime assets are local to project/lab and project/assets;
metadata paths rewritten after JSON parsing, preserving mesh hashes. Scripts
are the retained scene dependency closure with roots/selection flags adapted
only in delivered copies. Original authoring recipes still reference original
lab inputs; this is not a self-contained AI-generation environment.

Initial launcher hit known SDL stderr under Stop policy, corrected. First native
run had two stale module paths, corrected before the final independence check.
Final native run exits0:1779frames,59.7306meanFPS outside the first timeline second,
34.816s scene setup on this RTX5070Ti. No movie encoder in this measurement.
Contact, retaliation, final health and occlusion checks pass;38actual audio events
resolve to existing files inside bundle. Native preview actually inspected.
No final script/parse/missing-resource errors found; existing SDL gamepad
calibration warning remains. Godot cache junction targets E: and preserves any
initial cache data. Contact204 hand speed now uses real delta, not assumed30FPS.
Existing204video retained rather than unnecessarily rendering it again.

Evidence: verification/verified.json and native-run.log; project/evidence contains
native_summary.json, encounter.json, melee_contact.json, retaliation.json,
audio.json and preview.png. Clean-PC compatibility and overall artistic
acceptance NOT VERIFIED. No production edit, campaign test, push or release.
Remaining: repeated facade kit, main/medic face reuse, full-motion foot/grip
quality and final visual acceptance. CHANTIER GLOBAL INCOMPLET.


## Facade206 / latest artistic steering

206 gallery: `E:/CyberCity2085-3d-lab/generated/phase2/facade206/index.html`.
Eight retained urban-kit bays differentiate two buildings. Initial flat-wall
zero-depth error fixed; first two alignment takes preserved. Independent axis
normalization was not the real issue: world-space placement using actual wall
normals/centers fixed inherited reimport transform mismatch. Window depth.18m.
Final0030 inspected;902FullHD30frames/85s offline, package contact/audio/video
checks pass;1blockedshot/602occlusion frames, same health. Stable205 preserved.
Latest user steering: current market remains too contemporary.207 must replace
striped canopies with cyberpunk kiosks/ads/industrial equipment, then improve
class silhouettes, heavy robot materials/effects and occlusion. No old engine/
rig proofs, no production/campaign/mass conversion. Global art still incomplete.


### Cyberpunk kiosk pass207 ? 2026-11-26

Current art preview: `E:/CyberCity2085-3d-lab/generated/phase2/cyber207/index.html`.
The stable self-contained Delivery205 remains unchanged. Reproduce the new map
with `run_blender.ps1 -Script blender/cyber_kiosks207.py`, then
`run_movie169.ps1 -Cyber207` and `package_combat169.py --folder
E:/CyberCity2085-3d-lab/generated/phase2/cyber207`.
Seven cloth awnings become weathered technical kiosks with retained authored
vents/pipes, cables, medical holograms, energy/neural readouts and three brands.
Actual game illustration supplies medical screen art. All BLEND/GLB/PNG/media
stay on E:. The first attachment take was rejected and retained; updating the
Blender view layer before reading world matrices fixed accessory placement.
Final native902frames FullHD30 recorded90s offline; packaging assertions pass,
1blocked shot,831occlusion frames and expected final health. Overview and medical
capture inspected. Existing contact, audio, animations and sprite comparison
retained. No campaign/production changes, downloads, push or release.
Artistically incomplete: blank/overbright panels, repeated facade surfaces,
faded small signs crossing units, main/medic face reuse and complete motion
review. Next208 targets visible architecture and cutaway readability.

207 follow-up: small emissive kiosk/shop signs and holograms disappear while
owner materials fade below.9; large geometry keeps existing transition. Actual
final0750 inspected: no lettering crosses the medic. Re-captured FullHD30/902
frames90s offline, packaging/state checks pass again; gallery local links pass.
Blank panels/facade variation and distinct main/medic silhouette remain208 work.


### District208 ? exposed facade finishes and actual illustrated advertising

Preview: `E:/CyberCity2085-3d-lab/generated/phase2/district208/index.html`.
Reproduce: `run_blender.ps1 -Script blender/district208.py`,
`run_movie169.ps1 -District208`, then `package_combat169.py --folder
E:/CyberCity2085-3d-lab/generated/phase2/district208`.
Three building backing meshes use existing worn-metal PBR on their vertical
surfaces, three actual fitted bays receive medical advertising sourced from the
game. Wall/window kit geometry stays unchanged; exposed areas only, not a full
architectural redesign. Initial slot1 roof change rejected; world-normal material
selection corrected it. Final902frames1080p30 rendered87s offline. Native/package
state/contact checks PASS; overview/medical captures inspected, local gallery
links PASS. No production/campaign/download/push. Stable205 preserved.
Art remains incomplete: repeated wall kits and bright panels; distinct medic
silhouette with retained authored accessories is the next concrete task209.


### Medic209 and heavy robot210 ? consolidated character art preview

Current preview: `E:/CyberCity2085-3d-lab/generated/phase2/finish210/index.html`.
Build `blender/medic_helmet209.py` and `blender/robot_finish210.py` through
`run_blender.ps1`, then `run_movie169.ps1 -Finish210` and package its folder.
The medic reuses an actual acquired helmet (.29m wide) attached to the existing
head bone; original body, treatment and spine-mounted case stay intact. Short
native preview and actual medical pose inspected. Robot retains193 geometry,
14bones/five clips, texture and sockets; metal response and red-pixel emission
added, sensor emission shuts down during destruction. Rest tracks stay enabled.
Final210902frames1080p30/86s offline; package contact/state checks and gallery
links PASS, actual overview/medical captures inspected. Before/after crops use
native identical framing. Intermediate209movie not redundantly encoded.
Full-motion art, complete class wardrobe and finished environment remain open.
No production, campaign, downloads or push. Stable205 preserved. Next211 targets
contemporary lamps/repeated facade geometry rather than another palette trial.


### Street211 / tempo212 ? native rhythm1.7

Preview: `E:/CyberCity2085-3d-lab/generated/phase2/tempo212/index.html`.
Build `blender/street211.py`, run `run_movie169.ps1 -Tempo212`, then package
that folder. Two old lamps become angular worn-metal fixtures/local cyan lights;
east service bay generated, camera-facing art coverage still NOT VERIFIED.
After user feedback, final1.7 scene clock replaces initial1.35 trial. Paths,
manual animation/effects/camera share delta; audio pitch unchanged, no FFmpeg
speed filter. Final531frames30FPS=17.7s,69s offline. State/contact package PASS.
Actual overview/melee strip/final orbit inspected. Initial gallery check found
treatment/orbit thumbnails sought at old timestamps; seeks remapped and files
generated without full rerender/reencoding. Gallery links now PASS.
Existing final medical recovery/IK pose remains213, global art still incomplete.
No production/campaign/download/push. Stable205 retained.


### Recovery213 ? actual completion drives medical recovery

Preview: `E:/CyberCity2085-3d-lab/generated/phase2/recovery213/index.html`.
Run `run_movie169.ps1 -Recovery213`, then package that folder. Source medical
kneeling pose is held until actual100HP; IK releases, medic source rise and
patient CoverExitStudy recover together. Source clip5.2083s/hold4.1667s selected
with seven samples, no new rig. First take revealed unkeyed idle rest channels;
post-crossfade bone reset/current idle fixes the lingering arm. Actual final
close crop inspected: both upright, no arm reaching to the former target.
Final549frames1080p30=18.3s,1.7pace retained; extra1simsecond shows recovery.
Native/package state/contact/recovery checks and gallery links PASS. Old scene
30s/contact defaults unchanged. Full-motion global art NOT VERIFIED. No campaign,
production, push or release.214next: camera-facing hero facade then consolidation.


### Clinic214 / local delivery215

Current standalone: `E:/CyberCity2085-3d-lab/deliveries/tactical_demo215/Run.cmd`;
video/gallery `generated/phase2/clinic214/`. Buildclinic214, movie -Clinic214,
package folder; build_delivery205.py --latest; Run.ps1 -Verify;
verify_delivery205.py --latest.205 remains intact.
Frontal service bay corrects clipped first corner placement. Actual overview
inspected. New lamp assemblies join existing occlusion fade; final native
preview confirms medic stays visible. Current1.7tempo/recovery/cast retained.
Final214FullHD30/549frames18.3s, package/gallery PASS. Bundled native exit0,
55.615meanFPS here,35.412s setup,1004frames; verifier PASS108recorded assets,
2.1305GB,38actual audio events within bundle. No clean-PC/global art claim.
Recipes need original E: inputs, no AI environment bundled. No production,
campaign, downloads or push. Latest owner steering accepts direction and asks
richer roofs/shops/street furniture, aged PBR/lighting/atmosphere, combat/robot
VFX, human variety and a less simplified VTOL.216 next uses authored repair
machinery and restrained existing smoke; preserve rigs/motions and single map.


###216art work and storage maintenance

Industry216 uses two authored repair/salvage merchandise sets and foreground
roof ducts with restrained existing soft smoke. Final overview inspected, video
rendered549framesFullHD30/18.3s; subtle vapor motion review remains open.215stays
as standalone checkpoint. No216bundle regenerated.
Owner requested regular cleanup and no retention of obsolete validation outputs.
27old build UUIDs/install-smoke/incomplete Blender removed; newest two builds,
models/sources/environments/deliveries retained. uv cache18.1GiB cleared, six
redundant AVIs removed while MP4 references stay. About148GiB real free space
recovered. AGENTS records policy. Packager can regenerate galleries directly
from retained MP4, without re-encoding/gain duplication. No production/campaign.


### Selected lab after owner-requested cleanup

Only current216working assets,215standalone, selected model masters/source
library and one Hunyuan pipeline remain. Lab about37.14GiB versus128GiB.205and
old experiments were explicitly discarded. Current216gallery is self-contained
with selected asset links, not historical gallery chains. Active entry points:
`E:/CyberCity2085-3d-lab/config/selected_assets.json`. Source code history stays
in Git; historical recipes may need inputs that were deliberately pruned.
Hunyuan cache-linked dependencies were repaired/materialized; active setup uses
hardlinks so future cache pruning does not remove environment dependencies.
No production runtime/save changes. Artistic work continues from216/215.

## Current local lighting pass218

Scene `res://lighting218.tscn` inherits selected industry216. Seven authored
shop valances illuminate nearby surfaces with their actual emissive color;
cutaway alpha suppresses their lights. Neutral fill remains for readability.
Gallery/video: `E:/CyberCity2085-3d-lab/generated/phase2/lighting218/index.html`.
Capture with the same CLI arguments as industry216, substituting scene218 and
output folder218; package using `package_combat169.py --folder` with that folder.
No historical pruned inputs required. Previous standalone215 remains retained.

## Worn cladding219

Current scene `res://counter219.tscn` inherits lighting218. The seven retained
counter bodies receive metric worn PBR cladding; no geometry/collision change.
Editable source: `generated/phase2/showcase219/environment.blend` on E:.
Gallery: `generated/phase2/counter219/index.html`. White counter strips are gone;
muted tint variation remains subtle. Larger architectural variety is still open.

## Aircraft candidate221

`res://aircraft221.tscn` compares the actual Hunyuan stealth dropship at the
previous vehicle center/width. Brief wider opening shot shows its full silhouette.
This candidate is STATIC; fan/gear transfer remains open. Original animated178
and selected scene219 are retained. Gallery: generated/phase2/aircraft221/index.html.
The dark/soft texture is not accepted as final aircraft art.

## Animated generated aircraft222

Selected lab scene `res://aircraft222.tscn`: actual generated inner fans rotate
inside stationary original rings. Same source220 UV/albedo, metallic response
improved. No gear animation. Native movie and motion crop comparison are at
`generated/phase2/aircraft222/`. Editable aircraft: `vtol222/vtol_actions.blend`.
Soft texture/green marks remain; no production or standalone215 replacement.

## Service-access trial223

`res://services223.tscn` adds retained authored fire-escape and utility parts to
front facade bays, preserving map cells and building cutaway. Review media:
`generated/phase2/services223/index.html`. Full-scene artistic gain is modest;
this does not meet the broader architecture objective. Selected scene remains222.
Next direction: complete cyberpunk facade assets rather than more small attachments.

## Original-map reconstruction / library225

New source specification: attachment49f6518a-63ec-4e44-8a96-f057aab9e982.
Use original map images and existing surveys as the art reference. Tactical IDs
are not appearance labels. One map only; original PNG/tactical data unchanged.

`python experiments/2d_to_3d/environment_library.py --init --register-selected`
imports24 context references and indexes three retained meshes on E: without
copying models. `--find stealth_vtol` or `--find Buildings` searches before any
new generation. E:/CyberCity2085-3d-lab/environment-library/index.html is the
initial reference gallery. Crops are NOT segmented; unknown asset dimensions,
anchors/orientations and incomplete artistic statuses remain explicit.

Installed Hunyuan2mini shape and Hunyuan2.0turbo paint licenses explicitly
exclude EU territory; they do not meet the new France-permission requirement.
Official source texts are preserved in library/licenses. No new inference or
production integration while this is unresolved. Continue original extraction,
Blender and appropriately licensed assets. Prior experimental outputs preserved.

Next: one reproducibly isolated original roof machine/container, an actual
textured 3D equivalent, calibrated library entry and independent Godot placement.
Main production GOAL/runtime remains untouched. No campaign or massive conversion.

## First source-derived roof module226

Run `python experiments/2d_to_3d/extract_roof226.py`, then
`run_blender.ps1 -Script blender/roof_fan226.py`. The explicit manual mask
preserves original source pixels and records one genuine view. Repeated extraction
keeps existing model metadata. Hidden sides/mechanics are inferred in Blender.
No new Hunyuan inference. Source RGB/mask/provenance checks actually passed.

Godot scene `res://roof226.tscn` reads the library asset association and inserts
it before existing building cutaway registration. Previous generic duct is hidden;
existing vapor follows the new module. No collision/LOS/path data changed.
Gallery: E:/CyberCity2085-3d-lab/generated/phase2/roof226/index.html.
Library asset: environment-library/assets/roof_twin_fan/source.json and models.
A reviewed prototype, not final artistic acceptance. General scene-association
loader, further original object isolation and whole-building identity remain open.

## Library association compiler227

`python experiments/2d_to_3d/build_library_scene.py` writes placements.json and
an independent scene.tscn under E:/CyberCity2085-3d-lab/generated/phase2/library227.
Launch that absolute scene with existing run_godot.ps1 and current showcase flags.
Actual native100frame launch and screenshot checked. No additional movie was
created because art is unchanged from226. Bindings keep source placement, scale,
rotation, parent cutaway, replacement pattern and vapor offset explicit.

Only the current showcase map is supported by the scene runtime. The placement
compiler/module is reusable, but no arbitrary-map reconstruction is claimed.
No source/collision edits, no model duplication. Recompile unchanged bindings
reuses output files. Four small contract tests passed; no campaign test.

## Original paneled pair228

`extract_containers228.py` preserves actual east_bins RGB under explicit masks.
`run_blender.ps1 -Script blender/containers228.py` reconstructs the pair; unseen
faces/height remain inferred. Library metadata includes actual mesh bounds and
source placement. Re-run build_library_scene.py to load both roof fan and pair
through the same generic runtime. No per-object scene code was added.

Current FullHD movie/gallery: generated/phase2/library227/index.html. Opening
frame reviewed; ground-art duplication is not obvious there, but full-orbit edge
review is still open. Production floor/tactical cells and save remain untouched.

## Source-derived foreground roofs229

`run_blender.ps1 -Script blender/original_roofs229.py` replaces invented solar/
roof-sign parts on the two foreground buildings with original-inspired segmented
metal roofs and a service hatch. Existing library roof machine and container pair
are inserted with `build_library_scene.py --environment showcase229/environment.glb`.
Omitting --environment now preserves the prior selection. Four placement tests
and an outside-path rejection check pass. No tactical/source PNG changes.

Current gallery/video remains generated/phase2/library227/index.html; source
contexts and native roof detail crop are included. Native0030 inspected; facades
remain unfinished. This assembly is not yet a standalone library roof module.

## Interpreted service facade230

`run_blender.ps1 -Script blender/service_building230.py` loads229 and replaces
only the foreground west building's generic facade parts. Custom cut-corner
shell panels, recessed access, glazing and supply conduits share the building's
existing cutaway. Vertical facade is inferred, not an authentic original view.
Compile with --environment showcase230/environment.glb using build_library_scene.py.
Actual native overview/close crop inspected. Surface remains too clean/flat for
final artistic acceptance; improve material richness before broadening this style.
Current gallery/video: generated/phase2/library227/index.html.

Live playback correction (231): phase screenshots are now opt-in outside movie
exports (--capture-stills). Three real native runs isolated the capture stalls:
12 frames over33ms/max1.34s before, one initial134ms spike after capture guard and
material warmup; final mean59.61FPS,p9516.692ms. Startup36.65s is still separate.
Use --measure-live for optional post-draw measurements; E: library227/live_live.json.
These measurements cover this experimental scene, not production. No PNG writes
occurred in corrected live runs. Further art work remains open.

232 material pass: existing acquired worn plate PBR applied to four service doors
and utility covers, preserving geometry. Selected E: showcase232 environment.
Actual Godot crop: ../showcase232/facade_detail.png; subtle improvement, not final.
Existing encounter MP4 remains230; no new video was rendered for this material pass.

233: current gallery/video updated to source-derived green cloth canopy on market_nw.
True draped384quad mesh with thickness; authentic source RGB crop; overhead cap vent
removed after actual native inspection. Same scene/cast/path/camera; no tactical edit.
FullHD30 H264/AAC verified; raw AVI removed. Baked source light and stretched cloth
proportions still limit art quality; this partial shop is not a finished library model.

234: selected scene now loads a complete standalone market shop from the reusable
library at the original parent/anchor. Three original sage/green/plum cloth crops
replace the over-stretched single tarp; lower machinery/counter remain interpreted.
Full native549frame video refreshed at1080p30. Standalone shop GLB and Blender root
reference are linked in the gallery/library. Baked source lighting and generic lower
counter still need art work; no all-angle clipping or global completion claim.

235: southeast display counter now has four recessed trays with original source RGB
interiors, a blue draped canopy and physical rear supports. Standalone4.23MB shop GLB
loads as fourth original-parent library placement. Current comparison/stills at
../showcase235/index.html; video remains234, explicitly labeled. Final close view
inspected; baked illumination and generic base still limit art finish.
Redundant intermediate exports pruned, 1.037GiB file bytes reclaimed; current234/235
Blender masters and all original textures/scripts retained. No production changes.

236 current movie: original-layout northeast industrial roof with two unequal fans,
stepped service hatch and22cm acquired pipe runs. Actual opening crop/source reference
included in gallery. Final native549frames and saved pipe-scale regression passed;
not production/campaign acceptance. Brick facade remains inconsistent and is next.
Current fullHD30/AAC video now includes235 display counter as well as234 cloth shop.

237 current video: northeast industrial facade now uses acquired garage/service doors
and high windows on worn metallic cladding, retaining236 roof. Vertical design is
explicitly interpreted. Actual saved-model comparison preserves98roof/body meshes.
Native549frame sequence and H2641080p30/AAC packaging completed; raw AVI removed.
Facade close crop/source comparison in current gallery. Pale shutters and remaining
repetitive buildings still need artistic integration; no production/campaign claim.

238 door paint correction: real glTF factors verified with original normal/diffuse
textures retained. Actual native close preview at ../showcase238/index.html;
existing movie remains237 and is labeled explicitly. Pale-shutter issue reduced.

239 current movie includes toned238 doors and source-layout northern roof; brief
opening now24.5m before original action camera. Source/neutral northern comparison
added, old generic compressor removed. Final native549frames, H2641080p30/AAC.
Both reusable shop Blender pointers consolidated into239 packed master.11redundant
intermediate exports pruned (1.290GiB file bytes);219base and reconstruction recipes
retained. See E: environment-library/REBUILD_ENVIRONMENT.txt for old-state regeneration.
