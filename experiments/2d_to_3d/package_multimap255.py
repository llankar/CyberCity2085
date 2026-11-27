"""Local original-vs-native comparisons; no artistic success claims."""
from pathlib import Path
import argparse
import html
import json
from PIL import Image,ImageOps,ImageDraw
from prepare_multimap246 import SELECTION
from environment_library import LAB,ROOT
FOLDERS=['showcase245','residential253','lab248','factory249','metro250','wasteland254']

def main():
 parser = argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--catalogue-maps', nargs='+', metavar='MAP',
                     help='Render comparison sheets for selected catalogue IDs using their latest local captures')
 parser.add_argument('--top-down', action='store_true',
                     help='Compare the original with a Godot top-down capture')
 args = parser.parse_args()
 if args.top_down and not args.catalogue_maps:
  parser.error('--top-down requires --catalogue-maps')
 if args.catalogue_maps:
  from catalogue_test_assets import catalogue_environment
  catalogue = json.loads((Path(__file__).parent/'godot/preproduction_catalog.json').read_text())
  entries = {row['map']: row for row in catalogue}
  unknown = set(args.catalogue_maps) - entries.keys()
  if unknown:
   parser.error('Unknown map IDs: '+', '.join(sorted(unknown)))
  capture = 'top_down.png' if args.top_down else 'godot_overview.png'
  selection = [(name, name, entries[name]['scope'], catalogue_environment(name).with_name(capture))
               for name in dict.fromkeys(args.catalogue_maps)]
  out = LAB/'generated/phase2'/('catalogue_top_down' if args.top_down else 'catalogue_comparisons')
  title = 'CyberCity 2085 // original and experimental 3D'
  video = ''
 else:
  selection = [(name, family, reason, LAB/f'generated/phase2/{folder}/godot_overview.png')
               for (name,family,reason),folder in zip(SELECTION,FOLDERS)]
  out = LAB/'generated/phase2/multimap255'
  title = 'Six environments // experimental art review'
  video = '<video controls src="environment_tour_1080p30.mp4"></video>'
 out.mkdir(parents=True,exist_ok=True)
 cards=[]
 for name,family,reason,native in selection:
  original=ROOT/f'assets/maps/{name}.png'
  if not native.is_file():
   if family=='showcase':native=LAB/'generated/phase2/library227/clean_0030.png'
   if not native.is_file():raise FileNotFoundError(native)
  image=Image.new('RGB',(1920,1080),(7,15,22));draw=ImageDraw.Draw(image)
  for x,path in [(0,original),(960,native)]:
   thumbnail=ImageOps.contain(Image.open(path).convert('RGB'),(960,960))
   image.paste(thumbnail,(x+(960-thumbnail.width)//2,80+(960-thumbnail.height)//2))
  view = 'TOP DOWN' if args.top_down else 'ISOMETRIC'
  draw.text((30,30),name+' // ORIGINAL 2D',fill='white');draw.text((990,30),'EXPERIMENTAL GODOT // '+view,fill='white')
  target=out/(family+'_comparison.jpg');image.save(target,quality=92)
  cards.append('<section><h2>'+html.escape(family)+'</h2><p>'+html.escape(reason)+'</p><img loading="lazy" src="'+target.name+'"></section>')
 (out/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>CyberCity multi-map review</title><style>body{background:#07141b;color:#def;font:18px system-ui;max-width:1600px;margin:30px auto}img,video{width:100%}section{margin:30px 0}</style><h1>'+title+'</h1>'+video+''.join(cards),encoding='utf8')
 print('MULTIMAP_COMPARISONS_PACKAGED',len(cards))

if __name__=='__main__':main()
