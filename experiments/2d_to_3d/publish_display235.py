"""Publish actual native stills for235, keeping the previous video explicitly labeled."""
from pathlib import Path
from PIL import Image
base=Path('E:/CyberCity2085-3d-lab/generated/phase2');out=base/'showcase235'
with Image.open(base/'library227/clean_0030.png') as image:
 image.save(out/'overview.png');image.crop((770,630,1075,885)).save(out/'display_detail.png')
page='''<!doctype html><meta charset="utf-8"><title>Original southeast display counter</title><style>body{background:#08141b;color:#d8edef;font:18px system-ui;max-width:1300px;margin:30px auto}img{max-width:100%}a{color:cyan}</style><h1>Original-derived southeast display counter</h1><p>Current native Godot still. Four recessed trays, original interior RGB crops, blue draped cloth and rear supports. One authentic view; hidden geometry interpreted. Earlier video remains variant234.</p><img src="overview.png"><img src="display_detail.png"><h2>Original map context</h2><img src="../../../environment-library/references/city_exterior_neon_market_alley__market_se.png"><p><a href="../../../environment-library/assets/market_southeast_display/shop.glb">Standalone shop GLB</a> / <a href="environment.blend">Blender environment source</a></p>'''
(out/'index.html').write_text(page,encoding='utf8')
gallery=base/'library227/index.html';text=gallery.read_text(encoding='utf8')
notice='<p id="candidate235">Video: variant234. Current still previews: variant235, source-derived southeast display counter. <a href="../showcase235/index.html">Latest candidate and model</a>.</p>'
if 'id="candidate235"' not in text:text=text.replace('<video',notice+'<video',1)
gallery.write_text(text,encoding='utf8')
print('CANDIDATE235_PREVIEW_WRITTEN')
