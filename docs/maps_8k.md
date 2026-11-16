# 8K map restoration

All 122 playable maps use restored images resampled to a width of 7680 pixels.
Heights retain the original aspect ratio (rounded to the nearest pixel): 16:9
art is 7680×4320 and 3:2 art is 7680×5120. Generated restoration images are
smaller than 8K; these assets must not be described as native 8K detail.
The accepted neon market restoration is reused unchanged as the visual source.

The production asset paths remain unchanged, so both the Arcade and Godot
clients load the new images through the existing map selection logic.
The diagnostic `preview_control_center_edges.png` is excluded.

## Obstacles

Every `.walls.json` keeps its original obstacle IDs, grid cells, normalized
outlines, sight-blocking flags and survey method. Only `image_size` and
`image_sha256` change. Manual `.wall-traces.json` files remain byte-identical:
their coordinates belong to their own `canvas_size`, not the output image.
They must not be multiplied by four or rescanned from the restored art.

`assets/maps/restoration_8k.json` records original image sizes and hashes,
restoration sizes, target sizes, output hashes, original obstacle fingerprints
and manual trace fingerprints. Exact-pixel duplicate maps share the same
restored image, with independent survey metadata.

Automated checks verify data alignment, not that generated textures preserve
every visual edge exactly. The accepted sample and contact-sheet inspections
are visual checks; individual obstacle contours may still need manual review.

## Verification

From the repository root:

```sh
python -m pytest -q tests/test_map_8k.py tests/test_map_geometry.py tests/test_battle_maps.py
```

The metadata-only helper is `tools/maps/refresh_geometry_metadata.py`.
Maps are loaded one at a time; an RGBA 7680×4320 texture is about 127 MiB before
mipmaps (roughly 169 MiB with a full mip chain), and 3:2 maps use more memory.
Keep graphics memory in mind when testing machines with integrated graphics.

Five maps use their original artwork resampled to 8K without generated
restoration, because the image tool rejected three distinct source interiors:

- `city_interior_safehouse.png`
- `wasteland_inner_03_ruined_clinic.png` and its exact duplicate `wasteland_inner_08_ruined_clinic.png`
- `wasteland_inner_04_bunker_command_post.png` and its exact duplicate `wasteland_inner_09_bunker_command_post.png`

Their obstacle data is preserved by the same metadata-only process.

## Overview sheets

The 122 restored/resampled maps can be reviewed without downloading every PNG:

- [Maps 1–24](maps_8k_previews/01.jpg)
- [Maps 25–48](maps_8k_previews/02.jpg)
- [Maps 49–72](maps_8k_previews/03.jpg)
- [Maps 73–96](maps_8k_previews/04.jpg)
- [Maps 97–120](maps_8k_previews/05.jpg)
- [Maps 121–122](maps_8k_previews/06.jpg)

## Completed verification — November 16, 2026

- 92/92 distinct image/survey pairs passed dimension, PNG CRC, image hash and
  original obstacle fingerprint checks before promotion.
- The 122-entry catalogue contains 117 restored/resampled maps and five
  resample-only maps identified above and in the provenance manifest.
- Focused regression suite: **24 passed** in 377.86 seconds. This includes
  recompiling every stored survey from its unchanged manual trace source,
  verifying exact duplicates, catalogue integrity and Godot wall projection.
- All six overview sheets were inspected for overall layout consistency.
  This is not an exhaustive visual collision-edge approval inside the game.
