"""Acquire/verify only the three previously missing real body texture maps."""
import hashlib
import json
from pathlib import Path
import shutil
import urllib.request


def main():
    lab = Path("E:/CyberCity2085-3d-lab")
    metadata = lab / "tmp/rocketbox166-body-texture-metadata.json"
    if metadata.exists():
        entries = json.loads(metadata.read_text(encoding="utf-8-sig"))
    else:
        url = "https://api.github.com/repos/microsoft/Microsoft-Rocketbox/contents/Assets/Avatars/Adults/Male_Adult_08/Textures?ref=0943055db6ec570bcef9f2c8b41c9e5467c808f9"
        with urllib.request.urlopen(url) as response:
            entries = [e for e in json.load(response) if e["name"].startswith("m014_body_") and e["name"].endswith(".tga")]
    assert len(entries) == 3
    folder = lab / "sources/rocketbox/Male_Adult_08/Textures"
    report = []
    for entry in entries:
        name = entry["name"]
        assert name == Path(name).name and name.startswith("m014_body_") and name.endswith(".tga")
        target = folder / name
        if not target.exists():
            partial = target.with_suffix(".partial")
            with urllib.request.urlopen(entry["download_url"]) as response, partial.open("wb") as stream:
                shutil.copyfileobj(response, stream)
            partial.rename(target)
        data = target.read_bytes()
        assert len(data) == entry["size"]
        blob = hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()
        assert blob == entry["sha"], name
        report.append({"file": str(target), "git_blob": blob,
                       "sha256": hashlib.sha256(data).hexdigest(), "source": entry["download_url"]})
    (folder.parent / "texture_completion166.json").write_text(json.dumps(report, indent=2))
    print("THREE_REAL_BODY_TEXTURES_VERIFIED", json.dumps(report))


if __name__ == "__main__":
    main()
