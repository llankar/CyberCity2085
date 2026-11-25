"""One cyberpunk showcase: exact old footprints, varied PBR facades and authored roof props."""
from pathlib import Path
import sys,json,math,argparse
import bpy
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).parent.parent))
from cell_surfaces import surfaces

LAB=Path('E:/CyberCity2085-3d-lab')
SRC=LAB/'sources/environment169'
parser=argparse.ArgumentParser();parser.add_argument('--authored-facades',action='store_true')
parser.add_argument('--refined-stage',action='store_true')
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
OUT=LAB/'generated/phase2'/('showcase171' if args.refined_stage else 'showcase170' if args.authored_facades else 'showcase169');OUT.mkdir(exist_ok=True)
data=json.loads((LAB/'sources/tactical_map/city_exterior_neon_market_alley.walls.json').read_text())
heights={tuple(cell):3 if 'building' in wall['id'] else .7 for wall in data['walls'] for cell in wall['cells']}
bpy.ops.wm.read_factory_settings(use_empty=True)

def pbr(name,tint=None):
    mat=bpy.data.materials.new(name);mat.use_nodes=True
    nodes=mat.node_tree.nodes;links=mat.node_tree.links;shader=nodes.get('Principled BSDF')
    for key in ['diff','rough','nor_gl']:
        tex=nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(SRC/name/(key+'.jpg')))
        if key=='diff' and tint is not None:
            import numpy as np
            source_image=tex.image;tex.image=source_image.copy()
            pixels=np.empty(len(tex.image.pixels),dtype=np.float32);tex.image.pixels.foreach_get(pixels)
            pixels.reshape(-1,4)[:,:3]*=tint
            tex.image.pixels.foreach_set(pixels);tex.image.update()
            tex.image.filepath_raw=str(OUT/'roof_concrete.png');tex.image.file_format='PNG';tex.image.save()
        if key!='diff':tex.image.colorspace_settings.name='Non-Color'
        if key=='nor_gl':
            normal=nodes.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=.65
            links.new(tex.outputs['Color'],normal.inputs['Color']);links.new(normal.outputs['Normal'],shader.inputs['Normal'])
        else:links.new(tex.outputs['Color'],shader.inputs['Base Color' if key=='diff' else 'Roughness'])
    if 'metal' in name:shader.inputs['Metallic'].default_value=.55
    return mat

walls=[pbr('brick_wall_001'),pbr('concrete_wall_001'),pbr('blue_metal_plate')]
roof_concrete=pbr('concrete_wall_001',.12) if args.refined_stage else None
def flat(name,color,emit=0):
    mat=bpy.data.materials.new(name);mat.use_nodes=True;s=mat.node_tree.nodes.get('Principled BSDF')
    s.inputs['Base Color'].default_value=(*color,1);s.inputs['Roughness'].default_value=.55
    if emit:s.inputs['Emission Color'].default_value=(*color,1);s.inputs['Emission Strength'].default_value=emit
    return mat
trim=flat('Dark anodized frames',(.025,.035,.045))
glass=[flat('Warm apartment window',(.8,.35,.08),.4),flat('Cold office window',(.03,.22,.28),.3)]
neon=[flat('Cyan sign',(.01,.7,.8),2),flat('Magenta sign',(.7,.015,.3),2)]

def world(p):return Vector((p[0]-20,14-p[1],p[2]))
def box(name,point,size,mat,parent,normal=None):
    bpy.ops.mesh.primitive_cube_add(size=1,location=point)
    obj=bpy.context.object;obj.name=name;obj.dimensions=size
    if normal is not None:obj.rotation_euler=normal.to_track_quat('Y','Z').to_euler()
    obj.data.materials.append(mat);obj.parent=parent
    return obj

templates=[]
for filename in ['chimney-medium','detail-tank','solar-panel-flat','water-tower']:
    before=set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(SRC/'kenney_industrial/Models/GLB format'/(filename+'.glb')))
    objs=[o for o in set(bpy.data.objects)-before if o.type=='MESH']
    for obj in objs:
        obj.hide_render=True;obj.hide_viewport=True
    templates.append(objs)

modules=None
if args.authored_facades or args.refined_stage:
    sys.path.insert(0,str(Path(__file__).parent))
    from facade_modules170 import FacadeModules
    modules=FacadeModules(SRC)

seen=set();groups=0;roof_points=[];door_points=[]
for index,obstacle in enumerate(data['walls']):
    cells={tuple(c) for c in obstacle['cells']}-seen;seen.update(cells)
    if not cells:continue
    height=3 if 'building' in obstacle['id'] else .7
    parts=surfaces({cell:height for cell in cells})
    parent=bpy.data.objects.new('Occludable_'+obstacle['id'],None);bpy.context.collection.objects.link(parent)
    vertices=[];polygons=[];kinds=[]
    for kind,cell,points in parts:
        start=len(vertices);vertices.extend(world(p) for p in reversed(points))
        polygons.append(tuple(range(start,start+4)));kinds.append(kind)
    mesh=bpy.data.meshes.new(obstacle['id']);mesh.from_pydata(vertices,[],polygons);mesh.update()
    body=bpy.data.objects.new('PBR_Facade_'+obstacle['id'],mesh);bpy.context.collection.objects.link(body);body.parent=parent
    body.data.materials.append(walls[index%3]);body.data.materials.append(roof_concrete if args.refined_stage and index%3 else walls[2])
    uv=mesh.uv_layers.new(name='MetricFacadeUV')
    for poly,kind in zip(mesh.polygons,kinds):
        poly.material_index=int(kind!='wall')
        for li in poly.loop_indices:
            v=mesh.vertices[mesh.loops[li].vertex_index].co
            axis=0 if abs(poly.normal.y)>.5 else 1
            uv.data[li].uv=(v[axis]/2,v.z/2) if kind=='wall' else (v.x/3,v.y/3)
    bevel=body.modifiers.new('Facade edge bevel','BEVEL');bevel.width=.025;bevel.segments=2
    if height<2:continue
    groups+=1
    count=0
    for kind,cell,points in parts:
        if kind!='wall':continue
        verts=[world(p) for p in points];normal=-(verts[1]-verts[0]).cross(verts[2]-verts[0]).normalized()
        center=sum(verts,Vector())/4
        count+=1
        if count%3==0 and not modules:
            frame=box('Window frame',center+normal*.035,(.74,.07,1.05),trim,parent,normal)
            box('Recessed glazing',center+normal*.08,(.60,.035,.88),glass[(index+count)%2],parent,normal)
            box('Window mullion',center+normal*.11,(.025,.03,.9),trim,parent,normal)
        elif count%11==0:
            center.z=.95
            box('Service doorway',center+normal*.045,(.82,.08,1.9),trim,parent,normal)
            box('Door status strip',center+normal*.10+Vector((0,0,.7)),(.58,.04,.035),neon[index%2],parent,normal)
            door_points.append((center+normal*.13,normal,parent))
    if modules:modules.decorate(parent,parts,index,world)
    # Authored kit components, constrained to existing roof cells.
    cell=sorted(cells)[len(cells)//2];point=world((cell[0]+.5,cell[1]+.5,height))
    roof_points.append((point,parent))
    if modules:modules.roof(point,parent,index)
    for original in ([] if args.refined_stage else templates[index%len(templates)]):
        obj=original.copy();obj.data=original.data;bpy.context.collection.objects.link(obj)
        obj.hide_render=False;obj.hide_viewport=False;obj.parent=parent
        obj.location+=point;obj.scale*=1.3
    if -8<point.x<8:
        bpy.ops.object.text_add(location=point+Vector((0,-.55,.25)))
        sign=bpy.context.object;sign.name='Street sign';sign.parent=parent
        sign.data.body=['NEURO / CLINIC','BLACK MARKET','KIRIN / TECH','NIGHT CITY'][index%4]
        sign.data.size=.24;sign.data.extrude=.006;sign.rotation_euler=(math.pi/2,0,0)
        sign.data.materials.append(neon[index%2])

for objects in templates:
    for obj in objects:bpy.data.objects.remove(obj,do_unlink=True)
# Authored industrial pipe sections and street lights, not primitive stand-ins.
for name,positions in [('modular_industrial_pipes_01',[(-5,1,3),(4,-3,3)]),('street_lamp_01',[(-6,-2.5,0),(-2,-4,0)])]:
    before=set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(SRC/name/(name+'_1k.gltf')))
    meshes=[o for o in set(bpy.data.objects)-before if o.type=='MESH']
    if name.startswith('modular'):
        chosen=next(o for o in meshes if o.name=='modular_industrial_pipes_01_pipe08')
        for obj in meshes:
            if obj!=chosen:bpy.data.objects.remove(obj,do_unlink=True)
        meshes=[chosen]
    for index,point in enumerate(positions):
        if name.startswith('modular'):
            point=(point[0],point[1],heights.get((math.floor(point[0]+20),math.floor(14-point[1])),0))
        for source in meshes:
            obj=source if index==0 else source.copy()
            if index:bpy.context.collection.objects.link(obj)
            obj.parent=None
            height=max(obj.dimensions)
            factor=(1.6 if name.startswith('modular') else 3.2)/height
            obj.scale*=factor;obj.location=point
            bpy.context.view_layer.update()
            corners=[obj.matrix_world@Vector(corner) for corner in obj.bound_box]
            base=Vector(((min(c.x for c in corners)+max(c.x for c in corners))/2,
                         (min(c.y for c in corners)+max(c.y for c in corners))/2,
                         min(c.z for c in corners)))
            obj.location+=Vector(point)-base

def assembly(name,point,parent,size,normal=None):
    before=set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(SRC/name/(name+'_1k.gltf')))
    objects=[obj for obj in set(bpy.data.objects)-before if obj.type=='MESH']
    root=bpy.data.objects.new('Authored_'+name,None);bpy.context.collection.objects.link(root)
    for obj in objects:
        matrix=obj.matrix_world.copy();obj.parent=root;obj.matrix_world=matrix
    if normal is not None:root.rotation_euler=(-normal).to_track_quat('Y','Z').to_euler()
    bpy.context.view_layer.update()
    points=[obj.matrix_world@Vector(corner) for obj in objects for corner in obj.bound_box]
    low=Vector([min(p[i] for p in points) for i in range(3)]);high=Vector([max(p[i] for p in points) for i in range(3)])
    root.scale*=size/max(high-low)
    bpy.context.view_layer.update()
    points=[obj.matrix_world@Vector(corner) for obj in objects for corner in obj.bound_box]
    base=Vector(((min(p.x for p in points)+max(p.x for p in points))/2,(min(p.y for p in points)+max(p.y for p in points))/2,min(p.z for p in points)))
    root.location=Vector(point)-base;root.parent=parent

for index,(point,parent) in enumerate(roof_points[:3]):
    assembly('old_military_compressor',point+Vector((.7,0,0)),parent,1.3)
    if index==0:assembly('modular_electric_cables',point+Vector((0,0,.2)),parent,2.0)
for point,normal,parent in door_points[:3]:
    assembly('rollershutter_door',(point.x,point.y,0),parent,1.8,normal)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'environment.blend'))
bpy.ops.export_scene.gltf(filepath=str(OUT/'environment.glb'),export_format='GLB',use_selection=True)
(OUT/'environment.json').write_text(json.dumps({'source_cells':len(seen),'buildings':groups,
    'authored_facade_modules':modules.placements if modules else 0,
    'scope':'One map: unchanged627cell footprints, cosmetic PBR facades and authored roof props'},indent=2))
print('SHOWCASE_ENVIRONMENT_READY',len(seen),groups,flush=True)
