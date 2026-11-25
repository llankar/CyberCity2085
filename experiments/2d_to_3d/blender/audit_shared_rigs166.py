"""Read-only pair audit of existing authored humans; no fake garment swaps."""
import hashlib
import json
from pathlib import Path
import bpy


def inspect(path):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(path), use_anim=False)
    rigs = [obj for obj in bpy.context.scene.objects if obj.type == "ARMATURE"]
    if len(rigs) != 1:
        raise RuntimeError(f"Expected one real rig, got {len(rigs)}: {path}")
    bones = {bone.name: {"parent": bone.parent.name if bone.parent else None,
                         "matrix": [v for row in bone.matrix_local for v in row],
                         "length": bone.length} for bone in rigs[0].data.bones}
    return {"source": str(path), "source_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "bones": bones, "bone_count": len(bones),
            "mesh_count": sum(obj.type == "MESH" for obj in bpy.context.scene.objects)}


def main():
    lab = Path("E:/CyberCity2085-3d-lab")
    a = inspect(lab / "sources/rocketbox/Male_Adult_08/Export/Male_Adult_08.fbx")
    b = inspect(lab / "sources/rocketbox/Military_Male_03/Export/Military_Male_03_facial.fbx")
    common = sorted(a["bones"].keys() & b["bones"].keys())
    if not common:
        raise RuntimeError("No shared bone names")
    report = {"sources": [a, b], "common_bones": len(common),
              "only_a": sorted(a["bones"].keys() - b["bones"].keys()),
              "only_b": sorted(b["bones"].keys() - a["bones"].keys()),
              "parent_mismatches": [name for name in common if a["bones"][name]["parent"] != b["bones"][name]["parent"]],
              "max_rest_matrix_delta": max(abs(x-y) for name in common
                  for x, y in zip(a["bones"][name]["matrix"], b["bones"][name]["matrix"])),
              "scope": "Source skeleton compatibility only; clothing fit, animations and artistic quality unverified"}
    folder = lab / "generated/phase2/modularity166"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "rig_pair.json").write_text(json.dumps(report, indent=2))
    print("SHARED_RIG_PAIR_AUDITED", json.dumps({k:v for k,v in report.items() if k != "sources"}))


if __name__ == "__main__":
    main()
