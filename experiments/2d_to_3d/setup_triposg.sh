#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$(realpath "$0")")/trellis_env.sh"
env_path="$LAB/venvs/triposg"
"$UV" venv --python 3.11 --allow-existing "$env_path"
"$UV" pip install --link-mode symlink --python "$env_path/bin/python" torch==2.7.1 torchvision==0.22.1 --index-url https://download.pytorch.org/whl/cu128
"$UV" pip install --link-mode symlink --python "$env_path/bin/python" diffusers==0.33.1 transformers==4.51.3 peft==0.15.2 accelerate omegaconf trimesh pillow scipy scikit-image safetensors numpy==1.26.4 einops jaxtyping typeguard tqdm
"$env_path/bin/python" - <<'PY'
import os
from pathlib import Path
p = Path(os.environ['LAB']) / 'repos/TripoSG/triposg/inference_utils.py'
s = p.read_text()
old = 'from diso import DiffDMC\n'
line = '        dmc = DiffDMC(dtype=torch.float32).to(grid_logits.device)'
if s.count(old) == 1 and s.startswith('import numpy') and '\n'+old in s:
    if line not in s:
        raise RuntimeError('Unexpected upstream source: refuse blind patch')
    s = s.replace(old, '', 1).replace(line, '        from diso import DiffDMC\n' + line, 1)
    p.write_text(s)
elif '        from diso import DiffDMC\n'+line not in s:
    raise RuntimeError('Optional diso patch not recognizable')
print('TRIPOSG_OPTIONAL_DISO_LAZY_IMPORT_READY')
PY
cd "$LAB/repos/TripoSG"
if [[ "${1:-}" == "--prepare-only" ]]; then exit 0; fi
"$env_path/bin/python" -u -c 'from triposg.pipelines.pipeline_triposg import TripoSGPipeline; print("TRIPOSG_PIPELINE_IMPORT_PASS")'
