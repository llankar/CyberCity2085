#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$(realpath "$0")")/trellis_env.sh"
"$LAB/venvs/triposg/bin/python" "$(dirname "$(realpath "$0")")/run_triposg.py" "$@"
