"""One mechanical finish pass on the retained VTOL; no production replacement."""
from pathlib import Path
import json
import math
import sys
import bpy
import bmesh
import numpy as np
from mathutils import Vector

sys.path.insert(0,str(Path(__file__).parent))
from create_hardsurface_crate import box, make_material

LAB=Path('E:/CyberCity2085-3d-lab')
OUT=LAB/'generated/phase2/vtol178';OUT.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(LAB/'generated/phase2/vtol_finish135/vtol_actions.blend'),use_scripts=False)
scene=bpy.context.scene;scene.frame_set(0)
source_meshes=[obj for obj in scene.objects if obj.type=='MESH']
source_pivots={obj.name:[list(row) for row in obj.matrix_world] for obj in scene.objects if obj.name.startswith(('RotorPivot','GearPivot'))}
hardware=[]
dark=make_material('VTOL178 gunmetal',(.025,.035,.045,1),.65,.38)
glass=make_material('VTOL178 armored blue glazing',(.012,.075,.12,1),.45,.17)
cyan=make_material('VTOL178 coolant glow',(.015,.55,.8,1),.2,.3,2)
red=make_material('VTOL178 port light',(.8,.025,.015,1),.1,.3,3)
green=make_material('VTOL178 starboard light',(.025,.6,.25,1),.1,.3,3)

paint=bpy.data.materials.new('VTOL178 weathered painted alloy');paint.use_nodes=True
shader=paint.node_tree.nodes.get('Principled BSDF');shader.inputs['Metallic'].default_value=.5
textures=LAB/'sources/environment169/blue_metal_plate'
for channel in ['diff','rough','nor_gl']:
    image=bpy.data.images.load(str(textures/(channel+'.jpg')),check_existing=False)
    if channel=='diff':
        pixels=np.empty(len(image.pixels),dtype=np.float32);image.pixels.foreach_get(pixels)
        pixels.reshape(-1,4)[:,:3]*=.55;image.pixels.foreach_set(pixels);image.update()
        image.filepath_raw=str(OUT/'hull_basecolor.png');image.file_format='PNG';image.save()
    else:image.colorspace_settings.name='Non-Color'
    texture=paint.node_tree.nodes.new('ShaderNodeTexImage');texture.image=image
    if channel=='nor_gl':
        normal=paint.node_tree.nodes.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=.35
        paint.node_tree.links.new(texture.outputs['Color'],normal.inputs['Color'])
        paint.node_tree.links.new(normal.outputs['Normal'],shader.inputs['Normal'])
    else:paint.node_tree.links.new(texture.outputs['Color'],shader.inputs['Base Color' if channel=='diff' else 'Roughness'])

def metric_uv(obj):
    uv=obj.data.uv_layers.active or obj.data.uv_layers.new(name='MetricHullUV')
    for face in obj.data.polygons:
        dominant=max(range(3),key=lambda axis:abs(face.normal[axis]))
        axes=[axis for axis in range(3) if axis!=dominant]
        for loop in face.loop_indices:
            point=obj.data.vertices[obj.data.loops[loop].vertex_index].co
            uv.data[loop].uv=(point[axes[0]]/2,point[axes[1]]/2)

hull=bpy.data.objects['ProfiledFuselage']
inward=sum(face.normal.dot(Vector((face.center.x,0,face.center.z-1.05)))<0 for face in hull.data.polygons if len(face.vertices)==4)
bm=bmesh.new();bm.from_mesh(hull.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(hull.data);bm.free()
for obj in source_meshes:
    if obj.name.startswith(('ProfiledFuselage','WingRoot','TailFin','DuctedRotorHousing','LandingShoe')):
        obj.data.materials.clear();obj.data.materials.append(paint)
        metric_uv(obj)
        if obj.name.startswith('TailFin'):
            thick=obj.modifiers.new('Fin skin thickness','SOLIDIFY');thick.thickness=.035
        if obj.name.startswith('DuctedRotorHousing'):
            for face in obj.data.polygons:face.use_smooth=True
    if obj.name.startswith(('CockpitFacet','CabinWindow')):
        obj.data.materials.clear();obj.data.materials.append(glass)
    if obj.name.startswith('WingNavigationLight'):
        obj.data.materials.clear();obj.data.materials.append(red if obj.location.x<0 else green)

def rod(name,a,b,radius,material):
    a,b=Vector(a),Vector(b)
    bpy.ops.mesh.primitive_cylinder_add(vertices=10,radius=radius,depth=(b-a).length,location=(a+b)/2)
    obj=bpy.context.object;obj.name=name;obj.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler()
    obj.data.materials.append(material);hardware.append(obj)
    return obj

old_canopies=[obj for obj in source_meshes if obj.name.startswith('CockpitFacet')]
source_meshes=[obj for obj in source_meshes if obj not in old_canopies]
for obj in old_canopies:bpy.data.objects.remove(obj,do_unlink=True)
canopies=[]
for face in hull.data.polygons:
    if len(face.vertices)!=4 or face.center.y>=-1 or face.normal.z<=.25:continue
    points=[hull.matrix_world@hull.data.vertices[index].co for index in face.vertices]
    center=sum(points,Vector())/4
    points=[center+(point-center)*.84+face.normal*.02 for point in points]
    mesh=bpy.data.meshes.new('Fitted canopy glazing');mesh.from_pydata(points,[],[(0,1,2,3)]);mesh.update()
    obj=bpy.data.objects.new('Fitted cockpit pane',mesh);scene.collection.objects.link(obj)
    obj.data.materials.append(glass)
    solid=obj.modifiers.new('Glazing thickness','SOLIDIFY');solid.thickness=.012
    canopies.append(obj)
for cockpit in canopies:
    points=[cockpit.matrix_world@vertex.co for vertex in cockpit.data.vertices]
    for index,a in enumerate(points):rod('Cockpit pressure frame',a,points[(index+1)%len(points)],.027,dark)

for side in [-1,1]:
    # Static aft turbine hardware is separate from the retained lift-rotor pivots.
    center=Vector((side*.58,3.7,1.23))
    rod('Aft turbine casing',(center.x,3.20,center.z),(center.x,3.73,center.z),.25,paint)
    for radius,y,material in [(.25,3.69,dark),(.21,3.76,paint),(.16,3.80,dark)]:
        bpy.ops.mesh.primitive_torus_add(major_segments=32,minor_segments=8,
            major_radius=radius,minor_radius=.035,location=(center.x,y,center.z),rotation=(math.pi/2,0,0))
        obj=bpy.context.object;obj.name='Aft turbine rim';obj.data.materials.append(material);hardware.append(obj)
    rod('Recessed turbine core',(center.x,3.77,center.z),(center.x,3.79,center.z),.12,cyan)
    panel=box('Engine service recess',(side*.72,1.45,1.60),(.21,.42,.045),dark,.025);hardware.append(panel)
    for index in range(7):
        blade=box('Cooling louvre',(side*.72,1.12+index*.11,1.66),(.19,.024,.018),dark,.008);hardware.append(blade)

# Small fasteners follow real fitted-panel corners, rather than floating blocks.
for panel in [obj for obj in source_meshes if obj.name.startswith('FittedHullPanel')]:
    points=[panel.matrix_world@vertex.co for vertex in panel.data.vertices]
    center=sum(points,Vector())/len(points)
    normal=panel.data.polygons[0].normal
    for point in points:
        at=center+(point-center)*.90
        rod('Panel fastener',at+normal*.008,at+normal*.021,.018,dark)

for obj in hardware:
    if obj.data.materials and obj.data.materials[0]==paint:metric_uv(obj)
for obj in scene.objects:
    if obj.animation_data:
        for track in obj.animation_data.nla_tracks:track.mute=False
    obj.select_set(obj.type in ['MESH','EMPTY'])
bpy.context.view_layer.objects.active=hull
bpy.ops.file.pack_all()
bpy.ops.export_scene.gltf(filepath=str(OUT/'vtol_actions.glb'),export_format='GLB',use_selection=True,export_apply=True,
    export_animations=True,export_animation_mode='NLA_TRACKS',export_force_sampling=True)
for obj in scene.objects:
    if obj.animation_data:
        for track in obj.animation_data.nla_tracks:track.mute=track.name!='Rotor_Spin'
scene.frame_set(0)
assert source_pivots=={obj.name:[list(row) for row in obj.matrix_world] for obj in scene.objects if obj.name in source_pivots}
scene.render.engine='BLENDER_EEVEE_NEXT';scene.render.resolution_x=1280;scene.render.resolution_y=720;scene.render.resolution_percentage=100
if scene.camera is None:
    bpy.ops.object.camera_add();scene.camera=bpy.context.object
scene.camera.location=(10,-12,10);scene.camera.rotation_euler=(Vector((0,0,1))-scene.camera.location).to_track_quat('-Z','Y').to_euler()
scene.camera.data.type='ORTHO';scene.camera.data.ortho_scale=12
scene.render.filepath=str(OUT/'neutral.png');bpy.ops.render.render(write_still=True)
scene.camera.location=(9,10,6);scene.camera.rotation_euler=(Vector((0,0,1))-scene.camera.location).to_track_quat('-Z','Y').to_euler()
scene.render.filepath=str(OUT/'rear.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'vtol_actions.blend'))
(OUT/'finish.json').write_text(json.dumps({'previous_inward_side_faces':inward,'added_hardware':len(hardware),'fitted_canopy_panes':len(canopies),
    'motion_pivots_preserved':True,'scope':'Visible finish trial; native scene/artistic review required'},indent=2))
print('VTOL178_FINISH_EXPORTED',len(hardware),inward,flush=True)
(OUT/'CREDITS.txt').write_text('Original CyberCity2085 procedural VTOL and finish135 paint panels.\nPBR hull surface: existing local Poly Haven blue_metal_plate maps.\nFinish178 adds fitted glazing, frames, turbines and maintenance hardware. Experimental, not production Nighthawk art.\n',encoding='utf8')
