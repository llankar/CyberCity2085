# Phase-aware objective instructions

The fixed objective brief previously displayed `[E] near marker` and a generic
interaction-contest warning for every objective, including defense, containment
and assassination. A small pure presentation helper now distinguishes actual
objective kinds/phases. Passive world markers use the same helper rather than
showing a meaningless interaction counter.

Defense displays the current turn and actual hold requirement from combat flags,
with its marked-zone exclusion rule. Containment displays the living-hostile
count and line/elimination instruction. Assassination directs the player to the
marked priority target. Interactive objectives retain progress and describe
one-AP, once-per-squad-turn interaction with nearby hostile clearance. Completed
sabotage during its hold window displays counterpush instructions; failed
objectives prioritize their actual failure message. No objective rule changes.

The defense and assassination prototype success conditions now also describe
their real completion requirement in briefing/report consumers. Assassination's
world prompt no longer inherits a generic interact-with-marker instruction.
The view supplies the same current turn/hold/living-enemy context to both HUD
presentations. Default context remains available for standalone rendering tests.

Tests cover all three passive kinds, actual defense count, containment count,
interactive/counterpush/completed transitions and failure priority, alongside
the existing objective/HUD suite. These establish instruction semantics, not
actual font fit or human visual playability. No desktop control is used. The
earlier R2 executable predates this correction.

Validation: **38 focused tests and three subtests passed**; the full suite passed
**826 tests and eight subtests**, without opening a visible game window.
