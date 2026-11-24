"""Native geometric regression gate for source-surface attachment recovery."""
import sys
from pathlib import Path
import numpy as np
from mathutils import Matrix, Vector

sys.path.insert(0,str(Path(__file__).parent))
from rigid_surface_fit import fit_surface

points=np.asarray([(0,0,0),(1,0,0),(0,1,0),(0,0,1),(.2,.7,.9)],dtype=float)
wanted=Matrix.Translation((.3,-.5,1.7)) @ Matrix.Rotation(.7,4,'Y')
current=[tuple(wanted @ Vector(p)) for p in points]
fitted,error=fit_surface(points,current)
assert error<1e-6
assert max((fitted @ Vector(p)-Vector(q)).length for p,q in zip(points,current))<1e-6
changed=np.asarray(current); changed[-1]+=(.2,.1,-.3)
_,error=fit_surface(points,changed)
assert error>.05
planar=points[:3]
_,error=fit_surface(planar,[tuple(wanted @ Vector(p)) for p in planar])
assert error<1e-6
for bad in [np.zeros((2,3)),np.full((5,3),float('nan'))]:
    try: fit_surface(points,bad)
    except ValueError: pass
    else: raise AssertionError('Invalid source correspondence accepted')
print('RIGID_SURFACE_FIT_TEST_OK rotation_translation,deformation_residual,planar,invalid_inputs',flush=True)
