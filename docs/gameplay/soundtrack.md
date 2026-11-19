# Soundtrack integration

The shared catalogue is `game/audio/music_catalog.py`. Arcade selects its music
key directly; the Godot handoff carries the absolute chosen path and audio
preferences, so both clients use the same mission routing.

| Track | Context |
| --- | --- |
| Intro 1 | Title menu and campaign epilogue |
| Intro 2 | Management and mission briefing |
| Neon Street Warfare | Standard tactical combat |
| Subnet Breach | Data theft and sabotage / relay hacking |
| Neon Highway Chase | Missions mentioning chase, pursuit, convoy, or highway |
| Cybernetic Final Battle | Act 5 and finale-tagged missions |
| Cybernetic Final Battle 2 | Seven Minutes, the final campaign operation |
| Original music_debrief.wav | Post-mission debrief |

Finale routing takes priority over hacking/chase music. Existing WAV music is a
fallback when an MP3 is absent or cannot load. Re-entering the same music context
does not restart its track. Music loops and follows saved volume/mute settings.
Arcade decodes only the selected song as a loop-capable static source, releasing
the previous cached song on transition; it does not decode the whole catalogue
at startup. Streaming music sources in Arcade do not support reliable looping.
Godot loads MP3 bytes directly from the handoff asset location without requiring
an editor import or extra copies of the soundtrack. Arcade music stops after a
successful Godot launch to avoid two simultaneous soundtracks.

Validation: `python -m pytest tests/test_music_catalog.py -q` covers routing,
asset coverage, missing-file fallback, no-restart/mute behavior, real silent
Arcade decoder checks, and all MP3s loaded/looped in headless Godot with Dummy
audio. No desktop activation, input injection, or audible playback is used.

Latest verification: 13 soundtrack tests pass. Combined project/AI regression
run: 616 passed, 10 failed, 8 subtests passed. The same ten pre-existing failures
remain (IPC Windows setup, Godot result-script parsing, enemy intent labels and
backlog active-slice status). The isolated Godot audio test loads every MP3 and
validates looping/mute independently of the broken result script.
