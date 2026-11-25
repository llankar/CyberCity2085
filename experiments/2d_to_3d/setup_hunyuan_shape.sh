#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$(realpath "$0")")/trellis_env.sh"
env_path="$LAB/venvs/hunyuan-shape"
"$UV" venv --python 3.11 --allow-existing "$env_path"
# Symlink existing E: wheel cache rather than duplicating the CUDA downloads.
"$UV" pip install --link-mode symlink --python "$env_path/bin/python" torch==2.7.1 torchvision==0.22.1 --index-url https://download.pytorch.org/whl/cu128
"$UV" pip install --link-mode symlink --python "$env_path/bin/python" diffusers==0.33.1 transformers==4.57.6 accelerate omegaconf trimesh pillow scipy scikit-image safetensors numpy==2.4.6 einops rembg onnxruntime tqdm pygltflib pymeshlab
cd "$LAB/repos/Hunyuan3D-2"
"$env_path/bin/python" -u -c 'from hy3dgen.shapegen import Hunyuan3DDiTFlowMatchingPipeline; print("HUNYUAN_SHAPE_IMPORT_PASS")'
