"""Observable station delivery, no claim of complete map art or tactical combat."""
from pathlib import Path
from package_detail262 import comparison
from environment_library import LAB,ROOT

def main():
 out=LAB/'generated/phase2/metro264'
 comparison(ROOT/'assets/maps/city_transit_subway_platform.png',out/'top_down.png',out/'source_comparison.jpg')
 (out/'index.html').write_text('''<!doctype html><meta charset="utf-8"><title>CyberCity station detail</title>
<style>body{background:#07141b;color:#def;font:18px system-ui;max-width:1500px;margin:30px auto}img,video{width:100%;margin:15px 0}</style>
<h1>CyberCity // subway track and service columns</h1>
<p>Real-profile rails,96 sleepers and8 detailed service columns. Native scene, retained Rook scale reference. No interactive combat in this clip. Benches, terminals, walls and platform elevation remain unfinished.</p>
<video controls src="station_1080p30.mp4"></video>
<h2>Original / native top-down</h2><img src="source_comparison.jpg">
<h2>Agent scale</h2><img src="scale_agent.png"><img src="scale_close.png">
<p>Baseline metro250 preserved; production map and tactical rules unchanged.</p>''',encoding='utf8')
 print('STATION264_GALLERY_PACKAGED')

if __name__=='__main__':main()
