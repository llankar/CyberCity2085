"""One new Hunyuan mini shape trial; no texture-model bulk acquisition."""
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
    parser.add_argument("subject", choices=["crate", "robot", "rook", "raider_grunt", "vehicle", "industrial_machine", "rook_unarmed", "stealth_vtol"])
    args = parser.parse_args()
    lab = Path(os.environ["LAB"]).resolve()
    if str(lab) != "/mnt/e/CyberCity2085-3d-lab":
        raise ValueError("Experimental files must remain on E:")
    source = lab / f"sources/{args.subject}.png"
    trial = args.subject
    if args.subject == "rook":
        source = lab / "sources/rook_combat/00_E.png"
        trial = "rook_combat"
    if args.subject == "rook_unarmed":
        source = lab / "generated/phase2/reference175/rook_unarmed.png"
    if args.subject == "stealth_vtol":
        source = lab / "sources/vtol220/reference.png"
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    output = lab / f"generated/phase2/{'hunyuan175' if args.subject=='rook_unarmed' else 'hunyuan166'}/{trial}"
    if args.subject == "stealth_vtol":
        output = lab / "generated/phase2/hunyuan220/stealth_vtol"
    output.mkdir(parents=True, exist_ok=True)
    evidence = output / "result.json"
    if evidence.exists():
        if verified_existing_mesh(json.loads(evidence.read_text()), digest, output / "mesh.glb"):
            print("REUSED_VERIFIED_MESH", evidence)
            return
        raise RuntimeError("Preserve previous trial; diagnose it before retry")
    sys.path.insert(0, str(lab / "repos/Hunyuan3D-2"))
    import torch
    import trimesh
    from PIL import Image
    from hy3dgen.shapegen import Hunyuan3DDiTFlowMatchingPipeline
    from huggingface_hub import hf_hub_download
    print("HUNYUAN_SHAPE_IMPORT_PASS", flush=True)
    report = {"status": "FAIL", "source_sha256": digest, "seed": 1,
              "subject": args.subject, "model": "tencent/Hunyuan3D-2mini",
              "subfolder": "hunyuan3d-dit-v2-mini", "steps": 50,
              "octree_resolution": 384, "texture_generation": False}
    start = time.perf_counter()
    torch.cuda.reset_peak_memory_stats()
    try:
        # Upstream snapshot_download fetches both ckpt and safetensors (duplicates).
        # Materialize only the actual variant before invoking the normal loader.
        local = Path(os.environ["HY3DGEN_MODELS"]) / report["model"]
        for name in ("config.yaml", "model.fp16.safetensors"):
            hf_hub_download(report["model"], f"{report['subfolder']}/{name}", local_dir=local)
        pipeline = Hunyuan3DDiTFlowMatchingPipeline.from_pretrained(
            report["model"], subfolder=report["subfolder"])
        image = Image.open(source)
        if image.mode != "RGBA" or image.getchannel("A").getextrema() == (255, 255):
            from rembg import new_session, remove
            image = remove(image, session=new_session("u2net"))
            assert image.getchannel("A").getbbox() is not None
            image.save(output / "prepared.png")
            report["background_preparation"] = "existing local u2net"
            report["prepared_sha256"] = hashlib.sha256((output / "prepared.png").read_bytes()).hexdigest()
        mesh = pipeline(image=image, num_inference_steps=50,
                        octree_resolution=384,
                        generator=torch.Generator(device="cuda").manual_seed(1))[0]
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
