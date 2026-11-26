"""Compile existing library associations into one independent Godot scene."""
import argparse,hashlib,json,math
from pathlib import Path
LAB=Path('E:/CyberCity2085-3d-lab')

def vector(value,name,positive=False):
    if not isinstance(value,list) or len(value)!=3 or any(not isinstance(n,(int,float)) or not math.isfinite(n) or (positive and n<=0) for n in value):
        raise ValueError('Invalid '+name)
    return value

def compile_bindings(data,map_name,lab=LAB):
    parents={r['source_object_id'] for r in data['records'] if r['source_map']==map_name}
    bindings=[]
    for asset in data.get('assets',[]):
        for index,association in enumerate(asset.get('map_associations',[])):
            if association['map']!=map_name:continue
            model=Path(asset['models']['glb']).resolve()
            if not model.is_relative_to(lab.resolve()) or not model.is_file():raise ValueError('Model must exist inside E: lab')
            parent=association['occlusion_parent']
            if parent not in parents:raise ValueError('Unknown surveyed parent '+parent)
            rotation=association['rotation']
            if not isinstance(rotation,(int,float)) or not math.isfinite(rotation):raise ValueError('Invalid rotation')
            match_bounds=association.get('match_replaced_bounds',False)
            if not isinstance(match_bounds,bool):raise ValueError('Invalid replacement bounds flag')
            bindings.append({'id':asset['id']+':'+str(index),'asset_id':asset['id'],'glb':str(model),
                'model_sha256':hashlib.sha256(model.read_bytes()).hexdigest(),
                'position':vector(association['position'],'position'),'scale':vector(association['scale'],'scale',True),
                'rotation_y':rotation,'parent':parent,'anchor':asset['anchor'],
                'replaces':association.get('replaces',[]),'vapor_offset':association.get('vapor_offset'),
                'match_replaced_bounds':match_bounds})
    return {'schema_version':1,'map':map_name,'instances':bindings,'tactical_mutation':False}

def write_if_changed(path,text):
    if not path.exists() or path.read_text(encoding='utf8')!=text:path.write_text(text,encoding='utf8')

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--map',choices=['city_exterior_neon_market_alley'],default='city_exterior_neon_market_alley')
    parser.add_argument('--environment')
    args=parser.parse_args()
    data=json.loads((LAB/'environment-library/library.json').read_text(encoding='utf8'))
    output=LAB/'generated/phase2/library227';output.mkdir(exist_ok=True)
    bindings=compile_bindings(data,args.map)
    previous=json.loads((output/'placements.json').read_text()) if (output/'placements.json').exists() else {}
    environment_choice=args.environment or previous.get('environment_relative','showcase219/environment.glb')
    environment=(LAB/'generated/phase2'/environment_choice).resolve()
    if not environment.is_relative_to((LAB/'generated/phase2').resolve()) or not environment.is_file():
        raise ValueError('Environment must exist inside the selected E: experiment assets')
    bindings['environment_relative']=environment.relative_to(LAB/'generated/phase2').as_posix()
    path=output/'placements.json';write_if_changed(path,json.dumps(bindings,indent=2))
    scene='[gd_scene load_steps=2 format=3]\n[ext_resource type="Script" path="res://library227.gd" id="1"]\n[node name="LibraryShowcase227" type="Node3D"]\nscript = ExtResource("1")\nbindings_path = '+json.dumps(path.as_posix())+'\n'
    write_if_changed(output/'scene.tscn',scene)
    print('LIBRARY_SCENE_COMPILED',len(bindings['instances']),output/'scene.tscn')

if __name__=='__main__':main()
