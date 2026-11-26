# Rook unarmed neural candidate175

Separate experimental asset, not a production replacement. Source/reference,
models, textures, Blender files and movies remain on E:/CyberCity2085-3d-lab.

The actual combat sprite informed a new imagegen unarmed A-pose reference.
`generated/phase2/reference175` retains the exact prompt, source/output hashes
and derived-image provenance. It is not an unchanged original sprite.

Hunyuan mini produced a503540triangle shape. Neutral front/profile/back review
showed separate arms/hands and no weapon. Reduction and tiny-component cleanup
retained39916triangles. Paint generated a1024colour texture; manual metal0.15/
roughness0.58 settings are not generated PBR maps. Both raw outputs are preserved.

First automatic binding failed because the paint GLB split vertices at UV seams.
Coincident positions were welded while preserving per-loop UVs. Heat binding
then covered19956vertices. Five existing UAL actions were baked: Idle, Walk,
Shoot, Melee, Death. First rendered motion exposed coat influence from the arms.
Central coat weights and translation transfer were corrected; first failed
captures/files remain as `rig175/first_*`.

Native detail and game-scale movies each contain330FullHD frames at30fps,
11seconds, rendered offline. Five detail poses and the game-scale shooting pose
were inspected. Packaging checks cover media format and weight coverage, not
artistic acceptance. Remaining issues: underarm/coat deformation, leg fit/foot
contact, weapon attachment and tactical-scene evaluation. No campaign tests.

Shape took60.48s after imports, peak torch allocation4.87GB. Paint took139.24s
after imports, peak allocation11.03GB/reserved14.34GB. These figures exclude cold
WSL Python imports (several minutes), downloads and Blender work; reserved memory
is not whole-GPU usage. Existing model caches were reused.

Reproduce sequentially, preserving previous results:

```powershell
wsl -d Ubuntu-24.04 -- bash /mnt/d/SynologyDrive/rpg/Python/Cybercity-2085/CyberCity2085/experiments/2d_to_3d/run_hunyuan_shape.sh rook_unarmed
& experiments/2d_to_3d/run_blender.ps1 -Script blender/review_ai_mesh.py -ScriptArguments @('--input','E:/CyberCity2085-3d-lab/generated/phase2/hunyuan175/rook_unarmed/mesh.glb','--output','E:/CyberCity2085-3d-lab/generated/phase2/hunyuan175/rook_unarmed/review_upright','--target-triangles','40000')
& experiments/2d_to_3d/run_blender.ps1 -Script blender/clean_unarmed175.py
wsl -d Ubuntu-24.04 -- bash /mnt/d/SynologyDrive/rpg/Python/Cybercity-2085/CyberCity2085/experiments/2d_to_3d/run_hunyuan_paint168.sh --subject rook_unarmed
python experiments/2d_to_3d/painted_robot170.py --folder E:/CyberCity2085-3d-lab/generated/phase2/paint175/rook_unarmed
& experiments/2d_to_3d/run_blender.ps1 -Script blender/rig_unarmed175.py
& experiments/2d_to_3d/run_unarmed175_movie.ps1
& experiments/2d_to_3d/run_unarmed175_movie.ps1 -GameScale
python experiments/2d_to_3d/package_rig175.py
```

Paint refuses an existing result to prevent accidental inference repetition.
Do not remove that guard merely to replay the commands. Reuse the existing GLB.
The static neutral images in the gallery were generated with review_ai_mesh.py
using paint175/rook_unarmed/painted_material.glb and output paint175/rook_unarmed/review.

Visual delivery: generated/phase2/rig175/index.html, actions.mp4,
actions_game.mp4, human.glb and packed human.blend.

CHANTIER GLOBAL INCOMPLET.
