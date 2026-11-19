# Defense approach and visible breach zone

Defense encounters now place hostiles at least four cardinal movement steps
from every walkable cell in the objective's breach square. Distances follow the
authored walls, so a nearby enemy behind a wall can remain if its actual approach
is long enough. Objectives and obstacles are preserved; placement never opens
a wall or relaxes the bound to fit additional enemies.

Four steps exceed two normal AP plus the Starver's movement-only stride. This
prevents an ordinary first activation from immediately losing the objective;
there is no invulnerability period. Subsequent movement, suppression, attacks
and occupancy retain their normal rules.

The Arcade objective marker outlines all nine breach cells, with a translucent
fill and `KEEP HOSTILES OUT` label. The mission prompt and failure explanation
refer to this area. A completed objective no longer draws the danger square.

Validation: real Starver activation, wall-detour placement, all 122 maps at
three viewport sizes with six allies/eight enemies, and captured HUD geometry.
The full suite passes **761 tests and eight subtests** without desktop control.
These checks prove placement and drawing calls, not human visual playability
or overall balance. Containment uses its separate breach-line rules and still
requires a dedicated pacing pass.

The [122-case defense simulation](../qa/defense_opening_summary.json) completes
with 118 victories, four defeats, no turn limits and no geometry errors. Both
clinics now fail on turn 2 rather than turn 1 with the fixed rifle policy.
Overall outcomes are unchanged; later defensive pacing remains a balance issue.
