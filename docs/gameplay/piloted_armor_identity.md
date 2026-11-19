# Pilot identity in tactical armor

The deployment manifest correctly replaces a selected pilot's infantry slot
with their armor. The unit factory previously searched that already-filtered
infantry list for the pilot, so the resulting armor lost its `Character` link.
It now looks up the pilot in the original selected/deployable agent roster.
The same campaign character is attached exactly once; no duplicate infantry
unit is created. Armor combat statistics remain separate from human statistics.

This restores the pilot's name/portrait, agent-based memories and participation
in the existing debrief, XP and aftermath processing. Surviving armor structure
HP no longer overwrites the pilot's human HP at battle end. Asset integrity and
maintenance continue through their existing separate outcome path. This does
not introduce new ejection, repair or destroyed-armor survival rules.

Tests create a real selected pilot/teammate/suit manifest, assert exact character
identity and distinct stats, then run battle-end debrief generation with the
pilot attached. The HP regression isolates strategic recovery so an erroneous
armor-to-human HP transfer cannot be hidden by a later daily heal.

The live 1,098-case matrix was started before this correction and remains a
**R2 pre-pilot snapshot**, fingerprint
`aa0a267bf0b173577db61feafdf4757e8a7492b754f04a42217b99937490ded7`.
Its already-loaded simulation process is not restarted or relabeled as current
pilot-source coverage. R2's distributed executable also predates this fix.

Validation: **18 focused tests passed** and the full suite passed **789 tests
and eight subtests**, without a visible game window or desktop control.

## Pilot reservation follow-up

Selected asset eligibility now filters the hangar to requested assets before
reserving pilot capacity. An unselected suit cannot reserve a selected suit's
pilot. Explicit pilot names must belong to the selected deployable agents and
can be reserved once only; the first valid selected suit in hangar order wins a
duplicate assignment. Missing/recovering assigned pilots invalidate their suit.
Legacy unnamed suits retain the preexisting count-based eligibility behavior;
this is not proof of complete automatic pilot assignment for old saves.

Regressions cover selecting the second of two suits, duplicate named assignments
with another agent available, and a recovering assigned pilot. Actual unit
creation must agree with sanitized selection. Power-armor multi-cell occupancy
and broader sustained campaign balance remain open.

Follow-up validation: **15 focused tests passed**, then **792 tests and eight
subtests passed** in the full suite, without desktop control. The old matrix
job is now complete and its scope is documented in the R2 full-matrix report.
