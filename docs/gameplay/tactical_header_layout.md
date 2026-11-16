# Header separation and contextual footer

The fixed tactical header now separates mission title from right-aligned squad,
hostile and turn counters. Long titles use a conservative viewport-dependent
character budget with an ASCII ellipsis; the briefing still carries the full
title. Decorative lines that crossed text were removed. This is a layout budget,
not font-metric-perfect clipping for every possible localized string.

The phase pill sits on the resource row at the right, clear of the top counters
and left resource panel. Its redundant turn-number dot track is replaced by one
pulsing phase beacon; the actual turn number remains in the top bar. Pointer
occlusion includes the phase pill's new screen region.

Contextual shortcuts move to the reserved 18-pixel bottom footer rather than
overlaying resources. Transient action aftermath fills that same opaque footer
while active, then normal hints return. The existing font size is preserved.
No additional battlefield height is reserved, and controls/combat costs do not
change. Header/resource/objective rows now remain separate in the inspected
fixtures.

Actual Arcade/OpenGL hidden-window captures were rendered and inspected:

- [960x640](../qa/header_hud_20261116/tactical_header_960.png)
- [1280x720](../qa/header_hud_20261116/tactical_header_1280.png)
- [Long title at 960](../qa/header_hud_20261116/tactical_header_long_title.png)
- [Framebuffer metadata/hashes](../qa/header_hud_20261116/report.json)

Geometry/text tests cover resource/phase separation and long-title behavior at
three viewport widths; footer tests check reserved geometry and retained font
size. The first long-title render caught an encoding-corrupted truncation marker;
the corrected final capture uses three periods. These are constructed defense
frames, not a human playthrough. Units beneath HUD/fog, other objectives, all
preview/warning/controller combinations and large-roster rendering remain open.
No visible window, desktop control or desktop screenshot was used. R2 predates
this source layout.

Validation: **22 focused HUD tests passed** and the final full suite passed
**838 tests and eight subtests**. Three real hidden-window captures succeeded.
