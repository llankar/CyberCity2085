# Encounter composition baseline — 2026-11-15

Command: `python -m tools.simulate_encounters --output runtime/encounter_qa.json`

216 completed battles: **199 victories, 17 defeats, zero turn-limit runs**.
The longest battle took 28 turns. Matrix inputs are documented in
[encounter composition](../gameplay/encounter_composition.md); this is a synthetic
four-rifle elimination benchmark, not a campaign balance certification.

| Enemy theme | Victories / 36 | Defeats | Mean allied HP lost | Mean turns |
| --- | ---: | ---: | ---: | ---: |
| Starver | 34 | 2 | 74.2 | 7.6 |
| Mutant | 35 | 1 | 65.8 | 10.4 |
| Raider | 34 | 2 | 79.7 | 8.4 |
| Corporate samurai | 30 | 6 | 96.5 | 8.8 |
| Three Sevens robots | 36 | 0 | 61.1 | 11.2 |
| Novatek hybrid | 30 | 6 | 104.3 | 12.7 |

These HP means mix progression bands with different HP pools; use the raw rows
for level-matched comparisons. They are not damage balance coefficients.

| Progression sample | Victories / 72 | Defeats |
| --- | ---: | ---: |
| Level 1, risk 2, three enemies | 72 | 0 |
| Level 4, risk 5, six enemies | 71 | 1 |
| Level 7, risk 8, eight enemies | 56 | 16 |

Focus policy lost 11/108 battles; counterplay lost 6/108. Paired by faction,
level, seed and layout, counterplay lost less HP in 20 cases, more in 12 and the
same in 76. Its extra movement can sacrifice damage and prolong exposure; it is
not universally superior in this sample. RNG sequences also diverge with action
choices, so a matched seed is not an identical series of attack rolls.

The cover layout produced 12 defeats versus five in the open layout. The engine
announced 363 precision locks and 101 toxin projections across the matrix. These
counts demonstrate exercised behavior; they do not prove that every cast landed.

## Findings and remaining gates

- Initial encounters are very forgiving for this four-rifle squad. Check the
  real tutorial/team size before increasing early-game danger.
- Advanced Novatek/corporate encounters cause most defeats. Compare real
  equipment, psi and suppression responses before adjusting multipliers.
- Robot fights are longer but less lethal here. Check whether overly avoidable
  locks or lower faction agility explain this; do not equalize win rates blindly.
- Individual enemy levels still roll from one to squad average. More seeds and
  real mission rosters are needed to assess resulting difficulty variance.
- Non-elimination objectives, support assets, injured/understrength squads,
  real terrain, reinforcements and full campaign consequences remain unmeasured.

TAC-ENEMY-05 has an executable budget and QA baseline. Its encounter-balance
release gate stays open pending these checks and playable validation.
