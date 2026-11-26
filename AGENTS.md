# CyberCity 2085 Agent Rules

You are developing CyberCity2085.

Priorities:

1. Emergent storytelling
2. Emotional attachment
3. Modularity
4. Maintainability
5. Scope control

Never:

- create giant systems
- add features outside roadmap
- rewrite architecture unnecessarily
- create placeholder spaghetti code

Always:

- update documentation
- update backlog status
- create tests
- explain decisions

Agents are the emotional core.

Prefer:
small memorable systems
over
large shallow systems.

## Long-running work: continuity and acceptance

- A project may contain any number of successive batches, subject to the available session, tools, resources and budget.
- Completing a batch never means that the global objective is complete.
- At every resumption, read `docs/CODEX_PROGRESS.md`, inspect the actual repository state and continue from the first unfinished task.
- Maintain that persistent register using `TODO`, `IN_PROGRESS`, `DONE` and `BLOCKED`. Each task records affected files, tests actually executed, available evidence, remaining work and any explicit blocking reason.
- After every batch, save validation evidence, update the register, identify the next batch and create a regular Git checkpoint on the working branch.
- Continue automatically with the next batch while the session, tools and budget permit. Do not ask for unnecessary confirmation merely because a batch has ended.
- Do not declare a global objective complete until every mandatory acceptance criterion is verified with concrete evidence.
- Passing tests prove only what they actually cover. Report missing resources, tests not executed and absent artistic validation explicitly.
- On a blocker, quota or interruption, preserve the state and report `BLOQUÉ` or `INCOMPLET`, never `TERMINÉ`.
- Preserve the existing quality, modularity and scope rules across all batches.

## Mandatory balance before a final completion statement

Before claiming completion, reread the objective, `docs/CODEX_PROGRESS.md` and, for Combat Visual, `docs/COMBAT_VISUAL_ACCEPTANCE.md`. Run the documented reproducible acceptance check and inspect its evidence. Record:

- completed tasks / total tasks, keeping batch completion distinct from global completion;
- maps with verified native loading / expected maps, separately from artistically finalized maps;
- complete artistic resources and animation sets / expected coverage, with unknown expectations explicitly stated;
- tests passed, failed, skipped and not executed, within the recorded scope;
- every acceptance criterion still open and the exact next action.

If any mandatory criterion is open, report exactly `CHANTIER GLOBAL INCOMPLET`. Missing evidence is `NOT VERIFIED`, never an assumed `PASS`. A reproducible failure is `FAIL`; `DONE` requires both execution and verification. An automated load or frame-count check cannot stand in for artistic review.

## Storage hygiene (owner instruction, 2026-11-26)

- Regularly remove obsolete build workspaces and regenerable intermediates on E:.
- Under `E:/CyberCity2085-builds`, retain the current and previous production builds; old validation results alone are not a reason to retain large staging copies.
- Preserve the selected active source assets, AI weights, working environment, current work and current delivery; prune superseded experiments when the owner requests only necessary files. Before cache cleanup, inspect environment symlinks into that cache and materialize required dependencies. Use hardlinks/copies for active environments, never links into disposable caches.
- Retain completed MP4 references; obsolete native AVI intermediates may be removed once their retained video is complete. The gallery packager can reuse the MP4 without re-encoding it.
- Before recursive removal, resolve explicit paths within the intended root, reject reparse points, and check that no active job needs the target. Report reclaimed space, not long validation summaries.
