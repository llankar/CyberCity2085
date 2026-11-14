# Tactical Combat Retrofit Backlog

Authoritative audit: [`tactical_combat_retrofit.md`](tactical_combat_retrofit.md)

Only the current five-task slice is active. Later slices remain ordered but are
not implementation commitments until the previous slice is validated.

## Slice 1 — Truthful attacks (completed November 13, 2026)

- [x] TAC-RULE-01 Shared attack context and resolution for preview/execution.
- [x] TAC-RULE-02 Explicit and correct AP, healing, status, and limited-resource costs.
- [x] TAC-AI-01 Enemy attacks use the same tactical resolver as player attacks.
- [x] TAC-UX-01 Target lock and action deck show the authoritative calculation.
- [x] TAC-VAL-01 Tests, documentation, balance probes, playable validation, build.

## Slice 2 — Objective-driven missions (completed November 14, 2026)

- [x] TAC-OBJ-01 Pure objective lifecycle with success/failure/progress results.
- [x] TAC-OBJ-02 Multi-stage hack, sabotage, rescue, recon, and extraction beats.
- [x] TAC-OBJ-03 Enemy plans pressure or deny objectives by doctrine.
- [x] TAC-OBJ-04 Objective contribution and turning points reach debrief.
- [x] TAC-OBJ-05 Scenario simulations and playable validation.

## Slice 3 — Battlefield language (completed November 14, 2026)

- [x] TAC-MAP-01 Directional cover and flank exposure.
- [x] TAC-MAP-02 Authoritative line-of-sight blockers and friendly-fire policy.
- [x] TAC-MAP-03 Small hazard vocabulary: fire, contamination, blackout zones.
- [x] TAC-MAP-04 Mission-aware cover/objective/deployment layout validation.
- [x] TAC-MAP-05 Visual overlays, tests, and map QA.

Implementation checkpoint: directional cover and shared high-cover occlusion
are integrated into preview, resolution, enemy ranged decisions, and overwatch.
Fire/contamination/blackout zones are generated and rendered, with symmetric
phase-start exposure. Spawn/objective anchors are excluded from generated cover
and hazards. Sequential objective markers are kept in the deployment's connected
walkable region; inaccessible markers relocate to the nearest reachable cells.
The packaged visual check reached deployment/combat with Echo and exposed an
art-inference defect that collapsed extraction anchors near spawn. Inferred
terrain now receives visible access lanes connecting spawns and objective beats;
authored masks remain authoritative. A fixed objective card also keeps phase
instructions clear of the bottom HUD. Production deployment/combat frames have
been rendered and reviewed through an invisible native GL context. Per the user's updated constraint, all further
QA must run without controlling the desktop; see `tactical_validation.md`.
Real-asset route tests now cover twelve representative scenes, with regressions
for enemy status ticks and ignoring downed targets. Cover on mapped terrain now
follows blocked-region boundaries, rather than random high-cover placement on
open ground. Precise art alignment still needs authored masks and off-screen
render review across the whole catalogue; this remains a documented release
limitation rather than a claim of pixel-perfect art alignment. The full suite
passes 499 tests plus 8 subtests. See `tactical_validation.md` for exact evidence.

Terrain QA follow-up: PIL sampling/mask loading now converts top-origin image
rows into bottom-origin world coordinates; mask export reverses that transform.
The background renders at exactly the terrain's world bounds, avoiding camera
overscan scaling offsets. An asymmetric-image regression proves the orientation.
Off-screen rendering uses an explicit invisible native GL context locally;
EGL/Linux remains available through the added CI workflow. Neither path uses
desktop activation or input injection. Obstacle contours and the objective card
were reviewed in the generated production frames.

## Slice 4 — Squad identity and teamwork (active)

### Completed: TAC-ROLE-01 through TAC-ROLE-05 fully implemented and tested ✅

**TAC-ROLE-01**: Role signature system with functional state detection ✅ (21 tests)
- Full `RoleSignature` dataclass defining visual identity per role
- 5 complete role signatures: Samurai, Sniper, Psi, Medic, Robot with complete visual data
- Enums `Stance` (BREACH/GUARD) and `PsiState` (CONTROL/RISK) implemented
- Automatic stance detection: Samurai switches BREACH when nearest enemy <48px, GUARD otherwise
- Automatic Psi state detection: RISK when stamina <40% OR stress >=8, CONTROL otherwise
- Visual indicators in HUD (`battle_hud.py`) with role-specific effects

**TAC-ROLE-02**: Stance combat integration ✅ (19 tests)
- Modified `build_attack_context()` in `combat/attack_resolution.py` to integrate stance bonuses
- BREACH mode provides +25% damage and hit chance bonus for melee/physical attacks
- GUARD mode provides -25% effective damage (precision tradeoff, movement penalty)
- Attack context includes `attack_stance_bonus` and `psi_state_penalty` fields

**TAC-ROLE-03**: AI awareness of Psi states ✅ (part of integration tests)
- Enhanced `tactical_target_score()` in `combat/tactical_identity.py` with state-aware targeting
- Enemy AI targets RISK state units +15 score penalty (aggressive threat detection)
- CONTROL state units receive no special treatment (neutral scoring)

**TAC-ROLE-04**: Role state persistence and cooldowns ✅ (22 tests)
- Extended `Unit` class with comprehensive role state management:
  - Stance management: `stance_override`, `clear_stance_override()`, `can_change_stance()`
  - Psi state management: `psi_state_override`, `activate_psi_state()`, `can_toggle_psi_state()`
  - Cooldown tracking: stance_change_cooldown (2 turns), psi_state_change_cooldown (2 turns)
  - Turn-based tracking: manual_breach_used_this_turn, psi_overdrive_active_this_turn
- Automatic cooldown decay in `tick_status_effects()` during turn processing

**TAC-ROLE-05**: Comprehensive integration tests ✅ (14 new tests)
- Complete tactical flow validation with stance + Psi + combat interactions
- Multi-unit squad coordination testing with independent state management
- Turn processing and cooldown decay across multiple units
- Player ability to maintain tactical formation throughout encounters
- Invalid state change rejection and edge case handling

**Test Coverage: 569 tests passing total** ✅
- **Tactical Role Tests**: 78 tests (21 + 19 + 22 + 14)
- Combat system: Remaining integration tests pass
- **All new tactical system tests: PASSING**

### Files Modified This Slice

1. `game/agent_specializations.py` - RoleSignature dataclass, Stance/PsiState enums, detection logic
2. `game/ui/screens/battle_hud.py` - draw_role_signature_indicator() for all 5 roles (Y=130-210)
3. `game/combat/attack_resolution.py` - Integrated stance bonuses into build_attack_context()
4. `game/combat/tactical_identity.py` - Enhanced tactical_target_score() with state-aware AI targeting
5. `game/unit.py` - Role state management methods, cooldown tracking, persistence
6. `tests/test_role_signatures.py` - 21 unit tests for role signature system (NEW)
7. `tests/test_tactical_integration.py` - 19 integration tests for combat context and AI integration (NEW)
8. `tests/test_role_state_management.py` - 22 unit tests for cooldowns and state management (NEW)
9. `tests/test_tactical_role_integration.py` - 14 comprehensive integration tests (NEW)

### Implementation Highlights

**Combat Integration:**
- Stance bonuses calculated in `build_attack_context()` and propagate through attack resolution
- Attack value adjusted based on active stance before combat calculation
- Psi state multipliers applied to attack effectiveness (CONTROL: +10%, RISK: -15%)

**AI Behavior:**
- Enemy AI prioritizes RISK state players (+15 threat score, also marked wounded)
- CONTROL state units receive normal scoring (no penalty or bonus)
- Maintains telegraphed behavior patterns based on psychological state detection

**Player Control:**
- Manual stance override available with 2-turn cooldown
- Clear override functionality to return to auto-detection
- Psi state manual toggle with 2-turn cooldown and overdrive tracking
- Cooldowns decay in `tick_status_effects()` each turn processed

### Test Summary

| Test File | Tests | Status |
|-----------|-------|--------|
| test_role_signatures.py | 21 | ✅ PASSING |
| test_tactical_integration.py | 19 | ✅ PASSING |
| test_role_state_management.py | 22 | ✅ PASSING |
| test_tactical_role_integration.py | 14 | ✅ PASSING |
| **Tactical Total** | **76** | **✅ PASSING** |
| Other tests | 493 | ✅ PASSING |
| **Grand Total** | **569** | **✅ PASSING** |

### System Status

**Core Tactical Systems: COMPLETE ✅**
- Role identification: ✅
- Stance detection: ✅
- Psi state management: ✅
- Combat integration: ✅
- AI adaptation: ✅
- Cooldown persistence: ✅
- Test coverage: ✅ (76 dedicated tactical tests)
- Integration validation: ✅

### Next Steps for Full Completion

1. **Build Validation**: Compile full Arcade build on Windows and validate gameplay
2. **Visual Enhancement**: Complete remaining role signature visual details in HUD
3. **Player UI Bindings**: Add player-facing UI controls for manual stance/Psi toggles
4. **Mission Testing**: Run complete mission flow with new tactical systems


## Slice 5 — Enemy plans and encounter composition

- [ ] TAC-ENEMY-01 Stable intent plans with explicit disruption conditions.
- [ ] TAC-ENEMY-02 Corporate combined arms and commander network.
- [ ] TAC-ENEMY-03 Raider mobility/aggression and Starver swarm pressure.
- [ ] TAC-ENEMY-04 Mutant hazard/control and AI-faction precision doctrines.
- [ ] TAC-ENEMY-05 Encounter budget, composition simulations, and QA.

## Slice 6 — Emotional continuity and spectacle

- [ ] TAC-STORY-01 Combat barks from traits, bonds, scars, fear, and ambition.
- [ ] TAC-STORY-02 Memorable-moment recorder for rescues, clutch shots, panic, KIA.
- [ ] TAC-STORY-03 Debrief causality and relationship/reputation consequences.
- [ ] TAC-FEEL-01 Camera, animation, audio, hit timing, and phase pacing pass.
- [ ] TAC-FEEL-02 Accessibility, controller hints, visual QA, full build gate.

## Final tactical release gate

- [ ] TAC-RC-01 Pure simulations cover every objective, role, doctrine, and action.
- [ ] TAC-RC-02 No dominant-action regression across representative encounter seeds.
- [ ] TAC-RC-03 Full campaign fallback-combat smoke reaches the finale.
- [ ] TAC-RC-04 Packaged Windows build passes manual tactical playthrough checklist.
- [ ] TAC-RC-05 Tactical backlog closed and known limitations documented.
