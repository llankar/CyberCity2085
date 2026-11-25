"""Report measured contact quality honestly, independently of export fidelity."""
import hashlib,json
from pathlib import Path

def assess(report, limit=.005):
    result={}
    for clip,data in report['clips'].items():
        support=data['maximum_lowest_sole_height_m']<=limit
        drift=max(m['maximum_individual_contact_vertex_drift_m'] for m in data['metrics'].values())
        result[clip]={'support':'PASS' if support else 'FAIL','individual_contact_drift':'PASS' if drift<=limit else 'FAIL',
                      'maximum_individual_contact_vertex_drift_m':drift,'limit_m':limit,
                      'maximum_lowest_sole_height_m':data['maximum_lowest_sole_height_m']}
    return result

def main():
    root=Path('E:/CyberCity2085-3d-lab/generated/phase2')
    folder=root/'foot_contact161'
    source=json.loads((folder/'source_sole_contact.json').read_text())
    candidate=json.loads((folder/'candidate_sole_contact.json').read_text())
    for report,path in [(source,root/'cover_transitions160/human.blend'),(candidate,folder/'human.blend')]:
        assert report['blend_sha256']==hashlib.sha256(path.read_bytes()).hexdigest()
        assert set(report['clips'])=={'CoverEnterStudy','CoverExitStudy'}
        assert all(len(c['samples'])==73 for c in report['clips'].values())
    result={'source':assess(source),'candidate':assess(candidate),
            'scope':'Actual Blender fixed sole vertices at120Hz; 5mm point-contact test, not full artistic or native per-vertex contact acceptance'}
    (folder/'contact_assessment.json').write_text(json.dumps(result,indent=2))
    passed=all(c['support']=='PASS' and c['individual_contact_drift']=='PASS' for c in result['candidate'].values())
    print('FOOT161_CONTACT_QUALITY', 'PASS' if passed else 'FAIL', json.dumps(result['candidate']))
    return 0 if passed else 2

if __name__=='__main__':raise SystemExit(main())
