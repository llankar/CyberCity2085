#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$(realpath "$0")")/trellis_env.sh"
"$LAB/venvs/hunyuan-shape/bin/python" "$(dirname "$(realpath "$0")")/run_hunyuan_shape.py" "$@"
