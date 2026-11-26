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
