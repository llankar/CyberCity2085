# Authored story tactical baseline

`python -m tools.simulate_encounters --scenario story --seeds 3 --output runtime/story_tactical_objectives_corrected.json`

The new scenario executes all 15 story encounters independently using the same
story-to-mission conversion as the board, automatic map selection, real enemy
composition, authored terrain, objective rules and combat engine. It clones the
actual mission rather than replacing it with a generic elimination template.
Defense uses the Arcade duration-derived hold requirement. Each run starts with
four fresh level-4 rifle agents and a 60-turn cap.

The first audit exposed a production bug: `MissionTemplate.from_dict` rejected
`defend` and `assassination`, silently changing them to `eliminate` during launch
cloning or loading. Both supported kinds now survive cloning. The regression
checks every authored story objective; initial simulation results with corrupted
objectives are superseded and must not be treated as authored-mission evidence.

The corrected 45 runs produced **45 victories**, no limits or geometry errors.
Exact mission/seed coverage, reported objective kinds, serialized template
hashes, selected maps, survey hashes and combat-source fingerprint were checked.
Defense missions now finish on turn 9; the final assassination takes 10–16 turns.
See [derived evidence](story_tactical_summary.json).

The source fingerprint now also includes story definitions, mission conversion,
template cloning and map selection. Generic limited-case replay rejects story
rows rather than silently losing their mission-specific rules.

Limits: these are independent simulations, not a continuous campaign with
carried injuries, resources, XP and replacements. The automated player has one
fixed loadout/policy; this does not prove interesting difficulty or no dominant
strategy. It does not exercise the visible renderer or the full view-driven
mid-battle-event lifecycle. Human playability, mixed squads, continuous campaign
combat and updated Windows distribution remain open.

The final full suite passes **785 tests and eight subtests**, without desktop
control. The existing Windows archive does not contain this cloning fix.
