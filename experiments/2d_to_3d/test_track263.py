"""Actual export/source checks; deliberately no claim of artistic acceptance."""
import hashlib,json,unittest
import numpy as np
from PIL import Image
from test_industry256 import glb,LAB,ROOT

class TrackExport(unittest.TestCase):
 def test_floor_outside_track_band_and_stair_openings_are_preserved(self):
  folder=LAB/'generated/phase2/metro263';meta=json.loads((folder/'floor.json').read_text())
  old=np.array(Image.open(LAB/'generated/phase2/metro250/floor.png').convert('RGBA'))
  new=np.array(Image.open(folder/'floor.png').convert('RGBA'))
  x1,y1,x2,y2=meta['bounds_pixels'];mask=np.ones(old.shape[:2],bool);mask[y1:y2,x1:x2]=False
  self.assertTrue(np.array_equal(old[mask],new[mask]))
  self.assertTrue(np.array_equal(old[:,:,3],new[:,:,3]))
  self.assertEqual(meta['source_sha256'],hashlib.sha256((ROOT/'assets/maps/city_transit_subway_platform.png').read_bytes()).hexdigest())
 def test_track_has_real_vertical_geometry_and_retains_old_environment_groups(self):
  folder=LAB/'generated/phase2/metro263';track=glb(folder/'track.glb')
  self.assertEqual(len(track['meshes']),4)
  positions=[track['accessors'][p['attributes']['POSITION']] for m in track['meshes'] for p in m['primitives']]
  # glTF Y is height. Rails contain web, foot, and head at distinct heights.
  self.assertGreater(max(a['max'][1]-a['min'][1] for a in positions),.10)
  old=glb(LAB/'generated/phase2/metro250/environment.glb');new=glb(folder/'environment.glb')
  roots=lambda d:{n['name'] for n in d['nodes'] if n.get('name','').startswith('Occludable_')}
  self.assertEqual(roots(old),roots(new))

if __name__=='__main__':unittest.main()
