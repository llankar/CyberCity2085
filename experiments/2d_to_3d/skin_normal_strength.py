"""Explicit skin normal intensity study; original image and geometry are retained."""
import copy
import math


def set_skin_strength(document,strength):
    if not math.isfinite(strength) or not 0<strength<=1:
        raise ValueError('Positive normal intensity at most one required')
    result=copy.deepcopy(document)
    materials=[m for m in result['materials'] if m.get('name')=='sm004_head']
    if len(materials)!=1 or 'normalTexture' not in materials[0]:
        raise ValueError('Exactly one original textured skin material required')
    materials[0]['normalTexture']['scale']=strength
    return result
