"""Download CC0 cafe props from Poly Haven with checksum verification."""
import json
import hashlib
import urllib.request
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
root=Path(__file__).resolve().parent/'assets'
headers={'User-Agent':'CoastalCityStudy/1.0 (Powered by Poly Haven)'}

def manifest(name):
    """Read a cached provider manifest or fetch it once."""
    path=root/(name+'.json')
    if not path.exists():
        request=urllib.request.Request('https://api.polyhaven.com/files/'+name,headers=headers)
        path.write_bytes(urllib.request.urlopen(request,timeout=45).read())
    return json.loads(path.read_text())

jobs=[]
for name in ['bar_chair_round_01','croissant','carrot_cake']:
    entry=manifest(name)['blend']['2k']['blend']
    jobs.append((root/name/(name+'.blend'),entry))
    jobs.extend((root/name/key,value) for key,value in entry.get('include',{}).items())

def download(item):
    """Fetch a file and reject data that does not match the provider checksum."""
    path,entry=item
    path.parent.mkdir(parents=True,exist_ok=True)
    expected=entry.get('md5')
    if path.exists() and (not expected or hashlib.md5(path.read_bytes()).hexdigest()==expected): return
    data=urllib.request.urlopen(urllib.request.Request(entry['url'],headers=headers),timeout=120).read()
    if expected and hashlib.md5(data).hexdigest()!=expected: raise ValueError('Checksum mismatch: '+path.name)
    path.write_bytes(data)
    print('DOWNLOADED',path.name,flush=True)

with ThreadPoolExecutor(max_workers=5) as executor: list(executor.map(download,jobs))
print('CAFE_ASSETS_COMPLETE',len(jobs),flush=True)
