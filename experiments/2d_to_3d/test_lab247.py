"""Check the actual exported curved pod geometry, not artistic acceptance."""
import json,struct,unittest
from pathlib import Path

class PodExport(unittest.TestCase):
 def test_pod_bank_has_three_round_chambers_and_materials(self):
  p=Path('E:/CyberCity2085-3d-lab/generated/phase2/lab247/pod_bank.glb')
  self.assertTrue(p.is_file(),'Build laboratory247 before this explicit asset check')
  data=p.read_bytes();length,kind=struct.unpack_from('<II',data,12)
  self.assertEqual(kind,0x4e4f534a)
  gltf=json.loads(data[20:20+length])
  chambers=[n for n in gltf['nodes'] if 'chamber' in n.get('name','')]
  self.assertEqual(len(chambers),3)
  for node in chambers:
   primitive=gltf['meshes'][node['mesh']]['primitives'][0]
   self.assertGreater(gltf['accessors'][primitive['attributes']['POSITION']]['count'],32)
  self.assertTrue(any('blue glass' in m.get('name','') for m in gltf['materials']))

if __name__=='__main__':unittest.main()


def test_lab_upgrade_preserves_survey_identity_without_duplicate_geometry():
    path = Path("E:/CyberCity2085-3d-lab/generated/phase2/lab291/environment.glb")
    with path.open("rb") as glb:
        size = struct.unpack("<4sIII4s", glb.read(20))[3]
        nodes = json.loads(glb.read(size))["nodes"]
    groups = {node["name"]: node for node in nodes if node.get("children")}
    replacements = json.loads(Path(__file__).with_name("lab_fixtures290.json").read_text())["fixtures"]
    for replacement in replacements:
        original, = replacement["existing_overlaps"] or [replacement["id"]]
        node = groups[f"Occludable_{original}"]
        assert node["extras"]["visual_fixture"] == replacement["id"]
        if original != replacement["id"]:
            assert f"Occludable_{replacement['id']}" not in groups
