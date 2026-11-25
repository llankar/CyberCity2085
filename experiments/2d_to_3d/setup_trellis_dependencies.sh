#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$(realpath "$0")")/trellis_env.sh"
"$UV" pip install --python "$TRELLIS_PYTHON" spconv-cu126 pillow imageio imageio-ffmpeg tqdm easydict opencv-python-headless scipy ninja rembg onnxruntime trimesh xatlas pyvista pymeshfix igraph transformers==4.57.6 safetensors huggingface-hub plyfile tensorboard numpy==2.4.6
"$UV" pip install --python "$TRELLIS_PYTHON" 'git+https://github.com/EasternJournalist/utils3d.git@9a4eb15e4021b67b12c460c7057d642626897ec8'
