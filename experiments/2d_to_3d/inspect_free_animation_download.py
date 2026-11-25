"""Inspect the author's normal zero-price download flow; do not fetch paid files."""
import http.cookiejar
import json
import re
import sys
import hashlib
import zipfile
import urllib.parse
import urllib.request
from pathlib import Path

root=Path('E:/CyberCity2085-3d-lab/sources/asset_pages')
url='https://quaternius.itch.io/universal-animation-library'
opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
page=opener.open(url).read().decode()
assert '"min_price":0' in page and 'CC0' in page
token=re.search(r'<meta[^>]+name="csrf_token"[^>]+content="([^"]+)"',page)
body=urllib.parse.urlencode({'csrf_token':token.group(1)} if token else {}).encode()
request=urllib.request.Request(url+'/download_url',data=body,headers={'Referer':url,'Accept':'application/json'})
response=json.load(opener.open(request))
download_page=opener.open(response['url']).read().decode()
(root/'universal_animation_free_download.html').write_text(download_page,encoding='utf-8')
# Print only bounded public file metadata, not session/download tokens.
uploads=re.findall(r'data-upload_id="(\d+)"',download_page)
names=re.findall(r'<span[^>]+class="name"[^>]*>(.*?)</span>',download_page)
print(json.dumps({'uploads':uploads,'names':[re.sub('<[^>]+>','',name) for name in names]},indent=2))
if '--download' in sys.argv:
    assert uploads==['17958403'] and 'Universal Animation Library[Standard].zip' in download_page
    token=re.search(r'<meta[^>]+name="csrf_token"[^>]+content="([^"]+)"',download_page)
    body=urllib.parse.urlencode({'csrf_token':token.group(1)} if token else {}).encode()
    request=urllib.request.Request(url+'/file/'+uploads[0],data=body,
                                   headers={'Referer':response['url'],'Accept':'application/json','X-Requested-With':'XMLHttpRequest'})
    file_response=json.load(opener.open(request))
    target=Path('E:/CyberCity2085-3d-lab/downloads/quaternius_universal_animation_standard.zip')
    temporary=target.with_suffix('.part')
    size=0
    with opener.open(file_response['url']) as remote,temporary.open('wb') as output:
        while chunk:=remote.read(1024*1024):
            size+=len(chunk)
            if size>40*1024*1024: raise ValueError('Unexpectedly large free animation package')
            output.write(chunk)
    with zipfile.ZipFile(temporary) as archive:
        assert archive.testzip() is None
        members=archive.namelist()
    temporary.replace(target)
    provenance={'author':'Quaternius','source':url,'upload_id':uploads[0],
                'license':'CC0','license_source':'https://quaternius.com/packs/universalanimationlibrary.html',
                'bytes':size,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'members':members}
    target.with_suffix('.provenance.json').write_text(json.dumps(provenance,indent=2),encoding='utf-8')
    print('FREE_ANIMATION_ZIP_ACQUIRED',size,len(members),provenance['sha256'])
