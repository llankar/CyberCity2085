"""Package existing MP4 and ensemble captures; never rerender or re-encode assets."""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
from environment_library import LAB,ROOT

def main():
 out=LAB/'generated/phase2/delivery279';out.mkdir(parents=True,exist_ok=True);cards=[]
 for folder,name in [('factory278','city_industrial_factory_floor'),('residential278','city_district_apartment_block')]:
  source=Image.open(ROOT/f'assets/maps/{name}.png').convert('RGB');native=Image.open(LAB/'generated/phase2'/folder/'cast_wide.png').convert('RGB')
  pair=Image.new('RGB',(1920,600),(7,15,22));draw=ImageDraw.Draw(pair)
  for x,picture,title in [(0,source,'ORIGINAL 2D'),(960,native,'ASSEMBLED 3D // PROTOTYPE')]:
   picture=ImageOps.contain(picture,(960,540));pair.paste(picture,(x+(960-picture.width)//2,55+(540-picture.height)//2));draw.text((x+25,20),title,fill='white')
  pair.save(out/(folder+'_comparison.jpg'),quality=92)
  cards.append(f'<h2>{name}</h2><img src="{folder}_comparison.jpg"><a href="../{folder}/cast_close.png"><img src="../{folder}/cast_close.png"></a>')
 assert (LAB/'generated/phase2/production278_1080p30.mp4').is_file(),'Reuse the completed movie; encode it before packaging'
 (out/'index.html').write_text('''<!doctype html><meta charset="utf-8"><title>CyberCity production lot</title><style>body{background:#07141b;color:#def;font:18px system-ui;max-width:1500px;margin:30px auto}img,video{width:100%;margin:15px 0}</style><h1>CyberCity // assembled object lot</h1><p>Objects produced in sequence with shared local IA loading, then reviewed together in their source environments. Retained Rook, Raider and robot provide real scale. Prototype art; no interactive combat or live-FPS proof.</p><video controls src="../production278_1080p30.mp4"></video>'''+''.join(cards)+'''<details><summary>Wasteland candidate: scale not accepted</summary><p>The full 3D wreck is retained, but fitting it to the tiny original wreck_e footprint makes it too small. The selected Wasteland scene is unchanged pending a compatible fragment or reconstruction.</p><img src="../wasteland278/cast_close.png"><a href="../production278_candidate_1080p30.mp4">Earlier three-map candidate reference</a></details>''',encoding='utf8')
 print('PRODUCTION279_GALLERY_PACKAGED existing MP4 reused')

if __name__=='__main__':main()
