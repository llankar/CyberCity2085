# Windows tactical candidate — 2026-11-15

This candidate includes the local uncommitted tactical work based on `6fc2d67`.
It is a reviewable working build, not a declaration that the retrofit is complete.

## Artifacts

- Executable: `dist/tactical-candidate-20261115/CyberCity2085/CyberCity2085.exe`
- Portable archive: `dist/CyberCity2085-tactical-candidate-20261115.zip`
- Archive size: 681,582,001 bytes, approximately 650 MiB.
- Checksum: `dist/CyberCity2085-tactical-candidate-20261115.zip.sha256`

Archive SHA-256:
`8826dd74bf2c5a318cd5a37dde2b902c1098111de9d01b6192c5514c654571ca`

Executable SHA-256:
`1b5446270ad35ae29650c8a97857f771997e155b39cb957ba235561bc833d901`

Extract the whole archive, then launch `CyberCity2085/CyberCity2085.exe`. Keep its
asset/library directories beside the executable. The archive includes French
instructions, a validation manifest, packaged-smoke results and all 1,098 authored
battle rows. The older `dist/CyberCity2085` build was preserved.

## Build and verification

```
powershell -NoProfile -ExecutionPolicy Bypass -File tools/build_windows.ps1 -OutputDirectory dist/tactical-candidate-20261115
python main.py --smoke-test --smoke-report runtime/source_smoke.json
```

The build script runs the entire suite: **735 passed, eight subtests passed**,
then packages with PyInstaller 6.16.0/Python 3.12.10 and runs the actual frozen
executable with `--smoke-test`. No Arcade import or game window is needed for this
path; a subprocess regression explicitly blocks Arcade imports. Normal launch
still follows the graphical title-screen path.

The source and frozen smoke both verify all 122 reviewed map surveys, seven MP3
files, a campaign save/load using a temporary directory, and a legal terminal
reference-engine battle on the docks. The packaged battle ended in victory on
turn 23. These checks do not claim that MP3 playback or GPU rendering was heard
or visually reviewed. No player save is opened or modified.

Godot project/scripts remain bundled, but editor caches and live runtime handoffs
are excluded. The previous spec copied an active `mission_handoff.json`; it is
absent from the final candidate. Source files were preserved. A fixture regression
checks this selection rule, and the actual packaged directory was inspected.

The ZIP was opened and every member's CRC checked successfully. Its manifest
records the executable hash, combat-source fingerprint, test totals and measured
battle outcomes. This verifies archive integrity, not deterministic byte-for-byte
rebuilding or graphical startup on every Windows machine.

## Open release gates

The [authored battle matrix](authored_battle_baseline.md) completed with 947 wins,
118 defeats and 33 turn limits. Those limited cases, mixed/understrength squads,
support footprints, campaign pacing, graphical interaction and visual/audio
playthrough remain open. The goal stays active. No desktop control was used.
