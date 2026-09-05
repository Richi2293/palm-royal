"""Export the coastal city to a compressed glTF binary for the web viewer.

The city is built from linked duplicates: 11928 objects share 1090 unique
meshes. Exporting with GPU instancing keeps only the unique geometry in the
file and stores the repeated objects as instance transforms, which is what
makes the result small enough to load in a browser.

Run with Blender in background mode:
    blender --background --factory-startup --python viewer/export_web.py
"""
import bpy
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCENES = ROOT / 'scenes'
SOURCE = SCENES / 'coastal-city.blend'
TARGET = ROOT / 'viewer' / 'city.glb'

bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
scene = bpy.context.scene

# Lighting and framing are handled by the viewer, so only geometry is exported.
for obj in list(scene.objects):
    if obj.type in {'LIGHT', 'CAMERA'}:
        bpy.data.objects.remove(obj, do_unlink=True)

bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.gltf(
    filepath=str(TARGET),
    export_format='GLB',
    export_apply=True,
    export_yup=True,
    export_gpu_instances=True,
    export_draco_mesh_compression_enable=True,
    export_draco_mesh_compression_level=6,
    export_cameras=False,
    export_lights=False,
    export_animations=False,
    export_extras=False,
)

size_mb = TARGET.stat().st_size / 1024 / 1024
print(f'EXPORTED {TARGET.name} {size_mb:.1f} MB from {len(scene.objects)} objects')
