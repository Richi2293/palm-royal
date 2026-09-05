"""Download credited open assets and verify every file against its manifest."""
import hashlib
import json
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
ROOT=Path(__file__).resolve().parent/'assets'
HEADERS={'User-Agent':'CoastalCityStudy/1.0 (Powered by Poly Haven)'}

def fetch_json(name):
    """Read a cached provider manifest or fetch it once."""
    path=ROOT/(name+'.json')
    if not path.exists():
        request=urllib.request.Request('https://api.polyhaven.com/files/'+name,headers=HEADERS)
        path.write_bytes(urllib.request.urlopen(request,timeout=60).read())
    return json.loads(path.read_text(encoding='utf-8'))

def download(item):
    """Download one resource and validate the provider checksum when available."""
    path,details=item
    path.parent.mkdir(parents=True,exist_ok=True)
    expected=details.get('md5')
    if path.exists() and (not expected or hashlib.md5(path.read_bytes()).hexdigest()==expected): return
    request=urllib.request.Request(details['url'],headers=HEADERS)
    payload=urllib.request.urlopen(request,timeout=120).read()
    if expected and hashlib.md5(payload).hexdigest()!=expected: raise ValueError('Checksum mismatch: '+str(path))
    path.write_bytes(payload)
    print('DOWNLOADED',path.name,len(payload),flush=True)

jobs=[]
models={'island_tree_01':'1k','outdoor_table_chair_set_01':'1k','fire_hydrant':'2k','exterior_aircon_unit':'1k','water_manhole_cover':'2k','painted_wooden_bench':'2k','potted_plant_02':'2k','street_lamp_01':'2k'}
for name,resolution in models.items():
    data=fetch_json(name)['blend'][resolution]['blend']
    jobs.append((ROOT/name/(name+'.blend'),data))
    for relative,entry in data.get('include',{}).items(): jobs.append((ROOT/name/relative,entry))
textures={'asphalt_02':'4k','red_plaster_weathered':'4k','concrete_pavement':'2k','palm_bark':'2k','white_plaster_rough_02':'2k','blue_plaster_weathered':'2k','brown_brick_02':'2k'}
for name,resolution in textures.items():
    data=fetch_json(name)
    for channel in ['Diffuse','nor_gl','Rough','Displacement']:
        if channel in data:
            formats=data[channel][resolution]
            entry=formats.get('jpg') or formats.get('png') or formats.get('exr')
            jobs.append((ROOT/name/Path(entry['url']).name,entry))
hdri=fetch_json('venice_sunset')['hdri']['2k']['hdr']
jobs.append((ROOT/'venice_sunset.hdr',hdri))
base='https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Assets/main/Models/CarConcept/'
for relative in ['GLB/CarConcept.glb','LICENSE.md','README.md']:
    jobs.append((ROOT/'CarConcept'/Path(relative).name,{'url':base+relative}))
with ThreadPoolExecutor(max_workers=6) as executor:
    list(executor.map(download,jobs))
(ROOT/'download-manifest.json').write_text(json.dumps({'models':models,'textures':textures,'files':[str(path.relative_to(ROOT)) for path,_ in jobs]},indent=2),encoding='utf-8')
print('ASSETS_COMPLETE',len(jobs),flush=True)
