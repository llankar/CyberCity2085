#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$(realpath "$0")")/trellis_env.sh"
"$UV" pip install --python "$LAB/venvs/triposg/bin/python" --target "$LAB/tools/py-spy" py-spy==0.4.1
