# Mutant marked-tile denial

The reference Arcade engine gives mutant heavy, elite and commander subtypes a
telegraphed projection. Ordinary mutants retain their existing assault behavior.
This implements the mutant portion of TAC-ENEMY-04; precision doctrines remain open.

At the start of a player phase, an eligible specialist reserves the tile occupied
by its chosen target, or the objective tile when pressuring an objective. The tile
must be more than one and at most four cells away, with clear sight under the
shared high-cover rules. The HUD shows `TOXIN / MARKED TILE` and a destination
marker. The briefing describes leaving the mark or breaking sight.

Moving the agent does **not** move the mark. At activation, the specialist spends
both AP on the projection and makes no ordinary attack. Cutting sight or moving
the caster out of range spoils that activation, shown as `cast_blocked`; reopening
sight during the same phase does not rearm it. Suppression/stun/panic and loss of
the second AP to environmental exposure also prevent release. Range and sight
are checked again at execution, including changes earlier in the enemy phase.

The existing hazard system receives one sludge zone on that exact tile. At each
side's phase start, occupants lose one HP and one available AP. It affects allies
and enemies equally; overlapping sludge applies only once per unit per phase.
It causes no persistent status or Starver infection. Walking through the tile
between phase starts does not trigger exposure, consistent with other hazards.
The zone remains through the next player and enemy phases, then expires before
the following player phase. Static map hazards keep their unlimited lifetime.

A successful projection sets a two-activation cooldown. The next two enemy
activations use ordinary behavior before a new mark becomes available. Cooldown
is per unit and cannot accumulate or create bonus AP.

These limits make denial a positioning tradeoff rather than unavoidable homing
damage or an indefinitely accumulating map hazard. The shared reserved-order,
LOS, hazard, phase and HUD systems are reused; no separate tactical controller
was added. Both the pure engine and the legacy battle-view AI adapter publish
zones into the same battle state.

Verification uses real engine phases for dodging, staying on the tile, LOS/range
interruptions, energy loss, status control, cooldown, overlap and expiry, plus a
stubbed HUD rendering check for the exact mark and consequences. No desktop
control is needed. Balance and visual playthrough release gates remain open.
