"""Acquire one author's explicitly free character through the normal itch flow."""
import hashlib
import http.cookiejar
import json
from pathlib import Path
import struct
import urllib.parse
import urllib.request
from bs4 import BeautifulSoup

BASE='https://theunseenvulga.itch.io/3d-charater-riggeddiesel'
ROOT=Path('E:/CyberCity2085-3d-lab/sources/diesel_character')
UPLOAD='19450576'


def checked_glb(data):
    if len(data)<28 or struct.unpack_from('<III',data)!=(0x46546c67,2,len(data)):
        raise ValueError('Expected a complete GLB2 asset, not a landing page')
    return hashlib.sha256(data).hexdigest()


def read_bounded(opener,request,limit):
    with opener.open(request,timeout=45) as response:
        data=response.read(limit+1)
    if len(data)>limit:raise ValueError('Reviewed download size bound exceeded')
    return data


def main():
    ROOT.mkdir(exist_ok=True)
    existing=ROOT/'Diesel.glb'
    if existing.exists():
        print('DIESEL_EXISTING_GLB',checked_glb(existing.read_bytes()))
        return
    opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
    page=read_bounded(opener,BASE,262144)
    soup=BeautifulSoup(page,'html.parser')
    text=soup.get_text(' ',strip=True)
    assert 'CC0' in text and 'Modify and customize' in text and 'commercial projects' in text
    (ROOT/'publisher.html').write_bytes(page)
    purchase=read_bounded(opener,BASE+'/purchase',262144)
    soup=BeautifulSoup(purchase,'html.parser')
    assert soup.select_one('a.direct_download_btn') is not None
    csrf=soup.find('meta',attrs={'name':'csrf_token'})['value']
    def post(url,token):
        request=urllib.request.Request(url,data=urllib.parse.urlencode({'csrf_token':token}).encode(),headers={'Referer':BASE+'/purchase','X-Requested-With':'XMLHttpRequest'})
        result=json.loads(read_bounded(opener,request,262144))
        if result.get('errors') or result.get('lightbox_type')=='QuarantineLightbox':
            raise RuntimeError('Publisher denied or quarantined download; no bypass')
        return result
    free=post(BASE+'/download_url',csrf)
    assert free.get('url','').startswith(BASE+'/download/')
    download=read_bounded(opener,free['url'],262144)
    soup=BeautifulSoup(download,'html.parser')
    button=soup.find('a',attrs={'data-upload_id':UPLOAD})
    assert button is not None and 'Diesel.glb' in soup.get_text()
    csrf=soup.find('meta',attrs={'name':'csrf_token'})['value']
    result=post(BASE+'/file/'+UPLOAD+'?source=game_download&after_download_lightbox=1&as_props=1',csrf)
    assert result.get('url','').startswith('https://')
    payload=read_bounded(opener,result['url'],15_000_000)
    digest=checked_glb(payload)
    existing.write_bytes(payload)
    (ROOT/'provenance.json').write_text(json.dumps({'author':'THEUNSEENVULGA','asset':'Diesel','publisher':BASE,'license_label':'CC0','explicit_permissions':['personal and commercial projects','modify and customize','no attribution required'],'publisher_request':'Do not resell unmodified assets as-is or claim authorship','format':'GLB','upload_id':UPLOAD,'bytes':len(payload),'sha256':digest,'acquisition':'Normal public zero-price direct-download action and published file button, anonymous session; no account, purchase, quarantine bypass or protected endpoint workaround'},indent=2))
    (ROOT/'CREDITS.txt').write_text('Diesel by THEUNSEENVULGA.\n'+BASE+'\nPublisher explicitly grants CC0 personal/commercial use and modification; asks not to resell unmodified assets or claim authorship.\nOriginal GLB preserved. No endorsement implied.\n',encoding='utf8')
    print('DIESEL_FREE_CHARACTER_ACQUIRED',len(payload),digest)


if __name__=='__main__':main()
