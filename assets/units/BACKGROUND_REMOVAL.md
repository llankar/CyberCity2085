# Background Removal Log

- Date: 2026-06-09
- Scope: `*_512.png` unit assets in this folder
- Method: reused the matching 64x64 sprite alpha masks, scaled them to 512x512, and applied them to the corresponding 512px RGB renders
- Exclusions: `sample_agent_psi_compare.png` was left unchanged

## Validation

- Verified all `*_512.png` files are now `RGBA`
- Verified none of the `*_512.png` files remain fully opaque

## Generated Token Batch

- Date: 2026-06-12
- Scope: 100 new unit tokens, with matching `512x512` and `64x64` PNG exports
- Categories: mutants, starvers, raiders, mutant animals, giant combat robots
- Method: generated 5 category sheets, extracted 20 isolated units per category, removed chroma-key backgrounds, recentered each token, and exported transparent `RGBA` PNGs
- Manifest: `generated_token_manifest.json`
- Test: `python test_generated_token_assets.py`

## Generated Objective Token Batch

- Date: 2026-06-12
- Scope: 20 new mission objective tokens, with matching `512x512` and `64x64` PNG exports
- Categories: city mission objectives, wasteland mission objectives
- Method: generated 2 objective sheets, extracted 10 isolated props per category, removed chroma-key backgrounds, recentered each token, and exported transparent `RGBA` PNGs
- Manifest: `generated_objective_token_manifest.json`
- Test: `python test_generated_objective_token_assets.py`

## Generated Vehicle Token Batch

- Date: 2026-06-12
- Scope: 60 new vehicle tokens, with matching `512x512` and `64x64` PNG exports
- Categories: terrestrial civilian vehicles, terrestrial military vehicles, aerial civilian vehicles, aerial military vehicles, crashed aerial civilian vehicles, crashed aerial military vehicles
- Method: generated 6 vehicle sheets, extracted 10 isolated vehicles per category, removed chroma-key backgrounds, recentered each token, and exported transparent `RGBA` PNGs
- Notes: aerial civilian and aerial military batches include at least 4 VTOL tokens; each aerial vehicle has a crashed token with the same index
- Manifest: `generated_vehicle_token_manifest.json`
- Test: `python test_generated_vehicle_token_assets.py`
