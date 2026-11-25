"""Independent rigid industrial facades from the existing exact cell footprint."""
import hashlib
import json
import math
import sys
from pathlib import Path
import bpy
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).parent.parent))
from cell_surfaces import surfaces

root = Path('E:/CyberCity2085-3d-lab')
source = root/'sources/tactical_map/city_exterior_neon_market_alley.walls.json'
out = root/'generated/phase2/tactical_facades01'
out.mkdir(exist_ok=True)
data = json.loads(source.read_text())
heights = {}
for obstacle in data['walls']:
    for cell in obstacle['cells']:
        heights.setdefault(tuple(cell),3. if 'building' in obstacle['id'] else .7)
assert len(heights) == 627
faces = surfaces(heights)
print('FACADE_SOURCE_CELLS',len(heights),'surfaces',len(faces),flush=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene


def material(name,color,metallic,roughness,emission=0):
    value = bpy.data.materials.new(name)
    value.use_nodes = True
    shader = value.node_tree.nodes['Principled BSDF']
    shader.inputs['Base Color'].default_value = (*color,1)
    shader.inputs['Metallic'].default_value = metallic
    shader.inputs['Roughness'].default_value = roughness
    if emission:
        shader.inputs['Emission Color'].default_value = (*color,1)
        shader.inputs['Emission Strength'].default_value = emission
    return value


wall = material('Industrial blue painted metal',(.035,.065,.09),.65,.45)
roof = material('Roof deck graphite',(.055,.07,.08),.5,.7)
trim = material('Brushed structural alloy',(.19,.23,.25),.8,.36)
panel = material('Recessed service panel',(.012,.02,.03),.55,.4)
amber = material('Safety yellow painted trim',(.42,.20,.025),.35,.5)
cyan = material('Cyan edge terminal',(.015,.65,.8),.2,.3,2)
purple = material('Magenta edge terminal',(.5,.015,.25),.2,.3,1.5)
materials = [wall,roof,trim,panel,amber,cyan,purple]
width,depth = data['grid']


def world(point):
    x,y,z = point
    return Vector((x-width/2,-y+depth/2,z))


vertices = []
polygons = []
lookup = {}
for _,_,points in faces:
    polygon = []
    for point in reversed(points):
        if point not in lookup:
            lookup[point] = len(vertices)
            vertices.append(world(point))
        polygon.append(lookup[point])
    polygons.append(polygon)
mesh = bpy.data.meshes.new('Exact stepped627cell volume')
mesh.from_pydata(vertices,[],polygons)
mesh.update()
body = bpy.data.objects.new('ExactMapObstacleBody',mesh)
scene.collection.objects.link(body)
body.data.materials.append(wall)
body.data.materials.append(roof)
for polygon,(kind,_,_) in zip(mesh.polygons,faces):
    polygon.material_index = int(kind != 'wall')
bevel = body.modifiers.new('Manufactured corner bevels','BEVEL')
bevel.width = .018
bevel.segments = 2
bevel.limit_method = 'ANGLE'


buffers = {mat:([],[]) for mat in materials}
def box(center,size,mat,angle=0):
    # Direct mesh batches avoid thousands of context-sensitive Blender operators.
    verts,polys = buffers[mat]
    offset = len(verts)
    cosine,sine = math.cos(angle),math.sin(angle)
    for x,y,z in ((-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)):
        x,y,z = x*size[0]/2,y*size[1]/2,z*size[2]/2
        verts.append(center+Vector((cosine*x-sine*y,sine*x+cosine*y,z)))
    polys.extend(tuple(offset+i for i in face) for face in ((0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)))


panels = 0
vents = 0
for kind,cell,points in faces:
    if kind != 'wall':
        continue
    center = sum((world(p) for p in points),Vector())/4
    bottom,top = min(p[2] for p in points),max(p[2] for p in points)
    if top-bottom < .5:
        continue
    a,b,c = [world(p) for p in points[:3]]
    normal = -(b-a).cross(c-a).normalized()  # reversed winding used for body
    tangent = Vector((-normal.y,normal.x,0))
    angle = math.atan2(tangent.y,tangent.x)
    height = top-bottom-.12
    box(center+normal*.018,(.84,.04,height),panel,angle)
    for side in (-1,1):
        box(center+normal*.045+tangent*(side*.44),(.035,.045,height+.06),trim,angle)
    for side in (-1,1):
        box(center+normal*.045+Vector((0,0,side*(height/2+.025))),(.90,.045,.035),trim,angle)
    color = cyan if (cell[0]+cell[1])%3 else purple
    if top > 1:
        box(center+normal*.05+Vector((0,0,height*.31)),(.68,.025,.035),color,angle)
        for slat in range(4):
            box(center+normal*.05+Vector((0,0,-.13+slat*.08)),(.57,.025,.025),trim,angle)
    else:
        box(center+normal*.05+Vector((0,0,.16)),(.65,.03,.045),amber,angle)
    panels += 1
for (x,y),height in heights.items():
    if height < 2 or x%4 or y%4 or not all(heights.get((x+dx,y+dy))==height for dx,dy in ((1,0),(0,1),(1,1))):
        continue
    center = world((x+1,y+1,height+.22))
    box(center,(1.2,.8,.44),wall)
    for index in range(7):
        box(center+Vector((0,-.30+index*.1,.24)),(1.08,.045,.025),trim)
    vents += 1
# Build seven batched meshes directly, without per-piece dependency-graph updates.
for mat in materials:
    verts,polys = buffers[mat]
    if not verts:
        continue
    mesh = bpy.data.meshes.new(mat.name)
    mesh.from_pydata(verts,[],polys)
    mesh.update()
    obj = bpy.data.objects.new('Facade_'+mat.name,mesh)
    scene.collection.objects.link(obj)
    mesh.materials.append(mat)
    bevel = obj.modifiers.new('Batch machined edges','BEVEL')
    bevel.width=.006
    bevel.segments=2
    print('FACADE_MATERIAL_BATCH',mat.name,'boxes',len(polys)//6,flush=True)
for obj in scene.objects: obj.select_set(True)
notice = 'CyberCity2085 experimental rigid industrial facade geometry. Derived exact cell footprint from existing game map. Original authored procedural geometry/materials; no downloaded PBR material used. Production map and tactical rules untouched.'
bpy.data.texts.new('EXPERIMENT_CREDITS').write(notice)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'facades.blend'))
bpy.ops.export_scene.gltf(filepath=str(out/'facades.glb'),export_format='GLB',use_selection=True,export_animations=False,export_copyright=notice)
(out/'geometry_report.json').write_text(json.dumps({'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'source_cells':len(heights),'cell_heights':[[*cell,h] for cell,h in sorted(heights.items())],'nominal_volume_m3':sum(heights.values()),'service_panels':panels,'roof_vents':vents,'meshes':sum(obj.type=='MESH' for obj in scene.objects),'glb_sha256':hashlib.sha256((out/'facades.glb').read_bytes()).hexdigest(),'limitations':['Decorative frames project up to73mm beyond nominal volume; no gameplay collision changes','Constant PBR material factors, no authored high-frequency texture maps','Existing floor remains 2D reference; environment artistic acceptance open']},indent=2))
print('TACTICAL_FACADE_MODEL_EXPORTED',len(heights),panels,vents,flush=True)
