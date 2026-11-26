"""Package existing MP4 and ensemble captures; never rerender or re-encode assets."""
from pathlib import Path
import argparse
from PIL import Image,ImageOps,ImageDraw
from environment_library import LAB,ROOT

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--architecture',action='store_true');args=parser.parse_args()
 out=LAB/'generated/phase2'/('delivery281' if args.architecture else 'delivery279');out.mkdir(parents=True,exist_ok=True);cards=[]
 entries=[('residential280','city_district_apartment_block'),('wasteland280','wasteland_outdoor_02_ashfield_ruins')] if args.architecture else [('factory278','city_industrial_factory_floor'),('residential278','city_district_apartment_block')]
 video='architecture280_1080p30.mp4' if args.architecture else 'production278_1080p30.mp4'
 for folder,name in entries:
  source=Image.open(ROOT/f'assets/maps/{name}.png').convert('RGB');native=Image.open(LAB/'generated/phase2'/folder/'cast_wide.png').convert('RGB')
  pair=Image.new('RGB',(1920,600),(7,15,22));draw=ImageDraw.Draw(pair)
  for x,picture,title in [(0,source,'ORIGINAL 2D'),(960,native,'ASSEMBLED 3D // PROTOTYPE')]:
   picture=ImageOps.contain(picture,(960,540));pair.paste(picture,(x+(960-picture.width)//2,55+(540-picture.height)//2));draw.text((x+25,20),title,fill='white')
  pair.save(out/(folder+'_comparison.jpg'),quality=92)
  cards.append(f'<h2>{name}</h2><img src="{folder}_comparison.jpg"><a href="../{folder}/cast_close.png"><img src="../{folder}/cast_close.png"></a>')
 assert (LAB/'generated/phase2'/video).is_file(),'Reuse the completed movie; encode it before packaging'
 note='Physical wall UV/PBR repair, retained roof artwork, retinted acquired facade modules and attached service pipes. Simple architecture and flat wrecks remain unfinished.' if args.architecture else 'Objects produced in sequence with shared local IA loading, then reviewed together in their source environments.'
 candidate='' if args.architecture else '''<details><summary>Wasteland candidate: scale not accepted</summary><p>The full 3D wreck is retained, but fitting it to the tiny original wreck_e footprint makes it too small. The selected Wasteland scene is unchanged pending a compatible fragment or reconstruction.</p><img src="../wasteland278/cast_close.png"><a href="../production278_candidate_1080p30.mp4">Earlier three-map candidate reference</a></details>'''
 (out/'index.html').write_text('''<!doctype html><meta charset="utf-8"><title>CyberCity production lot</title><style>body{background:#07141b;color:#def;font:18px system-ui;max-width:1500px;margin:30px auto}img,video{width:100%;margin:15px 0}</style><h1>CyberCity // assembled object lot</h1><p>'''+note+''' Retained Rook, Raider and robot provide real scale. Prototype art; no interactive combat or live-FPS proof.</p><video controls src="../'''+video+'''"></video>'''+''.join(cards)+candidate,encoding='utf8')
 print('PRODUCTION279_GALLERY_PACKAGED existing MP4 reused')

if __name__=='__main__':main()
