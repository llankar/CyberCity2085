# Headquarters Visual 2.0

The main management overview now uses a live holographic Headquarters layer over
a refreshed six-room cutaway tower. Actual counters, interactive room labels,
linked footer navigation, hover/focus easing and atmospheric effects are Arcade
components. No screenshot of the reference is used as an interface.

## Art and framing

The new `assets/ui/headquarters/tower_visual_2.png` was generated from the original
base artwork. It retains the central elevator, two columns of three departments,
the rooftop and the broad vehicle hangar. Interiors now distinguish the command
map, city-control aircraft displays, squad globe, engineering arms/vehicle
blueprint, research DNA hologram and intelligence data/server racks. Cyan and
midnight blue dominate, with restrained amber and magenta accents.

`assets/ui/corporate_tower_base.png` remains unchanged and is the first fallback.
Both images have their own calibrated room coordinates. If neither is available,
the six functional room panels still render procedurally. The manifest records
image hashes, dimensions and the measured rectangles for both artwork variants.

## Exact interaction geometry

`game/ui/layouts/headquarters.py` owns drawing and hit-test geometry. The image is
fitted without cropping or stretching; the same transform maps every room frame,
label, pointer target and footer entry. This also handles the existing 1920×1000
window configuration in addition to 1280×720, 1920×1080 and 2560×1440.

The elevator, gaps between floors and vehicle hangar remain scenery. No obsolete
legacy hit rectangles are active behind the new overview. Function keys and the
footer reach the same six existing departments. Escape still closes an open
department and returns from the overview to the title screen.

Presentation-only fields on `RoomUIState` carry the visual origin rectangle and a
cached crop of the currently displayed room. Existing 0.28-second expansion uses
that origin and art; close/open clears the override. Existing room action strips
and department renderers retain their handlers. Squad Command and character
sheets remain their dedicated screens, rather than hidden panels over the tower.
No campaign/save fields or department mechanics were changed.

## Rendering and accessibility

`HeadquartersRenderer` reuses cached Visual 2.0 typography, textures, pictograms
and meshes. The HUD reads available corporate funds and the four strategic
resources directly from the current game state. Interface headings/resource
labels follow its configured language; department names retain their existing
proper names and F1–F6 identities.

A single room receives strong focus: the currently hovered room, or the last
opened department when the pointer leaves. Labels sit on dark beveled rails;
selected/hover frames, corner details and linked footer feedback remain cyan.
Ambient overlays stay restrained: exterior-only rain, small display scans,
hologram light breathing and elevator glow. Cached meshes avoid per-frame rain
construction or texture loading. The menu's saved reduced-motion preference also
applies here, with immediate department expansion and no ambient animation.

The overview omits the old target circles, full-image scan grids, duplicated
keyboard footer text and translucent room fills that dulled the original art.
Actual notifications and existing department information remain accessible.
The HUD grows vertically with large text; long footer department names wrap
onto two lines. Save/load notices use short localized feedback rather than
printing internal routing fields or filesystem paths over the building.

## Real Arcade captures

- [1280×720](images/headquarters-2/hq-1280x720.png)
- [1920×1080](images/headquarters-2/hq-1920x1080.png)
- [2560×1440](images/headquarters-2/hq-2560x1440.png)
- [1920×1000 fitting](images/headquarters-2/hq-1920x1000.png)
- [Research hover](images/headquarters-2/hq-hover-research.png)
- [720p large text](images/headquarters-2/hq-large-text.png)
- [English HUD](images/headquarters-2/hq-english.png)
- [Original-art fallback](images/headquarters-2/hq-original-fallback.png)
- [Opening the research department](images/headquarters-2/transition-research.png)

These captures come from the running Arcade/OpenGL view and isolated campaign
fixtures. Visual comparison checked frame alignment against all six interior
edges, strengthened label contrast, kept the hangar unobstructed and limited
strong focus to one room. Department captures are retained as navigation evidence;
their existing functional screens were preserved rather than redesigned here.

## Validation

**59 tests and five subtests pass**, including native screenshots and interactions.
The native driver checks all six rooms through mouse, footer and function keys,
actual hover easing, opening origins and crops, Escape return, real resource
refresh, full serialized campaign equality before/after overview rendering,
settings language, cached frames, reduced motion, original-art hit zones and
actual room-strip save/load in an isolated temporary directory.

```sh
DISPLAY=:103 ALSOFT_DRIVERS=null python -m pytest -q tests/test_management_hub_ui.py tests/test_room_interaction_ui.py tests/test_facility_ui.py tests/test_headquarters_ui.py
DISPLAY=:103 ALSOFT_DRIVERS=null python -m tools.check_headquarters_visual
```

Publication follows the user's standing authorization to push and merge validated
changes automatically.
