# Deployment camera alignment

Deployment cells and the selected-unit ring are world markers drawn in the GUI
pass. They now subtract the exact rendered camera offset, including shake, while
the phase banner and bottom controls remain fixed on screen. No terrain survey,
legal deployment cell or unit position is changed by drawing.

The camera follows the deployment selection with 40 pixels of control clearance.
Tab selection and successful arrow repositioning trigger a visibility check;
Home centres the deployment selection rather than the combat active index.
Entering combat triggers a new check even when the selected agent is unchanged,
using the larger 210-pixel combat HUD clearance. Deliberate pan is retained while
the selected agent remains visible.

## Verification, November 16, 2026

Two actual Arcade/OpenGL renders use an explicitly hidden window, mocked audio,
fresh fixture agents and no player saves or desktop input:

```
python -m tools.render_tactical_snapshot --output docs/qa/deployment_camera_20261116/deployment.png --deployment --pan-x 64 --pan-y -32
python -m tools.render_tactical_snapshot --output docs/qa/deployment_camera_20261116/combat_transition.png --deployment --begin-battle --pan-x 64 --pan-y -32
```

Both frames were visually inspected. Logical size is 1280 x 720; Windows DPI
produces a 1920 x 1080 framebuffer. The background and terrain both use 1280 x
720 world coordinates. Rendering asserts all allied positions remain unchanged.
Deployment pan is (64, -32), placing the selected agent at screen (32, 128).
The second fixture draws deployment, dispatches the actual Enter handler and
draws combat in the same view: pan becomes (64, -146), placing the same agent at
(32, 242), above the combat HUD. No visible window was opened.

Unit tests verify translated cells/ring, fixed controls, unchanged coordinates
and the larger clearance at transition. Full regression: **842 tests and eight
subtests passed**. This is fixture evidence, not a human
playthrough, every-map visual review, Godot verification or a new Windows build.
Crowded world labels and overlapping objective/hazard text remain visible UI
work for a later iteration.
