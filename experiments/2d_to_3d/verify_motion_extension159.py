"""Audit original animation channels while adding actual authored motion clips."""
import argparse,hashlib,json
from pathlib import Path
from glb_document import Glb

def channels(glb, clip):
    result={}
    for channel in clip['channels']:
        target=channel['target'];node=glb.doc['nodes'][target['node']]['name']
        key=(node,target['path']);assert key not in result
        sampler=clip['samplers'][channel['sampler']]
        result[key]=(sampler.get('interpolation','LINEAR'),glb.values(sampler['input']),glb.values(sampler['output']))
    return result

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--native-proof',action='store_true');args=parser.parse_args()
    root=Path('E:/CyberCity2085-3d-lab/generated/phase2')
    source=Glb(root/'face_review156/human_face035.glb');target=Glb(root/'motion_extension159/human.glb')
    new={a['name']:a for a in target.doc['animations']}
    assert len(new)==9 and {'HitStudy','CoverStudy'}<=new.keys()
    original={}
    for old in source.doc['animations']:
        a=channels(source,old);b=channels(target,new[old['name']])
        assert a.keys()==b.keys(),old['name']
        changed=[key for key in a if a[key]!=b[key]]
        original[old['name']]={'channels':len(a),'byte_exact_channels':len(a)-len(changed),'changed_channels':changed}
    report={'original_clips':original,'new_clips':['HitStudy','CoverStudy'],
            'variant_sha256':hashlib.sha256((root/'motion_extension159/human.glb').read_bytes()).hexdigest(),
            'scope':'Animation accessor channel preservation only, not artistic acceptance'}
    (root/'motion_extension159/original_animation_audit.json').write_text(json.dumps(report,indent=2))
    assert all(not item['changed_channels'] for item in original.values()),'Original animations changed; inspect audit'
    print('MOTION159_ORIGINAL_SEVEN_CLIPS_BYTE_EXACT')
    if args.native_proof:
        folder=root/'motion_extension159'
        native=json.loads((folder/'native_actions.json').read_text())
        reference=json.loads((folder/'native_reference.json').read_text())
        assert native['glb_sha256']==report['variant_sha256']
        assert native['reference_sha256']==hashlib.sha256((folder/'native_reference.json').read_bytes()).hexdigest()
        assert reference['blend_sha256']==hashlib.sha256((folder/'human.blend').read_bytes()).hexdigest()
        assert native['samples']==sum(len(s) for s in reference['clips'].values())
        assert set(native['clips'])==set(new) and native['maximum_error_m']<.0005
        for label in ('HitStudy','CoverStudy'):
            assert native['clips'][label]['floor_m']>=-.0005
            assert native['clips'][label]['maximum_floor_m']<.005
        captures={}
        from PIL import Image
        for label in ('HitStudy','CoverStudy'):
            for view in ('front','side','back'):
                path=folder/f'{label}_{view}.png'
                with Image.open(path) as image:
                    image.load();assert image.size==(1280,720)
                captures[path.name]=hashlib.sha256(path.read_bytes()).hexdigest()
        report.update(native=native,captures_sha256=captures,artistic_acceptance='NOT VERIFIED: static midpoint views only, full contact/motion review remains open')
        (folder/'acceptance159.json').write_text(json.dumps(report,indent=2))
        print('MOTION159_NATIVE_EVIDENCE_VERIFIED',native['samples'],'samples;6 actual captures')

if __name__=='__main__':main()
