# Tactical release evidence audit — R2

This audit distinguishes implemented subsystems from proof that the whole
retrofit meets the original release objective. Historical slice headings marked
completed do not certify current graphical playability or overall balance.

| Requirement | Current authoritative evidence | Remaining proof/work |
| --- | --- | --- |
| End-to-end local tactical loop | Actual-engine attack through Arcade battle-end, debrief, management and temporary campaign save/load in `test_static_game_flow_e2e.py` | Full visible input/playthrough and broader objectives |
| Differentiated story missions | Corrected objective cloning, shared story conversion; 45 independent actual-template/map simulations in `story_tactical_summary.json` | Continuous squad/campaign consequences across all fifteen played missions |
| Terrain and openings | Strict manual surveys on 122 maps; clinic bounds; defense/containment placement tests at three sizes | Authored-art fidelity outside the two reviewed clinic margins; support-unit footprints |
| Coherent faction AI | Real phase tests for corporate links, Raider/Starver movement, mutant control and precision locks; selected mixed-team action integration | Remaining enemy-plan stages and sustained mixed-team counterplay |
| No obvious dominant decision | Two fixed rifle policies, open/cover fixtures and faction/budget sweeps; selected roles/robots execute distinct actions in one engine fixture | Role/equipment alternatives in sustained encounters and meaningful human tactical choice; integration tests do not establish this |
| Emotional agents | Trait/fear clutch reactions, bond-sensitive aid/loss memories, actual persistence and prioritized debrief lines | Panic/scar/ambition coverage and deliberate relationship/reputation consequences |
| Professional, readable UX and effects | Captured HUD geometry/labels, targeting regression tests, map overlays and action feedback code | Actual rendered layout, keyboard/mouse, camera, pacing, accessibility and audio verification |
| Stable saves | Temporary real campaign roundtrips, legacy defaults, story progression after each mission outcome | Continuous played campaign with actual injuries, losses, replacements and spending |
| Windows distribution | R2 portable ZIP, CRC/SHA, 785 build-gate tests and frozen headless smoke | Graphical startup and playthrough of this executable; refresh after later source changes |
| Backlog closure | Active partial enemy/story/release tasks explicitly remain in `tactical_backlog.md` | Implement and verify those items; goal cannot close on test totals alone |

The 576-case R2 synthetic-objective sweep completed with **471 victories and
105 defeats**, no limits/errors. It covers eight objective families, six themes,
three danger settings, two policies and two layouts at seed zero. Exact input
coverage and source fingerprint were checked. See
[derived counts](objectives_r2_synthetic_summary.json). All allies are rifle
agents; this does not cover every allied role/action or campaign support asset.
Containment remains difficult: 58 defeats/72 cases in this sweep. Increasing
win rate alone is not a release criterion.

The source fingerprint is the same as the corrected story sweep. The complete
authored 1,098-case R2 matrix completed against the pre-pilot identity snapshot:
958 wins, 118 defeats, 22 limits, no geometry errors. Exact coverage and survey
hashes were checked; see [full report](authored_r2_full_matrix.md). This does not
certify later pilot corrections. Older subset results cannot be combined into
that total. No desktop control is used for these checks.
