# Experimental human asset selection

Status: IN_PROGRESS, 2026-11-24. No production changes. No further generic MPFB
armor recoloring. First convincing human must pass before character production
is generalized. MPFB anatomy remains optional, not the artistic ceiling.

## Candidate register

| Resource | Source and declared license | Evidence / decision |
| --- | --- | --- |
| Cyberpunk character, 4d_Bob | https://sketchfab.com/3d-models/019f4b3fd3c74ed0bc6c8dbe9cd50d51 ; CC BY 4.0 | Public API verified commercial use/attribution, downloadable, 24,500 faces, one animation. Author says rig was made for posing and may need replacement. Acquisition BLOCKED: download endpoint HTTP 401 without authentication. Artistic/rig validation NOT VERIFIED. Priority candidate. |
| CyberPunk Character, AlekseiPresnaykov | https://sketchfab.com/3d-models/bd161bb708a941f0b436c2e95eafc755 ; CC BY 4.0 | Public API verified commercial use/attribution, downloadable, 51,704 faces, zero animations. Acquisition HTTP 401. Rig, textures, modularity, origin and visual fit NOT VERIFIED. Priority candidate. |
| Soldier uniform, Marko1937 | https://sketchfab.com/3d-models/1047140aa64b4c0e923e1f20306eb625 ; page CC Attribution | Page lists 26.9k triangles, two camouflage patterns, 4K atlas. Vest/pouches/belt candidate; download and file-level license/provenance inspection TODO. |
| Tactical Gloves, DenisKorablyov | https://sketchfab.com/3d-models/45f9e55f493142a99b1673e4da1a4119 ; page CC Attribution | Candidate only; finger topology, rig fit and textures NOT VERIFIED. |
| Low Poly Female Tactical Vest, Paz | https://sketchfab.com/3d-models/7fd8a5c287624ba8975a9a6d0a1ac154 ; page CC Attribution | Author states modeled in Blender/textured in Substance; 10.3k triangles. Candidate for modular fitting, not yet downloaded. |
| Realistic Brown 3D Hair, Cinemorph.org | https://sketchfab.com/3d-models/c00848897b7f46da803d20dbc8f19861 ; page CC Attribution | Candidate only; hair cards, transparency, scalp fit, Rook silhouette and provenance need inspection. |
| Rain / Snow, Blender Studio | https://studio.blender.org/characters/ ; CC BY on character cards | Production-quality rig/anatomy reference, stylized art. Not selected as Rook. Current Rain v4 requires Blender 5.2 per card; installed version is 4.5.17. Earlier compatible version and exporter test needed before acquisition. |
| PBR leather/fabric/metal, Poly Haven | https://polyhaven.com/license ; CC0 | Suitable material library. Select actual maps only after clothing UV/texel-density review; no bulk download. |

CC BY adaptation/distribution requires attribution, license link and identification
of modifications. Keep creator, exact source, license and file hashes with acquired
assets. The uploader's license alone does not establish rights to third-party
characters: reject game rips, fan-character likenesses and uncertain provenance.
File-level checks remain required before integration or distribution.

Rejected: Oscar Creativo cyberpunk character and KIFIR Kirza boots (NonCommercial);
Judy Alvarez / Leon Kennedy reproductions (third-party character rights); generic
Kenney/Quaternius humans as final art (visual target mismatch); print-only posed
sculpts as animation-ready characters. Boots, detailed faces, weapons, mechanical
accessories and full modular armor still need qualified selections.

## Acquisition and acceptance

Additional inspected candidate: [Cyberpunk Samurai by Fajrul FN](https://fajrulfn.itch.io/cyberpunk-samurai).
Official free download acquired solely for inspection on E: (137,811,341 bytes;
SHA256 E12FE1F308374B443F339B3FCE4C06BB536490BC962877F78A90C1736FDF0A4C).
Archive has 36 files, modular body/clothing/gear, 18 declared PBR textures and
Blender/FBX sources. Blender inventory executed with embedded scripts disabled:
221-bone rig, separate jacket/head/hair/hands/legs/bag/weapons, 15 image blocks.
No license file, no Blender text block, no explicit adaptation/distribution grant
found on the page. Same creator has a paid Fab listing; its terms are not assumed
to cover the itch download. Status: RIGHTS NOT VERIFIED, quarantined from demo
and distribution. Do not export/adapt or claim this as the accepted human.

SCARLET PROXY excluded pending clarification: page mixes CC BY / CC BY-SA labels
and additional social-account requirements. Free availability alone is insufficient.

Use official download/API flows. Never extract protected viewer payloads to bypass
authentication. No paid purchase authorized. Authentication is a source-specific
blocker, not a blocker for the whole experiment.

For each acquired candidate: inspect neutral front/profile/back, textures and UVs,
rig/bone deformation, silhouette at actual combat zoom, weapon/grip/gear attachment,
triangle/material/texture memory costs and GLB roundtrip. Compare directly against
current sprites at identical screen pixel height. Do not claim professional quality
from a marketplace description or a successful import.

## Next work

- IN_PROGRESS: acquire/inspect first qualified authored human; no mass production.
- TODO: complete experimental tactical scene with existing map, human, robot,
  vehicle and furniture. Current comparison stage is not this deliverable.
- TODO: reproduce production viewport/zoom and create sprite/mesh comparison.
- TODO: final human and robot screenshots after actual artistic review.
- Preserve robot/hardsurface experiments; production game and main GOAL untouched.
