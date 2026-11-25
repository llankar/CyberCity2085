"""Restore only independently source-proven opaque robot material contracts."""
import copy


def restore(doc, report):
    names=set()
    for row in report['objects']:
        if row['all_adapter_alpha_constant_one'] or row['documented_opaque_visor_approximation']:
            names.update(row['baked_materials'])
    available={m['name'] for m in doc['materials']}
    if not names or names-available:raise ValueError('Source/target material mapping mismatch')
    result=copy.deepcopy(doc)
    changed=[]
    for material in result['materials']:
        if material['name'] in names:
            if material.get('alphaMode')!='BLEND':raise ValueError('Unexpected source alpha mode')
            material['alphaMode']='OPAQUE'
            changed.append(material['name'])
    return result,changed
