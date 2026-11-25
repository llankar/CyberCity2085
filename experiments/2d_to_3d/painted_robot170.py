"""Explicit painted-armour material for an otherwise default all-metal GLB.

Colour is Hunyuan-generated. Metal/roughness are manual settings, not AI maps.
"""
from pathlib import Path
import hashlib,json
from glb_document import Glb

folder=Path('E:/CyberCity2085-3d-lab/generated/phase2/paint168/robot_official')
source=folder/'mesh.glb';target=folder/'painted_material.glb'
model=Glb(source)
for material in model.doc['materials']:
    pbr=material.setdefault('pbrMetallicRoughness',{})
    pbr['metallicFactor']=.15
    pbr['roughnessFactor']=.58
model.save(target)
(folder/'painted_material.json').write_text(json.dumps({
    'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
    'glb_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
    'metallic':.15,'roughness':.58,
    'scope':'Manual painted-armour material; original colour/geometry retained, not generated PBR maps'},indent=2))
print('PAINTED_ARMOUR_MATERIAL_WRITTEN')
