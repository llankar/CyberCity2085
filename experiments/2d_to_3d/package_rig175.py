"""Publish local media for the first animated neural candidate; no art PASS."""
from pathlib import Path
import json
import argparse
import subprocess

OUT=Path('E:/CyberCity2085-3d-lab/generated/phase2/rig175')
BIN=Path('C:/Users/llank/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-9.1-full_build/bin')

def main():
    global OUT
    parser=argparse.ArgumentParser();parser.add_argument('--folder',default=str(OUT))
    OUT=Path(parser.parse_args().folder).resolve()
    assert OUT.is_relative_to(Path('E:/CyberCity2085-3d-lab').resolve())
    report=json.loads((OUT/'binding.json').read_text())
    assert report['unweighted']==0
    for name in ['actions','actions_game']:
        info=json.loads(subprocess.check_output([str(BIN/'ffprobe.exe'),'-v','error','-show_streams','-of','json',str(OUT/(name+'.avi'))]))
        video=next(stream for stream in info['streams'] if stream['codec_type']=='video')
        assert (video['width'],video['height'],video['avg_frame_rate'],int(video['nb_frames']))==(1920,1080,'30/1',330)
        subprocess.run([str(BIN/'ffmpeg.exe'),'-y','-loglevel','error','-i',str(OUT/(name+'.avi')),
            '-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-an','-movflags','+faststart',str(OUT/(name+'.mp4'))],check=True)
    (OUT/'index.html').write_text('''<!doctype html><html lang="fr"><meta charset="utf-8">
<title>CyberCity — Rook animé expérimental</title><style>
body{background:#10171c;color:#e4edf0;font:18px system-ui;margin:32px;max-width:1500px}
video,img{width:100%}.neutral{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}a{color:#39d8e7}p{line-height:1.5;max-width:1100px}</style>
<h1>ROOK // PREMIER CANDIDAT NEURAL ANIMÉ</h1>
<p>Référence dérivée du véritable sprite de combat, sans arme, en pose A.
Maillage Hunyuan et texture couleur 1024. Squelette et cinq mouvements UAL existants.
Les poids du manteau ont été corrigés après un premier essai déformé conservé.</p>
<div class="neutral"><img src="../paint175/rook_unarmed/review/front.png"><img src="../paint175/rook_unarmed/review/profile.png"><img src="../paint175/rook_unarmed/review/back.png"></div><video controls src="actions.mp4"></video>
<p>Repos, marche, pose de tir sans arme, mêlée et mort. Les épaules et le manteau
gardent des déformations visibles. Contact des pieds et équipement à finaliser.
Ce modèle ne remplace pas le personnage de la démonstration tactique.</p>
<h2>Échelle du combat</h2><video controls src="actions_game.mp4"></video>
<p><a href="human.glb">GLB animé</a> · <a href="human.blend">Source Blender</a> ·
<a href="../city174/encounter_1080p30.mp4">Scène tactique conservée</a></p>
<img src="pose_135.png"><img src="pose_285.png"></html>''',encoding='utf8')
    if OUT.name=='rig176':
        gallery=(OUT/'index.html').read_text(encoding='utf8')
        gallery=gallery.replace('pose de tir sans arme','pose de tir avec pistolet')
        gallery=gallery.replace('Contact des pieds et ?quipement ? finaliser.', 'Prise en main du pistolet encore approximative. Les poses de pieds examin?es ne justifient pas de recalage global.')
        (OUT/'index.html').write_text(gallery,encoding='utf8')
    print('RIG175_MEDIA_READY; artistic acceptance remains open')

if __name__=='__main__':main()
