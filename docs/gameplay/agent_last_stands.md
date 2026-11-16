# Remembering an agent's last stand

A player agent who neutralizes a hostile while alive at one quarter of maximum
HP or less now reacts in the combat log and retains a factual history entry.
The event includes the mission name and remaining HP. It uses the resolved
attack result, so previews, misses and nonlethal hits cannot manufacture a memory.

Fear produces a vulnerable but determined reaction; brave/bold/reckless agents
answer defiantly; cautious/careful/pragmatic agents ask for cover. Other agents
have a restrained default response. This is text feedback, not recorded speech.
It consumes no random rolls and changes no damage, AP or relationship scores.

Each agent records this event only once per battle, even after additional
clutch kills. Another battle can add a new memory. Existing character-history
serialization retains it without a new save schema. Mechanical assets without
a campaign character do not create agent memories. The Arcade view shares the
engine log list; Godot's external combat does not call this recorder.

Tests exercise a real engine kill, serialization roundtrip, repeat suppression,
new-battle reset, fear/personality text, RNG preservation and invalid triggers.
This is the first small piece of the emotional-continuity slice. Bond/scar/
ambition reactions, rescue/KIA/panic memories and a dedicated debrief presentation
remain open. No new combat advantage or automatic relationship reward is added.

Validation: all four focused tests passed; the full suite passed **771 tests
and eight subtests**, without desktop control. This verifies engine/log/data
integration, not a human visual playthrough or a newly distributed Windows build.

## Debrief integration

Resolved clutch kills and significant aid now also produce structured,
battle-local moment records. At battle end, Arcade passes only those records to
the narrative report. They appear before generic status lines in the existing
debrief panel and management's latest-debrief summary; the first real moment
also supplies the heroic-action field. The full structured list is retained in
`tactical_moments`, even when the existing display limits visible lines.

The report copies event data, so later combat-state mutation cannot rewrite it.
Character histories and the latest report survive the actual campaign JSON
save/load path. Old reports default to an empty list. A fresh battle cannot
replay old memories merely because they remain in a character's history.
The compatibility end-battle path without a combat state supplies an empty list.
This does not create further reputation awards or relationship changes.

Debrief validation: **17 focused tests passed**, then **776 tests and eight
subtests passed** in the full suite after fixing the no-combat-state fallback.
The save/load test uses a temporary campaign JSON file, not only a dictionary
roundtrip. Visual verification and updated Windows distribution remain open.
