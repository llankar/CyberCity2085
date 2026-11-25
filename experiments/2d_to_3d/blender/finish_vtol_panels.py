"""Add fitted rigid hull plates and original PBR paint without altering motion."""
import hashlib
import json
import shutil
from pathlib import Path
import sys
import bpy
from mathutils import Vector

root=Path('E:/CyberCity2085-3d-lab/generated/phase2')
source=root/'vtol_motion01/vtol_actions.blend'
source_hash=hashlib.sha256(source.read_bytes()).hexdigest()
out=root/'vtol_finish135'; out.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(source),use_scripts=False)
scene=bpy.context.scene
original=[o for o in scene.objects if o.type=='MESH']

def signature(obj):
    return hashlib.sha256(repr(([(tuple(v.co)) for v in obj.data.vertices],
        [tuple(p.vertices) for p in obj.data.polygons],obj.parent.name if obj.parent else None,
        [tuple(row) for row in obj.matrix_basis])).encode()).hexdigest()

before={o.name:signature(o) for o in original}
paint=bpy.data.materials.new('OriginalPaintedSteel135'); paint.use_nodes=True
nodes=paint.node_tree.nodes; links=paint.node_tree.links; bsdf=nodes.get('Principled BSDF')
for channel,socket in [('basecolor','Base Color'),('roughness','Roughness'),('metallic','Metallic')]:
    image=bpy.data.images.load(str(out/(channel+'.png')),check_existing=False)
    if channel!='basecolor': image.colorspace_settings.name='Non-Color'
    image.pack()
    node=nodes.new('ShaderNodeTexImage');node.image=image
    links.new(node.outputs['Color'],bsdf.inputs[socket])
parts=[]
hull=bpy.data.objects['ProfiledFuselage']
for face in hull.data.polygons:
    if len(face.vertices)!=4: continue
    points=[hull.matrix_world @ hull.data.vertices[i].co for i in face.vertices]
    center=sum(points,Vector())/4
    # Upper/side hull only; lower fuselage retains neutral service material.
    if center.z<1.05 or center.y < -1.0: continue
    normal=(points[1]-points[0]).cross(points[2]-points[0]).normalized()
    outward=Vector((center.x,0,center.z-1.05))
    if normal.dot(outward)<0: normal=-normal; points.reverse()
    # Inset follows the actual tapered hull quad, not a rectangular floating box.
    points=[center+(p-center)*.91+normal*.018 for p in points]
    mesh=bpy.data.meshes.new('FittedHullPanel');mesh.from_pydata(points,[],[(0,1,2,3)]);mesh.update()
    obj=bpy.data.objects.new('FittedHullPanel_%02d'%face.index,mesh);scene.collection.objects.link(obj)
    obj.data.materials.append(paint)
    uv=mesh.uv_layers.new(name='PanelUV')
    for loop,coord in zip(uv.data,[(0,0),(1,0),(1,1),(0,1)]):loop.uv=coord
    solid=obj.modifiers.new('PlateThickness','SOLIDIFY');solid.thickness=.008
    bevel=obj.modifiers.new('ManufacturedPlateEdge','BEVEL');bevel.width=.006;bevel.segments=2
    obj.modifiers.new('PlateNormals','WEIGHTED_NORMAL');parts.append(obj)
assert len(parts)==8, 'Only aft cabin plates: preserve cockpit glazing'
assert before=={o.name:signature(o) for o in original},'Original geometry/parent/transforms modified'
# Original Titanium is now bare alloy underneath fitted painted plates.
for obj in scene.objects:obj.select_set(obj.type=='MESH' or obj.type=='EMPTY')
bpy.context.view_layer.objects.active=hull
for obj in scene.objects:
    if obj.animation_data:
        for track in obj.animation_data.nla_tracks:track.mute=False
notice='Original CyberCity2085 experimental procedural VTOL and PBR maps. No third-party texture inputs. Existing mechanical action source preserved. Not production Nighthawk art.'
bpy.data.texts.new('FINISH135_CREDITS').write(notice)
bpy.ops.export_scene.gltf(filepath=str(out/'vtol_actions.glb'),export_format='GLB',use_selection=True,
    export_apply=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_force_sampling=True,
    export_optimize_animation_size=False,export_optimize_animation_keep_anim_object=True,export_copyright=notice)
for obj in scene.objects:
    if obj.animation_data:
        for track in obj.animation_data.nla_tracks:track.mute=track.name!='Rotor_Spin'
scene.frame_set(0)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'vtol_actions.blend'))
(out/'CREDITS.txt').write_text(notice,encoding='utf-8')
shutil.copyfile(source.parent/'source_surface_reference.json',out/'source_surface_reference.json')
assert hashlib.sha256(source.read_bytes()).hexdigest()==source_hash
(out/'finish_report.json').write_text(json.dumps({'source_sha256':source_hash,
    'protected_original_meshes':len(original),'original_geometry_parent_transforms_exact':True,
    'added_fitted_panels':len(parts),'paint_maps':[str(out/(n+'.png')) for n in ('basecolor','roughness','metallic')],
    'limitations':['No new landing-clearance proof','Not accepted final vehicle art','No new performance benchmark']},indent=2))
print('VTOL_FITTED_PBR_PANELS_EXPORTED',len(parts),flush=True)
