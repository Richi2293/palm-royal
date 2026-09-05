"""Prepare a free street-level viewport while retaining the render cameras."""
from pathlib import Path
import bpy
from mathutils import Vector
root=Path(__file__).resolve().parent
SCENES=root/'scenes'
SCENES.mkdir(exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(SCENES/'detailed-before-navigation.blend'))
bpy.ops.wm.open_mainfile(filepath=str(SCENES/'coastal-city-detailed.blend'))
eye=Vector((54,-26,1.8))
target=Vector((32,-14,3.4))
rotation=(target-eye).to_track_quat('-Z','Y')
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            space=area.spaces.active
            space.lens=26
            space.clip_start=.05
            space.clip_end=1500
            space.lock_camera=False
            space.region_3d.view_rotation=rotation
            space.region_3d.view_distance=12
            space.region_3d.view_location=eye+rotation@Vector((0,0,-12))
            space.region_3d.view_perspective='PERSP'
            space.overlay.show_overlays=False
bpy.context.workspace.name='City Walk'
bpy.ops.wm.save_as_mainfile(filepath=str(SCENES/'coastal-city-detailed.blend'))
