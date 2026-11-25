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

IN_PROGRESS: original TRELLIS first real project-image generation. No generated
TRELLIS model or artistic acceptance is claimed until its evidence exists.
TODO: neutral render review, Blender source, Godot import if generation succeeds;
then compare a human trial before expanding production. TripoSG/Hunyuan technical
evaluation remains pending. CHANTIER GLOBAL INCOMPLET.
