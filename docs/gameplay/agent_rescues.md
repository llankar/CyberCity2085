# Allied treatment and remembered help

Arcade's first-aid button/hotkey now opens an allied target selector. Left/right
cycles living wounded or bleeding allies within 32 pixels, including self when
eligible. Enter confirms and Escape cancels through the existing targeting
controls. A green marker shows name, HP and the one-AP cost. Opening selection
costs nothing; resolution still uses the engine and rechecks range/membership.
Healing feedback appears on the patient rather than always on the medic.

The engine rejects enemy patients and dead units. First aid restores the existing
two HP and clears bleeding; it does not revive, change infection clocks or cure
Starver infection. No healing amount or action-economy boost is introduced.

Helping another campaign agent at one-quarter HP or below, or clearing their
bleeding, records a factual memory for both agents. Self-treatment, ordinary
minor healing and failed treatment do not. Each ordered helper/patient pair is
recorded once per battle. Existing positive/negative/neutral relationship scores
select the patient's reaction without changing those scores or consuming RNG.
The entries use the actual mission title and existing history serialization.

This extends the clutch-shot recorder, not a general dialogue framework. No
automatic relationship reward, bespoke debrief card or external Godot treatment
flow is included. Their roadmap gates remain open.

Validation: **774 tests/eight subtests passed** in the full suite. The final
seven-test focused run also checks selecting and confirming allied treatment
through the view with real engine resolution and mocked visual effects.
No desktop takeover or game window was used. Windows distribution and human
visual playthrough remain separate open gates.
