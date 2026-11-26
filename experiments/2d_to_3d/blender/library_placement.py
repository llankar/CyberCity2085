"""Reuse rigid library GLBs with measured bounds and shared mesh data."""
from pathlib import Path
import bpy
from mathutils import Vector,Matrix
_cache={}

def reset_library_cache():
    """Discard Blender data references after opening a different source scene."""
    _cache.clear()

def place(source,parent,center,dimensions,*,preserve_anchor=False,yaw=0.0,merge=False):
    source=Path(source).resolve()
    if source.drive.upper()!='E:':raise ValueError('Experimental library asset must remain on E:')
    key = (source, merge)
    if key not in _cache:
        before=set(bpy.data.objects)
        bpy.ops.import_scene.gltf(filepath=str(source))
        objects=set(bpy.data.objects)-before
        meshes=[o for o in objects if o.type=='MESH']
        points=[o.matrix_world@Vector(c) for o in meshes for c in o.bound_box]
        lo=Vector([min(p[i] for p in points) for i in range(3)]);hi=Vector([max(p[i] for p in points) for i in range(3)])
        if merge and len(meshes) > 1:
            # Collapse rigid parts once in the template, keeping material
            # slots and one independent occlusion group per placed object.
            bpy.ops.object.select_all(action="DESELECT")
            combined = bpy.data.objects.new(source.stem, bpy.data.meshes.new(source.stem))
            bpy.context.collection.objects.link(combined)
            for obj in meshes:
                obj.select_set(True)
            combined.select_set(True)
            bpy.context.view_layer.objects.active = combined
            bpy.ops.object.join()
            bpy.context.view_layer.update()
            objects = set(bpy.data.objects)-before
            meshes = [combined]
        _cache[key]=([(o.data,o.matrix_world.copy(),o.name) for o in meshes],lo,hi)
        for o in objects:bpy.data.objects.remove(o,do_unlink=True)
    templates,lo,hi=_cache[key]
    # Preserve rigid asset proportions. Dimensions are a fitting envelope, not
    # permission to stretch a compressor or crate into an unrelated silhouette.
    factor=min(dimensions[i]/(hi[i]-lo[i]) for i in range(3))
    scale=Vector((factor,factor,factor))
    origin=Vector((0,0,0)) if preserve_anchor else Vector(((lo.x+hi.x)/2,(lo.y+hi.y)/2,lo.z))
    transform=Matrix.Translation(Vector(center))@Matrix.Rotation(yaw,4,'Z')@Matrix.Diagonal(Vector((*scale,1)))@Matrix.Translation(-origin)
    result=[]
    for data,world,name in templates:
        o=bpy.data.objects.new(parent.name+' '+name,data);bpy.context.collection.objects.link(o)
        o.parent=parent;o.matrix_world=transform@world;result.append(o)
    return result
