# Panic memories and remaining pacing observations

The allied phase now records a real `panicked` status before action reset and
status ticking clear it. A living campaign agent retains one factual panic
memory per battle, and the existing structured-moment pipeline shows it with a
tense debrief tone. Existing trauma changes the reaction to a recurrence; an
ambition produces a determination-oriented response; otherwise the agent asks
for cover. No trauma text is invented or new stress/relationship bonus applied.

The existing penalty is unchanged: the panicked activation has zero AP, the
one-turn status clears, and the next normal reset restores normal AP. Repeated
panic does not duplicate history during the same battle. This adds text feedback
and persistence through the existing history/report schema, not a new panic
mechanic or recorded voice. External Godot combat is not integrated here.

Separately, real phase traces were captured for the four remaining 60-turn
limited cases. A diagnostic with a 100-turn observation ceiling finds:

| Map/objective | Terminal turn |
| --- | ---: |
| Rooftop access / recon | 66 |
| Power substation / recon | 61 |
| Power substation / containment | 67 |
| Ruined downtown / extraction | 61 |

All four end in victory with legal geometry. Late-turn snapshots show travel,
objective progress or damage, rather than a static stall. These results diagnose
slow routes/combat; they **do not replace the 60-turn gate**, convert those four
limits to passes or justify raising the gate. See [measured cases](../qa/remaining_four_extended_diagnostic.json).
The diagnostic predates the panic-memory change and retains its own source and
survey fingerprints. Pacing and full-current-source coverage remain open.

Validation: **807 tests/eight subtests passed** in the full suite; after extending
the trauma/ambition assertion, **20 focused moment/narrative tests passed**.
The actual phase test checks zero AP, status clearing, subsequent recovery,
duplicate control and debrief tone. No visible window or desktop control was used.
