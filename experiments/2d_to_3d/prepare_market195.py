"""Convert the existing canvas normal map to the format used by the experiment."""
from pathlib import Path
from PIL import Image
LAB=Path('E:/CyberCity2085-3d-lab');out=LAB/'generated/phase2/showcase195';out.mkdir(exist_ok=True)
with Image.open(LAB/'sources/charge_studio/textures/tileable/canvas_01.normal.tif') as source:
 source.convert('RGB').save(out/'canvas_normal.png')
print('MARKET195_CANVAS_READY')
