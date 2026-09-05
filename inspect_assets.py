"""Inspect source asset geometry without executing embedded scripts."""
from pathlib import Path
import bpy
from mathutils import Vector
root=Path(__file__).resolve().parent/'assets'
for path in root.glob('*/*.blend'):
    with bpy.data.libraries.load(str(path),link=False) as (source,destination):
        print('LIBRARY',path.parent.name,'COLLECTIONS',source.collections)
        destination.objects=source.objects
    for obj in destination.objects:
        if obj is not None and obj.type=='MESH':
            coords=[obj.matrix_world@Vector(point) for point in obj.bound_box]
            lo=[min(p[i] for p in coords) for i in range(3)]
            hi=[max(p[i] for p in coords) for i in range(3)]
            print('MESH',obj.name,'vertices',len(obj.data.vertices),'bounds',lo,hi)
if (root/'CarConcept/CarConcept.glb').exists():
    bpy.ops.import_scene.gltf(filepath=str(root/'CarConcept/CarConcept.glb'))
    print('CAR',[(obj.name,tuple(obj.dimensions)) for obj in bpy.context.selected_objects if obj.type=='MESH'][:30])
