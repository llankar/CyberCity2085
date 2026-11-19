# Remembering fallen teammates

The reference combat engine retains references to allies alive when it is
created. Terminal checks detect those agents falling to zero HP even when the
enemy AI has already removed them from its living-unit list. A once-per-agent
battle guard prevents repeated checks from repeating memories.

The fallen character gets a factual mission-history entry and a structured
`downed` moment. If a campaign agent survives, the strongest existing outgoing
bond selects the reacting teammate, with distance breaking ties. That teammate
retains a memory; a positive bond produces a personal appeal, otherwise the
reaction acknowledges the loss and the remaining mission. It does not claim
that the survivor saw the attack. No relationship score, stress roll, combat AP
or recovery/permadeath rule changes.

The existing debrief pipeline receives the loss even if no characters survive.
Its tone is `loss`, rather than the relief used for aid. Only aid/clutch-kill
events can supply a factual heroic action; a loss-only moment list explicitly
reports no clutch action recorded. History and structured-report persistence use
the previously tested campaign save path.

Initially fallen units do not produce new loss events. Removing a living ally
from the current roster does not itself create a casualty. Both combat attacks
and start-of-phase status damage are covered. This records an agent falling;
it does not add a new downed-state, revival or death system. External Godot
combat and mid-battle reinforcements are outside this recorder's integration.

Validation: **779 tests and eight subtests passed** in the full suite. After
clarifying the loss-only heroic-action fallback, all **19 focused moment/
narrative tests passed**. Tests use the real enemy phase and status ticking,
without opening a window or taking desktop control. Visual/build release gates
remain open.
