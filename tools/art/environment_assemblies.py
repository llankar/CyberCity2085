"""Authored multi-part prop families, independent of maps and collisions."""
import math
from mathutils import Vector


def families(box, cylinder, parts, materials, material):
    if 'seat_blue' not in materials:
        material('seat_blue', (.018,.085,.16), .68, .42)
        material('ceramic', (.045,.033,.027), .10, .27)
        material('deadwood', (.105,.068,.032), 0, .94)

    def beam(name, a, b, radius, mat):
        a,b=Vector(a),Vector(b)
        obj=cylinder(name,(a+b)/2,radius,(b-a).length,mat)
        obj.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler()

    def insulator_array(columns=3):
        # A real open grid and six individual ceramic columns, not a solid slab.
        for x in [-1.5,1.5]:box('perimeter rail',(x,0,.12),(.075,2.9,.11),'steel',.015)
        for y in [-1.45,1.45]:box('end rail',(0,y,.12),(3.0,.075,.11),'steel',.015)
        for i in range(-10,11):box('grating bar',(i*.14,0,.09),(.018,2.86,.025),'metal',.005)
        for i in range(-9,10):box('cross grating',(0,i*.15,.095),(2.94,.018,.025),'metal',.005)
        for y in [-.70,.70]:
            for x in ([-.94,0,.94] if columns==3 else [-.70,.70]):
                box('column base',(x,y,.18),(.46,.46,.12),'metal',.025)
                cylinder('ceramic core',(x,y,.93),.12,1.40,'ceramic')
                for level in range(11):cylinder('ceramic shed',(x,y,.36+level*.11),.21-level*.006,.045,'ceramic')
                cylinder('terminal',(x,y,1.66),.07,.15,'steel')
                beam('bus connection',(x,y,.24),(x,y+.22,.28),.035,'steel')
        for x in [-1.45,1.45]:
            for y in [-1.38,1.38]:cylinder('standoff',(x,y,.045),.06,.09,'steel')

    def metal_bench():
        for x in [-.72,.72]:
            box('front foot',(x,-.20,.19),(.065,.08,.38),'steel',.012)
            box('back support',(x,.20,.37),(.065,.065,.73),'steel',.012)
        box('under-seat beam',(0,0,.28),(1.73,.055,.075),'metal',.014)
        for x in [-.45,.45]:
            box('blue seat',(x,-.04,.42),(.84,.48,.085),'seat_blue',.045)
            back=box('blue backrest',(x,.21,.64),(.84,.055,.36),'seat_blue',.035)
            back.rotation_euler.x=-.08
            for z in [.56,.65,.73]:box('seat rib',(x,.174,z),(.72,.008,.012),'metal',.003)
        for x in [-.89,0,.89]:
            box('armrest',(x,-.01,.63),(.045,.46,.045),'steel',.018)
            box('armrest support',(x,-.18,.52),(.04,.04,.20),'metal',.01)

    def metal_bench_pair():
        metal_bench()
        first=list(parts)
        for obj in first:obj.location.x-=.96
        start=len(parts);metal_bench()
        for obj in parts[start:]:obj.location.x+=.96

    def dry_planter():
        for x in [-.70,.70]:box('planter side',(x,0,.30),(.13,1.48,.55),'concrete',.06)
        for y in [-.68,.68]:box('planter end',(0,y,.30),(1.36,.13,.55),'concrete',.06)
        box('dry soil',(0,0,.35),(1.26,1.21,.08),'deadwood',.03)
        for i in range(5):
            x=math.sin(i*7.1)*.43;y=math.cos(i*5.7)*.40
            tip=(x+.11*math.sin(i),y+.13*math.cos(i),.96+i%2*.17)
            beam('bare trunk',(x,y,.39),tip,.027,'deadwood')
            for j in range(3):
                angle=i*1.4+j*2.1
                branch=(tip[0]+.24*math.cos(angle),tip[1]+.23*math.sin(angle),tip[2]+.05)
                beam('dead branch',(tip[0],tip[1],tip[2]-.24),branch,.012,'deadwood')

    def server_bank():
        for i in range(6):
            x=(i-2.5)*.66
            box('individual rack',(x,0,1.16),(.62,.90,2.20),'metal',.025)
            for z in [.26+j*.17 for j in range(11)]:
                box('blade',(x,-.465,z),(.53,.04,.13),'steel',.012)
                for dx in [-.15,-.05,.05]:box('blade vent',(x+dx,-.49,z),(.045,.008,.065),'rubber',.002)
                box('rack LED',(x+.21,-.495,z),(.025,.008,.055),'cyan',.002)
            for dx in [-.24,.24]:box('cabinet foot',(x+dx,0,.035),(.07,.65,.07),'steel',.01)

    return {'insulator_array6':insulator_array,'insulator_array4':lambda:insulator_array(2),'metal_bench2':metal_bench,
            'metal_bench_pair':metal_bench_pair,'dry_planter':dry_planter,'server_bank6':server_bank}


CAMERA_ELEVATION = {'server_bank6':55}
ASSEMBLY_METADATA = {
    'insulator_array6':{'columns':3,'rows':2,'count':6,'base':'open metal grating'},
    'insulator_array4':{'columns':2,'rows':2,'count':4,'base':'open metal grating'},
    'server_bank6':{'racks':6,'continuous_roof':False},
    'metal_bench2':{'seats':2,'material':'blue metal'},
    'metal_bench_pair':{'modules':2,'seats':4,'material':'blue metal'},
    'dry_planter':{'vegetation':'dead branches','base':'hollow concrete frame'},
}
