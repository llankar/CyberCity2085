"""Acquire only five reviewed authored hair files and publisher pack metadata."""
import hashlib,json,struct,re,urllib.request
from pathlib import Path
from inspect_hair_archive import open_reviewed_archive,read_range,ROOT,URL,SIZE,ETAG
from acquire_rocketbox_candidate import destination_for

REVIEWED={
 'hair/elvs_maxwell_hair/maxwell_hair_mh.obj':(75902,3541364460),
 'hair/elvs_maxwell_hair/elvs_maxwell_hair.mhclo':(53045,3644700491),
 'hair/elvs_maxwell_hair/maxhairtex6.png':(644519,4287912679),
 'hair/elvs_maxwell_hair/maxwell_hair_mh.mhmat':(820,3719083673),
 'hair/elvs_maxwell_hair/elvs_maxwell_hair.thumb':(51251,1240801403),
 'packs/hair02.json':(12233,3684337749),
}

def qualify_grant(metadata,mhclo,obj,faq):
 entry=metadata.get('elvs_maxwell_hair',{})
 if entry.get('author')!='Elvaerwyn' or entry.get('license')!='CC-BY' or entry.get('original_author') or entry.get('original_source'):
  raise ValueError('Unreviewed author/grant/upstream source')
 for text in [mhclo,obj]:
  if not re.search(r'^#\s*author\s+Elvaerwyn\s*$',text,re.M) or not re.search(r'^#\s*license\s+CC_by\s*$',text,re.M):
   raise ValueError('Source header contradicts publisher grant')
 if 'creativecommons.org/licenses/by/4.0/' not in faq or 'CC-BY' not in faq:
  raise ValueError('Publisher licence label definition missing')
 return {'source_grant_label':'CC-BY / CC_by','documented_platform_license':'CC-BY-4.0','version_basis':'MakeHuman public CC-BY asset FAQ; source headers use short label only','author':'Elvaerwyn','asset':'elvs_maxwell_hair','attribution_required':True}

def qualify_acquired(root):
 url='https://static.makehumancommunity.org/oldsite/faq/what_do_i_need_to_do_when_i_use_a_ccby_asset.html'
 faq=root/'publisher_ccby_faq.html'
 if not faq.exists():
  with urllib.request.urlopen(url,timeout=30) as response:data=response.read(262145)
  if len(data)>=262144:raise ValueError('Publisher FAQ exceeded review bound')
  faq.write_bytes(data)
 grant=qualify_grant(json.loads((root/'publisher_pack_metadata.json').read_text()),(root/'elvs_maxwell_hair.mhclo').read_text(),(root/'maxwell_hair_mh.obj').read_text(),faq.read_text(encoding='utf8'))
 grant['faq_url']=url
 (root/'qualified_grant.json').write_text(json.dumps(grant,indent=2))
 (root/'CREDITS.txt').write_text('Maxwell Hair (elvs_maxwell_hair) by Elvaerwyn.\nSource headers grant CC_by; publisher asset pack lists CC-BY.\nMakeHuman CC-BY asset FAQ documents the label as CC BY4.0: '+url+'\nhttps://creativecommons.org/licenses/by/4.0/\nOriginal asset page: http://www.makehumancommunity.org/node/1639\nPublisher catalog: https://static.makehumancommunity.org/assets/assetpacks/hair02.html\nOriginal files preserved without modification. No author endorsement implied.\n',encoding='utf8')
 return grant

def acquire():
 root=Path('E:/CyberCity2085-3d-lab/sources/makehuman_maxwell_hair');root.mkdir(exist_ok=True)
 memory,archive=open_reviewed_archive();report=[]
 for name,(size,crc) in REVIEWED.items():
  info=archive.getinfo(name)
  if (info.file_size,info.CRC)!=(size,crc) or info.file_size>1024*1024:raise ValueError('Reviewed member changed')
  path=root/'publisher_pack_metadata.json' if name=='packs/hair02.json' else destination_for(root,name,'hair/elvs_maxwell_hair/')
  if path.exists() and len(path.read_bytes())==size:
   import zlib
   data=path.read_bytes()
   if zlib.crc32(data)!=crc:raise ValueError('Existing acquired file changed')
  else:
   header=read_range(info.header_offset,info.header_offset+29)
   if header[:4]!=b'PK\x03\x04':raise ValueError('Invalid selected local ZIP header')
   name_size,extra_size=struct.unpack_from('<HH',header,26)
   last=info.header_offset+30+name_size+extra_size+info.compress_size-1
   payload=read_range(info.header_offset,last)
   memory.seek(info.header_offset);memory.write(payload)
   data=archive.read(info) # standard ZIP CRC verification, not untrusted extraction
   if len(data)!=size:raise ValueError('Selected file length changed')
   path.write_bytes(data)
  report.append({'archive_member':name,'local_name':path.name,'bytes':len(data),'crc32':crc,'sha256':hashlib.sha256(data).hexdigest()})
 grant=qualify_acquired(root)
 evidence={'archive_url':URL,'archive_remote_bytes':SIZE,'archive_etag':ETAG,'whole_archive_downloaded':False,'files':report,'publisher_author':'Elvaerwyn','publisher_catalog_license':'CC-BY','qualified_grant':grant,'publisher_catalog':'https://static.makehumancommunity.org/assets/assetpacks/hair02.html'}
 (root/'acquisition.json').write_text(json.dumps(evidence,indent=2))
 print('MAXWELL_HAIR_SELECTIVE_ACQUIRED',sum(f['bytes'] for f in report),json.dumps(report),flush=True)

if __name__=='__main__':acquire()
