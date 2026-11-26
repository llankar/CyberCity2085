#!/usr/bin/env bash
# Source in WSL. Never relocate HOME or change production environments.
export LAB=/mnt/e/CyberCity2085-3d-lab
export TMPDIR="$LAB/tmp"
export TMP="$TMPDIR" TEMP="$TMPDIR"
export UV_CACHE_DIR="$LAB/cache/uv"
export UV_PYTHON_INSTALL_DIR="$LAB/tools/python"
export PIP_CACHE_DIR="$LAB/cache/pip"
export HF_HOME="$LAB/cache/huggingface"
export HUGGINGFACE_HUB_CACHE="$HF_HOME/hub"
export TORCH_HOME="$LAB/cache/torch"
export HY3DGEN_MODELS="$LAB/models/hy3dgen"
export U2NET_HOME="$LAB/models/u2net"
export TORCH_EXTENSIONS_DIR="$LAB/cache/torch_extensions"
export CUDA_CACHE_PATH="$LAB/cache/cuda"
export TRITON_CACHE_DIR="$LAB/cache/triton"
export XDG_CACHE_HOME="$LAB/cache/xdg"
export XDG_CONFIG_HOME="$LAB/config/xdg"
export PYTHONPYCACHEPREFIX="$LAB/cache/python/hunyuan"
export PYTHONUNBUFFERED=1
export ATTN_BACKEND=xformers SPCONV_ALGO=native
export UV="$LAB/tools/uv/uv"
export TRELLIS_PYTHON="$LAB/venvs/trellis-wsl/bin/python"
export LD_LIBRARY_PATH="$LAB/tools/trellis-native/usr/lib/x86_64-linux-gnu${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
mkdir -p "$TMPDIR" "$XDG_CONFIG_HOME" "$XDG_CACHE_HOME" "$TORCH_HOME"
