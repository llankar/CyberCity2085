"""Prepare source-preserving subway floor and original display crop on E:."""
import json
from pathlib import Path
from PIL import Image,ImageDraw
from prepare_floor248 import prepare,ROOT,LAB

def main():
 name='city_transit_subway_platform';source=ROOT/f'assets/maps/{name}.png'
 survey=json.loads(source.with_suffix('.wall-traces.json').read_text())
 out=LAB/'generated/phase2/metro250';out.mkdir(parents=True,exist_ok=True)
 original=Image.open(source);image,mask=prepare(original,survey);image=image.convert('RGBA')
 alpha=Image.new('L',image.size,255);draw=ImageDraw.Draw(alpha)
 sx=image.width/survey['canvas_size'][0];sy=image.height/survey['canvas_size'][1]
 for item in survey['walls']:
  if 'stair' not in item['id']:continue
  x1,y1,x2,y2=item['rect'];draw.rectangle((round((x1+2)*sx),round((y1+2)*sy),round((x2-2)*sx),round((y2-2)*sy)),fill=0)
 image.putalpha(alpha);image.save(out/'floor.png')
 original.crop(tuple(round(v*(sx if i%2==0 else sy)) for i,v in enumerate((539,143,558,163)))).save(out/'source_display.png')
 print('METRO250_FLOOR_AND_DISPLAY_PREPARED')

if __name__=='__main__':main()
