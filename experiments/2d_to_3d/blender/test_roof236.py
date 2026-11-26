"""Targeted regression check for the oversized-pipe failure, on the saved model."""
from pathlib import Path
import bpy,json
root=Path('E:/CyberCity2085-3d-lab/generated/phase2/showcase236')
bpy.ops.wm.open_mainfile(filepath=str(root/'environment.blend'))
bpy.context.view_layer.update()
pipes=[o for o in bpy.context.scene.objects if o.name.startswith('Original236 acquired pipe run')]
assert len(pipes)==3
cross=[]
for pipe in pipes:
 diameter=max(sorted(pipe.dimensions)[:2]);assert abs(diameter-.22)<.001,(pipe.name,tuple(pipe.dimensions));cross.append(diameter)
fans=[o for o in bpy.context.scene.objects if o.name.startswith('Original236 reused extractor ')]
assert len(fans)==20
(root/'pipe_scale_check.json').write_text(json.dumps({'pipe_count':len(pipes),'diameters_m':cross,'reused_fan_parts':len(fans),'scope':'Saved model dimensions only, not visual acceptance'},indent=2))
print('ROOF236_PIPE_SCALE_PASS',cross)
