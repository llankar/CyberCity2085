# Experimental 2D to 3D progress

This register is separate from the principal CyberCity 2085 GOAL.

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

