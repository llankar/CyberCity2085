# Neon market 8K experiment

Isolated test only: the production map and game defaults are unchanged.

The restored image was generated from `assets/maps/city_exterior_neon_market_alley.png`.
The generator returned 1672×941, not 8K. Lanczos resampling produces the requested
7680×4320 file, but does not provide native 8K detail. This experiment must not be
presented as solving close-zoom blur.

The adjacent `.walls.json` retains all original obstacle IDs, grid cells and
normalized outlines exactly. Only image name, dimensions and SHA-256 change,
allowing the existing geometry loader to validate this independent image.
No obstacle rescan is performed. Generated art may shift local contours, so
visual collision alignment remains unapproved despite data equality.

Validate from the repository root with `PYTHONPATH=. python experiments/map_8k_test/validate.py`.
For a manual trial, use this image's path in a copied mission handoff together
with its geometry and camera zoom around 0.9. Do not replace the production art.
