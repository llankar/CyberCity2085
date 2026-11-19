# Campaign flow after tactical memories

The added integration test resolves an equipped agent's real melee kill at
critical HP using the combat engine, then calls the real Arcade battle-end
method. It verifies mission completion/calendar advance, the structured moment
in the generated narrative report, its priority in the debrief summary, and
campaign reward-journal output. It continues through the debrief's management
transition and saves/reloads the resulting campaign JSON from a temporary path.
Both the character memory and latest report must survive.

Only graphics/window initialization, random strategic events and the management
screen object are replaced. Actual attack resolution, battle-end orchestration,
mission fallout, debrief construction and persistence execute. No game window
is created. This complements the earlier mission-flow test, whose battle object
was a placeholder. It is one elimination mission, not a campaign-to-finale proof.

The source entry-point smoke also passed:

`python main.py --smoke-test --smoke-report runtime/source_smoke_after_agent_memories.json`

It validates all 122 manual map surveys, the presence of seven MP3 tracks,
temporary campaign save/load and a real authored dockside battle. That battle
ended in victory on turn 25 with one allied loss and no geometry error.
[Archived evidence](source_smoke_after_agent_memories.json) includes hashes of
the relevant source files. Music-file presence does not prove playback; neither
check proves GPU rendering. The existing Windows candidate is an older snapshot
and is not certified by this source-only result.

The full regression suite passes **780 tests and eight subtests**. No desktop
control was used. Human visual validation, wider mission balance, a complete
campaign-to-finale test and a refreshed Windows distribution remain open.
