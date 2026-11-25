"""Extract the small author-linked CC0 game prop with provenance and containment."""
import hashlib
import json
import zipfile
from pathlib import Path

source=Path('E:/CyberCity2085-3d-lab/downloads/firewarden_pistol.zip')
root=Path('E:/CyberCity2085-3d-lab/sources/firewarden_pistol').resolve()
root.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(source) as archive:
    assert archive.testzip() is None
    for entry in archive.infolist():
        target=(root/entry.filename).resolve()
        if not target.is_relative_to(root): raise ValueError('Archive extraction escaped E: source folder')
        if entry.is_dir(): target.mkdir(parents=True,exist_ok=True)
        else:
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(archive.read(entry))
    names=archive.namelist()
report={'author':'FireWarden','license':'CC0 1.0',
        'source':'https://opengameart.org/content/lowpoly-pistol',
        'download':'https://opengameart.org/sites/default/files/pistol_3.zip',
        'bytes':source.stat().st_size,'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
        'members':names,'author_description':'Original fictional pistol, approximately real scale,1350 triangles,256px atlas',
        'limitations':['Source art is low-poly; not accepted as final CyberCity equipment']}
(root/'provenance.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('FICTIONAL_PISTOL_SOURCE_INSPECTED',json.dumps(report))
