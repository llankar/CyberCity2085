"""Merge verified compatible GLB clips, retaining seconds and scoped morphs.

Geometry/materials are shared once. Every clip explicitly drives every union
morph so native action changes cannot retain corrections from the prior clip.
"""
import copy
import hashlib
import json
import struct
from pathlib import Path
from glb_document import Glb
from gltf_pose import rebase_flat_tracks

ROOT=Path('E:/CyberCity2085-3d-lab/generated/phase2')
SOURCES=['einar_ual_Pistol_Shoot01_surfaces','einar_idle01','einar_walk01',
         'einar_ual_Punch_Cross01_surfaces','einar_ual_Death0101_surfaces']


def padded_weights(values,source_count,total_count,offset,constant=None):
    if source_count<=0 or len(values)%source_count or offset<0 or offset+source_count>total_count:
        raise ValueError('Invalid morph range/count')
    if constant is not None and (constant<0 or constant>=total_count or offset<=constant<offset+source_count):
        raise ValueError('Constant correction overlaps motion targets')
    result=[]
    for start in range(0,len(values),source_count):
        row=[0.0]*total_count
        row[offset:offset+source_count]=values[start:start+source_count]
        if constant is not None: row[constant]=1.0
        result.extend(row)
    return result


def unpack_floats(glb,index):
    if glb.doc['accessors'][index]['componentType']!=5126: raise ValueError('Float accessor required')
    raw=glb.values(index)
    return struct.unpack('<'+'f'*(len(raw)//4),raw)


def bundle(*, root_path=ROOT, sources_spec=None, output_folder='einar_bundle02', output_name='human_actions.glb', credits=None, limitations=None):
    root_path=Path(root_path)
    source_files=list(sources_spec) if sources_spec is not None else [(name,'human_rig.glb') for name in SOURCES]
    if len(source_files)<2 or any(Path(folder).name!=folder or Path(filename).name!=filename for folder,filename in source_files):
        raise ValueError('Bounded local source folders/files required')
    if Path(output_folder).name!=output_folder or Path(output_name).name!=output_name:
        raise ValueError('Local output folder/file required')
    source_labels=[folder for folder,filename in source_files]
    sources=[Glb(root_path/folder/filename) for folder,filename in source_files]
    base=sources[0]
    original_animations=[copy.deepcopy(g.doc['animations']) for g in sources]
    mesh_maps=[{m['name']:index for index,m in enumerate(g.doc['meshes'])} for g in sources]
    node_maps=[{n['name']:index for index,n in enumerate(g.doc['nodes'])} for g in sources]
    for glb,mapping in zip(sources,node_maps):
        assert len(mapping)==len(glb.doc['nodes']) and mapping.keys()==node_maps[0].keys()
        assert len(glb.doc['skins'])==1
        joint_names=[glb.doc['nodes'][i]['name'] for i in glb.doc['skins'][0]['joints']]
        assert joint_names==[base.doc['nodes'][i]['name'] for i in base.doc['skins'][0]['joints']]
        joints=set(glb.doc['skins'][0]['joints'])
        for name,index in mapping.items():
            if index in joints: continue  # Explicitly rebase joint tracks below.
            for key in ['matrix','translation','rotation','scale']:
                assert glb.doc['nodes'][index].get(key)==base.doc['nodes'][node_maps[0][name]].get(key),(name,key)
    # Snapshot morph counts before modifying the first source document in place.
    counts={(s,m['name']):len(m['primitives'][0].get('targets',[]))
            for s,g in enumerate(sources) for m in g.doc['meshes']}
    copied={}
    def accessor(source,index):
        if source==0: return index
        key=(source,index)
        if key not in copied: copied[key]=base.copy_accessor(sources[source],index)
        return copied[key]
    ranges={}; normal_offsets={}; union={}
    for mesh in base.doc['meshes']:
        name=mesh['name']; targets=[[] for primitive in mesh['primitives']]
        target_names=[]
        for source,glb in enumerate(sources):
            candidate=glb.doc['meshes'][mesh_maps[source][name]]
            assert len(candidate['primitives'])==len(mesh['primitives'])
            offset=len(target_names); count=counts[source,name]
            correction=[]
            for p,(primitive,wanted) in enumerate(zip(candidate['primitives'],mesh['primitives'])):
                assert primitive['attributes'].keys()==wanted['attributes'].keys()
                assert glb.values(primitive['indices'])==base.values(wanted['indices'])
                differences={}
                for attribute,index in primitive['attributes'].items():
                    expected=wanted['attributes'][attribute]
                    if glb.values(index)==base.values(expected): continue
                    assert attribute=='NORMAL',(name,attribute)
                    before=unpack_floats(base,expected); after=unpack_floats(glb,index)
                    assert len(before)==len(after)
                    differences['NORMAL']=[b-a for a,b in zip(before,after)]
                correction.append(differences)
                assert len(primitive.get('targets',[]))==count
                for target in primitive.get('targets',[]):
                    targets[p].append({key:accessor(source,index) for key,index in target.items()})
            target_names.extend(f'{source_labels[source]}_{i:03d}' for i in range(count))
            constant=None
            if any(correction):
                constant=len(target_names); target_names.append(source_labels[source]+'_base_normal')
                normal_offsets[f'{source}:{name}']=max(abs(x) for part in correction for values in part.values() for x in values)
                for p,part in enumerate(correction):
                    # glTF permits NORMAL-only targets; other primitives get zero normals.
                    if not part:
                        vertex_count=base.doc['accessors'][mesh['primitives'][p]['attributes']['POSITION']]['count']
                        part={'NORMAL':[0.0]*(vertex_count*3)}
                    targets[p].append({key:base.add_floats(values,len(values)//3,'VEC3') for key,values in part.items()})
            ranges[source,name]=(offset,count,constant)
        if target_names:
            union[name]=len(target_names)
            for primitive,merged in zip(mesh['primitives'],targets): primitive['targets']=merged
            mesh['weights']=[0.0]*len(target_names)
            mesh.setdefault('extras',{})['targetNames']=target_names
    for node in base.doc['nodes']:
        if 'mesh' in node:
            name=base.doc['meshes'][node['mesh']]['name']
            if name in union: node['weights']=[0.0]*union[name]
    base.doc['animations']=[]; durations={}; rebase_errors={}
    for source,(glb,animations) in enumerate(zip(sources,original_animations)):
        assert len(animations)==1
        original=animations[0]; animation={'name':original['name'],'channels':[],'samplers':[]}
        duration=max(glb.doc['accessors'][sampler['input']]['max'][0] for sampler in original['samplers'])
        durations[animation['name']]=duration
        driven=set()
        source_joints=set(glb.doc['skins'][0]['joints'])
        needs_rebase=glb.values(glb.doc['skins'][0]['inverseBindMatrices'])!=base.values(base.doc['skins'][0]['inverseBindMatrices'])
        for channel in original['channels']:
            if needs_rebase and channel['target']['node'] in source_joints: continue
            sampler=original['samplers'][channel['sampler']]
            target_node=glb.doc['nodes'][channel['target']['node']]
            target_name=target_node['name']; path=channel['target']['path']
            new_sampler={'input':accessor(source,sampler['input']),
                         'interpolation':sampler.get('interpolation','LINEAR')}
            if path=='weights':
                assert new_sampler['interpolation']=='LINEAR'
                name=glb.doc['meshes'][target_node['mesh']]['name']
                offset,count,constant=ranges[source,name]
                expanded=padded_weights(unpack_floats(glb,sampler['output']),count,union[name],offset,constant)
                new_sampler['output']=base.add_floats(expanded,len(expanded))
                driven.add(name)
            else: new_sampler['output']=accessor(source,sampler['output'])
            animation['channels'].append({'sampler':len(animation['samplers']),
                'target':{'node':node_maps[0][target_name],'path':path}})
            animation['samplers'].append(new_sampler)
        if needs_rebase:
            times,rebased,error=rebase_flat_tracks(glb,base,original,unpack_floats)
            rebase_errors[original['name']]=error
            time_accessor=base.add_floats(times,len(times))
            base.doc['accessors'][time_accessor].update({'min':[min(times)],'max':[max(times)]})
            for node_name,tracks in rebased:
                for path,values in tracks.items():
                    animation['channels'].append({'sampler':len(animation['samplers']),
                        'target':{'node':node_maps[0][node_name],'path':path}})
                    animation['samplers'].append({'input':time_accessor,
                        'output':base.add_floats(values,len(times),'VEC4' if path=='rotation' else 'VEC3'),
                        'interpolation':'LINEAR'})
        for name,count in union.items():
            if name in driven: continue
            _,_,constant=ranges[source,name]
            row=[0.0]*count
            if constant is not None: row[constant]=1.0
            nodes=[i for i,n in enumerate(base.doc['nodes']) if n.get('mesh')==mesh_maps[0][name]]
            assert len(nodes)==1
            time=base.add_floats([0.0,duration],2)
            base.doc['accessors'][time].update({'min':[0.0],'max':[duration]})
            output=base.add_floats(row+row,count*2)
            animation['channels'].append({'sampler':len(animation['samplers']),
                'target':{'node':nodes[0],'path':'weights'}})
            animation['samplers'].append({'input':time,'output':output,'interpolation':'LINEAR'})
        base.doc['animations'].append(animation)
    folder=root_path/output_folder; folder.mkdir(exist_ok=True)
    credit=[{'asset':'Einar','author':'Blender Foundation','license':'CC BY4.0',
             'url':'https://studio.blender.org/characters/einar/v1/'},
            {'asset':'Universal Animation Library Standard','author':'Quaternius','license':'CC0 1.0',
             'url':'https://quaternius.com/packs/universalanimationlibrary.html'}]
    if credits is not None: credit=credits
    base.doc['asset'].setdefault('extras',{})['credits']=credit
    base.save(folder/output_name)
    report={'clips':durations,'meshes':len(base.doc['meshes']),'joints':len(base.doc['skins'][0]['joints']),
        'union_targets':union,'normal_base_offsets':normal_offsets,'joint_trs_recomposition_errors':rebase_errors,'credits':credit,
        'sources':[{'folder':name,'file':filename,'sha256':hashlib.sha256((root_path/name/filename).read_bytes()).hexdigest()} for name,filename in source_files],
        'limitations':limitations if limitations is not None else ['Five motion studies, not artistic acceptance','No weapon/hair included','Sampled morph size unoptimized']}
    (folder/'bundle_report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print('EINAR_ACTION_BUNDLE_CREATED',json.dumps({'clips':durations,'targets':union,'bytes':(folder/output_name).stat().st_size}))

    return report


if __name__=='__main__': bundle()
