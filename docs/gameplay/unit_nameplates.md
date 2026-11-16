# Crowded squad labels

World unit labels now reserve a complete plate (name, HP bar, enemy subtype and
status badges) in the shared world-caption layout. The active allied unit gets
first choice, then other allies and visible enemies in roster order. Deployment
uses the actual deployment cursor for this priority. Neighbouring plates move to
nearby free rectangles, with connectors back to their original sprite anchors.
No unit coordinates, hitboxes, HP or turn order are changed by the layout.

Each plate has a dark backplate and a width budget for its name and badges.
Overwatch appends `/ OW` instead of replacing the agent's identity. Enemy subtype
and status rows are separate; status badges are now centred correctly as a group.
Hidden enemies reserve no plate and reveal no name. Very long map names are
truncated at 18 characters before the overwatch suffix; dossiers retain identity.

Portrait cards use a full-width name row below the portrait and above HP, instead
of the insufficient space to the right of the portrait. Names retain up to nine
characters. Samurai/psi mode labels move to the upper portrait area, away from
the name row. No new input bindings or gameplay rules are introduced.

## Verification, November 16, 2026

Regression tests draw three agents at the same coordinates, including an active
overwatch agent with two statuses and a hidden enemy. They verify disjoint plate
rectangles, active-first identity, preserved status information, hidden-enemy
exclusion and unchanged world positions. Another test checks the portrait name
row and its separation from the stance label.

Full regression: **848 tests and eight subtests passed**.

Actual hidden Arcade/OpenGL renders were inspected:

- `docs/qa/unit_labels_20261116/combat_960.png`: 960 x 640 logical, 1440 x 960 framebuffer.
- `docs/qa/unit_labels_20261116/combat_1280.png`: 1280 x 720 logical, 1920 x 1080 framebuffer.

Both use `tools.render_tactical_snapshot` with `--deployment --begin-battle
--pan-x 64 --pan-y -32`, fresh agents, mocked audio and the actual Enter handler.
Rendering asserts unchanged positions and matching background/terrain dimensions.
No visible window, desktop control or player save is involved.

The renders expose remaining problems: map captions can leave the viewport or
pass behind resource chrome at small sizes, and plates do not reserve sprite
bodies or enemy-intent text. This iteration proves caption-to-caption separation,
not comprehensive viewport/HUD avoidance, every-map visual QA, Godot parity,
human playthrough or a new Windows distribution.
