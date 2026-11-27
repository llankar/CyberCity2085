# CyberCity 2085 — Release Candidate Checklist

Date: November 13, 2026

## Current Windows candidate · 183ee50c

- [x] Standalone build, Inno Setup compilation and silent installation on E:. The installed executable reports `183ee50c` and passes bundled Godot startup and test-save checks.
- [x] Four targeted source tests passed. The external native fog regression passed against the installed project, including the blocked patrol sector. The installed combat script matches source and the QA scripts are excluded.
- [x] The installed build passed WASAPI signal checks for movement, sniper fire and music, and injected gamepad checks for selection, movement, targeting and turn confirmation.
- [ ] Physical controller, human listening and visible installed handoff remain unverified.

Keep Setup and its three BIN files together in `E:/CyberCity2085-builds/cybercity-build-29400c3d2d15436292c1f8298ef9e1bb/dist/installer`.

| File | SHA-256 |
| --- | --- |
| CyberCity2085-Setup.exe | `33567BF626A858C667ED11375FEFF48077FEF62B3392F217506F74AD2585EDF4` |
| CyberCity2085-Setup-1.bin | `3F5DD8CEC509D1F6CABC5E588BD88039921C8A70884A8CD983CDEB22C520D869` |
| CyberCity2085-Setup-2.bin | `F1F6C476EA7FA8D45A766F0DD9B08E43239E4DE35A1742ADC6846256B39484CA` |
| CyberCity2085-Setup-3.bin | `381CBFCB187DA527FEFBA85E101F2BFE973192B45E71E8E292F3BC5D7D4BBA92` |

## Previous Windows candidate · 5522203a

- [x] PyInstaller build, Inno Setup compilation and separate silent installation on E:. The installed executable reports `5522203a`, starts bundled Godot, reads 122 maps and passes the test-save round trip.
- [x] Eleven targeted tests passed. The installed Godot also passed the external fog and tactical support regression. The three changed installed HUD/combat scripts match the checkout by SHA-256 and the bundle excludes Godot QA scripts.
- [x] External fixtures on installed Godot passed WASAPI signal checks for movement, sniper fire and music, plus injected controller selection, movement, targeting and turn confirmation.
- [x] Installed Godot restored player and enemy turns with robot and power armor support and returned containment victory and defeat. The checkout's campaign resolver applied both results once and rejected duplicate effects after save/reload.
- [ ] Physical controller and human listening remain unverified.

Keep Setup and its three BIN files together in `E:/CyberCity2085-builds/cybercity-build-436012bb1c7a47508e09b37e14dc2b31/dist/installer`.

| File | SHA-256 |
| --- | --- |
| CyberCity2085-Setup.exe | `F6C10A0F28ECED72AE3D9CA07C3D593C0108BD1FEA4B209F51C43DD7793AA8E9` |
| CyberCity2085-Setup-1.bin | `099B0DAE93A73A802586E8D7A90E4CC50805EEBF75A9BBE9A6A0046360676A39` |
| CyberCity2085-Setup-2.bin | `2CD12E112F408FF9641915235CC66EBE95AE505E3FBBBEBAF76B1E074D4CFAE3` |
| CyberCity2085-Setup-3.bin | `229099EF6F2FEB5C93122C4168B0CA42C863659B85B4E55BACCB364A5E86A5F2` |

## Previous Windows candidate · ee240a3e

- [x] Production build and silent installation on E:. The standalone installed executable reports build `ee240a3e`, starts bundled Godot, reads 122 maps, and passes the test-save round trip.
- [x] Targeted release gate: 92 tests passed. The full-campaign test was excluded.
- [x] Production bundle excludes Godot test drivers and combat source sheets.
- [ ] Human listening and physical controller acceptance remain open.

Setup and its three BIN files are in `E:/CyberCity2085-builds/cybercity-build-fa0884b7dc3f4a45b3c35a732a144ea6/dist/installer`.

SHA-256 for the installer set:

| File | SHA-256 |
| --- | --- |
| CyberCity2085-Setup.exe | `5AB5072D2D2AF212C053A626BB3059AD83524673095AD5B7B8A5C927F5C25F5F` |
| CyberCity2085-Setup-1.bin | `3B2CACC2BC6735D55BB6F850FE0D60E103EA4D1F5CB7947640E0920CAFDD6BB3` |
| CyberCity2085-Setup-2.bin | `302B3CC790405B3AA222A2F8F47CE27F1995100E3FF25918A5BEF9222DBC8DF4` |
| CyberCity2085-Setup-3.bin | `6F74F510B7B02369810816B54C1CADCA5CB9B4C1DF18FD491159C068E8E6687A` |

The installed Godot executable, tested tactical and audio scripts, and all 90 installed audio files match the previous candidate by SHA-256. The earlier mixer and injected-input results cover those matching components. Physical controls and listening still require observation.

## Previous Windows candidate · 44c9b5c6

- [x] Standalone build and separate silent installation on E:. Installed executable passes headless resource, test-save and Godot startup checks.
- [x] Installed Godot restores checkpoints in both phases and exports containment victory and defeat. The checkout's campaign resolver applies each result once across save/reload.
- [x] Installed WASAPI mixer produces signal for movement, sniper fire and music with the shipped audio files.
- [x] Installed Godot accepts injected controller events for unit selection, movement, targeting and turn confirmation.
- [ ] Physical controller check is blocked on this machine. Windows exposes a synthetic bus and the installed Godot enumerates zero joypads.
- [ ] Visible installed combat handoff, physical controller, and listening review remain unverified. Historical global tactical visual and full campaign checks do not gate this candidate.

QA build `e400dfdb` passed the frozen Windows data mission at 1280×720 from headquarters to debrief, promotions and return. A second run restored the enemy-phase checkpoint and finished the same path. This build contains test drivers and is separate from the production installer.

Storage maintenance ? 26 November 2026: at the owner's request, obsolete E: build/validation staging copies were removed. Retained production builds are `cybercity-build-6d87cffadf8f4cce979b274c4b94861d` and `cybercity-build-f93795d303ee435fb61065a9a9ede679` under `E:/CyberCity2085-builds`. Older executable paths below are historical and may no longer exist. This cleanup does not constitute a new production build or a new test result.


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

Latest local Windows build: `E:\CyberCity2085-builds\cybercity-build-dc37fff99f844d4daf5e954b4f8bd519\dist\CyberCity2085\CyberCity2085.exe` (2026-11-23), SHA-256 `371F8C35B099A5ED4AEBD2DCE460E6869D9008C2FD09BEC7C274A56C6D39901D`. Source checkpoint `7a259b0` preserves the full gate of 1218 tests, 36 skips and 14 subtests plus the post-gate quadruped slice of 25 passed/1 Windows-inapplicable X11 skip. The isolated package reused those gates with `-SkipTests`; smoke returned code 0 and the focused Combat Visual acceptance passed 22/22. The build label is `BUILD 7a259b00`, and the corrected quadruped JSON/PNG match source SHA-256 exactly. Physical Alt+Tab, multi-monitor DPI, controller and listening remain open and must not be inferred from these automated checks.

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
