"""Visible industrial family delivery; original art versus true native top-down view."""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageChops
from environment_library import ROOT,LAB

def main():
 out=LAB/'generated/phase2/factory257'
 canvas=Image.new('RGB',(1920,1080),(7,15,22));draw=ImageDraw.Draw(canvas)
 original=Image.open(ROOT/'assets/maps/city_industrial_factory_floor.png').convert('RGB')
 # Compare in the same40x28 coordinate rectangle as the original tactical grid.
 original=original.resize((1200,840))
 native=Image.open(out/'top_down.png').convert('RGB')
 difference=ImageChops.difference(native,Image.new('RGB',native.size,native.getpixel((0,0))))
 bounds=difference.convert('L').point(lambda p:255 if p>4 else 0).getbbox()
 if bounds:native=native.crop(bounds)
 for x,image in [(0,original),(960,native)]:
  picture=ImageOps.contain(image,(960,960));canvas.paste(picture,(x+(960-picture.width)//2,65+(960-picture.height)//2))
 draw.text((25,25),'ORIGINAL // calibrated40x28 grid',fill='white');draw.text((985,25),'NATIVE GODOT // TOP-DOWN // WORK IN PROGRESS',fill='white')
 canvas.save(out/'original_vs_topdown.jpg',quality=93)
 (out/'index.html').write_text('''<!doctype html><meta charset="utf-8"><title>Industrial detail pass</title>
<style>body{background:#07141b;color:#def;font:18px system-ui;max-width:1600px;margin:30px auto}img,video{width:100%;margin:14px 0}</style>
<h1>CyberCity2085 // industrial family prototype</h1>
<p>Six textured Hunyuan arms and five precise roller-conveyor modules replace three original assembly groups. Other important machines remain unreconstructed. No final map or combat acceptance implied.</p>
<video controls src="detail258_1080p30.mp4"></video>
<h2>Actual combat-scale reference</h2><img src="combat_scale_agent.png">
<h2>Close view with retained Rook</h2><img src="close_agent.png">
<h2>Original / native top-down comparison</h2><img src="original_vs_topdown.jpg">
<p>Original top-down source plus one explicitly inferred imagegen view fed the local Hunyuan pipeline. Roughness and metal masks are artistic estimates. Original source PNGs and rules remain unchanged.</p>''',encoding='utf8')
 print('INDUSTRY258_VISUAL_DELIVERY_PACKAGED')

if __name__=='__main__':main()
