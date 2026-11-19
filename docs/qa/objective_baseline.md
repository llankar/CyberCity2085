# Objective battle baseline — 2026-11-15

Command:
`python -m tools.simulate_encounters --scenario objectives --output runtime/objective_qa.json`

Scope: eight objective types × six enemy families × three level/risk/count bands
× seeds 0–2 × two layouts × two objective-first policies = **1,728 battles**.
The four-rifle squad and synthetic arenas retain the limitations of the earlier
[elimination baseline](encounter_baseline.md). The defend marker is behind allied
lines; containment enemies start above the breach line. Neither starts pre-failed.

| Objective | Victories / 216 | Defeats | 30-turn limits |
| --- | ---: | ---: | ---: |
| Extraction | 210 | 6 | 0 |
| Data theft | 210 | 6 | 0 |
| Sabotage/counterpush | 210 | 6 | 0 |
| Recon scan | 208 | 8 | 0 |
| Civilian rescue | 202 | 13 | 1 |
| Defend | 107 | 109 | 0 |
| Containment | 58 | 158 | 0 |
| Assassination | 216 | 0 | 0 |
| **Total** | **1,421** | **306** | **1** |

576 victories occurred with enemies still alive. Contributions are recorded only
for actual successful interactions; their AP are spent by the same lifecycle as
the playable E-key path. Defeats comprise 259 durable objective breaches and 47
squad wipes. Defense and containment can no longer be bypassed by interacting.

The one limited run was an open civilian rescue against Three Sevens robots,
level 7/risk 8/eight enemies/seed 0/objective policy. A trace at turns 25–30 showed
the last enemy contesting the final rescue marker while its HP fell from 111 to
7; units were acting, rather than stuck. A separate run allowing 40 turns ended
in victory at turn 33, with all three groups rescued and two allied losses. The
30-turn matrix row remains `turn_limit` rather than retroactively counted as a win.

## Interpretation and remaining work

- Defense/containment are much less forgiving than interaction objectives in
  these layouts. Check authored marker positions, access lanes, reaction tools
  and breach timing before changing enemy damage.
- Extraction, download and sabotage share high success rates for this fixed
  squad. Different real maps and scripted pressure must prove their campaign
  differentiation; distinct counters alone do not establish good pacing.
- Assassination is trivial for these target-first policies here. Check target
  placement/protection and extraction requirements in real missions.
- The long rescue shows sustained contesting can create attrition and length.
  Evaluate whether that feels tense or repetitive in a playable mission.
- These results do not cover manually surveyed map geometry, support assets,
  mixed-role/understrength squads, reinforcements or campaign aftermath.

TAC-ENEMY-05 remains partial. The baseline supplies evidence for the next tuning
pass and closes the interaction-economy loopholes; it does not close balance,
Windows distribution or playable release gates.
