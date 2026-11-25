#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$(realpath "$0")")/trellis_env.sh"
export CUDA_HOME="$LAB/tools/cuda168/usr/local/cuda-12.8"
export PATH="$CUDA_HOME/bin:$PATH"
export LD_LIBRARY_PATH="$LAB/venvs/hunyuan-shape/lib/python3.11/site-packages/torch/lib:$CUDA_HOME/lib64:$LD_LIBRARY_PATH"
"$LAB/venvs/hunyuan-shape/bin/python" -u "$(dirname "$(realpath "$0")")/run_hunyuan_paint168.py"
