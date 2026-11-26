"""Reuse rigid library GLBs with measured bounds and shared mesh data."""
from pathlib import Path
import bpy
from mathutils import Vector,Matrix
_cache={}

def place(source,parent,center,dimensions):
    source=Path(source).resolve()
    if source.drive.upper()!='E:':raise ValueError('Experimental library asset must remain on E:')
    if source not in _cache:
        before=set(bpy.data.objects)
        bpy.ops.import_scene.gltf(filepath=str(source))
        objects=set(bpy.data.objects)-before
        meshes=[o for o in objects if o.type=='MESH']
        points=[o.matrix_world@Vector(c) for o in meshes for c in o.bound_box]
        lo=Vector([min(p[i] for p in points) for i in range(3)]);hi=Vector([max(p[i] for p in points) for i in range(3)])
        _cache[source]=([(o.data,o.matrix_world.copy(),o.name) for o in meshes],lo,hi)
        for o in objects:bpy.data.objects.remove(o,do_unlink=True)
    templates,lo,hi=_cache[source]
    # Preserve rigid asset proportions. Dimensions are a fitting envelope, not
    # permission to stretch a compressor or crate into an unrelated silhouette.
    factor=min(dimensions[i]/(hi[i]-lo[i]) for i in range(3))
    scale=Vector((factor,factor,factor))
    origin=Vector(((lo.x+hi.x)/2,(lo.y+hi.y)/2,lo.z))
    transform=Matrix.Translation(Vector(center))@Matrix.Diagonal(Vector((*scale,1)))@Matrix.Translation(-origin)
    result=[]
    for data,world,name in templates:
        o=bpy.data.objects.new(parent.name+' '+name,data);bpy.context.collection.objects.link(o)
        o.parent=parent;o.matrix_world=transform@world;result.append(o)
    return result
