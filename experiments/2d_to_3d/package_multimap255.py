"""Local original-vs-native comparisons; no artistic success claims."""
from pathlib import Path
import argparse
import html
import json
from PIL import Image,ImageOps,ImageDraw,ImageChops
from prepare_multimap246 import SELECTION
from environment_library import LAB,ROOT
FOLDERS=['showcase245','residential253','lab248','factory249','metro250','wasteland254']


def frame_isometric_capture(panel):
    """Trim flat review-camera margins without cropping scenes that touch a corner."""
    width, height = panel.size
    background = panel.getpixel((0, 0))
    corners = ((width-1, 0), (0, height-1), (width-1, height-1))
    if any(panel.getpixel(point) != background for point in corners):
        return panel
    difference = ImageChops.difference(panel, Image.new("RGB", panel.size, background))
    bounds = difference.getbbox()
    if bounds is None:
        return panel
    left, top, right, bottom = bounds
    padding = max(4, min(width, height)//40)
    return panel.crop((max(0,left-padding),max(0,top-padding),
                       min(width,right+padding),min(height,bottom+padding)))


def main():
 parser = argparse.ArgumentParser(description=__doc__)
 maps = parser.add_mutually_exclusive_group()
 maps.add_argument('--catalogue-maps', nargs='+', metavar='MAP',
                   help='Render comparison sheets for selected catalogue IDs using their latest local captures')
 maps.add_argument('--all-catalogue', action='store_true',
                   help='Render comparison sheets for the entire catalogue')
 parser.add_argument('--top-down', action='store_true',
                     help='Compare the original with a Godot top-down capture')
 args = parser.parse_args()
 if args.top_down and not (args.catalogue_maps or args.all_catalogue):
  parser.error('--top-down requires a catalogue selection')
 if args.catalogue_maps or args.all_catalogue:
  from catalogue_test_assets import catalogue_environment
  catalogue = json.loads((Path(__file__).parent/'godot/preproduction_catalog.json').read_text())
  entries = {row['map']: row for row in catalogue}
  selected_maps = list(entries) if args.all_catalogue else args.catalogue_maps
  unknown = set(selected_maps) - entries.keys()
  if unknown:
   parser.error('Unknown map IDs: '+', '.join(sorted(unknown)))
  capture = 'top_down.png' if args.top_down else 'godot_overview.png'
  selection = []
  for name in dict.fromkeys(selected_maps):
   model = catalogue_environment(name)
   native = model.with_name(capture)
   description = entries[name].get('scope', entries[name]['family'])
   if native.is_file() and model.is_file() and native.stat().st_mtime < model.stat().st_mtime:
    description += ' · Capture predates the current 3D export.'
   selection.append((name, name, description, native))
  output_name = 'catalogue_top_down' if args.top_down else 'catalogue_comparisons'
  out = LAB/'generated/phase2'/(output_name+'_all' if args.all_catalogue else output_name)
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
   panel = Image.open(path).convert('RGB')
   if args.top_down:
    # The review camera spans 28 vertical world units; normalize both panels
    # to the tactical grid so the same cell occupies the same area.
    grid_width, grid_height = json.loads(original.with_suffix('.walls.json').read_text())['grid']
    if path == native:
     map_width = round(panel.height*grid_width/28)
     map_height = round(panel.height*grid_height/28)
     if map_width > panel.width or map_height > panel.height:
      raise ValueError(f'Top-down capture clips the tactical grid: {native}')
     left, top = (panel.width-map_width)//2, (panel.height-map_height)//2
     panel = panel.crop((left, top, left+map_width, top+map_height))
    panel = panel.resize((960, round(960*grid_height/grid_width)), Image.Resampling.LANCZOS)
   elif path == native:
    panel = frame_isometric_capture(panel)
   thumbnail=ImageOps.contain(panel,(960,960))
   image.paste(thumbnail,(x+(960-thumbnail.width)//2,80+(960-thumbnail.height)//2))
  view = 'TOP DOWN' if args.top_down else 'ISOMETRIC'
  draw.text((30,30),name+' // ORIGINAL 2D',fill='white');draw.text((990,30),'EXPERIMENTAL GODOT // '+view,fill='white')
  target=out/(family+'_comparison.jpg');image.save(target,quality=92)
  cards.append('<section><h2>'+html.escape(family)+'</h2><p>'+html.escape(reason)+'</p><img loading="lazy" src="'+target.name+'"></section>')
 (out/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>CyberCity multi-map review</title><style>body{background:#07141b;color:#def;font:18px system-ui;max-width:1600px;margin:30px auto}img,video{width:100%}section{margin:30px 0}</style><h1>'+title+'</h1>'+video+''.join(cards),encoding='utf8')
 print('MULTIMAP_COMPARISONS_PACKAGED',len(cards))

if __name__=='__main__':main()
