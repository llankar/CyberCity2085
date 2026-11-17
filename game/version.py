"""Truthful build identity: distribution metadata or the actual checkout revision."""

from functools import lru_cache
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
import os
import sys
import json
import subprocess


@lru_cache(maxsize=1)
def build_label():
    revision = os.environ.get("CYBERCITY_BUILD_REVISION", "").strip()
    if revision:
        return "BUILD " + revision[:12]
    try:
        return "v" + version("CyberCity2085")
    except PackageNotFoundError:
        pass
    if getattr(sys, "frozen", False):
        try:
            root = Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
            data = json.loads((root / "build_info.json").read_text(encoding="utf-8"))
            return str(data["label"])
        except (OSError, ValueError, KeyError, TypeError):
            return "DEVELOPMENT BUILD"
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=Path(__file__).resolve().parents[1],
            capture_output=True,
            text=True,
            timeout=1,
            check=True,
        )
        return "BUILD " + result.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return "DEVELOPMENT BUILD"
