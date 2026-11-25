"""Bounded one-character acquisition, original publisher credits plus pinned blobs."""
import hashlib,json
from html.parser import HTMLParser
from pathlib import Path
import requests
from acquire_rocketbox_candidate import destination_for,verified_payload,blob_hash
CONFIG=Path(__file__).with_name('unvanquished_human_source.json')
ROOT=Path('E:/CyberCity2085-3d-lab/sources/unvanquished_human')

class Rows(HTMLParser):
    def __init__(self):super().__init__();self.rows=[];self.row=None;self.cell=None
    def handle_starttag(self,tag,attrs):
        if tag=='tr':self.row=[]
        if tag in ('td','th') and self.row is not None:self.cell=[]
    def handle_data(self,data):
        if self.cell is not None:self.cell.append(data)
    def handle_endtag(self,tag):
        if tag in ('td','th') and self.cell is not None:
            self.row.append(' '.join(''.join(self.cell).split()));self.cell=None
        if tag=='tr' and self.row is not None:self.rows.append(self.row);self.row=None

def reviewed_credits(html):
    parser=Rows();parser.feed(html)
    selected={row[0]:row for row in parser.rows if len(row)>=3 and row[0] in {'Male','Light Armour','Medium Armour'} and row[-2]=='In game'}
    if set(selected)!={'Male','Light Armour','Medium Armour'}:raise ValueError('Exact player/armor publisher credits missing')
    for row in selected.values():
        if row[-1]!='CC BY-SA 3.0' or not any('Angelo' in value for value in row):raise ValueError('Reviewed author/license changed')
    return selected

def bounded_get(url,limit):
    chunks=[];size=0
    with requests.get(url,timeout=60,stream=True) as response:
        response.raise_for_status()
        for chunk in response.iter_content(65536):
            size+=len(chunk)
            if size>limit:raise ValueError('Reviewed size limit exceeded')
            chunks.append(chunk)
    return b''.join(chunks)

def acquire():
    cfg=json.loads(CONFIG.read_text());assert sum(f['size'] for f in cfg['files'])<64_000_000
    ROOT.mkdir(exist_ok=True)
    html=bounded_get(cfg['license_source'],1_000_000);credits=reviewed_credits(html.decode())
    (ROOT/'publisher_credits.html').write_bytes(html)
    legal=bounded_get('https://creativecommons.org/licenses/by-sa/3.0/legalcode.en',500_000)
    assert b'Attribution-ShareAlike' in legal
    (ROOT/'CC-BY-SA-3.0-legalcode.html').write_bytes(legal)
    report=[]
    for item in cfg['files']:
        target=destination_for(ROOT,item['path'],cfg['prefix']);target.parent.mkdir(parents=True,exist_ok=True)
        data=target.read_bytes() if target.exists() else b''
        url=f"https://raw.githubusercontent.com/{cfg['repository']}/{cfg['commit']}/{item['path']}"
        if len(data)!=item['size'] or blob_hash(data)!=item['git_blob']:
            data=verified_payload(bounded_get(url,item['size']),item);target.write_bytes(data)
        report.append({**item,'relative_path':str(target.relative_to(ROOT)),'sha256':hashlib.sha256(data).hexdigest(),'url':url})
        print('UNV_SOURCE_VERIFIED',target.name,len(data),flush=True)
    notice='Unvanquished Human Male / Light Armour / Medium Armour.\nAuthors: Angelo; armor texture touch-ups Stannum; medium armor texture variation Viech.\nCC BY-SA 3.0 https://creativecommons.org/licenses/by-sa/3.0/\nPublisher grant: '+cfg['license_source']+'\nPinned original files; no modifications at acquisition. Attribution and ShareAlike retained for derivatives; no production integration or relicensing performed.\n'
    (ROOT/'CREDITS.txt').write_text(notice,encoding='utf8')
    (ROOT/'acquisition.json').write_text(json.dumps({**cfg,'files':report,'publisher_credit_rows':credits,'bytes':sum(f['size'] for f in cfg['files']),'scope':'One authored game character for wardrobe qualification, no full library clone, no acquired IQE/helmet maps; originals untouched'},indent=2),encoding='utf8')
    print('UNV_LICENSED_CHARACTER_ACQUIRED',len(report),sum(f['size'] for f in report),flush=True)

if __name__=='__main__':acquire()
