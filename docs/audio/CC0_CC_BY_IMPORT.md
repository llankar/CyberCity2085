# CyberCity 2085 — Licensed audio import and review (CC0/CC BY)

This document accompanies the machine-readable [source catalog](cc0_ccby_sources.json)
and the actual [receipts](cc_import_receipts.json). **A verified URL or a
planned filename is not an installed audio file.** Installed files are listed in
the receipts only once they physically exist as WAVs.

## Licenses and authors

| Source | Author | License | Source and obtaining the original |
|---|---|---|---|
| Seamless City Loop | qubodup | CC0 | https://freesound.org/people/qubodup/sounds/223093/ (FLAC; Freesound login) |
| Raining In the City | RyanKingArt | CC0 | https://freesound.org/people/RyanKingArt/sounds/607228/ (M4A; Freesound login) |
| Robot / Mech Movement | Breviceps | CC0 | https://freesound.org/people/Breviceps/sounds/505670/ (WAV; Freesound login) |
| Metal footsteps on concrete | Thimras | CC0 | https://opengameart.org/content/metal-footsteps-on-concrete (7z) |
| Dark Sci-Fi Laboratory Atmosphere | TommasoMotteran | CC BY 4.0 | https://freesound.org/people/TommasoMotteran/sounds/864658/ (WAV; Freesound login) |
| Impact Sounds (130 originals) | Kenney | CC0 | https://kenney.nl/assets/impact-sounds |
| Sci-fi Sounds (70 originals) | Kenney | CC0 | https://kenney.nl/assets/sci-fi-sounds |
| Interface Sounds (100 originals) | Kenney | CC0 | https://kenney.nl/assets/interface-sounds |
| 25 CC0 bang/firework SFX | rubberduck | CC0 | https://opengameart.org/content/25-cc0-bang-firework-sfx (ZIP) |

The three Kenney pages explicitly label their packs CC0. For reproducibility,
18 selected original OGG files were located in a public mirrored archive
at https://github.com/Mcamento8/open-game-sfx-index and pinned by exact
commit **34bbe8b525b5ceff3804915ea745532af11f6055** plus Git blob SHA.
This source mirror is a transport only. Kenney is the author.

## Import commands

Requirements: Python 3.10+, ffmpeg; and 7z/7zz if importing Thimras.
Running an import generates only real WAVs in `assets/audio/overhaul/`, plus
receipts and `assets/audio/CREDITS_CC_AUDIO.md`.

```bash
# Automated CC0 pack selection (18 real audio files, no placeholders)
python tools/import_cc0_audio.py --kenney

# Original Freesound recordings obtained by the user through their account
python tools/import_cc0_audio.py --external seamless_city_qubodup "/downloads/seamless-city.flac"
python tools/import_cc0_audio.py --external city_rain_ryankingart "/downloads/city-rain.m4a"
python tools/import_cc0_audio.py --external robot_mech_breviceps "/downloads/robot.wav"
python tools/import_cc0_audio.py --external laboratory_tommasomotteran "/downloads/lab.wav"

# CC0 OpenGameArt archives — direct fetch can be blocked in some environments
python tools/import_cc0_audio.py --fetch-direct metal_footsteps_thimras
python tools/import_cc0_audio.py --fetch-direct oga_25_bang_rubberduck

# Or import archives already downloaded
python tools/import_cc0_audio.py --external metal_footsteps_thimras "/downloads/metal_steps_48k24b.7z"
python tools/import_cc0_audio.py --external oga_25_bang_rubberduck "/downloads/25-CC0-bang-sfx.zip"
```

Only a *curated five-file subset* from each OpenGameArt archive is staged by
default; the OGA bang candidates require audition before being mapped to
real game events. This avoids flooding GitHub with unreviewed samples.

## Use in Arcade and Godot

- The code uses only WAVs that exist on disk, with a legacy-SFX fallback.
- Arcade selects the next installed variant without immediate repetition.
- Godot copies installed WAVs via `game/combat/godot_bridge.py`, loads
  `res://audio/*.wav`, and has a dedicated ambience player.
- City, rainy city and laboratory environments are assigned separate ambient
  profiles. Their WAVs are optional and never replace the MP3 soundtrack.
- Current context-less events such as generic `hit` can use only a generic
  default. More granular weapon/material routing requires source event metadata.
- Original MP3 music and the historical 19 WAVs are preserved.

## Review and release gates

Generated/imported WAVs are **installed_unreviewed**, not "auditorily approved".
Before merging the audio branch or releasing a build, listen in the engine and
verify absence of sharp digital UI bleeps, overload, unwanted sound layers,
noticeable repetition, long clipped tails, and clicks at loop junctions.
Confirm gain balance with existing soundtrack. Existing CC BY source
attributions must remain in credits if an installed sound is CC BY; also record
the conversion from its original format as an adaptation.

Run targeted checks:

```bash
python -m unittest discover -s tests -p 'test_cc0_audio_import.py' -v
python -m pytest -q tests/test_cc0_audio_routing.py
```

The GitHub Audio build workflow also validates source Git blob SHA before
conversion, checks output WAV properties and attempts a headless Godot smoke
test. The smoke test is technical, *not listening validation*.

## Licenses in the code repository

The source code remains AGPL-3.0. CC0 sounds may be redistributed without
attribution. CC BY 4.0 sounds may be redistributed when the creator, original
source page, license URL and changes are credited. They are independent audio
works with their own licenses, not relicensed as AGPL solely by inclusion.
