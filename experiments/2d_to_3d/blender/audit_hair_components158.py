import bpy,json
from pathlib import Path
bpy.ops.wm.open_mainfile(filepath='E:/CyberCity2085-3d-lab/generated/phase2/hair_cards157/human.blend',use_scripts=False)
report=[]
for o in bpy.context.scene.objects:
 if not o.name.startswith('AuthoredHairCards157_'):continue
 parent=list(range(len(o.data.vertices)))
 def find(x):
  while parent[x]!=x:parent[x]=parent[parent[x]];x=parent[x]
  return x
 for e in o.data.edges:
  a,b=map(find,e.vertices);parent[a]=b
 groups={}
 for i in range(len(parent)):groups.setdefault(find(i),[]).append(i)
 report.append({'name':o.name,'components':len(groups),'sizes':sorted([len(x) for x in groups.values()]),'ranges':[{'vertices':len(vs),'min':[min(o.data.vertices[i].co[k] for i in vs) for k in range(3)],'max':[max(o.data.vertices[i].co[k] for i in vs) for k in range(3)]} for vs in groups.values()]})
Path('E:/CyberCity2085-3d-lab/generated/phase2/hair_sweep158/components.json').write_text(json.dumps(report,indent=2));print([(x['name'],x['components'],x['sizes'][:20]) for x in report])
