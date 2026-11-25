"""New TripoSG standard decoder trial using actual combat art, never portraits."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import time
from run_trellis_mesh import verified_existing_mesh


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("subject", choices=["rook", "robot"])
    args = parser.parse_args()
    lab = Path(os.environ["LAB"]).resolve()
    if str(lab) != "/mnt/e/CyberCity2085-3d-lab":
        raise ValueError("Experimental files must stay on E:")
    source = lab / ("sources/rook_combat/00_E.png" if args.subject == "rook" else "sources/robot.png")
    trial = "rook_combat" if args.subject == "rook" else "robot"
    output = lab / "generated/phase2/triposg166" / trial
    output.mkdir(parents=True, exist_ok=True)
    evidence = output / "result.json"
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    if evidence.exists():
        if verified_existing_mesh(json.loads(evidence.read_text()), digest, output / "mesh.glb"):
            print("REUSED_VERIFIED_MESH", evidence); return
        raise RuntimeError("Prior trial preserved; diagnose before a changed retry")
    sys.path.insert(0, str(lab / "repos/TripoSG"))
    print("IMPORTING_TRIPOSG", flush=True)
    import torch
    import trimesh
    from PIL import Image
    from huggingface_hub import snapshot_download
    from triposg.pipelines.pipeline_triposg import TripoSGPipeline
    print("TRIPOSG_PIPELINE_IMPORT_PASS", flush=True)
    report = {"status": "FAIL", "source": str(source), "source_sha256": digest,
              "model": "VAST-AI/TripoSG", "decoder": "hierarchical_standard",
              "steps": 50, "dense_octree_depth": 8, "hierarchical_octree_depth": 9,
              "seed": 1, "texture_generation": False}
    start = time.perf_counter()
    torch.cuda.reset_peak_memory_stats()
    try:
        weights = snapshot_download(report["model"], allow_patterns=["*.json", "*.safetensors"])
        pipeline = TripoSGPipeline.from_pretrained(weights, torch_dtype=torch.float16,
                                                   low_cpu_mem_usage=True).to("cuda")
        image = Image.open(source).convert("RGBA")
        background = Image.new("RGBA", image.size, (255, 255, 255, 255))
        image = Image.alpha_composite(background, image).convert("RGB")
        with torch.inference_mode():
            result = pipeline(image=image, generator=torch.Generator(device="cuda").manual_seed(1),
                              use_flash_decoder=False, num_inference_steps=50,
                              dense_octree_depth=8, hierarchical_octree_depth=9)
        mesh = result.meshes[0]
        if len(mesh.vertices) < 4 or len(mesh.faces) < 4:
            raise RuntimeError("Invalid generated mesh")
        path = output / "mesh.glb"
        mesh.export(path)
        reloaded = trimesh.load(path, force="mesh")
        assert len(reloaded.faces) == len(mesh.faces)
        report.update(status="PASS", vertices=len(mesh.vertices), triangles=len(mesh.faces),
                      glb_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                      artistic_acceptance="NOT VERIFIED")
    except Exception as exc:
        report["error"] = repr(exc)
        raise
    finally:
        report["elapsed_seconds"] = time.perf_counter() - start
        report["torch_peak_allocated_bytes"] = torch.cuda.max_memory_allocated()
        report["torch_peak_reserved_bytes"] = torch.cuda.max_memory_reserved()
        evidence.write_text(json.dumps(report, indent=2))
        print(json.dumps(report, indent=2), flush=True)


if __name__ == "__main__":
    main()
