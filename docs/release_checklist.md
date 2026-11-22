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
  The current bench now creates agents through the real role-biased recruitment path, applies one conservative signature-stat point per completed level, limits self-aid to once per medic turn, rejects attacks with zero hit/damage value, keeps one pursuit target and uses overwatch instead of passive defense when appropriate. Across the 14 current 60-turn limits, replay to turn 100 produces nine late victories, three late defeats and two continuing combats. Neither persistent case is static (longest unchanged streak: five rounds). The production cap was not raised to hide them.
- [x] Validate current mixed/understrength squads, support footprints and campaign balance. Current-source QA uses real deployment manifests and recruited role statistics for mixed, two-agent, robot/drone-support and piloted-armor profiles. Across 122 authored elimination maps at risk 5/count 6: mixed 102 wins/20 defeats/0 limits; understrength 119 defeats/3 limits; support 113 wins/8 defeats/1 limit; piloted armor 2 wins/110 defeats/10 limits. This deliberately harsh matrix confirms that two-agent and three-body piloted squads are not balanced for maximum-risk six-hostile missions, while also removing the old generic-stat and zero-value-action bias against normal squads. Across the 15 authored story templates, mixed and support profiles win 15/15, piloted armor 14/15 and understrength 14/15. Single-cell support occupancy is verified on all maps; multi-cell footprints are not a production feature. The remaining 60-turn pacing cases stay tracked by the preceding open item and are not hidden.
- [ ] Perform current graphical keyboard/mouse, visual and audio playthrough validation.

The retrofit goal remains active; no desktop control was used for the new checks.

Latest local Windows build: `E:\CyberCity2085-builds\cybercity-build-f7747d62f839433e85ee9c30bf9c172a\dist\CyberCity2085\CyberCity2085.exe` (2026-11-22), SHA-256 `1F8864EF818072560782BF3D1D8280C9F385D1E592DEA5CB2D8C1D67ACA3E9B0`. The isolated source gate passed 1216 tests, 36 skips and 14 subtests with no failures. Packaged smoke passed with 122 maps, 7 MP3 tracks, 15 story objectives, save round-trip, tactical victory and bundled Godot 4.7.2 startup. Physical Alt+Tab, multi-monitor DPI and listening remain open and must not be inferred from these automated checks.

Previous local Windows build: `dist/windows-runtime-06377fd/CyberCity2085/CyberCity2085.exe`. Production build 06377fd bundles the allied VTOL atlas and the corrected financial debrief. The bundled Godot passed the native Dust Road VTOL fixture, headless startup and save reload. The source Arcade build with bundled Godot completed an unforced 720p victory on data_theft_d1_s2: mission funds +75, corporate balance +113, promotions, HQ return, save reload and duplicate reward rejection. A graphical campaign run on this production build remains open.

Current E-isolated candidate: `E:/CyberCity2085-builds/cybercity-build-0d0d402a7cbb4e129d003357b77412d8/dist/CyberCity2085/CyberCity2085.exe`. The complete gate passed 1,164 tests, skipped 35 platform-inapplicable tests and passed 14 subtests. The packaged headless smoke passed with bundled Godot 4.7.2, 122 maps, 15 story objectives and save round-trip. Native graphical acceptance remains open.

Previous local Windows build: dist/windows-current/CyberCity2085/CyberCity2085.exe. Baseline release gate: 1,145 passed, 35 skipped, 12 subtests passed. The later Windows result-read retry passed 23 targeted tests and was included in the rebuilt production executable. The production executable rejects the QA entry point. Bundled Godot 4.6.3 headless startup and save reload passed. Arcade and bundled Godot each opened a responsive native window from an independent working directory. The integrated graphical playthrough of this build remains open.

Packaging regression: the production executable now includes Arcade 3.3.3 version metadata as a readable file. Nine packaging tests and the packaged headless smoke passed.

- [x] One native Windows QA package campaign completed all 15 authored missions with Godot, reloaded the final save and displayed Dawn Without Masters with named epilogues.

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

Pass `-ScratchRoot E:\CyberCity2085-builds` to keep the package, build
intermediates, cache, and process temporary files together on `E:`. The
directory must already exist. Each invocation creates a fresh
`cybercity-build-<id>` directory and prints the verified executable path.
