# Local image-to-3D continuation (batch 164)

Scope: missing local AI experiments only. The broader experimental GOAL remains
paused; production runtime, saves, maps and previously accepted animations are
outside this batch. No publication, build, desktop automation or push.

The user requested personal-use technical evaluation without spending further
time on licensing. Existing licence observations are retained as metadata,
not represented as a grant of distribution rights. No gated access is bypassed.

## Reused evidence, not rerun

TripoSR already generated six real meshes: crate, industrial machine, robot,
Rook, Raider Grunt and vehicle. All six existing GLBs were found and SHA-256
recorded in `E:/CyberCity2085-3d-lab/tmp/image3d164-prior-evidence.json`.
Existing Blender/GLB/Godot trials remain authoritative; all six were rejected
as final art. No inference, atlas, animation or Godot test for these was repeated.

SPAR3D/Stable Fast 3D: existing authentication/access blocker unchanged. No
repeat gated download attempts. TripoSG/Hunyuan3D are pending technical trials;
earlier territorial licence observations remain documented separately.
TRELLIS.2 officially targets at least 24 GB, exceeding this 16 GB GPU; no large
download. TRELLIS original is the first untested candidate being installed.

## Isolated environment and commands

All environments, source checkouts, downloads, caches and generated assets:
`E:/CyberCity2085-3d-lab`. WSL Ubuntu 24.04, Python 3.11.18, RTX 5070 Ti
16,303 MiB, driver 621.24, compute capability 12.0. TRELLIS source revision
`193e0502b5cb3eb5997ec457d5340e95d09b158e`; FlexiCubes submodule
`815e075a2a400d06c48d94c347674344ed6ae5c5`.
Other public source checkouts: TripoSG
`fc5c40990181e2a756c4e0b1c2f4d6b5202faf8c`, Hunyuan3D-2
`f8db63096c8282cb27354314d896feba5ba6ff8a`.

Run the scripts sequentially with `wsl -d Ubuntu-24.04 -- bash SCRIPT_PATH`:

1. `experiments/2d_to_3d/setup_trellis_wsl.sh`
2. `experiments/2d_to_3d/setup_trellis_dependencies.sh`
3. `experiments/2d_to_3d/setup_trellis_native.sh`
4. `experiments/2d_to_3d/setup_trellis_mesh.sh`
5. `experiments/2d_to_3d/run_trellis_probe.sh`
6. `experiments/2d_to_3d/run_trellis_mesh.sh crate`

Use `/mnt/d/SynologyDrive/rpg/Python/Cybercity-2085/CyberCity2085/` as
the absolute script-path prefix. `trellis_env.sh` routes caches to E: without
changing HOME. Native libusb is extracted from the Ubuntu package into E:,
not installed into the WSL system. Existing ComfyUI/TripoSR are unchanged.

Pinned PyTorch 2.7.1 CUDA 12.8, torchvision 0.22.1, xFormers 0.0.31 and
Kaolin 0.18.0; spconv-cu126 uses Native algorithm. Ordinary GPU matmul PASS.
xFormers automatic dispatch FAIL: Flash3 Hopper launch invalid argument on
sm_120. Retained `tmp/trellis164-gpu-auto-fail.log`. Explicit CUTLASS attention
and Native sparse convolution both actually PASS; machine-readable results
in `tmp/trellis164-gpu-probe.json`. Only this changed backend justified retry.

Pipeline import initially FAIL: Open3D needs libusb-1.0.so.0. Extraction-only
dependency setup added; subsequent runner reached real model/DINO weight loading,
so that missing-library error is resolved. Windows then reported virtual-memory
exhaustion (PowerShell 800705af), and WSL restarted before mesh evidence existed.
No result is inferred from the completed downloads. The previously absent user
`.wslconfig` was created with a 12 GB RAM limit and 12 GB swap at
`E:/CyberCity2085-3d-lab/tmp/wsl-swap.vhdx`; actual `free -h` verifies both limits.
Only one heavy process is now allowed at once. Hunyuan setup packages were
installed but its import did not finish before interruption; NOT VERIFIED.
Retry uses cached weights and `tmp/trellis164-crate-memoryfix.log`.
No full CUDA toolkit or old CUDA 11.8 environment was installed.

The mesh runner checks actual kernel results before downloading any weight.
It keeps official samplers and excludes only unused Gaussian/radiance decoders.
Source/image/GLB hashes prevent duplicate inference. Exports use actual generated
vertices, faces and vertex colours, followed by GLB reload. This is not a rig,
UV/PBR texture bake, artistic approval or proof of Godot compatibility.
PyTorch peak allocations exclude non-PyTorch VRAM; never label them total VRAM.

## Verification and pending work

New guard tests: **2 passed, 0 failed, 0 skipped**, `tmp/tests164.xml`.
They reject incomplete/crashed kernel evidence and changed/missing trial files.
Previous production, contact, motion and TripoSR checks were not rerun.

Initial checkpoint deferred generation/render/import to the continuation below.
TripoSG/Hunyuan technical evaluation remains pending. CHANTIER GLOBAL INCOMPLET.

## Executed continuation

Crate generation **PASS**, real GLB reload, 431,020 vertices / 862,064 triangles,
83.465 seconds including cached model loading. Raw GLB SHA-256
`8df7e9ab42859aed94e64c42a73b18491c1d4554bce6c9bf197779c51de6fca9`.
PyTorch max allocated 11,978,586,112 bytes, max reserved 17,622,368,256 bytes;
these counters do not prove total dedicated VRAM consumption or a strict 16 GB
budget. No external VRAM peak or frame-time benchmark was captured.

Blender 4.5.17 generated four neutral views, raw `model.blend`, then an actual
19,999-triangle reduction, `optimized.blend` / `optimized.glb` and fifth preview.
Both isometric images inspected: recognizable crate, residual dents/waviness,
low-poly faceting after reduction, white surface. This mesh decoder did not
produce useful colour; no PBR/texture completeness claim. Godot 4.7.2 headless
native import **PASS**, one mesh/material surface, 19,999 triangles and matching
optimized GLB SHA `eaf9011becefa16f8a4e202bd170905869ea3b5947f9a02275cb3df08859c139`.
All evidence under `generated/phase2/trellis164/crate/review`, original preserved.

User priority became Rook and the combat robot, then explicitly Rook's actual
Godot combat sprite. No portrait inference was executed. Both are new TRELLIS
trials, not reruns of their rejected TripoSR trials. Serial inference execution.
Hunyuan runner prepared with explicit two-file acquisition to avoid downloading
duplicate ckpt/safetensors weights; its inference is still NOT EXECUTED.

## Requested human and combat robot trials (batch 165)

Godot resolves the actual name `Rook` to `agent_diverse_14`; its production
texture mapping selects `agent_diverse_14_armored_vanguard`. The name is passed
unchanged by `godot_bridge.py`, not uppercased. Actual engine hash probe executed.
`prepare_rook_combat_reference.py` checks the source atlas SHA, extracts genuine
idle frames E/S/W/SE and checks exact saved RGBA values. Four transparent 256px
frames plus provenance are under `E:/CyberCity2085-3d-lab/sources/rook_combat`.
No portrait, legacy samurai fallback, invented views or image upscaling.

Run `run_trellis_mesh.sh rook --combat-reference` for the official multiview API;
`run_trellis_mesh.sh robot` uses the exact `assets/units/robot_combat_512.png`
image already copied to E:. Existing successful matching outputs are reused.

| Trial | Raw vertices / triangles | Optimized triangles | Measured runner time |
|---|---:|---:|---:|
| Rook combat, four views | 190,252 / 378,602 | 40,000 | 77.113s |
| Combat robot | 337,356 / 674,710 | 39,996 | 123.143s |

These times include cached model loading, not full process startup. Both real
GLBs were reloaded, then processed by `blender/review_ai_mesh.py` through the
Blender CLI wrapper. TRELLIS/trimesh raw GLBs need `--source-z-up`; without it,
the robot lies sideways. The initial incorrect-axis review is preserved in
`robot/review/`; use **review_upright/** for both final diagnostic bundles.
No inference was repeated for this orientation correction.

Each bundle contains four 768px neutral renders, an optimized isometric,
`model.blend`, `optimized.blend`, `optimized.glb`, review hashes and native
`godot.json`. Actual Godot 4.7.2 headless imports pass. Run
`verify_ai_mesh_trial.py robot` or `... rook_combat` to validate producer/source
hashes, triangle counts, render hashes/sizes, Blender files and native GLB hash.
Both verifiers actually PASS. This proves artifact consistency, not usable art.

All four raw views for both subjects were visually inspected. Robot shape is
recognizable, with soft/deformed mechanical surfaces and missing fine details.
**Human art FAIL**: a large hallucinated plane intersects the lower legs, and
the face, clothing and weapon lose detail. It is deliberately visible in the
screenshots and retained in the sources. Neither output has final textures,
rigging, animations or gameplay-zoom validation. No production asset changed.

Raw Rook SHA: `499946bbe368b221276fc380b5012f26f225d32dab7aa1f8413622382db87815`.
Optimized Rook: `4767971792b515b26a36f2ce4075c945bd38f6ce5ca37b4736c6171a443b98db`.
Raw robot: `240b9ee73b20b55fba788c7e3210a6913eb48cc5929538b80eed552643940b12`.
Optimized robot: `7b93c0ab2554bc967ab3201742a0f80f54d0387f47f5cbbbe13a4c13758bc6b7`.

Requested trials: **2/2 generated, 10/10 renders, 2/2 native imports, 2/2
cross-artifact checks**. Existing kernel/guard/motion/TripoSR tests not repeated.
Next: qualify another human reconstruction or actual mesh cleanup, then colour,
materials and real combat-scale review. Hunyuan/TripoSG inference remains pending.
Broader experimental acceptance remains open: **CHANTIER GLOBAL INCOMPLET**.
