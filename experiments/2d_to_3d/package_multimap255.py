"""Local original-vs-native comparisons; no artistic success claims."""
from pathlib import Path
import html
from PIL import Image,ImageOps,ImageDraw
from prepare_multimap246 import SELECTION
from environment_library import LAB,ROOT
FOLDERS=['showcase245','residential253','lab248','factory249','metro250','wasteland254']

def main():
 out=LAB/'generated/phase2/multimap255';out.mkdir(parents=True,exist_ok=True)
 cards=[]
 for (name,family,reason),folder in zip(SELECTION,FOLDERS):
  # SELECTION lists metro before wasteland, matching the source queue.
  original=ROOT/f'assets/maps/{name}.png';native=LAB/f'generated/phase2/{folder}/godot_overview.png'
  if not native.is_file():
   if family=='showcase':native=LAB/'generated/phase2/library227/clean_0030.png'
   if not native.is_file():raise FileNotFoundError(native)
  image=Image.new('RGB',(1920,1080),(7,15,22));draw=ImageDraw.Draw(image)
  for x,path in [(0,original),(960,native)]:
   thumbnail=ImageOps.contain(Image.open(path).convert('RGB'),(960,960))
   image.paste(thumbnail,(x+(960-thumbnail.width)//2,80+(960-thumbnail.height)//2))
  draw.text((30,30),name+' // ORIGINAL 2D',fill='white');draw.text((990,30),'EXPERIMENTAL NATIVE GODOT // WORK IN PROGRESS',fill='white')
  target=out/(family+'_comparison.jpg');image.save(target,quality=92)
  cards.append('<section><h2>'+html.escape(family)+'</h2><p>'+html.escape(reason)+'</p><img src="'+target.name+'"></section>')
 (out/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>CyberCity multi-map review</title><style>body{background:#07141b;color:#def;font:18px system-ui;max-width:1600px;margin:30px auto}img,video{width:100%}section{margin:30px 0}</style><h1>Six environments // experimental art review</h1><p>Partial reconstructions. No completed tactical combat adapter or artistic acceptance implied.</p><video controls src="environment_tour_1080p30.mp4"></video>'+''.join(cards),encoding='utf8')
 print('MULTIMAP_COMPARISONS_PACKAGED',len(cards))

if __name__=='__main__':main()
