"""Inspect real exported maps/UVs/offline image packing, not artistic quality."""
import hashlib
import io
import json
import sys
from pathlib import Path
from PIL import Image
from glb_document import Glb


def inspect(path, expected, require_colour_map=True):
    assert hashlib.sha256(path.read_bytes()).hexdigest() == expected
    glb = Glb(path)
    images = []
    for image in glb.doc.get("images", []):
        assert "uri" not in image, "External image dependency"
        view = glb.doc["bufferViews"][image["bufferView"]]
        offset = view.get("byteOffset", 0)
        data = glb.bin[offset:offset+view["byteLength"]]
        with Image.open(io.BytesIO(data)) as pixels:
            pixels.verify()
        with Image.open(io.BytesIO(data)) as pixels:
            images.append({"size": list(pixels.size), "format": pixels.format,
                           "sha256": hashlib.sha256(data).hexdigest()})
    materials = []
    for material in glb.doc.get("materials", []):
        pbr = material.get("pbrMetallicRoughness", {})
        materials.append({"name": material.get("name"), "base_colour_map": "baseColorTexture" in pbr,
                          "normal_map": "normalTexture" in material,
                          "metallic_roughness_map": "metallicRoughnessTexture" in pbr,
                          "roughness_factor": pbr.get("roughnessFactor", 1),
                          "alpha_mode": material.get("alphaMode", "OPAQUE"),
                          "extensions": sorted(material.get("extensions", {}))})
    assert images
    if require_colour_map:
        assert any(m["base_colour_map"] for m in materials)
    assert any(m["normal_map"] for m in materials)
    for mesh in glb.doc["meshes"]:
        for primitive in mesh["primitives"]:
            assert "TEXCOORD_0" in primitive["attributes"]
    return {"file": str(path), "source_sha256": expected, "images": images, "materials": materials}


def main():
    if "--baked-normal" in sys.argv:
        folder = Path("E:/CyberCity2085-3d-lab/generated/phase2/triposg166/rook_combat/normal_bake166")
        proof = json.loads((folder / "bake.json").read_text())
        report = inspect(folder / "mesh.glb", proof["glb_sha256"], require_colour_map=False)
        (folder / "material_audit.json").write_text(json.dumps(report, indent=2))
        print("BAKED_NORMAL_GLTF_AUDITED", json.dumps(report["materials"]))
        return
    folder = Path("E:/CyberCity2085-3d-lab/generated/phase2/modularity166")
    manifest = json.loads((folder / "exports.json").read_text())
    proof = json.loads((folder / "helmet_transfer_restfixed.json").read_text())
    subjects = [(Path(s["file"]), s["sha256"]) for s in manifest["exports"]]
    subjects.append((folder / "body_0_helmet_restfixed.glb", proof["output_sha256"]))
    report = {"status": "PASS", "subjects": [inspect(p, digest) for p, digest in subjects],
              "scope": "Actual embedded colour/normal images and UV bindings. PBR calibration, unseen anatomy and artistic acceptance unverified"}
    (folder / "material_audit.json").write_text(json.dumps(report, indent=2))
    print("THREE_TEXTURED_GLBS_AUDITED", [(len(s["images"]), len(s["materials"])) for s in report["subjects"]])


if __name__ == "__main__":
    main()
