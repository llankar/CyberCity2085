#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$(realpath "$0")")/trellis_env.sh"
"$UV" pip install --link-mode hardlink --python "$LAB/venvs/hunyuan-shape/bin/python" opencv-python-headless
