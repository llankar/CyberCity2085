# Squad Command UI 2.0

The live Python/Arcade squad room now uses a dedicated full-screen command deck,
replacing the previous inset legacy panels and duplicate graphical-hub controls.
Other management rooms retain their existing presentation and handlers.

## Reference composition

The supplied reference drives the three-column layout: roster at left, portrait
and six equipment slots in the center, mission intelligence at right. A resource
strip spans the top and eleven pictogram commands span the bottom. Beveled dark
panels, cyan edge light, orange active-agent emphasis, mint mission activation,
Rajdhani typography, hover states and a pulsing mission control match the visual
language of Combat Visual 2.0 and the holographic World Map.

- **Roster:** real portraits, class, current/max HP, segmented HP/stress bars,
  readiness/recovery state, squad assignment check, active-agent glow and pending
  upgrade points. Five cards fit at standard text size. Scrolling and cursor
  navigation expose the entire roster, including newly recruited members.
- **Equipment:** the selected agent's actual portrait, attribute values and
  existing point-allocation buttons, six illustrated slots with previous/next
  controls, actual item names, range/damage/mitigation, bonuses and totals.
  Clicking the portrait opens the original complete sheet, including skills
  and talents. Double-clicking a roster card retains the same behavior.
- **Mission:** actual selected title/objective, reward, risk, duration and site;
  context-matched existing city/wasteland artwork; real enemy, doctrine, squad,
  loadout, capability and recovery intelligence. The primary control opens the
  existing World Map rather than launching an unreviewed mission.
- **Downtime:** all three activities remain visible, with real day/resource costs
  and morale/stress effects. `M` and `S` abbreviate morale and stress in compact
  rows; hover supplies the full detail. Keyboard 7–9 uses the same handlers.
- **Navigation:** next step, recruitment, mission selection, removal, previous/
  next agent, squad toggle, previous/next save slot, save and load. Header controls
  open settings and close the room. F1–F6, arrows, Space, B, Enter, D, S, L and
  Escape retain their established management routes.

## Data, language and deliberate adaptations

No names, character statistics, mission rewards or equipment values from the
mockup are embedded in the renderer. The screen reads the current GameState,
AgentLoadout, mission template and tactical-briefing model every frame; existing
management methods perform every mutation. Authored character/item/mission
content retains its original language. Interface chrome and modal labels use
`ui_language` (French and English), and the existing text-size preference applies.

The real portrait library contains small square images. The large portrait is
therefore composed with live attribute cards below it instead of stretching a
narrow face crop over the entire equipment column. The six new illustrations
represent equipment categories; their names and stats remain the real catalog
items. Blade-tagged weapons use a blade pictogram rather than a rifle image.
Mission art is selected deterministically from the existing scene library by
explicit image, environment and contextual keywords; the site label comes from
the same inference as the World Map.

The reference displays one downtime row; this screen displays all five to keep
all activities directly usable, including [Rest and Hospital](character_sheet_visual_2.md). At 720p with **large text**, the roster presents
four cards with a count/scroll rail, and footer icons become faint watermarks
behind centered captions. This preserves reading size and all eleven commands.
Long item/intelligence summaries use measured ellipsis. Hover provides full item
and total-bonus details plus extended tactical summaries; the existing World Map
provides the complete scrollable mission briefing.

Action outcomes occupy a reserved footer line, never a permanent overlay across
mission or equipment content. Internal action/result routing fields are removed
from that presentation while the original notification/event data stays intact.
Invisible legacy room buttons no longer receive clicks behind the new screen.

## Components and rendering

- `game/ui/layouts/squad_command.py`: pure responsive rectangles and roster paging.
- `game/ui/components/squad_command.py`: shared painter, chrome and input regions.
- `squad_agents.py`, `squad_equipment.py`, `squad_mission.py`: independent live panes.
- `squad_copy.py`, `squad_style.py`: localized modal copy/feedback and palette.
- `assets/ui/squad_command/`: generated category art and versioned vector/PNG icons.

The existing holographic painter is reused. Its optional shared text batch is
backward compatible with the World Map's immediate drawing path. Repeated labels
at different card positions have distinct batch instances; inactive labels are
hidden after data/language changes. Text, panels, image crops, glow textures,
scan lines and segmented-meter geometry are cached. Only animation/changed data
requires new work. The SVG export script is an asset-build utility; the live
screen and interaction logic are entirely Python/Arcade.

## Real interface captures

All captures below are actual Arcade/OpenGL framebuffers, not mockups. The
isolated fixture uses real character generation, the current mission catalog
and actual equipment objects. Its funds/resources differ from the mockup.

- [1280 × 720](images/squad-command-2/squad-1280x720.png)
- [1672 × 941 — reference dimensions](images/squad-command-2/squad-1672x941.png)
- [1920 × 1080](images/squad-command-2/squad-1920x1080.png)
- [2560 × 1440](images/squad-command-2/squad-2560x1440.png)
- [720p with large text](images/squad-command-2/squad-large-text.png)
- [English interface](images/squad-command-2/squad-english.png)
- [Real full agent sheet](images/squad-command-2/agent-sheet.png)
- [Real recruitment window](images/squad-command-2/recruitment.png)
- [Capture/interaction report](images/squad-command-2/report.json)

Visual review corrected the logo overlap, padded portrait crop, long mission
headings, stress-label collisions, navigation line spacing, missing repeated
batch labels, oversized primary-button text, feedback overlays and small-screen
large-text density. Existing portraits, equipment values and mission data remain
unchanged; this is a presentation redesign, not replacement character models.

## Validation

The final integration gate passed **84 tests plus 5 subtests**, including the real
Arcade capture driver, World Map regression and native Godot launch round trip.

The native capture test exercises every equipment direction, direct attribute
spending, single/double selection, squad keyboard toggles, the real full-sheet
attribute/skill/talent allocation controls, paid recruitment, overflow scrolling,
all downtime activities, save-slot selection, real temporary-directory save/load,
agent removal, day advance, room shortcuts, settings round-trip, mission routes,
empty rosters, English chrome and large text. Main-screen hits are checked against
viewport bounds at all four capture sizes. Repeated ready labels and old-language
batch visibility are checked explicitly. Navigation destination construction is
observed at the window boundary; the separate native launch regression covers
actual Arcade → Godot → management execution.

```sh
DISPLAY=:103 ALSOFT_DRIVERS=null python -m tools.check_squad_command_visual
DISPLAY=:103 ALSOFT_DRIVERS=null python -m pytest -q tests/test_management_hub_ui.py tests/test_room_interaction_ui.py tests/test_agent_equipment.py tests/test_downtime_management.py tests/test_squad_command_ui.py tests/test_static_game_flow_e2e.py tests/test_funds_management.py tests/test_world_map_ui.py tests/test_world_map_beacons.py tests/test_world_map_native.py tests/test_godot_launch_routing.py tests/test_music_continuity.py
```

Use the available X11 display instead of `:103`. Native capture tests skip without
one. Captures here use Mesa llvmpipe software rendering; their timing report is
not a hardware-GPU performance benchmark. No player save is modified by the driver.
