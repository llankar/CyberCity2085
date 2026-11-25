"""Local visual delivery of the two completed colour trials, without AI reruns."""
from pathlib import Path
import hashlib
import html
import json

ROOT = Path('E:/CyberCity2085-3d-lab/generated/phase2')


def main():
    cards = []
    for label, relative in [('Rook', 'paint171/rook_official'),
                            ('Combat robot', 'paint168/robot_official')]:
        folder = ROOT / relative
        result = json.loads((folder / 'result.json').read_text())
        assert result['status'] == 'PASS'
        assert hashlib.sha256((folder / 'mesh.glb').read_bytes()).hexdigest() == result['glb_sha256']
        for name in ['painted_isometric.png', 'painted_material.glb', 'colour.png']:
            assert (folder / name).is_file()
        url = '../' + relative
        cards.append(f'''<section><h2>{html.escape(label)}</h2>
<img src="{url}/painted_isometric.png" alt="Neutral three-quarter render">
<p>Generated colour, 1024 × 1024. {result['triangles']:,} triangles.
Manual metal/roughness settings; static model.</p>
<p><a href="{url}/painted_material.glb">GLB</a> ·
<a href="{url}/colour.png">Colour texture</a> ·
<a href="{url}/painted_scale_close.png">Native combat scale</a></p></section>''')
    target = ROOT / 'paint171/index.html'
    target.write_text('''<!doctype html><html lang="en"><meta charset="utf-8">
<title>CyberCity — colour trials</title><style>
body{background:#10171c;color:#e5eef0;font:18px system-ui;margin:32px}
main{display:grid;grid-template-columns:repeat(2,minmax(300px,768px));gap:24px}
img{width:100%}a{color:#39d8e7}p{max-width:1000px;line-height:1.5}
</style><h1>CYBERCITY 2085 // COLOUR TRIALS</h1>
<p>Existing Hunyuan geometry, textured from the original combat artwork.
Rook retains a fused rifle and bent arms. Neither candidate is rigged.
These results preserve the animated characters in the tactical showcase.</p>
<main>''' + ''.join(cards) + '</main></html>', encoding='utf8')
    print('PAINT_VISUAL_DELIVERY_READY', target)


if __name__ == '__main__':
    main()
