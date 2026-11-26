"""Publish one actual native art-preview still; identify the preceding video explicitly."""
import argparse,html,re
from pathlib import Path
from PIL import Image
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--folder',required=True);parser.add_argument('--video-variant',required=True)
parser.add_argument('--title',required=True);parser.add_argument('--note',required=True)
parser.add_argument('--crop',nargs=4,type=int,required=True)
args=parser.parse_args()
base=Path('E:/CyberCity2085-3d-lab/generated/phase2')
if not re.fullmatch(r'showcase\d+',args.folder):raise ValueError('Expected selected showcase directory')
out=base/args.folder
if not (out/'environment.glb').is_file():raise ValueError('Selected model missing')
with Image.open(base/'library227/clean_0030.png') as image:
 x0,y0,x1,y1=args.crop
 if not (0<=x0<x1<=image.width and 0<=y0<y1<=image.height):raise ValueError('Crop outside native frame')
 image.save(out/'overview.png');image.crop(args.crop).save(out/'detail.png')
title=html.escape(args.title);note=html.escape(args.note);video=html.escape(args.video_variant)
(out/'index.html').write_text(f'<!doctype html><meta charset="utf-8"><title>{title}</title><style>body{{background:#08141b;color:#d8edef;font:18px system-ui;max-width:1400px;margin:30px auto}}img{{max-width:100%}}a{{color:cyan}}</style><h1>{title}</h1><p>{note}</p><p>Native still: {args.folder}. Existing movie: {video}.</p><img src="overview.png"><img src="detail.png"><p><a href="environment.blend">Blender source</a> / <a href="environment.glb">Environment GLB</a></p>',encoding='utf8')
gallery=base/'library227/index.html';text=gallery.read_text(encoding='utf8')
text=re.sub(r'<p id="current-candidate">.*?</p>','',text)
notice=f'<p id="current-candidate">Movie: {video}. Current native still preview: <a href="../{args.folder}/index.html">{title}</a>.</p>'
gallery.write_text(text.replace('<video',notice+'<video',1),encoding='utf8')
print('NATIVE_CANDIDATE_PUBLISHED',out/'index.html')
