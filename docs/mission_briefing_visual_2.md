# Mission Briefing Visual 2.0

The live Python Arcade briefing now presents a cinematic three-column military
briefing, using the same cached holographic painter as Squad Command and the
operative dossier. It retains the original mission launch and abort handlers.

## Presentation

- A full-width title strip shows the actual mission, campaign day, district and
  faction. Interface labels follow the configured French or English language.
- The left column uses contextual art selected from the existing scene library
  by the shared mission-art resolver. It is not a single fixed background.
  Objective text overlays the scene. The tactical preview is the exact image
  returned by `select_battle_map_entry(mission)`, not illustrative scene art.
  Clicking the preview opens an uncropped, aspect-preserving map inspection.
- Center cards show actual risk, duration, funds after selected support costs,
  domain-calculated projected stress, every complication and emotional impact.
  Tags and temporary scars remain accessible in the human-impact panel.
- The deployed roster shows actual portraits, names, roles, stress states,
  individual stress meters and the existing integer average. Narrow screens and
  large text show fewer cards per page rather than compressing all portraits.
- Support cards use selected assets and their real deployment costs. Existing
  robot/power-armor portrait routing supplies the illustrations; unknown future
  categories use a generic pictogram instead of inventing a vehicle portrait.
- Success and failure have distinct green/red panels. Narratives come directly
  from the mission's consequence data; empty lists say so explicitly.
- Abort and Deploy have large beveled frames, icons and animated hover/glow.
  A restrained scanning line moves across the scene.

Existing authored mission narratives and item names retain their source language,
consistent with the rest of the game. No reference-image statistics, people,
mission names or invented consequences are injected into campaign data.

## Controls and overflow

Abort/Deploy and Escape/Enter preserve their original actions. While the map
inspection is open, Escape closes it first and Enter does not accidentally launch
a mission behind the modal. Clicking the inspection also closes it.

Every long text section has independent wheel scrolling and arrow controls;
Page Up/Down operates the last hovered section. Squad and support cards use the
same controls. No fixed `[:3]`, `[:4]` or `[:6]` cuts remain. Wrapped text preserves
long tokens and tail entries. Hovering the net funds/stress cards reveals the
gross reward/support cost and added mission pressure in the footer rail.

## Structure

`mission_briefing_view.py` owns loading, audio, input and existing launch routing.
The pure `layouts/mission_briefing.py` computes the responsive regions. Small
`briefing_scene`, `briefing_squad`, `briefing_widgets` and `briefing_content`
components handle the panels; `components/mission_briefing.py` composes them with
shared cached text, textures, meshes and meters. Scene resolution happens during
asset loading. Painting and scrolling do not change campaign data.

Godot handoff, its explicit Arcade fallback, music setup and management return
behavior remain unchanged.

## Real game captures and validation

Captures are taken from a running Arcade/OpenGL view, with isolated test campaign
data, rather than composited mockups:

- [1280×720](images/mission-briefing-2/briefing-1280x720.png)
- [1920×1080](images/mission-briefing-2/briefing-1920x1080.png)
- [2560×1440](images/mission-briefing-2/briefing-2560x1440.png)
- [Alternate mission and illustration](images/mission-briefing-2/briefing-alternate-mission.png)
- [Full tactical inspection](images/mission-briefing-2/briefing-map.png)
- [Large text, long lists](images/mission-briefing-2/briefing-large-overflow.png)
- [Empty deployment](images/mission-briefing-2/briefing-empty.png)
- [English interface](images/mission-briefing-2/briefing-english.png)

Native checks exercise mouse and keyboard actions, map inspection, 9 selected
agents, 10 support assets, 14 complications, repeated consequences, empty
selections, language changes and campaign immutability. Pure tests verify
geometry, lossless wrapping, complete facts and contextual asset selection.
Existing launch-routing tests cover Godot startup failures and explicit fallback.
Visual review corrected truncated duration, raw state keys, tight portrait
metadata, overlapping meters and pager placement at 720p with large text.

Reproduce the captures with:

```sh
DISPLAY=:103 ALSOFT_DRIVERS=null python -m tools.check_mission_briefing_visual
```

Validation result: **58 passed, plus five subtests**. Management's legacy UI
tests install a global Arcade test double, so they run in a separate process from
the actual-Arcade briefing/launch suite:

```sh
python -m pytest -q tests/test_management_hub_ui.py
DISPLAY=:103 ALSOFT_DRIVERS=null python -m pytest -q tests/test_mission_briefing_visual.py tests/test_mission_briefing_view.py tests/test_agent_readiness.py tests/test_godot_launch_routing.py tests/test_music_continuity.py tests/test_static_game_flow_e2e.py
```

Publication authorized on November 17, 2026: push the verified feature branch and merge into main.
