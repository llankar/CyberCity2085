# Readable world-marker captions

The reference Arcade view now draws a single compact objective caption, keeping
the full objective instructions and progress in the fixed HUD brief. Defense
still outlines all nine breach cells and says `HOLD / KEEP HOSTILES OUT`.
Completion and failure have explicit captions. Other phase names are capped at
32 characters on the map; the fixed brief retains the full phase text.

Hazard captions retain their actual named HP/AP consequences. All captions use
dark backplates, colored underlines and connector lines. A small deterministic
rectangle layout chooses the nearest free position around neighbouring captions.
The fixed objective brief is reserved in world coordinates using the actual
rendered camera offset, preventing captions from disappearing underneath it.
Marker centres, hazard radii, defense boundaries and gameplay rules are unchanged.
The detailed marker drawing option remains available to other callers; the live
reference view explicitly selects compact captions.

## Verification, November 16, 2026

Pure tests cover dense placement, stable output, separated labels and a reserved
objective panel. HUD integration tests combine a real hazard descriptor and
defense objective, checking disjoint caption boxes, preserved hazard effects,
compact instructions and unchanged marker position.

Full regression: **846 tests and eight subtests passed**.

Actual Arcade/OpenGL render: `docs/qa/world_labels_20261116/combat.png`.

```
python -m tools.render_tactical_snapshot --output docs/qa/world_labels_20261116/combat.png --deployment --begin-battle --pan-x 64 --pan-y -32
```

The fixture enters combat through the actual deployment Enter handler, uses a
hidden window with mocked audio and fresh agents, and asserts background/terrain
coordinate equality and unchanged allied positions. Logical size is 1280 x 720,
framebuffer 1920 x 1080 under Windows DPI. The selected agent remains at screen
(32, 242). The resulting frame was visually inspected, including the corrected
collision with the objective brief. No desktop input or player save was used.

This does not prove collision avoidance against unit names, every HUD panel,
viewport edges or every map. Densely stacked labels can still leave the viewport;
further label prioritisation and edge handling remain open. Crowded unit names,
Godot parity, a human campaign playthrough and a current Windows build are also
outside this iteration's evidence.
