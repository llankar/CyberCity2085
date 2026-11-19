# Pointer targeting in reference combat

When an attack or first aid has already opened target selection, left-clicking
a living visible candidate selects it. Clicking the same selected candidate
again confirms through the existing Enter handler; right-click cancels through
Escape. A first click never spends AP. Keyboard target cycling and confirmation
remain available. Action-bar clicks keep priority and reset pointer confirmation.
Opening a new attack/aid also resets it, preventing stale confirmation state.

The pure hit test selects the closest candidate within 24 world pixels, with
stable list-order ties. Pointer coordinates use the exact offset stored by the
last battlefield render, including camera pan and shake. Before the first draw,
the configured pan is the fallback. Dead/hidden candidates and off-target clicks
are ignored. Damage, range, line of sight, AP and aid membership are revalidated
by the existing engine when the Enter path commits the action.

Mouse events now correctly set keyboard/mouse hints rather than classifying
ordinary left/right clicks as controller input. Other mouse buttons do not
activate action-bar commands, and tactical targeting is inactive during
deployment. This does not add click-to-move, free unit switching, deployment
dragging or new Godot controls.

Tests cover coordinate conversion, hidden/dead exclusion, nearest/tie behavior
and the actual BattleView mouse dispatcher's two-click/Enter and right-click/
Escape routing. The dispatcher test replaces the key handler; separate real
engine/view tests cover attack and aid commitment. These tests do not certify
GPU rendering, click accuracy on every sprite size or a human mouse playthrough.
No desktop control or visible game window is used.

Validation: three focused pointer/dispatcher tests passed; the full suite passed
**811 tests and eight subtests**. The distributed R2 candidate predates these
controls and must be refreshed before they can be evaluated in that executable.
