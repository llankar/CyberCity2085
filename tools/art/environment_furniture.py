"""Source-reviewed narrow furniture; no map names or tactical data are inferred."""
import math


def families(box, cylinder, parts, materials, material):
    material('cot_canvas', (.075,.105,.095), 0, .91)
    material('bedding_olive', (.10,.115,.06), 0, .88)
    material('pillow_linen', (.34,.31,.24), 0, .91)

    def single_bed():
        for x in [-.43,.43]:
            for y in [-.95,.95]:box('bed leg',(x,y,.17),(.065,.065,.34),'wood',.015)
        box('single frame',(0,0,.32),(1.0,2.16,.20),'wood',.035)
        box('single mattress',(0,0,.48),(.91,2.03,.20),'pillow_linen',.085)
        box('one pillow',(0,.68,.65),(.75,.47,.14),'pillow_linen',.095)
        box('olive blanket',(0,-.31,.615),(.94,1.35,.11),'bedding_olive',.06)
        for j in range(7):
            seam=box('blanket fold',(.025*math.sin(j),-.85+j*.18,.678),(.84,.014,.017),'cot_canvas',.006)
            seam.rotation_euler.z=.025*math.sin(j*2)
        for y in [-1.04,1.04]:box('low bed end',(0,y,.46),(1.01,.065,.36),'wood',.025)

    def field_cot():
        for x in [-.45,.45]:
            box('tubular side',(x,0,.44),(.055,2.22,.055),'steel',.024)
            for y in [-.86,.86]:box('cot leg',(x,y,.22),(.045,.045,.44),'steel',.02)
        for y in [-1.09,1.09]:box('end tube',(0,y,.44),(.94,.055,.055),'steel',.024)
        box('stretched canvas',(0,0,.435),(.84,2.12,.055),'cot_canvas',.025)
        box('worn blanket',(0,-.24,.51),(.83,1.52,.095),'fabric',.05)
        box('single pillow',(0,.77,.54),(.68,.40,.12),'pillow_linen',.08)
        for y in [-.84,-.57,-.30,-.03,.24]:box('stitched fold',(0,y,.565),(.75,.014,.012),'cot_canvas',.005)

    def transit_bench(seats=2):
        # Source benches have shallow metal seats, no thick upholstered base.
        width=seats*.70+.08
        for x in [-width*.36,width*.36]:
            box('bench leg',(x,0,.22),(.055,.62,.44),'steel',.015)
        box('cross member',(0,0,.31),(width-.12,.055,.065),'metal',.012)
        for i in range(seats):
            x=(i-(seats-1)/2)*.70
            box('formed metal seat',(x,-.055,.45),(.66,.65,.045),'paint',.025)
            box('shallow back',(x,.30,.59),(.66,.045,.26),'paint',.022)
            for z in [.53,.58,.63]:box('back perforation',(x,.272,z),(.54,.008,.012),'rubber',.003)
        for x in [-width/2,width/2]:
            box('end arm',(x,-.02,.60),(.035,.73,.035),'steel',.015)
            box('arm post',(x,-.335,.52),(.035,.035,.16),'steel',.013)

    return {'single_bed':single_bed,'field_cot':field_cot,
            'transit_bench2':transit_bench,'transit_bench4':lambda:transit_bench(4)}


FURNITURE_METADATA = {
    'single_bed':{'sleepers':1,'pillows':1,'base':'individual bed legs'},
    'field_cot':{'sleepers':1,'pillows':1,'base':'open tubular frame'},
    'transit_bench2':{'seats':2,'material':'formed metal','base':'two legs'},
    'transit_bench4':{'seats':4,'material':'formed metal','base':'two legs'},
}
