"""Concise visible detail-pass gallery and source-group coverage, not load-count acceptance."""
import json,struct
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageChops
from environment_library import LAB,ROOT

def comparison(source,native,target):
 canvas=Image.new('RGB',(1920,1080),(7,15,22));draw=ImageDraw.Draw(canvas)
 original=Image.open(source).convert('RGB').resize((1200,840))
 image=Image.open(native).convert('RGB');bg=Image.new('RGB',image.size,image.getpixel((0,0)))
 bounds=ImageChops.difference(image,bg).convert('L').point(lambda p:255 if p>4 else 0).getbbox()
 if bounds:image=image.crop(bounds)
 for x,picture in [(0,original),(960,image)]:
  picture=ImageOps.contain(picture,(960,960));canvas.paste(picture,(x+(960-picture.width)//2,65+(960-picture.height)//2))
 draw.text((25,25),'ORIGINAL //40x28 coordinate rectangle',fill='white');draw.text((985,25),'NATIVE TOP-DOWN // DETAIL PASS INCOMPLETE',fill='white')
 canvas.save(target,quality=93)

def main():
 out=LAB/'generated/phase2/detail262';out.mkdir(parents=True,exist_ok=True)
 cards=[]
 for name,folder,title in [('city_industrial_factory_floor','factory260','Industrial family'),('city_interior_research_lab','lab261','Scientific wall services')]:
  base=LAB/'generated/phase2'/folder
  comparison(ROOT/f'assets/maps/{name}.png',base/'top_down.png',out/(folder+'_comparison.jpg'))
  cards.append(f'<h2>{title}</h2><img src="{folder}_comparison.jpg"><img src="../{folder}/scale_agent.png"><img src="../{folder}/scale_close.png">')
 factory=LAB/'generated/phase2/factory260/environment.glb';binary=factory.read_bytes();length=struct.unpack_from('<I',binary,12)[0]
 names={n.get('name') for n in json.loads(binary[20:20+length])['nodes']}
 survey=json.loads((ROOT/'assets/maps/city_industrial_factory_floor.wall-traces.json').read_text())
 new={'west_assembly','east_assembly_north','east_assembly_south','reactor_north','reactor_middle'}
 groups=[{'id':r['id'],'state':'DETAILED_VOLUME_PROTOTYPE' if r['id'] in new else 'COARSE_VOLUME_NEEDS_DETAIL' if 'Occludable_'+r['id'] in names else 'FLAT_SOURCE_ART_ONLY'} for r in survey['walls']]
 (out/'factory_source_coverage.json').write_text(json.dumps({'scope':'Survey-group coverage only; unsurveyed art items not counted','groups':groups,'new_asset_types':3,'new_machine_instances':13,'final_map_acceptance':False},indent=2))
 (out/'index.html').write_text('''<!doctype html><meta charset="utf-8"><title>CyberCity environment detail</title>
<style>body{background:#07141b;color:#def;font:18px system-ui;max-width:1600px;margin:30px auto}img,video{width:100%;margin:15px 0}</style>
<h1>CyberCity2085 // environment detail pass</h1>
<p>Three reusable industrial types,13 new machine instances. Scientific wall skins improved. Important machines and other map families remain unfinished. These are visual references, not interactive combat acceptance.</p>
<video controls src="environment_detail_1080p30.mp4"></video>'''+''.join(cards),encoding='utf8')
 print('DETAIL262_GALLERY_PACKAGED',len(groups),'source groups;3 new asset types/13 instances')

if __name__=='__main__':main()
