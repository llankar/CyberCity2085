"""Encode the native Full HD movie and its recorded game sounds for review."""
from pathlib import Path
import json,subprocess,shutil,argparse

OUT=Path('E:/CyberCity2085-3d-lab/generated/phase2/combat169')
TOOLS=Path('C:/Users/llank/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-9.1-full_build/bin')

def run(*args):subprocess.run([str(TOOLS/'ffmpeg.exe'),'-y','-loglevel','error',*map(str,args)],check=True)

def main():
    global OUT
    parser=argparse.ArgumentParser();parser.add_argument('--folder',default=str(OUT))
    OUT=Path(parser.parse_args().folder).resolve()
    assert OUT.is_relative_to(Path('E:/CyberCity2085-3d-lab').resolve())
    state=json.loads((OUT/'encounter.json').read_text())
    assert state['blocked_shots']>=1,'Cover has not stopped a shot'
    assert state.get('occlusion_frames',0)>0,'Camera occlusion not demonstrated'
    probe=json.loads(subprocess.check_output([str(TOOLS/'ffprobe.exe'),'-v','error','-show_streams','-of','json',str(OUT/'encounter.avi')]))
    video=next(s for s in probe['streams'] if s['codec_type']=='video')
    assert (video['width'],video['height'],video['avg_frame_rate'])==(1920,1080,'30/1')
    assert any(s['codec_type']=='audio' for s in probe['streams'])
    assert int(video['nb_frames'])==state['frames']
    run('-i',OUT/'encounter.avi','-c:v','libx264','-crf','18','-pix_fmt','yuv420p',
        '-af','volume=9dB','-c:a','aac','-b:a','160k','-movflags','+faststart',OUT/'encounter_1080p30.mp4')
    run('-ss','7','-t','15','-i',OUT/'encounter_1080p30.mp4','-filter_complex',
        'fps=10,scale=960:-1:flags=lanczos,split[a][b];[a]palettegen[p];[b][p]paletteuse',
        '-loop','0',OUT/'combat_excerpt.gif')
    (OUT/'index.html').write_text('''<!doctype html><html lang="fr"><meta charset="utf-8"><title>CyberCity — combat 3D</title>
<style>body{background:#081117;color:#dceef1;font:18px system-ui;margin:32px;max-width:1500px}h1{color:#21dce9}video,img{width:100%;border:1px solid #1f505b;margin:12px 0}p{line-height:1.5;color:#a8bdc4}</style>
<h1>CYBERCITY 2085 // NEON ALLEY</h1><video controls src="encounter_1080p30.mp4"></video>
<p>Full HD, 30 images/s, sons du jeu. Deux agents, deux raiders et un robot. Déplacements continus, tir arrêté par une couverture, échanges de tirs, mêlée, arcs PSI, destruction et soins. Caméra animée avec fondu des bâtiments masquant les agents.</p>
<p>Rencontre mise en scène dans le laboratoire indépendant : aucune campagne ni IA de production exécutée. La vidéo est rendue hors temps réel. Le style architectural et les contacts de soins restent perfectibles.</p>
<img src="clean_0254.png"><img src="clean_0590.png"><img src="clean_0750.png">
<p>Modèles humains et robot conservés. Matériaux PBR et accessoires Poly Haven, composants de toiture Kenney, sol et sons CyberCity existants. Ressources privées locales, aucune publication.</p></html>''',encoding='utf8')
    if len(state['health'])==6:
        page=(OUT/'index.html').read_text(encoding='utf8')
        page=page.replace('Deux agents, deux raiders et un robot.', 'Trois agents, deux raiders et un robot, avec le candidat Hunyuan armé.')
        page=page.replace('Modèles humains et robot conservés.', 'Cast conservé et candidat Hunyuan ajouté pour comparaison.')
        (OUT/'index.html').write_text(page,encoding='utf8')
    if OUT.name=='vehicle178':
        page=(OUT/'index.html').read_text(encoding='utf8')
        page=page.replace('</html>','''<h2>VTOL — finition mécanique</h2>
<p>Coque PBR, verrière ajustée, turbines et détails de maintenance.
Les pivots existants sont conservés. La rotation des rotors boucle dans cette scène.
L'atterrissage et la qualité artistique finale restent à vérifier.</p>
<p><a href="../vtol178/vtol_actions.glb">GLB animé</a> ·
<a href="../vtol178/vtol_actions.blend">Source Blender</a></p>
<img src="../vtol178/neutral.png"><img src="../vtol178/rear.png"></html>''')
        (OUT/'index.html').write_text(page,encoding='utf8')
    if OUT.name=='fall181':
        page=(OUT/'index.html').read_text(encoding='utf8')
        page=page.replace('</html>','''<h2>Robot : impact et chute</h2>
<p>Impulsion PSI, chute continue hors du masque de la caisse, fumée et fragments.
La rencontre reste une séquence mise en scène indépendante.</p>
<img src="impact_0603.png"><img src="clean_0630.png">
<p><a href="../rig177/human.glb">Humain GLB</a> ·
<a href="../security_opaque137/robot_actions.glb">Robot GLB</a> ·
<a href="../vtol178/vtol_actions.glb">VTOL GLB</a></p></html>''')
        (OUT/'index.html').write_text(page,encoding='utf8')
    (OUT/'delivery.json').write_text(json.dumps({'native_video':video,'encounter':state,
        'scope':'Native rendered visual sequence, not campaign or production AI acceptance'},indent=2))
    print('COMBAT169_DELIVERED',state)

if __name__=='__main__':main()
