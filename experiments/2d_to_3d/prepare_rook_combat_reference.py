"""Extract actual Godot idle frames, without repainting or changing game assets."""
import hashlib
import json
from pathlib import Path
from PIL import Image


def main():
    root = Path(__file__).resolve().parents[2]
    # Godot's actual String.hash("Rook") resolved by resolve_rook_reference.gd.
    key = "agent_diverse_14_armored_vanguard"
    manifest_path = root / f"assets/combat_visual/animations/{key}.json"
    manifest = json.loads(manifest_path.read_text())
    texture = root / manifest["texture"]
    digest = hashlib.sha256(texture.read_bytes()).hexdigest()
    if digest != manifest["texture_sha256"]:
        raise RuntimeError("Combat atlas does not match its runtime manifest")
    atlas = Image.open(texture).convert("RGBA")
    width, height = manifest["frame_size"]
    columns = atlas.width // width
    output = Path("E:/CyberCity2085-3d-lab/sources/rook_combat")
    output.mkdir(parents=True, exist_ok=True)
    report = {"name": "Rook", "runtime_key": key, "atlas": str(texture),
              "atlas_sha256": digest, "clip": "idle", "frames": [],
              "scope": "Actual combat sprite; not the portrait or legacy samurai fallback"}
    # Names describe manifest facing, not an assumed world-space camera angle.
    for name, direction in (("00_E", 0), ("01_S", 2),
                            ("02_W", 4), ("03_SE", 1)):
        index = manifest["animations"]["idle"]["rows"][direction][0]
        x, y = index % columns * width, index // columns * height
        frame = atlas.crop((x, y, x + width, y + height))
        if frame.getchannel("A").getbbox() is None:
            raise RuntimeError("Empty combat frame")
        file = output / f"{name}.png"
        frame.save(file)
        assert Image.open(file).convert("RGBA").tobytes() == frame.tobytes()
        report["frames"].append({"file": str(file), "index": index,
                                 "direction": direction, "rect": [x, y, width, height],
                                 "sha256": hashlib.sha256(file.read_bytes()).hexdigest()})
    (output / "provenance.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
