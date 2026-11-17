# Main Menu Visual 2.0

The Arcade title screen is now a cinematic city overlook with a large metallic
wordmark, beveled command controls and restrained atmospheric animation. The
reference determines the framing: skyline emblem/logo at the upper center,
four real buttons vertically centered beneath it, wet city foreground and a
three-zone technological footer.

## Art and rendering

The new city image was generated using the previous title background as the
architectural base: side skyscrapers, rooftop railings and the central city vista
remain recognizable. New cyan/magenta holograms, flying vehicles, storm clouds,
fog and wet reflections provide the requested visual transformation. The chrome
CYBERCITY 2085 wordmark is a separate transparent generated asset. Neither asset
contains functional menu buttons; every control and subtitle is drawn by Arcade.

`assets/ui/title_background.png` remains byte-for-byte unchanged as the first
fallback if the new city art is unavailable. A procedural skyline provides a
second fallback. Missing wordmark art falls back to actual text. Asset dimensions,
origins and hashes are recorded in `assets/ui/title/manifest.json`.

The pure `layouts/title_menu.py` defines responsive geometry. `TitleMenuRenderer`
reuses cached typography/textures from Squad Command, adding cached beveled
frame meshes and a skyline emblem. `TitleAtmosphere` builds a bounded seeded rain
mesh once per resolution, translates it during frames, and animates low-intensity
city lights and drifting fog. Frames do not reload textures or regenerate rain.
The generated scene includes static vehicles and holograms; runtime rain, light,
fog, focus easing, active-button glow and sweep supply the motion.

## Actions and accessibility

- NEW GAME opens the original setup screen.
- CONTINUE resumes the most recently modified existing slot among the five real
  save slots. With no save it is visibly disabled and keyboard navigation skips
  it. Corrupt/unreadable data produces feedback; it never creates a replacement
  campaign. Save formats and campaign rules are unchanged.
- SETTINGS opens the original settings screen and returns to the same title view.
- QUIT and Escape retain the original exit action. Enter/Space selects the active
  item; arrows or W/S navigate; left click selects, right click is ignored.
- The active item has an orange rim/halo and sweep. Inactive enabled items use
  cyan; disabled Continue uses muted colors. Selection stays visible when the
  pointer leaves a button.
- Clicking the footer's **MOTION** control or pressing **M** toggles persistent
  reduced motion. It stops atmospheric time, rain, fog, pulses and sweeps, and
  makes focus changes immediate. Static rain drawn into the source image remains
  part of the artwork. Existing audio/display/text-size settings and extra flags
  are preserved when the preference is saved.

The title soundtrack still uses `SoundManager`'s original configuration/playback
API. No combat or campaign data changes during menu rendering.

## Actual version/build identity

The previous hardcoded `v3.0` has been removed. `game/version.py` reads declared
build revision metadata, installed package version, or the actual Git revision
once and caches the result. PyInstaller stamps that same identity into a bundled
`build_info.json`, so the footer remains accurate without Git on the player's
machine. If no version evidence exists it truthfully displays DEVELOPMENT BUILD.
AEGIS CORPORATION preserves the menu's existing identity.

## Native captures and verification

These images are real captures from the running Arcade menu:

- [1280×720](images/main-menu-2/menu-1280x720.png)
- [1920×1080](images/main-menu-2/menu-1920x1080.png)
- [2560×1440](images/main-menu-2/menu-2560x1440.png)
- [No saved campaign](images/main-menu-2/menu-no-save.png)
- [720p with large text](images/main-menu-2/menu-large-text.png)
- [Reduced motion](images/main-menu-2/menu-reduced-motion.png)
- [Original artwork fallback](images/main-menu-2/menu-legacy-fallback.png)
- [Procedural last fallback](images/main-menu-2/menu-procedural-fallback.png)

Visual comparison corrected shallow frame corners, overly small footer text,
unsupported arrow glyphs and long reduced-motion captions. The current layout
keeps the logo, subtitle, controls, notice and footer disjoint at all supported
resolutions. The native driver checks readable labels, actual save loading from
slot 3, all four actions, keyboard/mouse, right-click rejection, settings return,
corrupt saves, motion persistence/freezing, soundtrack calls and fallback art.
It also renders 20 warm frames without any texture loading and confirms the
rain mesh and logo stay cached. Frame timing is recorded as observational data,
not a hardware-independent performance guarantee.

The UI, settings and packaging suites are run separately because legacy UI tests
install different global Arcade test doubles. Reproduce with:

```sh
DISPLAY=:103 ALSOFT_DRIVERS=null python -m pytest -q tests/test_title_screen_ui.py tests/test_title_screen_background.py
python -m pytest -q tests/test_settings_screen_display.py tests/test_music_continuity.py
python -m pytest -q tests/test_release_packaging.py
DISPLAY=:103 ALSOFT_DRIVERS=null python -m tools.check_title_menu_visual
```

Validation: 28 tests pass, including native interactions and the packaged-entry
headless campaign smoke. The build identity stamp is validated without changing
any campaign data or save schema.
