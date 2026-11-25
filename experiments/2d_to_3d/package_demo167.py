"""Package actual native scene captures; never generate substitute screenshots."""
from pathlib import Path
import json
import shutil
import subprocess
from PIL import Image, ImageDraw

ROOT=Path('E:/CyberCity2085-3d-lab/generated/phase2')
OUT=ROOT/'demo167_final'
FFMPEG=Path('C:/Users/llank/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-9.1-full_build/bin/ffmpeg.exe')

def encode(folder, prefix):
    files=sorted(folder.glob('*.png'))
    assert files and [int(p.stem) for p in files]==list(range(1,len(files)+1)), 'Incomplete capture sequence'
    with Image.open(files[0]) as img: assert img.size==(1920,1080)
    if (OUT/f'{prefix}.mp4').exists(): return len(files)
    subprocess.run([str(FFMPEG),'-y','-loglevel','error','-framerate','15','-start_number','1',
        '-i',str(folder/'%04d.png'),'-c:v','libx264','-crf','20','-pix_fmt','yuv420p',
        str(OUT/f'{prefix}.mp4')],check=True)
    return len(files)

def main():
    report=json.loads((OUT/'demo.json').read_text())
    assert report['status']=='PASS'
    count=encode(OUT/'frames','tactical_1080p')
    assert count==report['frames']
    encode(ROOT/'demo167_support/showcase_frames','detail_1080p')
    if not (OUT/'tactical.gif').exists():
        subprocess.run([str(FFMPEG),'-y','-loglevel','error','-i',str(OUT/'tactical_1080p.mp4'),
            '-filter_complex','fps=10,scale=960:-1:flags=lanczos,split[a][b];[a]palettegen[p];[b][p]paletteuse',
            '-loop','0',str(OUT/'tactical.gif')],check=True)
    # Native close-view screenshots from the same retained assets; crops only.
    source=ROOT/'demo167_support/showcase_frames/0030.png'
    with Image.open(source) as img:
        for name,box in [('rook',(600,335,800,585)),('raider',(1090,540,1285,790)),('robot',(945,115,1130,370))]:
            img.crop(box).save(OUT/f'{name}_textured.png')
    shutil.copyfile(OUT/'frames/0110.png',OUT/'tactical_1920x1080.png')
    with Image.open(OUT/'frames/0030.png') as img:
        img.crop((620,75,1020,355)).save(OUT/'vehicle.png')
    package={'frames':count,'fps':15,'seconds':count/15,'resolution':[1920,1080],
             'visual_review':'Required; native capture is not final artistic acceptance',
             'files':['tactical_1080p.mp4','detail_1080p.mp4','tactical.gif','tactical_1920x1080.png',
                      'rook_textured.png','raider_textured.png','robot_textured.png','vehicle.png']}
    (OUT/'delivery.json').write_text(json.dumps(package,indent=2))
    (OUT/'index.html').write_text('''<!doctype html><html lang="fr"><meta charset="utf-8">
<title>CyberCity 2085 — démonstration 3D privée</title>
<style>body{margin:40px;background:#091017;color:#e6f4f7;font:18px system-ui;max-width:1400px}h1,h2{color:#25e1ee}video,.scene{width:100%;border:1px solid #25aaba}section{display:flex;gap:24px;flex-wrap:wrap}figure{margin:0;background:#14202a;padding:16px}figure img{height:250px;object-fit:contain}p{color:#aabbc7;line-height:1.6}</style>
<h1>CYBERCITY 2085 // DÉMONSTRATION 3D</h1>
<p>Prototype privé. Ressources existantes réutilisées. Aucun changement du jeu de production.</p>
<h2>Séquence tactique — 1920 × 1080</h2><video controls src="tactical_1080p.mp4"></video>
<p>27 secondes : prêt, déplacement simultané, tir, mêlée, couverture, PSI, soins expérimentaux et mort.</p>
<h2>Personnages et véhicule texturés</h2><section>
<figure><img src="rook_textured.png"><figcaption>Rook — candidat cyberpunk AmJViZ</figcaption></figure>
<figure><img src="raider_textured.png"><figcaption>Raider — militaire Rocketbox</figcaption></figure>
<figure><img src="robot_textured.png"><figcaption>Security Bot — Blender Studio</figcaption></figure>
<figure><img src="vehicle.png"><figcaption>VTOL — rotors animés</figcaption></figure></section>
<h2>Détail des mouvements</h2><video controls src="detail_1080p.mp4"></video>
<p>Vue agrandie pour examiner les mouvements. Les soins sont une adaptation à genoux, sans contact patient finalisé. La marche et les raccords de phases restent perfectibles. Les modèles Hunyuan sans couleur ne sont pas substitués à ces personnages animés.</p>
<h2>Échelle du jeu</h2><img class="scene" src="tactical_1920x1080.png">
<p>Environ 62 pixels par personnage humain. Le sprite 2D de référence est visible à droite ; ce n'est pas le même costume.</p>
<img class="scene" src="overview_21px.png"><p>Vue éloignée ~21 pixels : silhouette prioritaire, détails fins perdus.</p>
<p>Notices sources conservées. Images et vidéos locales uniquement, aucune publication.</p></html>''',encoding='utf8')
    print('VISUAL_DELIVERY_WRITTEN',json.dumps(package))

if __name__=='__main__': main()
