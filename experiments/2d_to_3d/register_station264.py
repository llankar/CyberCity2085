"""Register standalone station family without duplicating bulky Blender sources."""
import json,hashlib
from environment_library import LAB,ROOT

def main():
 library=LAB/'environment-library/library.json';data=json.loads(library.read_text(encoding='utf8'))
 folder=LAB/'generated/phase2/metro264'
 asset=json.loads((folder/'service_column.json').read_text())
 asset.update(family='Transit',artistic_status='NATIVE_REVIEWED_PROTOTYPE',authentic_views=1,generated_views=0)
 source=ROOT/'assets/maps/city_transit_subway_platform.png'
 asset['source_sha256']=hashlib.sha256(source.read_bytes()).hexdigest()
 asset['glb_sha256']=hashlib.sha256((folder/'service_column.glb').read_bytes()).hexdigest()
 asset['used_in']=[{'map':'city_transit_subway_platform','scene':str(folder/'environment.glb'),'instances':8}]
 data['assets']=[a for a in data['assets'] if a['id']!=asset['id']]+[asset]
 library.write_text(json.dumps(data,indent=2),encoding='utf8')
 print('STATION264_LIBRARY_REGISTERED',asset['id'])

if __name__=='__main__':main()
