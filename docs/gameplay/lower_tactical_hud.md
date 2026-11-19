# Separate lower-HUD rows

The real hidden-window review exposed two overlapping layers: the active-agent
panel occupied the command buttons, while action-bar messages/previews were
drawn on top of those buttons. The lower HUD now uses separate rows without
increasing its existing reserved screen band:

- Commands remain at the bottom. Unit/AP information and a message or attack
  preview occupy two header lines; buttons occupy the lower part. A warning
  shares the upper line with restrained length. The redundant large panel title
  is removed so it does not consume the command/header space.
- Active-agent details and squad portraits share the row above commands.
  Portraits reserve room for the 300-pixel detail panel when they fit. If the
  roster needs that space, the detail panel hides and portraits retain the row.
  The portrait HP/AP bars and action header remain available.

Button width now accounts for every inter-button gap. Layout tests cover four,
eight and twelve commands at widths 960, 1280 and 1920, checking containment,
nonoverlap, header clearance and actual hit testing. Captured drawing tests
check the detail panel's separate row and four-agent portrait placement.

Corrected real Arcade/OpenGL frames were inspected at both sizes:

- [960x640 logical](../qa/lower_hud_20261116/tactical_lower_hud_960.png)
- [1280x720 logical](../qa/lower_hud_20261116/tactical_lower_hud_1280.png)
- [Framebuffer metadata/hashes](../qa/lower_hud_20261116/report.json)

The fixture has four agents and seven available actions. Twelve-action font fit,
large-roster visual presentation, warning/preview combinations and human input
still need rendered/playthrough coverage; rectangle tests alone do not certify
those. Top-header congestion and battlefield units obscured beneath HUD remain
visible issues. No desktop control or visible window was used, and R2 predates
this layout change.

Validation: **30 focused tests passed**, the full suite passed **837 tests and
eight subtests**, and both real hidden-window frames rendered successfully.
