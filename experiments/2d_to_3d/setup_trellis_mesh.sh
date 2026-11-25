#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$(realpath "$0")")/trellis_env.sh"
"$UV" pip install --python "$TRELLIS_PYTHON" open3d 'kaolin==0.18.0' --find-links https://nvidia-kaolin.s3.us-east-2.amazonaws.com/torch-2.7.1_cu128.html
cd "$LAB/repos/TRELLIS"
"$TRELLIS_PYTHON" -c 'from trellis.pipelines import TrellisImageTo3DPipeline; print("TRELLIS_PIPELINE_IMPORT_PASS")'
