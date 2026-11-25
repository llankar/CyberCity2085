"""Deterministic original PBR paint maps for the experimental rigid vehicle."""
import random
from PIL import Image, ImageDraw


def maps(size=1024):
    if size < 64 or size > 4096:
        raise ValueError('Texture size outside supported range')
    base = Image.new('RGB', (size, size), (32, 53, 62))
    rough = Image.new('L', (size, size), 145)
    metal = Image.new('L', (size, size), 20)
    b, r, m = ImageDraw.Draw(base), ImageDraw.Draw(rough), ImageDraw.Draw(metal)
    width = max(2, size // 128)
    # Rescue-orange recognition band on painted steel; not a new game faction.
    b.rectangle((size*.7, 0, size*.84, size), fill=(214, 92, 21))
    rng = random.Random(2085)
    for _ in range(size // 2):
        x, y = rng.randrange(size), rng.randrange(size)
        edge_distance = min(x, y, size-1-x, size-1-y)
        if edge_distance > size*.055:
            continue
        end = (min(size-1, x+rng.randrange(width, width*6)), min(size-1, y+width))
        b.line(((x,y),end), fill=(120,129,130), width=width)
        r.line(((x,y),end), fill=100, width=width)
        m.line(((x,y),end), fill=240, width=width)
    for x in (.08,.92):
        for y in (.08,.92):
            point=(x*size,y*size)
            box=(point[0]-width*2,point[1]-width*2,point[0]+width*2,point[1]+width*2)
            b.ellipse(box, fill=(85,95,98)); r.ellipse(box,fill=110); m.ellipse(box,fill=240)
    return {'basecolor':base, 'roughness':rough, 'metallic':metal}


if __name__ == '__main__':
    from pathlib import Path
    folder=Path('E:/CyberCity2085-3d-lab/generated/phase2/vtol_finish135')
    folder.mkdir(parents=True,exist_ok=True)
    for name,image in maps().items():image.save(folder/(name+'.png'))
