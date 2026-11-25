#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$(realpath "$0")")/trellis_env.sh"
command -v gcc
command -v g++
command -v nvcc || true
command -v dpkg-deb
cuda_root="$LAB/tools/cuda168"
mkdir -p "$cuda_root"
for component in "$LAB/downloads/cuda168/"*.deb; do
    dpkg-deb -x "$component" "$cuda_root"
done
export CUDA_HOME="$cuda_root/usr/local/cuda-12.8"
export PATH="$CUDA_HOME/bin:$PATH"
export LD_LIBRARY_PATH="$CUDA_HOME/lib64:$LD_LIBRARY_PATH"
export TORCH_CUDA_ARCH_LIST="12.0"
export MAX_JOBS=1
nvcc --version
python="$LAB/venvs/hunyuan-shape/bin/python"
for includes in "$LAB/venvs/hunyuan-shape/lib/python3.11/site-packages/nvidia/"*/include; do
    export CPLUS_INCLUDE_PATH="$includes${CPLUS_INCLUDE_PATH:+:$CPLUS_INCLUDE_PATH}"
done
"$UV" pip install --python "$python" xatlas ninja pybind11 setuptools wheel
"$UV" pip install --python "$python" --no-build-isolation --no-deps "$LAB/repos/Hunyuan3D-2/hy3dgen/texgen/custom_rasterizer"
cd "$LAB/repos/Hunyuan3D-2"
"$python" -u -c 'import torch; import custom_rasterizer; from hy3dgen.texgen import Hunyuan3DPaintPipeline; print("HUNYUAN_PAINT_IMPORT_READY",flush=True)'
