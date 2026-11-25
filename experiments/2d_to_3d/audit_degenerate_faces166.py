"""Explain exact importer face-count changes, without a numerical tolerance."""
import hashlib
import argparse
import json
from pathlib import Path
import numpy as np
from glb_document import Glb


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--folder", default="E:/CyberCity2085-3d-lab/generated/phase2/triposg166/rook_combat")
    folder = Path(parser.parse_args().folder).resolve()
    if folder.drive.upper() != "E:":
        raise ValueError("Experimental resources must stay on E:")
    file = folder / "mesh.glb"
    source = Glb(file)
    raw, duplicate = 0, 0
    for mesh in source.doc["meshes"]:
        for primitive in mesh["primitives"]:
            accessor = source.doc["accessors"][primitive["indices"]]
            dtype = {5121: "u1", 5123: "<u2", 5125: "<u4"}[accessor["componentType"]]
            faces = np.frombuffer(source.values(primitive["indices"]), dtype=dtype).reshape(-1, 3)
            raw += len(faces)
            duplicate += int(np.count_nonzero((faces[:,0] == faces[:,1]) |
                                              (faces[:,0] == faces[:,2]) | (faces[:,1] == faces[:,2])))
    result = json.loads((folder / "result.json").read_text())
    review = json.loads((folder / "review_upright/review.json").read_text())
    assert raw == result["triangles"] and raw - duplicate == review["triangles"]
    report = {"source_sha256": hashlib.sha256(file.read_bytes()).hexdigest(),
              "raw_triangles": raw, "duplicate_index_faces": duplicate,
              "expected_import_triangles": raw - duplicate,
              "scope": "Exact duplicate-index triangle removal at import, not permissive count matching"}
    (folder / "geometry_import_audit.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
