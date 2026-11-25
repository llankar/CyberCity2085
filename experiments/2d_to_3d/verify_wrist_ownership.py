"""Identify bright wrist pixels by actual native emission ownership captures."""
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image


def analyze(original,owner,roi):
    if original.shape!=owner.shape or original.ndim!=3 or original.shape[2]!=3:
        raise ValueError('Matching RGB captures required')
    x0,y0,x1,y1=roi
    if not(0<=x0<x1<=original.shape[1] and 0<=y0<y1<=original.shape[0]):
        raise ValueError('Nonempty in-bounds review ROI required')
    p=original[y0:y1,x0:x1];q=owner[y0:y1,x0:x1]
    bright=(p[:,:,0]>180)&(p[:,:,1]>140)&(p[:,:,2]>100)
    body=(q[:,:,0]>240)&(q[:,:,1]<10)&(q[:,:,2]>240)
    glove=(q[:,:,0]<10)&(q[:,:,1]>240)&(q[:,:,2]>240)
    return {'bright_band_pixels':int(bright.sum()),'bright_pixels_on_retained_body':int((bright&body).sum()),'bright_pixels_on_authored_glove':int((bright&glove).sum())}


def main():
    root=Path('E:/CyberCity2085-3d-lab/generated/phase2')
    baseline=root/'rook_cuff132/baseline_MeleeStudy.png'
    ownership=root/'rook_wrist132/mesh_owner_all_melee.png'
    roi=(480,375,520,435)
    report=analyze(np.asarray(Image.open(baseline).convert('RGB')),np.asarray(Image.open(ownership).convert('RGB')),roi)
    assert report['bright_band_pixels']>20 and report['bright_pixels_on_retained_body']>20
    report.update({'roi_xyxy':roi,'baseline_png_sha256':hashlib.sha256(baseline.read_bytes()).hexdigest(),'owner_png_sha256':hashlib.sha256(ownership.read_bytes()).hexdigest(),'scope':'Reviewed wrist ROI surface ownership; not a general watertightness/contact test'})
    (root/'rook_wrist132/band_ownership_pixel_check.json').write_text(json.dumps(report,indent=2))
    print('NATIVE_WRIST_PIXEL_OWNERSHIP_VERIFIED',json.dumps(report))


if __name__=='__main__':main()
