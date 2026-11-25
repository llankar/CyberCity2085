"""Small real Blackwell kernel checks before downloading TRELLIS weights."""
import json
import os
from pathlib import Path
import time


def main():
    import torch
    report = {"torch": torch.__version__, "cuda": torch.version.cuda, "checks": {}}
    report["device"] = torch.cuda.get_device_name()
    report["capability"] = torch.cuda.get_device_capability()
    report["attention_operator"] = "cutlass"
    checks = report["checks"]
    output = Path(os.environ["LAB"]) / "tmp/trellis164-gpu-probe.json"
    for name in ("matmul", "attention", "sparse_conv"):
        checks[name] = {"status": "RUNNING"}
        output.write_text(json.dumps(report, indent=2))
        print("RUNNING", name, flush=True)
        start = time.perf_counter()
        try:
            if name == "matmul":
                a = torch.randn(256, 256, device="cuda")
                assert torch.isfinite(a @ a.T).all()
            elif name == "attention":
                import xformers.ops as xops
                q = torch.randn(1, 128, 8, 64, device="cuda", dtype=torch.float16)
                out = xops.memory_efficient_attention(q, q, q, op=xops.MemoryEfficientAttentionCutlassOp)
                assert out.shape == q.shape and torch.isfinite(out).all()
            else:
                import spconv.pytorch as spconv
                from spconv.core import ConvAlgo
                coords = torch.tensor([[0, x, y, z] for x in range(4)
                                       for y in range(4) for z in range(4)],
                                      device="cuda", dtype=torch.int32)
                features = torch.randn(64, 8, device="cuda")
                tensor = spconv.SparseConvTensor(features, coords, [8, 8, 8], 1)
                layer = spconv.SubMConv3d(8, 8, 3, padding=1,
                                          algo=ConvAlgo.Native).cuda().eval()
                with torch.inference_mode():
                    out = layer(tensor).features
                assert torch.isfinite(out).all()
            torch.cuda.synchronize()
            checks[name] = {"status": "PASS", "seconds": time.perf_counter() - start}
        except Exception as exc:
            checks[name] = {"status": "FAIL", "error": repr(exc)}
        output.write_text(json.dumps(report, indent=2))
    output.write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
    return int(any(item["status"] != "PASS" for item in checks.values()))


if __name__ == "__main__":
    raise SystemExit(main())
