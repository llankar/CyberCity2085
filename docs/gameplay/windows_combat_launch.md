# Portable combat launch — November 15, 2026

## Campaign routing

New campaigns use Arcade as the reference tactical path. Launching from the
insertion room records `active_mission` and opens the local battle/deployment
view without starting a child process. Briefing deployment respects the same
default. Existing saves explicitly selecting `godot` retain that preference;
the save schema and campaign progress are unchanged.

The optional Godot route uses the nonblocking handoff view. If the executable
cannot start, the mission opens in Arcade. If its child exits before publishing
a result, the handoff view restores Arcade and starts the local battle. Results
are polled before searching for a native window, so an early result or early
crash cannot strand the campaign in the loading screen. A result is applied
once, and its completion takes precedence over process-exit fallback.

The broken direct-launch block formerly accessed a nonexistent `success` field
and attempted a separate aftermath call. That block is removed; normal Arcade
resolution and the existing optional Godot handoff own their respective outcomes.

## File exchange and process ownership

`godot_ipc` now uses files on every OS, without `mkfifo` or Unix sockets. Names
are local basenames under the supplied session directory; the old code nested
`runtime/godot_combat` twice. Starting a session removes only its stale exchange
files. The nonblocking launcher also removes the previous standard result before
starting another mission, preventing accidental reuse of old rewards.

The writer publishes `ipc_result.json` via a temporary sibling and rename before
the completion marker. Readers tolerate missing, malformed or partial JSON and
honor their deadline even if an incomplete file already exists.

Godot uses Godot 4 `FileAccess` and `DirAccess`; the invalid `File`/`Socket` API
references that prevented script loading are removed. The handoff's legacy
`ipc_pipe_path` field now denotes the optional completion-marker path. Godot
writes the matching session result in that directory.

The blocking compatibility API observes its own `Popen` handle. A child exit
without results returns promptly. An explicitly supplied timeout terminates and
reaps that child. There is no default five-minute cap on a legitimate battle.
Campaign UI uses the nonblocking route, not this compatibility method. The
nonblocking result also retains its own process handle for crash detection and
cleanup, rather than relying solely on a potentially reused PID.

## Evidence and limits

`python -m pytest -q`: **634 passed, 8 subtests passed** (Windows).

Coverage includes default Arcade launch with no external process, selected
Godot failure fallback, active-mission identity, existing save roundtrip with a
Godot preference, child-exit/result precedence, one-time result handling, timeout
cleanup, malformed-file deadlines and portable result publication. The full
Godot combat scene loads using `--headless` in the existing bridge regression.
Tests used stubbed windows/processes or a headless Godot process; no desktop
control or interactive window was used.

This proves automated launch/lifecycle behavior. It does not close the final
manual tactical playthrough, Windows packaging/distribution, complete Godot
campaign-aftermath parity, faction-coordination or tactical balance gates.
