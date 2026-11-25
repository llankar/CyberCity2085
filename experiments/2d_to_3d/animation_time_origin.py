"""Normalize each GLB clip's timeline without altering pose samples or shared inputs."""
import math,struct


def normalize_origins(glb):
    report={}
    for animation in glb.doc.get('animations',[]):
        original={s['input'] for s in animation['samplers']};times={}
        for index in original:
            accessor=glb.doc['accessors'][index]
            if accessor['componentType']!=5126 or accessor['type']!='SCALAR':
                raise ValueError('Float scalar animation time required')
            values=struct.unpack('<'+'f'*accessor['count'],glb.values(index))
            if not values or not all(math.isfinite(t) for t in values) or any(a>=b for a,b in zip(values,values[1:])):
                raise ValueError('Finite increasing sample times required')
            times[index]=values
        start=min(v[0] for v in times.values());end=max(v[-1] for v in times.values())
        copies={}
        for index,values in times.items():
            shifted=[t-start for t in values]
            copies[index]=glb.add_floats(shifted,len(shifted))
            glb.doc['accessors'][copies[index]].update(min=[min(shifted)],max=[max(shifted)])
        for sampler in animation['samplers']:sampler['input']=copies[sampler['input']]
        report[animation.get('name','') ]={'original_start_s':start,'original_end_s':end,'duration_s':end-start}
    return report
