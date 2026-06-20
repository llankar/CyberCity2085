# GameState Domain Split Plan

Date: June 20, 2026

## Goal

Reduce `GameState` god-object risk without breaking saves, UI screens, or the current playable loop.

`GameState` should remain the save-compatible state root for now. New behavior should move into small domain services that accept a `GameState` instance, mutate only their owned fields, and return simple result payloads for UI/logging.

## Current responsibility clusters

- Persistence root: `save()` / `load()` serialize campaign, roster, missions, funds, events, research, UI preferences, and tutorial state.
- Strategic clock: `advance_one_day()` ticks recovery, scars, funds, research, events, campaign act progression, and event logs.
- Finance facade: funds, corp budget, weekly income, mission payouts, and strategic resources.
- Mission facade: selected mission, mission board state, rewards, aftermath, faction fallout, and unavailable missions.
- Campaign facade: act progression, intel reveal, world state, global scenario consequences.
- UI compatibility facade: flags such as contrast, audio feedback, language, tutorial progress, and Godot handoff preference.

## Non-negotiable constraints

- Keep existing save payload keys readable until explicit migration tests cover a new schema.
- Do not move dataclass fields out of `GameState` before behavior has been extracted and tested.
- Keep wrappers on `GameState` thin and backwards-compatible while screens still call them.
- Prefer pure functions or small service modules over stateful manager classes.
- Move at most one domain slice per PR/commit.

## Target service boundaries

| Service | Candidate module | Owns behavior | Keeps data on `GameState` |
|---|---|---|---|
| Campaign service | `game/campaign/service.py` | Campaign ticking, act transitions, intel reveal, global event feed entries. | `campaign`, `_pending_act_advance`, campaign-facing `event_log` lines. |
| Mission flow service | `game/missions/flow.py` | Board generation, launch selection, mission reward/consequence resolution, unavailable mission tagging. | `mission_templates`, `active_mission`, `selected_mission_index`, `mission_board_generated_day`, `recent_consequences`. |
| Finance service | `game/management/finance_service.py` | Funds facade, weekly income, mission fund split, strategic resource spending. | `funds`, `budget_pool`, `corp_budget`, `mission_fund_allocations`, `strategic_resources`. |
| Recovery service | `game/agents/recovery_service.py` | Daily stress recovery, wound recovery, temporary scar ticking, recovery-room event lines. | `characters`, `recovery_narrative_memory`, `event_log`. |
| Event service | `game/management/event_service.py` | Active event expiration, random event rolling, event choice application. | `active_events`, `next_event_id`, `event_log`. |
| Save migration service | `game/persistence/migrations.py` | Version-aware payload defaults and old-key compatibility. | Adds optional `save_schema_version` only after tests lock current behavior. |

## Incremental migration phases

### Phase 1 - Characterize current behavior

- Add focused tests around `GameState.advance_one_day()` side effects before moving code.
- Add save/load tests for older payloads that omit newer fields such as `campaign`, `funds`, `selected_asset_ids`, `mission_board_generated_day`, and UI flags.
- Add a small fixture payload for a legacy save and keep it stable.

### Phase 2 - Extract behavior, keep facade methods

- Move one behavior cluster into a service module.
- Keep the existing `GameState` method name as a wrapper when UI/tests already call it.
- Service functions should return compact result data when UI needs summary lines.
- Do not change save keys in this phase.

Example pattern:

```python
def advance_one_day(self, reason: str = "manual") -> None:
    from game.management.daily_tick_service import advance_one_day

    advance_one_day(self, reason=reason)
```

### Phase 3 - Narrow UI imports

- New screens in `game/ui/screens/` should call service APIs for transitions instead of adding new `GameState` methods.
- Compatibility wrappers may remain for older `game/views.py` paths.
- Keep render code out of services; services return strings, ids, and data dictionaries.

### Phase 4 - Add schema versioning only when needed

- Introduce `save_schema_version` after a real field migration is required.
- Version migrations should normalize raw payload dictionaries before `GameState.load()` hydrates dataclasses.
- Every migration must have tests for old payload, current payload, and missing optional fields.

### Phase 5 - Move data only after behavior is stable

- Once behavior is service-owned and save migrations are covered, consider nested state containers for domains with high churn.
- Prefer existing containers where available, such as `CampaignState`, `CorporateFunds`, `StrategicCalendar`, and `ResearchTree`.
- Avoid cosmetic data moves that do not reduce coupling or test risk.

## First safe extraction candidates

1. Campaign ticking and act progression, because `game/campaign/engine.py` already exists and can become the stable service boundary.
2. Mission flow and reward resolution, because mission launch, consequences, and debrief now form a Wave 6 loop.
3. Finance facade, because funds already have a dedicated ledger object and good regression coverage.
4. Recovery/scar ticking, because agent attachment work will add more post-mission continuity.
5. Event expiration/rolling, because management events are already module-owned but still orchestrated by `advance_one_day()`.

## Test gates for each extraction

- Existing focused tests pass for the moved domain.
- Save/load round trip remains byte-key compatible for untouched fields.
- At least one regression test proves the `GameState` wrapper still works.
- UI-facing result text remains deterministic enough for existing assertions.
- No new screen imports from deep persistence internals.

## Stop conditions

- Stop if a slice requires changing multiple save keys at once.
- Stop if UI behavior and persistence migration are being changed in the same step.
- Stop if a new service needs broad knowledge of unrelated domains; return a result object and let the caller coordinate.

## Decision

Keep `GameState` as the stable campaign state root, but stop adding new domain behavior directly to it. Future Wave 6 work should add or extend domain services first, then leave `GameState` as a compatibility facade until save migration tests justify moving serialized data.
