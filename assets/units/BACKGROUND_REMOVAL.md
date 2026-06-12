# Background Removal Log

- Date: 2026-06-09
- Scope: `*_512.png` unit assets in this folder
- Method: reused the matching 64x64 sprite alpha masks, scaled them to 512x512, and applied them to the corresponding 512px RGB renders
- Exclusions: `sample_agent_psi_compare.png` was left unchanged

## Validation

- Verified all `*_512.png` files are now `RGBA`
- Verified none of the `*_512.png` files remain fully opaque
