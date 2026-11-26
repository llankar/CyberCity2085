"""First colour-texture trial on the existing Hunyuan robot; never regenerates shape."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import sys
import time
import urllib.request

LAB=Path('/mnt/e/CyberCity2085-3d-lab')
sys.path.insert(0,str(LAB/'repos/Hunyuan3D-2'))
_PAINT_PIPELINE=None

def main():
    global _PAINT_PIPELINE
    parser=argparse.ArgumentParser();parser.add_argument('--subject',choices=['robot','rook_combat','rook_unarmed','stealth_vtol'],default='robot')
    parser.add_argument('--local-only',action='store_true')
    parser.add_argument('--mesh',type=Path)
    parser.add_argument('--reference',type=Path)
    parser.add_argument('--output',type=Path)
    parser.add_argument('--label',help='Actual asset label for custom references')
    args=parser.parse_args();subject=args.subject
    output=LAB/('generated/phase2/paint168/robot_official' if subject=='robot' else 'generated/phase2/paint171/rook_official')
    if subject=='rook_unarmed':output=LAB/'generated/phase2/paint175/rook_unarmed'
    if subject=='stealth_vtol':output=LAB/'generated/phase2/paint220/stealth_vtol'
    custom=(args.mesh,args.reference,args.output)
    if any(p is not None for p in custom):
        if not all(p is not None for p in custom):raise ValueError('Custom mesh, reference and output are required together')
        if not all(p.resolve().is_relative_to(LAB) for p in custom):raise ValueError('Custom paths must remain inside E: lab')
        output=args.output.resolve()
        if not output.is_relative_to(LAB/'generated'):raise ValueError('Output must remain in generated experiments')
    output.mkdir(parents=True,exist_ok=True)
    if (output/'result.json').exists():
        raise RuntimeError('Preserve prior result; diagnose before changed retry')
    source=LAB/'generated/phase2/hunyuan166'/subject/'review_upright/optimized.glb'
    reference=LAB/'generated/phase2/hunyuan166'/subject/'prepared.png'
    if not reference.exists(): reference=LAB/('sources/robot.png' if subject=='robot' else 'sources/rook_combat/00_E.png')
    if subject=='rook_unarmed':
        source=LAB/'generated/phase2/hunyuan175/rook_unarmed/clean.glb'
        reference=LAB/'generated/phase2/reference175/rook_unarmed.png'
    if subject=='stealth_vtol':
        source=LAB/'generated/phase2/hunyuan220/stealth_vtol/review/optimized.glb'
        reference=LAB/'sources/vtol220/reference.png'
    if args.mesh is not None:source=args.mesh.resolve();reference=args.reference.resolve()
    assert source.is_file() and reference.is_file(),'Missing actual mesh/reference'
    import torch
    import custom_rasterizer as cr
    # The32px projection check already passed in paint168-robot-first.log.
    # Actual texture generation is the next useful exercise of this kernel.
    print('PAINT_PROJECTION_KERNEL_REUSED',flush=True)
    from hy3dgen.texgen.pipelines import Hunyuan3DPaintPipeline,Hunyuan3DTexGenConfig
    from huggingface_hub import snapshot_download
    import trimesh
    from PIL import Image
    print('PAINT_PIPELINE_IMPORT_READY',flush=True)
    # The published safetensors contains IP-adapter weights absent from the
    # official loader architecture. Use its required BIN, retaining strict=True.
    repo='tencent/Hunyuan3D-2'
    local=LAB/'models/hy3dgen'/repo
    if args.local_only:
        revision='retained-local-weights'
        assert (local/'hunyuan3d-paint-v2-0-turbo/unet/diffusion_pytorch_model.bin').is_file()
    else:
        meta=json.load(urllib.request.urlopen('https://huggingface.co/api/models/'+repo))
        revision=meta['sha']
        files=json.load(urllib.request.urlopen('https://huggingface.co/api/models/'+repo+'/tree/'+revision+'?recursive=true&limit=1000'))
        selected=[f for f in files if f['type']=='file' and f['path'].startswith(('hunyuan3d-delight-v2-0/','hunyuan3d-paint-v2-0-turbo/')) and f['path']!='hunyuan3d-paint-v2-0-turbo/unet/diffusion_pytorch_model.safetensors']
        total=sum(f.get('size',0) for f in selected)
        assert total<15_000_000_000
        print('PAINT_WEIGHT_PLAN',len(selected),total,flush=True)
        local=LAB/'models/hy3dgen'/repo
        snapshot_download(repo,revision=revision,allow_patterns=[f['path'] for f in selected],local_dir=local,max_workers=2)
    # Preserve the official state dictionary and strict key matching. Cast the
    # empty network first and memory-map the BIN to stay within WSL RAM limits.
    module=local/'hunyuan3d-paint-v2-0-turbo/unet/modules.py'
    code=module.read_text()
    if 'CC2085_SAFE_LOADER' in code:
        code=(LAB/'generated/phase2/paint168/robot/modules.upstream.py').read_text()
    needle="        unet_ckpt = torch.load(unet_ckpt_path, map_location='cpu', weights_only=True)"
    if 'CC2085_MEMORY_LOADER' not in code:
        assert code.count(needle)==1,'Upstream loader changed; inspect before patching'
        (output/'modules.upstream.py').write_text(code)
        replacement='''        # CC2085_MEMORY_LOADER: official BIN, strict keys unchanged.
        unet = unet.to(torch_dtype)
        unet_ckpt = torch.load(unet_ckpt_path, map_location='cpu', weights_only=True, mmap=True)'''
        module.write_text(code.replace(needle,replacement))
    report={'status':'FAIL','model':repo,'revision':revision,'source':str(source),
        'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
        'reference_sha256':hashlib.sha256(reference.read_bytes()).hexdigest(),
        'subject':args.label or subject,'scope':'Generated colour texture on existing mesh; not rigging or final art acceptance'}
    start=time.perf_counter()
    torch.cuda.reset_peak_memory_stats()
    try:
        config=Hunyuan3DTexGenConfig(str(local/'hunyuan3d-delight-v2-0'),str(local/'hunyuan3d-paint-v2-0-turbo'),'hunyuan3d-paint-v2-0-turbo')
        config.render_size=1024;config.texture_size=1024
        if _PAINT_PIPELINE is None:
            _PAINT_PIPELINE=Hunyuan3DPaintPipeline(config)
            print('PAINT_MODELS_LOADED',flush=True)
        else:print('PAINT_MODELS_REUSED_FOR_NEXT_ASSET',flush=True)
        pipeline=_PAINT_PIPELINE
        mesh=trimesh.load(source,force='mesh',process=False)
        result=pipeline(mesh,Image.open(reference))
        result.export(output/'mesh.glb')
        material=result.visual.material
        texture=getattr(material,'baseColorTexture',None)
        if texture is None: texture=getattr(material,'image',None)
        assert texture is not None,'Colour texture missing'
        texture.save(output/'colour.png')
        torch.cuda.synchronize()
        report.update(status='PASS',seconds=time.perf_counter()-start,
            torch_peak_allocated=torch.cuda.max_memory_allocated(),
            torch_peak_reserved=torch.cuda.max_memory_reserved(),
            texture_size=list(texture.size),triangles=len(result.faces),
            glb_sha256=hashlib.sha256((output/'mesh.glb').read_bytes()).hexdigest())
    except Exception as exc:
        report['error']=repr(exc)
        raise
    finally:
        (output/'result.json').write_text(json.dumps(report,indent=2))
        print('PAINT168_RESULT',json.dumps(report),flush=True)

if __name__=='__main__': main()
