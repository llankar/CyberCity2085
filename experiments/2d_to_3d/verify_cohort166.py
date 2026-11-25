"""Correlate the new cohort intervals with actual GPU-wide observations."""
import hashlib
import json
from pathlib import Path
from PIL import Image
from verify_benchmark_window import summarize


def main():
    folder = Path("E:/CyberCity2085-3d-lab/generated/phase2/modularity166")
    benchmark = json.loads((folder / "cohort_benchmark.json").read_text())
    gpu = json.loads((folder / "gpu166.json").read_text(encoding="utf-8-sig"))
    assert benchmark["status"] == "PASS" and benchmark["viewport"] == [1920, 1080]
    assert abs(benchmark["close_1_8m_pixels"] - 62.208) < .1
    assert abs(benchmark["overview_1_8m_pixels"] - 20.736) < .1
    assert [m["units"] for m in benchmark["measurements"]] == [2, 8, 16]
    for source in benchmark["sources"]:
        assert hashlib.sha256(Path(source["file"]).read_bytes()).hexdigest() == source["sha256"]
    result = {"status": "PASS", "measurements": [], "captures": {},
              "scope": "Two distinct source assets, multiple instances. Not ten unique texture sets, production mission performance or artistic acceptance."}
    for measurement in benchmark["measurements"]:
        result["measurements"].append({"units": measurement["units"], **summarize(measurement, gpu)})
    for name in ("cohort_close.png", "cohort_overview.png"):
        file = folder / name
        with Image.open(file) as image:
            assert image.size == (1920, 1080)
        result["captures"][name] = hashlib.sha256(file.read_bytes()).hexdigest()
    (folder / "cohort_verified.json").write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
