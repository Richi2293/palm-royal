"""Finalize the framing and use the HDR environment only for lighting and reflections."""
from pathlib import Path
import bpy
from mathutils import Vector
root=Path(__file__).resolve().parent
SCENES=root/'scenes'
RENDERS=root/'renders'
bpy.ops.wm.open_mainfile(filepath=str(SCENES/'coastal-city-detailed.blend'))
scene=bpy.context.scene
camera=bpy.data.objects['06 - Detailed Palm Royal block']
camera.rotation_euler=(Vector((31,-12,10))-camera.location).to_track_quat('-Z','Y').to_euler()
camera.data.lens=23
nodes=scene.world.node_tree.nodes
links=scene.world.node_tree.links
background=nodes.get('Background')
output=nodes.get('World Output')
path=nodes.new('ShaderNodeLightPath')
sky=nodes.new('ShaderNodeBackground')
sky.name='Clean coastal sky for camera rays'
sky.inputs['Color'].default_value=(.23,.34,.52,1)
sky.inputs['Strength'].default_value=.6
mix=nodes.new('ShaderNodeMixShader')
links.new(path.outputs['Is Camera Ray'],mix.inputs[0])
links.new(background.outputs[0],mix.inputs[1])
links.new(sky.outputs[0],mix.inputs[2])
links.new(mix.outputs[0],output.inputs['Surface'])
scene.camera=camera
scene.render.filepath=str(RENDERS/'showcase-hero.png')
bpy.ops.wm.save_as_mainfile(filepath=str(SCENES/'coastal-city-detailed.blend'))
bpy.ops.render.render(write_still=True)
scene.camera=bpy.data.objects['07 - Cafe materials and street props']
scene.render.resolution_x=1600
scene.render.resolution_y=1100
scene.render.filepath=str(RENDERS/'showcase-closeup.png')
bpy.ops.render.render(write_still=True)
print('FINAL_SHOWCASE_COMPLETE',flush=True)
