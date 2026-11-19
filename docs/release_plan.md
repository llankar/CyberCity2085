# CyberCity 2085 — Release Plan

## Release target

Ship a small, complete single-player campaign that can be launched from a clean
checkout, played through five acts, concluded with an explicit ending, saved and
loaded reliably, and distributed with clear setup instructions.

The release keeps the current hybrid architecture:

- Python and Arcade own campaign state, management, rules, saves, and the
  fallback tactical battle.
- Godot remains an optional tactical presentation client until it can return a
  complete, versioned mission result to the Python campaign.
- The Arcade fallback must remain capable of completing every required mission.

This decision avoids a high-risk rewrite. The existing Python game already owns
the tested rules and campaign shell, while the Godot client still has an
incomplete return path. A full engine migration is therefore outside the 1.0
scope.

## Audit baseline — 12 November 2026

This section records the state found at the beginning of release work. The
current verified state is summarized immediately below so historical failures
are not mistaken for present limitations.

## Current release evidence — 13 November 2026

- All five acts contain exactly three authored story missions and lead to an
  explicit, state-derived finale with named agent epilogues.
- Legacy and current saves have focused migration and round-trip coverage.
- The canonical suite passes 462 tests plus 8 subtests.
- Management command cards, recruitment, world map, briefing, deployment, live
  Arcade combat, and tactical preflight were visually checked at 1920×1000.
- The Windows onedir package builds after tests and its executable survives the
  startup smoke window.
- The authoritative performed checks and honest limitations live in
  [`docs/release_checklist.md`](release_checklist.md).

- The repository contains a broad management and tactical prototype with a
  five-act campaign model, story missions, agent aftermath, relationships,
  strategic systems, saves, and two combat presentations.
- The active worktree's enemy-AI upgrade is part of the release baseline, not
  deferred work: target scoring, cover seeking, flanking, commander buffs, and
  defensive-objective pressure are covered by 18 passing focused combat tests.
- `python -m pytest tests -q` executes 419 tests: 404 pass and 15 fail at this
  baseline. The failures cover recruitment-role expectations, headless Arcade
  stubs, one missing generated map set, one localisation expectation, and one
  screen bypassing semantic theme tokens.
- Plain `pytest` previously collected the duplicate `cybercity2085_push/` tree
  and failed during collection. The root `pytest.ini` now defines the canonical
  suite and import path.
- Acts I–IV can advance. Act V cannot conclude: its advancement threshold is
  `999`, and campaign state has no explicit ending outcome.
- The original campaign thresholds exceeded the authored mission count. The
  release campaign now targets three distinct story missions per act (fifteen
  total), so progression is earned through playable narrative content rather
  than lowered gates or hidden counters.
- Godot can receive mission handoff data, but result import is not a complete
  production loop. Arcade is therefore the release-safe combat path.
- The backlog and generated roadmap contain completed items mixed with stale
  priorities; release work needs a small authoritative gate list.

## Definition of done for 1.0

1. A new player can start, understand the next action, recruit/select a squad,
   launch missions, resolve consequences, progress through all five acts, and
   reach a visible final outcome.
2. The ending is derived from accumulated campaign choices and world state,
   not from a single arbitrary last click, and names surviving agents or their
   legacy so the emotional core is preserved.
3. Save/load preserves all information required to resume before and after the
   finale, including backward-compatible loading of older saves.
4. The canonical automated suite passes, plus a headless full-campaign smoke
   test covering start to ending.
5. The default presentation is coherent and readable at the supported window
   size; no release-path screen bypasses semantic theme tokens.
6. A clean-machine launch path and a distributable build are documented and
   verified. Godot is optional unless its round trip is fully proven.
7. No blocker or critical data-loss bug remains in the documented release path.

## Ordered release slices

After the finishability and quality gates, development is deliberately centred
on two equal pillars: strategic management and tactical combat. Narrative and
visual polish must make those pillars more legible, consequential, and exciting
rather than becoming separate feature layers.

### Slice 1 — Make the campaign finishable

Create a compact campaign-ending domain model, deterministic outcome evaluation,
Act V completion trigger, save compatibility, ending presentation, and a
headless campaign-completion test. This is the highest priority because every
other polish task otherwise improves a game that cannot be finished.

### Slice 2 — Restore the quality gate

Resolve the 15 known failures by fixing production regressions where behavior is
wrong and updating stale tests only where an intentional design change is
documented. Generate or restore required map assets. Keep the canonical suite
green from this slice onward.

### Slice 3 — Strategic management with pressure and payoff

Turn the management hub into a readable command surface: expose projected
income and upkeep, mission opportunity cost, district/faction consequences,
agent readiness, and the next looming threat before commitment. Add a compact
weekly planning decision with genuine trade-offs by composing existing funds,
research, events, squad recovery, and assets rather than creating a second
economy. Polish room transitions, hierarchy, feedback, and state changes so the
base feels responsive and alive.

### Slice 4 — Tactical identity, readability, and spectacle

Build on the active enemy-AI upgrade with faction-specific tactical profiles,
clear intent telegraphs, stronger cover/flank/objective feedback, and encounter
composition that makes story missions play differently. Improve battlefield
depth, unit readability, action feedback, camera motion, and mission atmosphere
using the existing combat engine, maps, audio, particles, and shaders. Every
visual effect must clarify threat, action, or consequence.

### Slice 5 — One coherent visual language

Remove remaining direct palette access from release-path screens, standardize
typography and spacing, and perform a visual pass on title, management, mission
briefing, battle, debrief, act transition, and ending. Prefer existing assets,
shaders, motion, and semantic tokens over adding another UI framework.

### Slice 6 — Emotional continuity

Surface a small number of persistent agent memories in briefing, recovery,
debrief, and the finale. Reuse relationships, scars, reputation, nicknames, and
mission history rather than adding a new simulation system.

### Slice 7 — Package and release

Verify clean setup, saves, fallback combat, full campaign smoke flow, and build
packaging. Publish launch, controls, troubleshooting, and known-limitations
instructions. Produce a versioned release candidate and complete a manual
playthrough checklist.

## Visual QA and packaging batch — 12 November 2026

Completed as a five-task release slice:

1. `[x] UI-QA-01` Wrap difficulty descriptions inside their setup cards.
2. `[x] UI-QA-02` Add restrained F1-F6 room nameplates to the collapsed base.
3. `[x] UI-QA-03` Remove duplicated recruitment feedback from the downtime panel;
   the existing footer/toast remains the single feedback surface.
4. `[x] PKG-01` Add an onedir PyInstaller specification that includes assets,
   scenes, and the optional Godot project without making Godot mandatory.
5. `[x] PKG-02` Add a test-gated PowerShell build command, packaging tests, and
   player-facing build instructions.

Manual QA covered title/setup, collapsed base, command planning, squad/recruit
management, and the world mission map at 1920×1000. The following tactical
batch extended that validation through briefing, deployment, and live combat.

## Tactical deployment continuity batch — 13 November 2026

Completed as a five-task slice: role-specific starter kits, automatic open-slot
squad assignment, visible armed/readiness preflight, enemy-doctrine preview,
and visual QA from recruitment through live Arcade combat. The QA pass also
changed large recruit pools to a readable 3-column grid and converts rich
mission tags into short player-facing labels. District pressure and success /
failure fallout are now formatted as readable consequences rather than raw
data or clipped lines. The rebuilt Windows distribution passed 448 tests plus
8 subtests. This borrows XCOM/Zero Company’s
clarity of commitment while keeping CyberCity’s existing rules and architecture.

## Iteration rule

Each implementation slice is split into no more than five tasks. Every slice
must include focused tests, documentation updates, backlog status updates, and a
playable or headless validation appropriate to the change.

## Management command-card polish — 13 November 2026

Completed as a five-task slice after direct player feedback: squad capability
coverage, recovery-load forecasting, responsive command-card layout, semantic
button hierarchy, and visual QA. The old oversized square tiles and detached
labels are replaced by compact cyber-command cards with integrated iconography,
labels, category captions, accent rails, shadows, and clear primary / danger /
system states. Command Core and the eleven-action Squad Ops layout were checked
at 1920×1000, along with the enriched tactical preflight. The rebuilt Windows
distribution passed 450 tests plus 8 subtests and a packaged-executable smoke run.

## First implementation batch (maximum five tasks)

1. `RELEASE-01` — Add a serialisable campaign-ending state and deterministic
   outcome evaluator based on world state, intel, faction pressure, and agent
   survival/legacy.
2. `RELEASE-02` — Trigger the finale after the required Act V story missions and
   prevent further campaign ticking once resolved.
3. `RELEASE-03` — Add an ending presentation reachable from the management flow,
   with outcome, world consequences, and named agent epilogue lines.
4. `RELEASE-04` — Cover old-save migration, final-state round trips, Act V
   completion, and a start-to-ending headless campaign smoke path.
5. `RELEASE-05` — Update player-facing run/progression documentation and mark the
   batch complete only after focused and canonical test gates pass.

## Tactical reliability and handoff contract — 13 November 2026

Completed as a five-task release slice: legacy-save migration coverage, a
versioned and validated Godot handoff contract, bounded tactical camera pan,
active-agent recentering, and dedicated code-drawn combat-action icons. These
changes improve tactical readability without introducing a new UI framework or
rewriting combat architecture. Focused and canonical test gates, documentation,
Windows packaging, and executable smoke validation close the slice.
