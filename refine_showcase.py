"""Remove legacy foliage from the showcase and improve its close compositions."""
import ast
import math
from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parent
SCENES=ROOT/'scenes'
RENDERS=ROOT/'renders'
for filename in ['build_world.py','build_city.py']:
    for node in ast.parse((ROOT/filename).read_text()).body:
        if isinstance(node,ast.FunctionDef) and node.name in ['material','collection','box','rod']:
            exec(compile(ast.Module(body=[node],type_ignores=[]),filename,'exec'))
bpy.ops.wm.open_mainfile(filepath=str(SCENES/'coastal-city-detailed.blend'))
scene=bpy.context.scene
CURRENT_GROUP='Showcase - Cafe tabletop details'
MESH_CACHE={}
removed=0
for obj in list(scene.objects):
    if not obj.name.startswith(('Palm frond','Segmented palm trunk','Palm planter')): continue
    if obj.type!='MESH': continue
    points=[obj.matrix_world@Vector(corner) for corner in obj.bound_box]
    center=sum(points,Vector())/8
    if -6<center.x<88 and -65<center.y<33:
        bpy.data.objects.remove(obj,do_unlink=True)
        removed+=1
ceramic=material('Glazed ivory porcelain',(.84,.79,.66),roughness=.18)
coffee=material('Dark espresso crema',(.07,.026,.008),roughness=.25)
wax=material('Amber table candle',(.95,.42,.08),roughness=.3,emission=1.5)

def lathe(name,x,y,z,profile,surface):
    """Create a smooth rotational vessel from a radius-height profile."""
    count=32
    vertices=[(x+r*math.cos(i*math.tau/count),y+r*math.sin(i*math.tau/count),z+h) for r,h in profile for i in range(count)]
    faces=[]
    for ring in range(len(profile)-1):
        for i in range(count):
            a=ring*count+i
            b=ring*count+(i+1)%count
            faces.append((a,b,b+count,a+count))
    mesh=bpy.data.meshes.new(name)
    mesh.from_pydata(vertices,[],faces)
    mesh.materials.append(surface)
    obj=bpy.data.objects.new(name,mesh)
    collection(CURRENT_GROUP).objects.link(obj)
    for face in mesh.polygons: face.use_smooth=True
for x in [11.5,17,22.5]:
    for dx in [-.16,.16]:
        lathe('Porcelain saucer',x+dx,-16.5,1.235,[(0,0),(.09,.002),(.105,.018),(.10,.024),(.07,.012),(0,.01)],ceramic)
        lathe('Espresso cup',x+dx,-16.5,1.25,[(.025,0),(.037,.02),(.05,.075),(.045,.079),(.032,.02)],ceramic)
        rod('Espresso surface',(x+dx,-16.5,1.315),(x+dx,-16.5,1.316),.042,coffee,32)
    lathe('Table candle',x,-16.25,1.23,[(0,0),(.05,0),(.05,.13),(.045,.135),(0,.135)],wax)
hero=bpy.data.objects['06 - Detailed Palm Royal block']
hero.location=(58,-33,5)
hero.rotation_euler=(Vector((31,-12,8))-hero.location).to_track_quat('-Z','Y').to_euler()
hero.data.lens=25
scene.camera=hero
scene.render.resolution_x=1800
scene.render.resolution_y=1250
scene.render.filepath=str(RENDERS/'showcase-hero.png')
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(SCENES/'coastal-city-detailed.blend'))
print('CLEANUP',removed,flush=True)
bpy.ops.render.render(write_still=True)
scene.camera=bpy.data.objects['07 - Cafe materials and street props']
scene.render.filepath=str(RENDERS/'showcase-closeup.png')
scene.render.resolution_x=1600
scene.render.resolution_y=1100
bpy.ops.render.render(write_still=True)
missing=[image.filepath for image in bpy.data.images if image.source=='FILE' and image.filepath and not image.packed_file and not Path(bpy.path.abspath(image.filepath)).exists()]
print('VALIDATION',{'objects':len(scene.objects),'packed_images':sum(bool(image.packed_file) for image in bpy.data.images),'missing_images':missing},flush=True)
