# UI Controllers Architecture (Squad/RPG)

Date: May 24, 2026

## Goal

Clarify responsibilities by extracting render-neutral transition logic from `game/views.py` into dedicated controllers.

## Modules

- `game/ui/controllers/mission_controller.py`
  - Mission selection index transitions (`previous`, `next`)
  - Focus-derived mission index parsing (`mission_<n>`)

- `game/ui/controllers/room_actions_controller.py`
  - Agent/action state transitions that must reset risky-launch pending confirmation
  - Roster card selection transition payload
  - Asset toggle transition payload

- `game/ui/controllers/focus_controller.py`
  - Focus-kind decision helpers (`room`, `action`, `mission`)

## Orchestration boundary

`game/views.py` now keeps:
- input binding (`on_key_press`, `on_mouse_press`)
- room opening/closing orchestration
- rendering calls
- game-state side effects (audio, notifications, view swaps)

Controllers keep:
- pure, testable transition rules
- no Arcade rendering calls
- no window/view mutation

## Why this split

- Small memorable systems over large abstractions
- Easier unit testing for fragile navigation/selection flows
- Safer iterative changes with lower regression risk in view code
