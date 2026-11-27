"""Actual export/source coverage checks; not artistic or combat acceptance."""
import hashlib,json,struct,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];LAB=Path('E:/CyberCity2085-3d-lab/generated/phase2')

def exported_names(path):
 data=path.read_bytes();length,kind=struct.unpack_from('<II',data,12)
 if kind!=0x4e4f534a:raise ValueError('Missing GLB JSON')
 return {n.get('name','') for n in json.loads(data[20:20+length])['nodes']}

class OutdoorCoverage(unittest.TestCase):
 def check_source(self,name):
  source=ROOT/f'assets/maps/{name}.png';walls=json.loads(source.with_suffix('.walls.json').read_text())
  self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(),walls['image_sha256'])
  return json.loads(source.with_suffix('.wall-traces.json').read_text())['walls']
 def test_residential_exports_surveyed_buildings(self):
  survey=self.check_source('city_district_apartment_block')
  expected={'Occludable_'+r['id'] for r in survey if any(k in r['id'] for k in ['building','tower','extension'])}
  actual={n for n in exported_names(LAB/'residential253/environment.glb') if n.startswith('Occludable_')}
  self.assertEqual(actual,expected)
 def test_ruins_preserve_wrecks_as_2d(self):
  survey=self.check_source('wasteland_outdoor_02_ashfield_ruins')
  expected={'Occludable_'+r['id'] for r in survey if 'wreck' not in r['id']}
  actual={n for n in exported_names(LAB/'wasteland254/environment.glb') if n.startswith('Occludable_')}
  self.assertEqual(actual,expected)

if __name__=='__main__':unittest.main()


def test_apartment_block_exports_street_fixtures_in_cutaway_groups():
    import json
    from pathlib import Path
    import struct

    import pytest

    folder = Path("E:/CyberCity2085-3d-lab/generated/phase2/residential317")
    if not (folder / "street_fixtures.json").is_file():
        pytest.skip("Build the residential street fixtures on E: first")
    traces = json.loads((folder / "street_fixtures.json").read_text())["walls"]
    with (folder / "environment.glb").open("rb") as glb:
        size = struct.unpack("<4sIII4s", glb.read(20))[3]
        nodes = json.loads(glb.read(size))["nodes"]
    roots = {node["name"] for node in nodes if node.get("children")}
    assert len(traces) == 20
    assert {f"Occludable_{row['id']}" for row in traces} <= roots

    northwest = next(node for node in nodes if node["name"] == "Occludable_northwest_building")
    assert any(nodes[index]["name"] == "Northwest rooftop cargo" for index in northwest["children"])
    sills = {index for index, node in enumerate(nodes)
             if node["name"].startswith("Residential projected window sill")}
    building_children = {index for node in nodes if node["name"].startswith("Occludable_")
                         for index in node.get("children", [])}
    assert sills and sills <= building_children
