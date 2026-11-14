"""Runtime path setup shared by source and frozen entry points."""

import os
import sys
from pathlib import Path


def configure_runtime_directory() -> Path:
    """Make bundled relative asset paths resolve beside the onedir executable."""
    if getattr(sys, "frozen", False):
        root = Path(sys.executable).resolve().parent
        os.chdir(root)
        return root
    return Path.cwd()
