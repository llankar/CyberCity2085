"""Only new acquisition/deduplication guards; do not rerun old asset trials."""
import hashlib
import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "experiments/2d_to_3d/run_trellis_mesh.py"
spec = importlib.util.spec_from_file_location("trellis_experiment", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_missing_or_crashed_kernel_cannot_authorize_weight_download():
    report = {"attention_operator": "cutlass", "checks": {
        name: {"status": "PASS"} for name in ("matmul", "attention", "sparse_conv")}}
    assert module.gpu_checks_pass(report)
    report["checks"]["attention"]["status"] = "RUNNING"
    assert not module.gpu_checks_pass(report)
    del report["checks"]["attention"]
    assert not module.gpu_checks_pass(report)


def test_prior_trial_reuse_requires_both_reference_and_output_integrity(tmp_path):
    mesh = tmp_path / "mesh.glb"
    mesh.write_bytes(b"test fixture, not a real model")
    prior = {"status": "PASS", "source_sha256": "original-reference",
             "glb_sha256": hashlib.sha256(mesh.read_bytes()).hexdigest()}
    assert module.verified_existing_mesh(prior, "original-reference", mesh)
    assert not module.verified_existing_mesh(prior, "changed-reference", mesh)
    mesh.write_bytes(b"changed output")
    assert not module.verified_existing_mesh(prior, "original-reference", mesh)
    mesh.unlink()
    assert not module.verified_existing_mesh(prior, "original-reference", mesh)
