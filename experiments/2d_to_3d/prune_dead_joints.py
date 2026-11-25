"""Prune unused joint branches from a game GLB, retaining all weighted ancestors."""
import copy
import numpy as np


def append_accessor(glb,template,payload,count=None):
    accessor=copy.deepcopy(template);accessor.pop('byteOffset',None)
    if count is not None:accessor['count']=count
    glb.bin.extend(b'\0'*(-len(glb.bin)%4))
    accessor['bufferView']=len(glb.doc['bufferViews'])
    glb.doc['bufferViews'].append({'buffer':0,'byteOffset':len(glb.bin),'byteLength':len(payload)})
    glb.bin.extend(payload);glb.doc['accessors'].append(accessor)
    return len(glb.doc['accessors'])-1


def prune(glb):
    d=glb.doc
    if len(d.get('skins',[]))!=1:raise ValueError('One reviewed skin required')
    skin=d['skins'][0];joints=skin['joints'];joint_nodes=set(joints)
    parent={}
    for i,node in enumerate(d['nodes']):
        if node.get('skin',0)!=0:raise ValueError('Unknown skin')
        for child in node.get('children',[]):
            if child in parent:raise ValueError('Multiple node parents')
            parent[child]=i
    weighted=set();attributes=[]
    for mesh in d['meshes']:
        for primitive in mesh['primitives']:
            a=primitive['attributes']
            for suffix in ('0','1'):
                if 'JOINTS_'+suffix not in a:continue
                ji,wi=a['JOINTS_'+suffix],a['WEIGHTS_'+suffix]
                ja,wa=d['accessors'][ji],d['accessors'][wi]
                if ja['componentType'] not in (5121,5123) or wa['componentType']!=5126:
                    raise ValueError('Review integer weights/indices explicitly')
                dtype='u1' if ja['componentType']==5121 else '<u2'
                js=np.frombuffer(glb.values(ji),dtype=dtype);ws=np.frombuffer(glb.values(wi),dtype='<f4')
                if len(js)!=len(ws) or not np.isfinite(ws).all() or (ws<0).any() or (js>=len(joints)).any():
                    raise ValueError('Invalid skin influences')
                weighted.update(int(i) for i in js[ws>0]);attributes.append((a,'JOINTS_'+suffix,ji,wi,js,ws))
    if not weighted:raise ValueError('No weighted geometry')
    # Keep all ordinary scene nodes and every ancestor of every weighted joint.
    keep=(set(range(len(d['nodes'])))-joint_nodes)|{joints[i] for i in weighted}
    if 'skeleton' in skin:keep.add(skin['skeleton'])
    for node in list(keep):
        seen={node}
        while node in parent:
            node=parent[node]
            if node in seen:raise ValueError('Cyclic hierarchy')
            seen.add(node);keep.add(node)
    old_indices=[i for i,node in enumerate(joints) if node in keep]
    remap_joint={old:new for new,old in enumerate(old_indices)}
    converted={}
    for a,key,index,weight_index,js,ws in attributes:
        cache_key=(index,weight_index)
        if cache_key not in converted:
            mapped=np.array([remap_joint[int(j)] if w>0 else 0 for j,w in zip(js,ws)],dtype=js.dtype)
            converted[cache_key]=append_accessor(glb,d['accessors'][index],mapped.tobytes())
        a[key]=converted[cache_key]
    ibm=skin['inverseBindMatrices'];accessor=d['accessors'][ibm]
    if accessor['type']!='MAT4' or accessor['componentType']!=5126 or accessor['count']!=len(joints):
        raise ValueError('Explicit inverse bind matrices required')
    raw=glb.values(ibm)
    skin['inverseBindMatrices']=append_accessor(glb,accessor,b''.join(raw[i*64:(i+1)*64] for i in old_indices),len(old_indices))
    node_map={old:new for new,old in enumerate(sorted(keep))}
    nodes=[]
    for old in sorted(keep):
        node=copy.deepcopy(d['nodes'][old])
        if 'children' in node:node['children']=[node_map[i] for i in node['children'] if i in keep]
        nodes.append(node)
    skin['joints']=[node_map[joints[i]] for i in old_indices]
    if 'skeleton' in skin:skin['skeleton']=node_map[skin['skeleton']]
    for scene in d.get('scenes',[]):scene['nodes']=[node_map[i] for i in scene['nodes'] if i in keep]
    removed_channels=0
    for animation in d.get('animations',[]):
        channels=[]
        for channel in animation['channels']:
            if 'node' not in channel['target']:raise ValueError('Non-node animation target requires separate review')
            node=channel['target']['node']
            if node not in keep:removed_channels+=1;continue
            channel=copy.deepcopy(channel);channel['target']['node']=node_map[node];channels.append(channel)
        used=sorted({c['sampler'] for c in channels});mapping={old:new for new,old in enumerate(used)}
        for channel in channels:channel['sampler']=mapping[channel['sampler']]
        animation['samplers']=[animation['samplers'][i] for i in used];animation['channels']=channels
    before=len(d['nodes']);d['nodes']=nodes
    return {'source_nodes':before,'output_nodes':len(nodes),'source_skin_joints':len(joints),
            'output_skin_joints':len(old_indices),'weighted_joints':len(weighted),
            'removed_animation_channels':removed_channels,
            'scope':'Pruned unused joint branches; weighted ancestry and retained animation payloads preserved'}


if __name__=='__main__':
    import hashlib,json
    from pathlib import Path
    from glb_document import Glb
    root=Path('E:/CyberCity2085-3d-lab')
    source=root/'sources/blenderkit_cyberpunk143';out=root/'generated/phase2/amjviz_pruned145';out.mkdir(exist_ok=True)
    path=source/'source_godot.glb';glb=Glb(path)
    originals=[glb.expanded_values(i) for i in range(len(glb.doc['accessors']))]
    samples={}
    for animation in glb.doc['animations']:
        times=sorted({float(t) for sampler in animation['samplers']
                      for t in np.frombuffer(glb.values(sampler['input']),dtype='<f4')})
        samples[animation['name']]=sorted(set(times)|{(a+b)/2 for a,b in zip(times,times[1:])})
    report=prune(glb)
    assert all(glb.expanded_values(i)==payload for i,payload in enumerate(originals))
    glb.save(out/'human.glb')
    report.update(source_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                  output_sha256=hashlib.sha256((out/'human.glb').read_bytes()).hexdigest(),
                  output_bytes=(out/'human.glb').stat().st_size)
    (out/'pruning_report.json').write_text(json.dumps(report,indent=2))
    (out/'samples.json').write_text(json.dumps(samples,indent=2))
    (out/'CREDITS.txt').write_text((source/'CREDITS.txt').read_text(encoding='utf8')+'\n145 derived game GLB: unused joint branches removed without re-exporting anatomy or source animation poses. Fidelity verification pending.\n',encoding='utf8')
    print('AMJVIZ_PRUNED_GAME_SOURCE',json.dumps(report))
