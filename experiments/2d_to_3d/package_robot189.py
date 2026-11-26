"""Package the actual neutral articulation movie, without campaign validation."""
from pathlib import Path
import subprocess,json
OUT=Path('E:/CyberCity2085-3d-lab/generated/phase2/robot189')
TOOLS=Path('C:/Users/llank/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-9.1-full_build/bin')
probe=json.loads(subprocess.check_output([str(TOOLS/'ffprobe.exe'),'-v','error','-show_streams','-of','json',str(OUT/'actions.avi')]))
v=next(s for s in probe['streams'] if s['codec_type']=='video');assert (v['width'],v['height'],v['avg_frame_rate'],int(v['nb_frames']))==(1920,1080,'30/1',330)
def run(*args):subprocess.run([str(TOOLS/'ffmpeg.exe'),'-y','-loglevel','error',*map(str,args)],check=True)
run('-i',OUT/'actions.avi','-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-an','-movflags','+faststart',OUT/'actions_1080p30.mp4')
run('-i',OUT/'actions_1080p30.mp4','-filter_complex','fps=10,scale=960:-1,split[a][b];[a]palettegen[p];[b][p]paletteuse','-loop','0',OUT/'actions.gif')
(OUT/'index.html').write_text('''<!doctype html><html lang="fr"><meta charset="utf-8"><title>CyberCity — robot Hunyuan articulé</title><style>body{background:#10171d;color:#dfedf1;font:18px system-ui;margin:32px}video,img{width:100%;max-width:1920px}a{color:#43dce8}p{max-width:1200px;line-height:1.5}</style><h1>Robot Hunyuan — premier essai articulé</h1><p>Ressource couleur déjà générée, nouveau rig mécanique. Attente, marche, mêlée, impact et arrêt. Capture native Full HD30fps,11secondes, sans audio. Le robot actuel de la scène tactique est conservé.</p><video controls src="actions_1080p30.mp4"></video><p>Prototype incomplet : déformation visible du coude en mêlée, rigidité des plaques et contacts de marche à améliorer. Ces défauts empêchent son adoption. La chute est une étude indépendante, pas encore raccordée aux effets de destruction.</p><p><a href="robot_actions.glb">GLB animé</a> · <a href="robot_actions.blend">Source Blender</a> · <a href="actions.gif">GIF</a></p><img src="pose_075.png"><img src="pose_135.png"><img src="pose_285.png"><h2>Échelle du combat</h2><img src="comparison_native.png"><p><a href="../materials186/index.html">Démonstration tactique retenue</a></p></html>''',encoding='utf8')
(OUT/'delivery.json').write_text(json.dumps({'native_video':v,'scope':'articulation prototype; elbow/plate deformation unresolved; not promoted'},indent=2))
print('ROBOT189_PACKAGED native330frames; artistic acceptance open')
