#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$(realpath "$0")")/trellis_env.sh"
"$UV" venv --python 3.11 --allow-existing "$LAB/venvs/trellis-wsl"
"$UV" pip install --python "$TRELLIS_PYTHON" torch==2.7.1 torchvision==0.22.1 xformers==0.0.31 numpy==2.4.6 --index-url https://download.pytorch.org/whl/cu128
