"""Artistic PBR estimates from the generated colour map; never claimed as measured."""
from pathlib import Path
import argparse
import numpy as np
from PIL import Image
LAB=Path('E:/CyberCity2085-3d-lab')

def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--source',type=Path,default=LAB/'generated/phase2/arm256/paint/colour.png')
 parser.add_argument('--output',type=Path,default=LAB/'environment-library/assets/industrial_arm256')
 parser.add_argument('--surface',choices=['painted','metal'],default='painted')
 parser.add_argument('--keep-colour',action='store_true',help='Preserve generated source-matched enamel rather than applying the arm palette grade')
 args=parser.parse_args();source=args.source.resolve();out=args.output.resolve()
 if not source.is_relative_to(LAB.resolve()) or not out.is_relative_to(LAB.resolve()):raise ValueError('Materials must stay on E: lab')
 out.mkdir(parents=True,exist_ok=True)
 rgb=np.asarray(Image.open(source).convert('RGB'),dtype=np.float32)/255
 red,green,blue=rgb[:,:,0],rgb[:,:,1],rgb[:,:,2]
 painted=(red>green*1.15)&(green>blue*1.1)
 if args.surface=='metal':painted[:]=False
 dark=rgb.mean(axis=2)<.13
 scuffed=(rgb.max(axis=2)-rgb.min(axis=2)<.12)&(rgb.mean(axis=2)>.48)
 rough=np.full(red.shape,125,dtype=np.uint8);metal=np.full(red.shape,220,dtype=np.uint8)
 rough[painted]=155;metal[painted]=70
 rough[dark]=175;metal[dark]=140
 rough[scuffed]=105;metal[scuffed]=240
 # Bring overly yellow generated enamel toward the burnt-orange source palette.
 # Retain original paint output and neutral steel/grime pixels separately.
 graded=rgb.copy();graded[:,:,0][painted]*=.94;graded[:,:,1][painted]*=.83;graded[:,:,2][painted]*=.9
 if args.keep_colour:graded=rgb
 Image.fromarray(np.clip(graded*255,0,255).astype(np.uint8)).save(out/'albedo.png')
 Image.fromarray(rough).save(out/'roughness.png');Image.fromarray(metal).save(out/'metallic.png')
 print('ARM256_INFERRED_PBR_MAPS',list(red.shape))

if __name__=='__main__':main()
