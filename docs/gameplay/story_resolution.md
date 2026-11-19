# Story progression through the shared mission lifecycle

Successful story missions now record campaign completion in
`resolve_mission_outcome`, after the existing consequences/rewards and elapsed
days. Arcade's battle-end view no longer owns a separate campaign completion
block. Any caller using the shared resolution path receives the same story
progression. Defeats leave story progress unchanged.

The campaign service remains responsible for valid act membership, duplicate
completion checks, intel/world rewards, act advancement and ending evaluation.
The legacy `story_complete_...` board marker is added only when the mission
actually belongs to the completed-story list. Unknown/future-act IDs therefore
cannot hide a mission from the board just by matching the prefix.

The new window-free test starts with a normal campaign, advances one day to
refresh its introductory static board, then selects and launches each actual
story template from the generated mission board. It resolves fifteen successful
mission outcomes, saving/reloading after each, and reaches the ending through
all five acts. A second test verifies defeat/retry availability. Random strategic
events and audio are replaced; the board, launch, mission/campaign resolution,
calendar and persistence are real.

These tests deliberately supply successful outcomes rather than playing fifteen
tactical battles. They prove the strategic transition chain and persistence,
not mission difficulty, objective playability or the campaign fallback-combat
release gate. The separate battle-to-management integration test covers one
real elimination encounter; both evidence scopes must remain distinct.

Validation: eight focused progression/ending tests passed; the full suite passed
**782 tests and eight subtests**. No desktop control or visible game window was
used. The Windows candidate still predates these source changes.
