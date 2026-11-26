"""Remove only experimental flat boundary artwork across the two railway exits."""
import json,hashlib
import numpy as np
from PIL import Image
from environment_library import LAB,ROOT

def main():
 old=np.array(Image.open(LAB/'generated/phase2/metro263/floor.png').convert('RGBA'))
 image=old.copy();h,w=image.shape[:2];mask=np.zeros((h,w),bool)
 y1,y2=round(236*h/540),round(304*h/540)
 for x1,x2,sample in [(0,round(30*w/960),round(40*w/960)),(round(930*w/960),w,round(920*w/960))]:
  image[y1:y2,x1:x2,:3]=old[y1:y2,sample:sample+1,:3]
  mask[y1:y2,x1:x2]=True
 assert np.array_equal(image[~mask],old[~mask])
 assert np.array_equal(image[:,:,3],old[:,:,3])
 out=LAB/'generated/phase2/metro270';out.mkdir(parents=True,exist_ok=True)
 Image.fromarray(image).save(out/'floor.png')
 (out/'rail_exit_floor.json').write_text(json.dumps({'source_sha256':hashlib.sha256((ROOT/'assets/maps/city_transit_subway_platform.png').read_bytes()).hexdigest(),'outside_exit_masks_identical':True,'stair_alpha_preserved':True,'note':'Experimental boundary paint removed only within track exits; original PNG/tactical files untouched'},indent=2))
 print('METRO272_EXIT_FLOOR_CLEARED')

if __name__=='__main__':main()
