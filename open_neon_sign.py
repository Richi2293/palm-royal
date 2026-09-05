"""Open the renovated city and position its free viewport inside the cafe."""
from pathlib import Path
import bpy
from mathutils import Vector
root=Path(__file__).resolve().parent
if bpy.app.background:
    raise SystemExit(
        'open_neon_sign.py backs up the current session before switching scenes, which only '
        'makes sense in an interactive Blender. In background mode that backup '
        'would be an empty startup scene, overwriting a real one. Open Blender '
        'and run this from the Scripting workspace instead.'
    )
bpy.ops.wm.save_as_mainfile(filepath=str(root/'interiors-before-neon.blend'))
bpy.ops.wm.open_mainfile(filepath=str(root/'coastal-city-neon.blend'))
camera=bpy.data.objects['07 - Cafe materials and street props']
rotation=camera.rotation_euler.to_quaternion()
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            space=area.spaces.active
            space.lens=25
            space.lock_camera=False
            space.region_3d.view_rotation=rotation
            space.region_3d.view_distance=8
            space.region_3d.view_location=camera.location+rotation@Vector((0,0,-8))
            space.region_3d.view_perspective='PERSP'
            space.shading.type='MATERIAL'
            space.shading.use_scene_lights=True
            space.shading.use_scene_world=True
            space.show_gizmo=False
            space.overlay.show_overlays=False
bpy.ops.wm.save_as_mainfile(filepath=str(root/'coastal-city-neon.blend'))
