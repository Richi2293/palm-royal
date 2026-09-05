"""Download CC0 cafe props from Poly Haven with checksum verification."""
import json
import hashlib
import urllib.request
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
root=Path(__file__).resolve().parent/'assets'
headers={'User-Agent':'CoastalCityStudy/1.0 (Powered by Poly Haven)'}
jobs=[]
for name in ['bar_chair_round_01','croissant','carrot_cake']:
    request=urllib.request.Request('https://api.polyhaven.com/files/'+name,headers=headers)
    manifest=json.load(urllib.request.urlopen(request,timeout=45))
    (root/(name+'.json')).write_text(json.dumps(manifest))
    entry=manifest['blend']['2k']['blend']
    jobs.append((root/name/(name+'.blend'),entry))
    jobs.extend((root/name/key,value) for key,value in entry.get('include',{}).items())
def download(item):
    """Fetch a file and reject data that does not match the provider checksum."""
    path,entry=item
    path.parent.mkdir(parents=True,exist_ok=True)
    data=urllib.request.urlopen(urllib.request.Request(entry['url'],headers=headers),timeout=120).read()
    if hashlib.md5(data).hexdigest()!=entry['md5']: raise ValueError('Checksum mismatch: '+path.name)
    path.write_bytes(data)
    print(path.name,flush=True)
with ThreadPoolExecutor(max_workers=5) as executor: list(executor.map(download,jobs))
print('CAFE_ASSETS_COMPLETE',flush=True)
