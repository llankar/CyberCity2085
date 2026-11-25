"""Cross-check first-time inference, Blender renders and native GLB evidence."""
import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(folder):
    result = json.loads((folder / "result.json").read_text())
    review_dir = folder / "review_upright"
    review = json.loads((review_dir / "review.json").read_text())
    native = json.loads((review_dir / "godot.json").read_text())
    assert result["status"] == native["status"] == "PASS"
    assert result["glb_sha256"] == review["source_sha256"] == sha(folder / "mesh.glb")
    assert result["triangles"] == review["triangles"]
    assert review["source_z_up_correction"] is True
    assert review["optimized_triangles"] == native["triangles"]
    assert review["optimized_glb_sha256"] == native["source_sha256"] == sha(review_dir / "optimized.glb")
    for name, digest in review["renders"].items():
        path = review_dir / f"{name}.png"
        assert sha(path) == digest
        with Image.open(path) as image:
            assert image.size == (768, 768)
    with Image.open(review_dir / "optimized_isometric.png") as image:
        assert image.size == (768, 768)
    for name in ("model.blend", "optimized.blend"):
        assert (review_dir / name).stat().st_size > 1000
    return {"status": "PASS", "trial": folder.name,
            "triangles": result["triangles"], "optimized_triangles": native["triangles"],
            "optimized_glb_sha256": native["source_sha256"],
            "scope": "Artifact integrity and native mesh import, not artistic acceptance"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("trial", choices=["robot", "rook_combat"])
    args = parser.parse_args()
    folder = Path("E:/CyberCity2085-3d-lab/generated/phase2/trellis164") / args.trial
    report = verify(folder)
    (folder / "verified.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
