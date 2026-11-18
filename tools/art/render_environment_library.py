"""Blender 4.x: build real reusable props and render transparent steep-view sprites.
Run: blender -b --threads 2 --python tools/art/render_environment_library.py -- OUTPUT
No source map or tactical survey is read or written.
"""
import bpy, math, sys, json
from pathlib import Path
from mathutils import Vector
OUT=Path(sys.argv[sys.argv.index('--')+1]);OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=int(sys.argv[sys.argv.index("--samples")+1]) if "--samples" in sys.argv else 96
scene.cycles.use_denoising=False;scene.render.resolution_x=512;scene.render.resolution_y=512;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA';scene.render.film_transparent=True
scene.view_settings.view_transform='AgX';scene.world.color=(.18,.22,.28)
M={}
def material(name,color,metal=0,rough=.5,emission=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;n=m.node_tree.nodes;p=n.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 if emission:p.inputs['Emission Color'].default_value=(*color,1);p.inputs['Emission Strength'].default_value=emission
 else:
  noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=95 if name!='concrete' else 24
  bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.15;bump.inputs['Distance'].default_value=.025
  m.node_tree.links.new(noise.outputs['Fac'],bump.inputs['Height']);m.node_tree.links.new(bump.outputs['Normal'],p.inputs['Normal'])
 M[name]=m;return m
material('metal',(.075,.105,.125),.72,.34);material('steel',(.27,.32,.35),.85,.27);material('paint',(.10,.19,.22),.55,.42)
material('leather',(.085,.035,.018),0,.54);material('fabric',(.055,.085,.095),0,.85);material('wood',(.17,.075,.025),0,.4)
material('concrete',(.18,.17,.145),0,.88);material('rubber',(.015,.018,.020),0,.86);material('amber',(.85,.22,.025),.3,.4)
material('cyan',(.025,.64,.9),.2,.25,2);material('screen',(.005,.055,.08),.4,.22);material('white',(.42,.49,.49),.35,.5)
parts=[]
def box(name,loc,size,mat='metal',bevel=.04):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(M[mat])
 if bevel:
  b=o.modifiers.new('formed edges','BEVEL');b.width=bevel;b.segments=3
  o.modifiers.new('weighted normals','WEIGHTED_NORMAL')
 parts.append(o);return o

def cylinder(name,loc,radius,depth,mat='steel',rotation=None):
 bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=radius,depth=depth,location=loc);o=bpy.context.object;o.name=name;o.data.materials.append(M[mat]);o.rotation_euler=rotation or (0,0,0)
 b=o.modifiers.new('machined rim','BEVEL');b.width=.025;b.segments=2;o.modifiers.new('normals','WEIGHTED_NORMAL');parts.append(o);return o

def feet(w,d,z=.14):
 for x in [-w/2+.14,w/2-.14]:
  for y in [-d/2+.12,d/2-.12]:box('foot',(x,y,z/2),(.10,.10,z),'steel',.015)

def sofa(chair=False):
 w=1.05 if chair else 2.8;feet(w,1.05)
 box('underframe',(0,0,.25),(w,.95,.22),'wood')
 n=1 if chair else 3
 for i in range(n):
  x=(i-(n-1)/2)*(w-.34)/n
  box('seat cushion',(x,-.08,.49),((w-.38)/n-.025,.72,.24),'leather',.10)
  back=box('back cushion',(x,.37,.80),((w-.30)/n-.025,.26,.66),'leather',.09);back.rotation_euler.x=math.radians(-8)
  # Raised seams follow individual upholstered panels, never a slab under them.
  for dx in [-(w-.38)/n/2+.05,(w-.38)/n/2-.05]:box('piping',(x+dx,-.08,.602),(.009,.58,.009),'wood',.003)
 for x in [-w/2+.10,w/2-.10]:box('rolled arm',(x,-.02,.63),(.23,1.03,.48),'leather',.105)

def table():
 feet(1.65,1.05,.48);box('table edge',(0,0,.51),(1.80,1.14,.08),'steel',.045);box('wood inset',(0,0,.56),(1.69,1.02,.035),'wood',.03)
 box('tablet',(0,-.12,.60),(.30,.21,.025),'screen',.018);box('tablet display',(0,-.12,.615),(.25,.16,.006),'cyan',.008)
 cylinder('cup',(.52,.20,.64),.07,.14,'steel')

def console():
 feet(1.65,.83,.10);box('cabinet',(0,0,.45),(1.65,.80,.72),'paint');box('worktop',(0,-.08,.84),(1.77,.91,.09),'steel')
 for x in [-.43,.43]:
  cylinder('screen stalk',(x,.26,1.03),.045,.30)
  panel=box('monitor',(x,.24,1.25),(.73,.10,.45),'metal',.035);panel.rotation_euler.x=math.radians(-12)
  box('display',(x,.177,1.25),(.65,.012,.36),'screen',.015)
  for row in range(5):box('telemetry',(x-.08,.167,1.14+row*.045),(.40-row*.025,.006,.009),'cyan',.002)
 for x in [-.55,-.18,.18,.55]:box('key group',(x,-.25,.895),(.20,.16,.012),'rubber',.006)
 for x in [-.58,.58]:
  for z in [.25,.31,.37,.43]:box('vent',(x,-.408,z),(.32,.012,.019),'rubber',.004)

def crate():
 box('sealed body',(0,0,.49),(1.20,.85,.92),'paint',.07)
 for z in [.10,.87]:box('band',(0,0,z),(1.26,.91,.10),'steel',.035)
 for x in [-.44,.44]:box('strap',(x,0,.99),(.09,.87,.035),'steel',.015)
 box('lock',(0,-.46,.52),(.20,.06,.18),'steel');box('status',(0,-.496,.55),(.08,.006,.025),'cyan',.002)

def barrier(wall=False):
 h=2.2 if wall else .88;w=2.6
 box('concrete body',(0,0,h/2),(w,.34,h),'concrete',.07)
 for x in [-1.22,1.22]:box('end brace',(x,0,h/2),(.12,.42,h+.04),'steel',.025)
 box('cap',(0,0,h+.02),(w+.04,.39,.08),'metal',.025)
 if not wall:
  for x in [-.9,-.3,.3,.9]:
   stripe=box('warning stripe',(x,-.179,.52),(.15,.012,.47),'amber',.002);stripe.rotation_euler.y=math.radians(25)

def machine():
 feet(1.4,1.15,.14);box('chassis',(0,0,.25),(1.4,1.15,.27),'metal')
 cylinder('pressure vessel',(0,0,.84),.49,1.15,'paint')
 for z in [.36,1.17]:cylinder('reinforcing collar',(0,0,z),.54,.11)
 cylinder('cap',(0,0,1.45),.33,.08)
 for x in [-.55,.55]:
  cylinder('pipe',(x,0,.79),.08,1.14,'steel');box('mount',(x,0,.29),(.23,.23,.10),'metal')
 box('controller',(0,-.52,.89),(.37,.14,.35),'metal');box('screen',(0,-.60,.92),(.27,.008,.19),'cyan',.01)

def server():
 box('rack',(0,0,1.05),(1.0,.85,2.10),'metal')
 for z in [.22+i*.23 for i in range(8)]:
  box('rack blade',(0,-.43,z),(.86,.06,.17),'steel',.015)
  for x in [-.29,-.18,-.07,.04]:box('air vent',(x,-.466,z),(.045,.008,.09),'rubber',.002)
  box('status LED',(.32,-.47,z),(.025,.005,.055),'cyan',.002)

def hvac():
 box('fan cabinet',(0,0,.44),(1.70,1.1,.82),'steel',.05)
 for x in [-.43,.43]:
  cylinder('fan rim',(x,0,.89),.36,.08,'metal')
  cylinder('fan hub',(x,0,.94),.075,.07,'steel')
  for a in range(6):
   angle=a*math.pi/3;o=box('fan blade',(x+.17*math.cos(angle),.17*math.sin(angle),.94),(.28,.08,.022),'rubber',.015);o.rotation_euler.z=angle+.45
 for z in [.17,.28,.39,.50,.61]:box('grille',(0,-.56,z),(1.51,.013,.035),'rubber',.005)

def bench():
 feet(2.0,.65,.46)
 for y in [-.22,0,.22]:box('seat slat',(0,y,.49),(2.05,.18,.09),'wood',.03)
 for z in [.77,.98]:box('back slat',(0,.31,z),(2.05,.08,.16),'wood',.025)
 for x in [-.88,.88]:box('back post',(x,.32,.71),(.07,.08,.73),'steel',.02)

def vehicle():
 box('car lower',(0,0,.45),(1.7,3.5,.48),'metal',.18);box('bonnet',(0,-1.12,.75),(1.62,1.14,.20),'paint',.12)
 box('cabin',(0,.18,.97),(1.48,1.49,.65),'paint',.20)
 box('windshield',(0,-.56,1.02),(1.30,.04,.39),'screen',.06)
 for x in [-.84,.84]:
  for y in [-1.05,1.12]:cylinder('tire',(x,y,.37),.35,.22,'rubber',(0,math.pi/2,0))
 for x in [-.57,.57]:box('headlight',(x,-1.77,.62),(.30,.035,.10),'amber',.025)

def container():
 box('cargo body',(0,0,1.05),(2.4,5.4,2.10),'paint',.07)
 for y in [-2.72,2.72]:box('door frame',(0,y,1.05),(2.49,.12,2.18),'steel',.025)
 for y in [i*.25 for i in range(-10,11)]:
  for x in [-1.21,1.21]:box('corrugation',(x,y,1.05),(.07,.08,1.95),'metal',.015)
 for x in [-.56,.56]:box('door locking bar',(x,-2.81,1.08),(.045,.045,1.85),'steel',.012)

def market_stall():
 feet(2.0,1.3,.15);box('counter',(0,0,.75),(2.0,1.3,1.2),'wood',.035)
 for x in [-1.04,1.04]:
  for y in [-.70,.70]:cylinder('canopy pole',(x,y,1.2),.035,2.4)
 roof=box('fabric canopy',(0,0,2.3),(2.3,1.65,.10),'fabric',.05)
 for x in [-.82,-.28,.28,.82]:box('canopy seam',(x,0,2.36),(.025,1.64,.012),'paint',.005)
 for x in [-.65,0,.65]:box('wares box',(x,-.28,1.42),(.5,.5,.18),'paint')

def barrels():
 for x,y in [(-.36,-.22),(.36,-.22),(0,.42)]:
  cylinder('rusted drum',(x,y,.54),.33,1.08,'wood')
  for z in [.14,.88]:cylinder('steel hoop',(x,y,z),.35,.055,'metal')
  cylinder('lid',(x,y,1.09),.31,.035,'steel');cylinder('filler',(x+.11,y,1.12),.05,.035,'metal')

def rust_wreck():
 vehicle()
 if 'rust' not in M:
  m=material('rust',(.12,.045,.014),.2,.94)
  nodes=m.node_tree.nodes;noise=nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=7
  ramp=nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(.035,.014,.006,1);ramp.color_ramp.elements[1].color=(.32,.11,.025,1)
  m.node_tree.links.new(noise.outputs['Fac'],ramp.inputs['Fac']);m.node_tree.links.new(ramp.outputs['Color'],nodes.get('Principled BSDF').inputs['Base Color'])
 for obj in list(parts):
  if obj.name.startswith('tire') and obj.location.x<0 and obj.location.y<0:
   parts.remove(obj);bpy.data.objects.remove(obj,do_unlink=True);continue
  for slot in obj.material_slots:
   if slot.material in [M['metal'],M['paint'],M['steel']]:slot.material=M['rust']
   elif slot.material==M['amber']:slot.material=M['rubber']
  if obj.name.startswith('cabin'):obj.rotation_euler.y=.07;obj.scale.z=.78
 for x in [-.34,.10,.42]:
  crack=box('broken glazing',(x,-.592,1.0),(.025,.012,.28),'rubber',.002);crack.rotation_euler.y=.5+x

def bed():
 feet(1.5,2.4,.18)
 box('bed frame',(0,0,.30),(1.5,2.4,.28),'metal',.08)
 box('mattress',(0,-.03,.54),(1.43,2.27,.30),'fabric',.14)
 box('headboard',(0,1.15,.83),(1.55,.15,1.12),'wood',.055)
 for x in [-.36,.36]:box('pillow',(x,.73,.77),(.62,.51,.19),'white',.13)
 box('folded quilt',(0,-.37,.75),(1.40,1.13,.13),'fabric',.07)
 for x in [-.64,.64]:box('quilt piping',(x,-.37,.82),(.012,1.04,.012),'paint',.004)

def desk():
 feet(2.0,.95,.72)
 box('desk top',(0,0,.77),(2.10,1.05,.09),'wood',.045)
 box('drawer pedestal',(.72,0,.38),(.55,.85,.72),'paint',.04)
 for z in [.20,.42,.64]:
  box('drawer face',(.72,-.44,z),(.48,.035,.19),'metal',.015)
  box('drawer pull',(.72,-.47,z),(.20,.04,.025),'steel',.008)
 box('monitor stand',(-.25,.21,.92),(.06,.08,.26),'steel')
 box('monitor',(-.25,.21,1.18),(.85,.11,.49),'metal')
 box('screen',(-.25,.145,1.18),(.75,.012,.39),'screen',.015)
 for z in [1.08,1.15,1.22]:box('screen text',(-.28,.135,z),(.42,.004,.013),'cyan',.002)
 box('keyboard',(-.23,-.23,.83),(.58,.25,.035),'rubber',.018)

def locker():
 feet(1.2,.65,.12)
 box('locker cabinet',(0,0,1.03),(1.20,.67,1.92),'paint',.035)
 for x in [-.30,.30]:
  box('door',(x,-.35,1.05),(.56,.035,1.81),'metal',.025)
  box('handle',(x+.17,-.40,1.02),(.035,.07,.22),'steel',.01)
  for z in [1.55,1.61,1.67]:box('vent slot',(x,-.374,z),(.32,.008,.022),'rubber',.002)

def planter():
 if 'foliage' not in M:material('foliage',(.055,.14,.065),0,.83)
 box('planter basin',(0,0,.34),(2.20,.85,.68),'concrete',.09)
 box('soil',(0,0,.69),(2.03,.70,.035),'wood',.04)
 for i in range(13):
  x=-.9+(i%7)*.30;y=-.20+(i//7)*.35
  cylinder('stem',(x,y,.88),.022,.43,'wood')
  for j in range(3):
   leaf=box('leaf',(x+.10*math.sin(i+j),y+.11*math.cos(i+j),.93+j*.09),(.27,.13,.035),'foliage',.055)
   leaf.rotation_euler=(.4*math.sin(i),.35*math.cos(j),i+j*1.8)

def transformer():
 feet(1.65,1.1,.15)
 box('transformer casing',(0,0,.75),(1.65,1.1,1.2),'paint',.065)
 for x in [-.90,.90]:
  for y in [-.43,-.21,0,.21,.43]:box('cooling fin',(x,y,.74),(.15,.065,1.05),'steel',.02)
 for x in [-.50,0,.50]:
  cylinder('insulator',(x,0,1.53),.095,.39,'rubber')
  for z in [1.42,1.51,1.60]:cylinder('insulator ring',(x,0,z),.14,.035,'white')
 box('diagnostic panel',(0,-.57,.89),(.51,.045,.36),'metal')
 box('status screen',(0,-.60,.94),(.33,.009,.16),'cyan',.01)

def bin():
 for x in [-.43,.43]:cylinder('wheel',(x,.23,.13),.13,.10,'rubber',(0,math.pi/2,0))
 box('refuse bin',(0,0,.56),(1.05,.83,.93),'paint',.08)
 box('hinged lid',(0,0,1.06),(1.12,.89,.10),'metal',.05)
 box('lift handle',(0,-.47,.95),(.39,.06,.07),'steel',.025)
 for x in [-.34,0,.34]:box('reinforcing rib',(x,-.43,.54),(.045,.045,.63),'metal',.02)

def workbench():
 feet(2.35,.95,.84)
 box('steel worktop',(0,0,.89),(2.46,1.05,.11),'steel',.035)
 box('lower shelf',(0,0,.23),(2.28,.82,.055),'metal',.025)
 box('vice',(-.80,-.38,1.03),(.35,.30,.21),'paint',.04)
 cylinder('vice screw',(-.80,-.61,1.01),.025,.30,'steel',(math.pi/2,0,0))
 for x in [-.25,.20,.65]:box('tool',(x,.16,.96),(.08,.46,.035),'metal',.012)
 box('parts tray',(.76,-.16,.97),(.42,.39,.075),'paint',.025)

def vending():
 feet(1.05,.82,.12)
 box('vending cabinet',(0,0,1.05),(1.05,.82,1.98),'paint',.065)
 box('glass front',(-.10,-.43,1.26),(.66,.018,1.28),'screen',.035)
 for x in [-.31,-.08,.15]:
  for z in [.88,1.16,1.44,1.72]:cylinder('product',(x,-.40,z),.068,.18,'amber')
 box('payment screen',(.38,-.44,1.30),(.15,.018,.22),'cyan',.018)
 box('delivery slot',(-.08,-.44,.40),(.69,.018,.21),'rubber',.025)

def planter_square():
 planter()
 for obj in parts:obj.location.x*=.52;obj.scale.x*=.52

def medical_bed():
 feet(1.0,2.3,.32)
 box('medical chassis',(0,0,.46),(1.02,2.3,.22),'steel',.065)
 box('blue mattress',(0,0,.65),(.92,2.12,.21),'paint',.11)
 box('pillow',(0,.74,.82),(.78,.44,.14),'white',.11)
 box('folded sheet',(0,-.35,.80),(.88,1.05,.10),'fabric',.07)
 for x in [-.54,.54]:
  box('safety rail',(x,0,.93),(.045,1.85,.055),'steel',.022)
  for y in [-.83,.83]:box('rail post',(x,y,.73),(.045,.045,.40),'steel',.015)
 for x in [-.41,.41]:
  for y in [-.98,.98]:cylinder('castor',(x,y,.15),.12,.09,'rubber',(0,math.pi/2,0))
 box('medical monitor',(.70,.75,1.06),(.31,.15,.40),'metal',.025)
 box('vital display',(.70,.66,1.06),(.25,.012,.29),'cyan',.012)

BUILD={'sofa':sofa,'armchair':lambda:sofa(True),'table':table,'console':console,'crate':crate,'barrier':barrier,'wall':lambda:barrier(True),'reactor':machine,'server':server,'hvac':hvac,'bench':bench,'wreck':vehicle,'container':container,'market_stall':market_stall,'barrels':barrels,'rust_wreck':rust_wreck,'bed':bed,'desk':desk,'locker':locker,'planter':planter,'transformer':transformer,'bin':bin,'workbench':workbench,'vending':vending,'planter_square':planter_square,'medical_bed':medical_bed}
sys.path.insert(0,str(Path(__file__).resolve().parent))
from environment_assemblies import families,CAMERA_ELEVATION,ASSEMBLY_METADATA
BUILD.update(families(box,cylinder,parts,M,material))
bpy.ops.object.camera_add(location=(0,-4,10));camera=bpy.context.object;scene.camera=camera;camera.data.type='ORTHO'
for loc,power,size,color in [((-3,-4,7),1100,5,(.65,.82,1)),((4,2,6),1300,4,(1,.64,.32)),((0,4,5),700,3,(.12,.62,1))]:
 bpy.ops.object.light_add(type='AREA',location=loc);light=bpy.context.object;light.data.energy=power;light.data.shape='DISK';light.data.size=size;light.data.color=color;light.rotation_euler=(Vector((0,0,.5))-light.location).to_track_quat('-Z','Y').to_euler()
manifest={'schema_version':1,'generator':'Blender 4.3 Cycles, 96 samples, transparent RGBA','view':'steep_top_down','assets':{}}
selected=sys.argv[sys.argv.index("--only")+1].split(",") if "--only" in sys.argv else list(BUILD)
assert set(selected)<=set(BUILD),'Unknown prop family'
for key,build in BUILD.items():
 if key not in selected:continue
 for o in list(parts):bpy.data.objects.remove(o,do_unlink=True)
 parts.clear();build()
 # Keep an editable source model alongside the generated sprites.
 parent=bpy.data.objects.new('PropPivot',None);scene.collection.objects.link(parent)
 for o in parts:o.parent=parent
 for yaw in [0,90,180,270]:
  parent.rotation_euler.z=math.radians(yaw)
  bpy.context.view_layer.update()
  corners=[o.matrix_world@Vector(v) for o in parts for v in o.bound_box]
  center=sum(corners,Vector())/len(corners);center.z=.65
  elevation=math.radians(CAMERA_ELEVATION.get(key,68.2))
  camera.location=center+Vector((0,-10*math.cos(elevation),10*math.sin(elevation)));camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.ortho_scale=max(3.5,max((v-center).length for v in corners)*2.3)
  scene.render.filepath=str(OUT/f'{key}-{yaw}.png');bpy.ops.render.render(write_still=True)
 manifest['assets'][key]={'yaw':[0,90,180,270],'materials':sorted({slot.material.name for o in parts for slot in o.material_slots if slot.material}),'status':'rendered_pending_in_game_art_review'}
 if key in ASSEMBLY_METADATA:manifest['assets'][key]['assembly']=ASSEMBLY_METADATA[key]
 parent.rotation_euler.z=0;bpy.ops.wm.save_as_mainfile(filepath=str(OUT/f'{key}.blend'),compress=True)
 bpy.data.objects.remove(parent,do_unlink=True)
if (OUT/'library.json').is_file():
 old=json.loads((OUT/'library.json').read_text());old['assets'].update(manifest['assets']);manifest=old
(OUT/'library.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('ENVIRONMENT_LIBRARY_RENDERED',len(BUILD),flush=True)
