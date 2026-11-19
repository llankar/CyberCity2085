# HUD-aware focus and matching map coordinates

Real renders exposed a coordinate mismatch: Arcade drew the background at
`height - 300` while authored terrain, walls, objectives and units used the full
window height. The background and grid now use the same full world dimensions
as terrain. HUD panels overlay that world rather than compressing its image.
This corrects display alignment; no stored obstacle or tactical position moves.

The battle camera now accepts an explicit lower-HUD clearance. Its negative
vertical pan can reveal low units above the 210-pixel reserved band with a
32-pixel margin. Positive/horizontal bounds remain restrained. Pure camera
callers that omit clearance retain their existing behavior.

On an active-agent change after deployment, the view minimally adjusts the pan
to keep that agent inside the usable screen. Successful movement requests a
fresh visibility check. Otherwise manual pan is retained; drawing does not
continually force recentering. Home centers toward the available area, and
manual pan uses the same HUD-aware clamp. Pointer hit testing continues to use
the last actually rendered camera offset. Deployment is deliberately excluded
from automatic focus because its GUI/world overlay needs separate verification.

The hidden-window render tool now checks the actual background draw rectangle
against terrain dimensions and verifies that rendering does not move units.
Both real defense frames place the active unit at screen Y=242:

- [960x640 logical](../qa/camera_hud_20261116/tactical_camera_960.png)
- [1280x720 logical](../qa/camera_hud_20261116/tactical_camera_1280.png)
- [Metadata/hashes](../qa/camera_hud_20261116/report.json)

Pure tests cover low/visible focus, manual-pan retention, Home and clamp behavior
at three viewport sizes. Existing pointer/view tests also pass. The rendered
fixture is one map/phase, not proof of all authored-art fidelity, deployment,
all overlays or a human input playthrough. Fog still deliberately darkens
unseen areas. No desktop control or visible window was used; R2 predates this fix.

Validation: **50 focused camera/pointer/view tests passed**; the full suite
passed **840 tests and eight subtests**. Both enhanced hidden-window render
checks completed successfully.
