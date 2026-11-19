# Windows tactical candidate R2 — November 15, 2026

R2 includes the current uncommitted tactical work: objective cloning fixes,
manual clinic bounds, defense/containment opening placement and overlays, allied
first-aid targeting, agent moments/debrief continuity and shared story resolution.
The previous candidate and ZIP remain intact.

Build command:

`powershell -NoProfile -ExecutionPolicy Bypass -File tools/build_windows.ps1 -OutputDirectory dist/tactical-candidate-20261115-r2`

The build gate passed **785 tests and eight subtests**. After adding an explicit
assertion for preserved story objectives, all five focused packaging tests passed.
PyInstaller produced the Windows executable, whose own window-free smoke passed:
122 reviewed surveys, seven MP3 files, fifteen story objective roundtrips,
temporary campaign save/load and a legal terminal dockside battle. This is the
actual frozen program, not just source execution. No desktop control was used.

The portable candidate contains French extraction instructions, the smoke report,
current 45-run story results and clearly labeled historical geometry/pacing
summaries. Its validation manifest records executable and source-file hashes;
older summaries retain their own source fingerprints and are not represented
as current full-matrix results. Live Godot handoffs are absent.

Executable: `dist/tactical-candidate-20261115-r2/CyberCity2085/CyberCity2085.exe`.
Extract the whole portable archive and keep the asset/library directories beside
that executable. Artifact hashes and archive-integrity results are recorded in
[the machine-readable report](windows_candidate_20261115_r2.json).

Portable ZIP: `dist/CyberCity2085-tactical-candidate-20261115-r2.zip`,
678,141,296 bytes (about 647 MiB). Every member passed CRC verification.
Archive SHA-256:
`d1fa77d185ffdcf0535e9c2631fb78db7ae77cee25fbb24825a75a901ba5fb68`.
The adjacent `.zip.sha256` file contains the same checksum. The packaged battle
finished in victory on turn 25.

This is a review candidate, not a completed retrofit. Graphical startup/input,
GPU rendering and audible playback have not been certified by this headless
check. Continuous campaign combat, mixed/support squads, overall balance and
the remaining tactical backlog are still open.
