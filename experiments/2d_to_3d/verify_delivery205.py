"""Check the assembled local delivery and its actual native-run evidence."""
from pathlib import Path
import json
import re
import argparse

parser=argparse.ArgumentParser();parser.add_argument("--latest",action="store_true");LATEST=parser.parse_args().latest
ROOT = Path("E:/CyberCity2085-3d-lab/deliveries/"+("tactical_demo215" if LATEST else "tactical_demo205"))
project = ROOT / "project"
manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf8"))
for item in manifest["files"]:
    path = (ROOT / item["file"]).resolve()
    assert path.is_relative_to(ROOT.resolve()), path
    assert path.is_file() and path.stat().st_size == item["bytes"], path
for file in project.glob("*.gd"):
    assert not re.search(r"[A-Z]:[\\/]", file.read_text(encoding="utf8")), file
config = json.loads((project / "lab/generated/phase2/amjviz_modules153/modules.json").read_text())
for item in config["variants"].values():
    assert item["file"].startswith("res://lab/"), item
    assert (project / item["file"][6:]).is_file(), item
for link in re.findall(r'(?:href|src)="([^"]+)"', (ROOT / "index.html").read_text(encoding="utf8")):
    assert (ROOT / link).is_file(), link
evidence = project / "evidence"
state = json.loads((evidence / "encounter.json").read_text())
native = json.loads((evidence / "native_summary.json").read_text())
melee = json.loads((evidence / "melee_contact.json").read_text())
shot = json.loads((evidence / "retaliation.json").read_text())
audio = json.loads((evidence / "audio.json").read_text())
assert not native["movie_mode"] and native["mean_fps"] >= 30, native
assert native["sample_frames"] > 800, native
assert state["health"] == [100, 0, 0, 100, 76, 100], state
assert state["blocked_shots"] >= 1 and state["occlusion_frames"] > 0, state
assert melee["wrist_to_chest_m"] <= .35 and melee["forward_hand_speed_m_s"] > .12, melee
assert shot["health_before"] - shot["health_after"] == 12, shot
assert shot["teammate_clearance_m"] > .35, shot
assert audio and all(Path(event["file"]).resolve().is_relative_to(project.resolve()) for event in audio)
assert all(Path(event["file"]).is_file() for event in audio)
if LATEST:
    recovery=json.loads((evidence/"recovery.json").read_text())
    assert recovery["health"]==100 and not recovery["contact_active"] and recovery["idle_rest_channels_reset"],recovery
report = {"status": "PASS", "recorded_files": len(manifest["files"]),
          "recorded_asset_bytes": manifest["bytes"], "native": native,
          "audio_events_inside_bundle": len(audio),
          "scope": "one local native run and explicit bundle paths/resources; not clean-PC or artistic acceptance"}
(ROOT / "verification").mkdir(exist_ok=True)
(ROOT / "verification/verified.json").write_text(json.dumps(report, indent=2), encoding="utf8")
print(json.dumps(report))
