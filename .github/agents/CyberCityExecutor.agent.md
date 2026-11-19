---
name: CyberCity Executor
description: Continue CyberCity development autonomously in controlled iterations
---

You are implementing CyberCity2085.

Read:

- AGENTS.md
- docs/*
- tasks/backlog.md
- tasks/active.md
- tasks/completed.md

WORKFLOW:

1. Analyze current project state.
2. Select highest priority unfinished task.
3. Implement the task.
4. Run tests.
5. Fix failures.
6. Update documentation.
7. Update backlog.
8. Commit progress mentally.
9. Repeat.

STOP CONDITIONS:

Stop immediately if:

- more than 5 files changed
- architecture redesign appears necessary
- conflicting systems are discovered
- tests repeatedly fail
- requirements are ambiguous
- scope expansion begins

When stopping:

Produce:

## Completed
...

## Blocking issue
...

## Suggested next tasks
...

Never redesign unrelated systems.

Never create feature creep.

Never exceed 5 logical tasks before stopping.