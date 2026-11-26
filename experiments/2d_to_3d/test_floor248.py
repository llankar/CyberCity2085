import unittest
import numpy as np
from PIL import Image
from prepare_floor248 import prepare

class SourcePreservation(unittest.TestCase):
 def test_only_replacement_rectangles_change(self):
  pixels=np.full((64,96,3),100,dtype=np.uint8);pixels[20:40,20:40]=220
  image=Image.fromarray(pixels)
  result,mask=prepare(image,{'canvas_size':[96,64],'walls':[{'id':'table','rect':[20,20,40,40]},{'id':'west_wall','rect':[0,0,3,64]}]})
  self.assertTrue(np.array_equal(np.asarray(result)[mask==0],pixels[mask==0]))
  self.assertTrue(np.array_equal(np.asarray(image),pixels))
  self.assertEqual(np.count_nonzero(mask),400)
  self.assertFalse(np.array_equal(np.asarray(result)[mask>0],pixels[mask>0]))
 def test_polygon_does_not_mask_its_whole_bounding_box(self):
  image=Image.new('RGB',(80,80),(100,110,120))
  result,mask=prepare(image,{'canvas_size':[80,80],'walls':[{'id':'ruin','polygon':[[10,10],[60,10],[10,60]]}]})
  self.assertEqual(mask[15,15],255)
  self.assertEqual(mask[55,55],0)
  self.assertTrue(np.array_equal(np.asarray(result)[mask==0],np.asarray(image)[mask==0]))

if __name__=='__main__':unittest.main()
