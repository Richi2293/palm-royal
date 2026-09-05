"""Improve the pedestrian camera and verify the expanded scene."""
from pathlib import Path
import bpy
from mathutils import Vector
output=Path(__file__).resolve().parent
SCENES=output/'scenes'
SCENES.mkdir(exist_ok=True)
RENDERS=output/'renders'
RENDERS.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(SCENES/'coastal-city.blend'))
scene=bpy.context.scene
camera=bpy.data.objects['02 - Walk Ocean Boulevard']
camera.location=(78,-28,2.1)
camera.rotation_euler=(Vector((-95,-24,9))-camera.location).to_track_quat('-Z','Y').to_euler()
# Save the reusable city with the overview active, then render the street camera.
bpy.ops.wm.save_as_mainfile(filepath=str(SCENES/'coastal-city.blend'))
scene.camera=camera
scene.render.resolution_x=1500
scene.render.resolution_y=1000
scene.render.filepath=str(RENDERS/'coastal-city-street.png')
bpy.ops.render.render(write_still=True)
print('VALIDATION', {'objects':len(scene.objects),'cameras':sum(obj.type=='CAMERA' for obj in scene.objects),'missing_external_images':[image.filepath for image in bpy.data.images if image.source=='FILE' and image.filepath and not image.packed_file and not Path(bpy.path.abspath(image.filepath)).exists()]})
