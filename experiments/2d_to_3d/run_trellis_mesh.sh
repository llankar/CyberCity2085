#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$(realpath "$0")")/trellis_env.sh"
"$TRELLIS_PYTHON" "$(dirname "$(realpath "$0")")/run_trellis_mesh.py" "$@"
