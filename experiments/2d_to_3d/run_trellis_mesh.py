"""Guarded, deduplicated image-to-mesh experiment; generated files stay on E:."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import time


def gpu_checks_pass(report):
    checks = report.get("checks", {})
    return (set(checks) == {"matmul", "attention", "sparse_conv"}
            and all(check.get("status") == "PASS" for check in checks.values())
            and report.get("attention_operator") == "cutlass")


def verified_existing_mesh(prior, source_sha, mesh):
    return (prior.get("status") == "PASS" and prior.get("source_sha256") == source_sha
            and mesh.is_file() and hashlib.sha256(mesh.read_bytes()).hexdigest()
            == prior.get("glb_sha256"))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("subject", choices=["crate", "robot", "rook", "raider_grunt",
                                             "vehicle", "industrial_machine"])
    parser.add_argument("--combat-reference", action="store_true")
    args = parser.parse_args()
    lab = Path(os.environ["LAB"]).resolve()
    if str(lab) != "/mnt/e/CyberCity2085-3d-lab":
        raise ValueError("Experimental data must remain on E:")
    checks = json.loads((lab / "tmp/trellis164-gpu-probe.json").read_text())
    if not gpu_checks_pass(checks):
        raise RuntimeError("Real GPU dependency probes must pass before model download")
    source = lab / "sources" / f"{args.subject}.png"
    sources = [source]
    trial = args.subject
    if args.combat_reference:
        if args.subject != "rook":
            raise ValueError("Combat reference selection is currently qualified for Rook only")
        sources = sorted((lab / "sources/rook_combat").glob("*.png"))
        if len(sources) != 4:
            raise RuntimeError("Four verified Godot combat views required")
        trial = "rook_combat"
    source_sha = hashlib.sha256(source.read_bytes()).hexdigest() if len(sources) == 1 else hashlib.sha256(
        b"".join(p.name.encode() + hashlib.sha256(p.read_bytes()).digest() for p in sources)).hexdigest()
    output = lab / "generated/phase2/trellis164" / trial
    output.mkdir(parents=True, exist_ok=True)
    evidence = output / "result.json"
    if evidence.exists():
        prior = json.loads(evidence.read_text())
        mesh = output / "mesh.glb"
        if verified_existing_mesh(prior, source_sha, mesh):
            print("REUSED_VERIFIED_MESH", evidence)
            return
        raise RuntimeError("Existing trial preserved; review it before a different retry")
    from huggingface_hub import hf_hub_download
    import torch
    import trimesh
    import numpy as np
    from PIL import Image
    sys.path.insert(0, str(lab / "repos/TRELLIS"))
    from trellis.pipelines import TrellisImageTo3DPipeline
    import xformers.ops as xops
    from functools import partial
    # Explicit supported operator; automatic Flash3 selection failed on sm_120.
    xops.memory_efficient_attention = partial(
        xops.memory_efficient_attention, op=xops.MemoryEfficientAttentionCutlassOp)
    repo = "microsoft/TRELLIS-image-large"
    config = json.loads(Path(hf_hub_download(repo, "pipeline.json")).read_text())
    # Keep official samplers/parameters, remove only unused output decoders.
    config["args"]["models"] = {
        key: value for key, value in config["args"]["models"].items()
        if key not in {"slat_decoder_gs", "slat_decoder_rf"}
    }
    local = lab / "models/TRELLIS-image-mesh"
    local.mkdir(parents=True, exist_ok=True)
    for key, model in list(config["args"]["models"].items()):
        for suffix in (".json", ".safetensors"):
            file = Path(hf_hub_download(repo, model + suffix))
            target = local / (model + suffix)
            target.parent.mkdir(parents=True, exist_ok=True)
            if not target.exists():
                target.symlink_to(file)
    (local / "pipeline.json").write_text(json.dumps(config, indent=2))
    start = time.perf_counter()
    torch.cuda.reset_peak_memory_stats()
    report = {"subject": args.subject, "source_sha256": source_sha,
              "formats": ["mesh"], "seed": 1, "status": "FAIL"}
    report["references"] = [{"file": str(p), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
                            for p in sources]
    try:
        pipeline = TrellisImageTo3DPipeline.from_pretrained(str(local))
        pipeline.cuda()
        with torch.inference_mode():
            if len(sources) == 1:
                generated = pipeline.run(Image.open(source), seed=1, formats=["mesh"])
            else:
                generated = pipeline.run_multi_image([Image.open(p) for p in sources],
                                                     seed=1, formats=["mesh"])
        mesh = generated["mesh"][0]
        vertices = mesh.vertices.detach().cpu().numpy()
        faces = mesh.faces.detach().cpu().numpy()
        colors = None
        if mesh.vertex_attrs is not None:
            colors = (mesh.vertex_attrs.detach().cpu().numpy().clip(0, 1) * 255).astype(np.uint8)
        if len(vertices) < 4 or len(faces) < 4 or not np.isfinite(vertices).all():
            raise RuntimeError("Invalid generated mesh")
        result = trimesh.Trimesh(vertices=vertices, faces=faces,
                                 vertex_colors=colors, process=False)
        path = output / "mesh.glb"
        result.export(path)
        reloaded = trimesh.load(path, force="mesh")
        assert len(reloaded.faces) == len(faces)
        report.update(status="PASS", vertices=len(vertices), triangles=len(faces),
                      glb_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                      artistic_acceptance="NOT VERIFIED")
    except Exception as exc:
        report["error"] = repr(exc)
        raise
    finally:
        torch.cuda.synchronize()
        report["elapsed_seconds"] = time.perf_counter() - start
        report["torch_peak_allocated_bytes"] = torch.cuda.max_memory_allocated()
        report["torch_peak_reserved_bytes"] = torch.cuda.max_memory_reserved()
        evidence.write_text(json.dumps(report, indent=2))
        print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
