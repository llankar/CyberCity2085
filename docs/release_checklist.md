# CyberCity 2085 — Release Candidate Checklist

Date: November 13, 2026

## Current tactical retrofit status — November 15, 2026

The earlier candidate is preserved. Current R2 evidence is
[documented separately](qa/windows_candidate_20261115_r2.md):

- [x] R2 build-gate suite: 785 passed, eight subtests passed.
- [x] Isolated Windows candidate builds and its actual executable passes a window-free resource/save/combat smoke.
- [x] Portable ZIP has validated CRCs, SHA-256 and reports; active Godot handoffs/editor caches are excluded.
- [x] Fifteen actual story templates execute at three seeds with corrected objectives: 45 victories, no limits or geometry errors.
- [x] Complete the R2 pre-pilot 1,098-case matrix: 958 wins/118 defeats/22 limits, exact coverage and survey hashes verified. See [report](qa/authored_r2_full_matrix.md).
- [ ] Resolve the remaining pacing limits and verify later pilot fixes across appropriate mixed-team scenarios; the fixed-rifle R2 snapshot does not certify those fixes.
- [ ] Validate current mixed/understrength squads, support footprints and campaign balance.
- [ ] Perform current graphical keyboard/mouse, visual and audio playthrough validation.

The retrofit goal remains active; no desktop control was used for the new checks.

Current local Windows build: dist/windows-current/CyberCity2085/CyberCity2085.exe. Release gate: 1,145 passed, 35 skipped, 12 subtests passed. Bundled Godot 4.6.3 headless startup and save reload passed. Native graphical acceptance remains open.

## Automated gates

- [x] New game state can progress through all 15 authored story missions.
- [x] Act V resolves to a deterministic ending with named agent epilogues.
- [x] Current and legacy saves load; campaign, intel, scars, assets, faction
  tags, mission-board state, and endings round-trip.
- [x] Arcade remains a complete fallback when Godot is unavailable.
- [x] Godot handoff schema is validated before JSON is written.
- [x] Battle actions use distinct icons; camera pan is bounded and Home focuses
  the active unit.
- [x] Semantic-theme and release-screen architecture contracts pass.
- [x] Canonical test suite passes.
- [x] Test-gated Windows onedir package builds.
- [x] Packaged executable survives the startup smoke window.

## Player-path checks performed at 1920×1000

- [x] Title and new-campaign setup are readable.
- [x] Management rooms, weekly command planning, squad selection, recruitment,
  and the responsive command cards are usable.
- [x] World map, mission consequences, tactical preflight, deployment, and live
  Arcade combat are readable.

## Known 1.0 limitations

- Godot is an optional presentation client. Arcade is the authoritative,
  finishable tactical path until the Godot result round trip is fully proven.
- The large Arcade `BattleView` remains in `game/views.py` for compatibility;
  new screens belong in `game/ui/screens/`.
- Balance across a human-played five-act campaign still benefits from community
  feedback; automated progression proves reachability, persistence, and ending
  resolution rather than subjective difficulty.
- Windowed play at 1920×1000 is the visually validated target. Smaller layouts
  are responsive but have not received the same exhaustive visual pass.

## Release command

Run `powershell -ExecutionPolicy Bypass -File tools/build_windows.ps1` from the
repository root. The playable package is written to
`dist/CyberCity2085/CyberCity2085.exe`.
