"""Build an original tropical street diorama using Blender's Python API."""
import math
import random
from pathlib import Path
import bpy
from mathutils import Vector

OUTPUT = Path(__file__).resolve().parent
SCENES = OUTPUT / 'scenes'
SCENES.mkdir(exist_ok=True)
RENDERS = OUTPUT / 'renders'
RENDERS.mkdir(exist_ok=True)
random.seed(18)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, metallic=0.0, roughness=0.5, emission=0.0):
    """Create a reusable physically based surface material."""
    result = bpy.data.materials.new(name)
    result.diffuse_color = (*color, 1)
    result.use_nodes = True
    shader = result.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value = (*color, 1)
    shader.inputs['Metallic'].default_value = metallic
    shader.inputs['Roughness'].default_value = roughness
    if emission:
        shader.inputs['Emission Color'].default_value = (*color, 1)
        shader.inputs['Emission Strength'].default_value = emission
    return result

coral = material('Sun-faded coral stucco', (.62,.21,.24))
teal = material('Seafoam painted plaster', (.17,.53,.47))
cream = material('Warm ivory architectural trim', (.86,.77,.58))
pink = material('Neon flamingo pink', (1,.035,.23), emission=5)
cyan = material('Neon lagoon cyan', (.04,.8,1), emission=4)
yellow = material('Warm interior lighting', (1,.51,.16), emission=2)
road = material('Asphalt', (.045,.055,.075), roughness=.82)
concrete = material('Pale sidewalk concrete', (.43,.42,.39), roughness=.85)
white = material('Road paint', (.85,.81,.63))
line = material('Double yellow road paint', (.95,.57,.06))
glass = material('Smoked blue glass', (.025,.105,.15), metallic=.5, roughness=.17)
metal = material('Dark bronze metal', (.07,.085,.10), metallic=.7)
wood = material('Palm bark and timber', (.24,.115,.065))
leaf = material('Palm frond green', (.085,.29,.095), roughness=.75)
sand = material('Fine golden sand', (.68,.50,.29))
water = material('Lagoon water', (.025,.29,.34), metallic=.45, roughness=.2)
purple = material('Midnight plum base', (.075,.045,.105))
red = material('Sports car vermilion', (.72,.045,.025), metallic=.55, roughness=.22)
rubber = material('Tire rubber', (.015,.017,.021), roughness=.9)

# Fine procedural bump keeps the larger surfaces from looking perfectly smooth.
for surface, scale, strength in [(road,95,.22),(sand,130,.15),(coral,45,.12),(teal,45,.12)]:
    nodes = surface.node_tree.nodes
    noise = nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = scale
    bump = nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = strength
    bump.inputs['Distance'].default_value = .08
    surface.node_tree.links.new(noise.outputs['Fac'],bump.inputs['Height'])
    surface.node_tree.links.new(bump.outputs['Normal'], nodes.get('Principled BSDF').inputs['Normal'])

def box(name, location, size, surface, bevel=.04):
    """Add a beveled architectural or prop element."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(surface)
    if bevel:
        modifier = obj.modifiers.new('Soft manufactured edges','BEVEL')
        modifier.width = bevel
        modifier.segments = 2
        obj.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL')
    return obj

def rod(name, start, end, radius, surface, vertices=12):
    """Connect two points with a cylindrical detail."""
    delta = Vector(end)-Vector(start)
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=delta.length, location=(Vector(start)+Vector(end))/2)
    obj = bpy.context.object
    obj.name = name
    obj.rotation_euler = delta.to_track_quat('Z','Y').to_euler()
    obj.data.materials.append(surface)
    return obj

def text(name, body, location, size, surface):
    """Place readable signage on a street-facing facade."""
    curve = bpy.data.curves.new(name,'FONT')
    curve.body = body
    curve.align_x = 'CENTER'
    curve.size = size
    curve.extrude = .012
    curve.bevel_depth = .004
    obj = bpy.data.objects.new(name,curve)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    obj.rotation_euler = (math.pi/2,0,0)
    obj.data.materials.append(surface)
    return obj

def area_light(name, position, target, color, power, size):
    """Aim a soft area light toward a scene feature."""
    data = bpy.data.lights.new(name,'AREA')
    data.energy = power
    data.color = color
    data.shape = 'DISK'
    data.size = size
    obj = bpy.data.objects.new(name,data)
    bpy.context.collection.objects.link(obj)
    obj.location = position
    obj.rotation_euler = (Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()

box('Raised island foundation',(0,1,-.65),(59,39,1.2),purple,.5)
box('Boulevard asphalt',(-4,-6,.015),(50,10,.15),road)
box('North sidewalk',(-4,1,.19),(50,4,.45),concrete)
box('South promenade',(-4,-13,.19),(50,4,.45),concrete)
box('Building plots',(-4,10,.08),(50,14,.25),concrete)
box('Beach',(25,1,.04),(8,37,.25),sand,.15)
box('Ocean strip',(29,1,.03),(2,37,.15),water,.06)
for x in range(-28,22,2):
    box('Sidewalk expansion joint',(x,1,.425),(.025,3.8,.008),metal,0)
    box('Promenade joint',(x,-13,.425),(.025,3.8,.008),metal,0)
for y in [-6.18,-5.82]:
    box('Continuous center line',(-4,y,.101),(49,.10,.016),line,.005)
for x in range(-27,21,5):
    box('Lane dash',(x,-8.6,.103),(2,.10,.016),white,0)
for x in [-24,17]:
    for y in [-10.4,-9.2,-8,-6.8,-5.6,-4.4,-3.2,-2]:
        box('Crosswalk stripe',(x,y,.109),(2.6,.52,.02),white,.01)
for x in range(-27,21,3):
    box('Parking bay marking',(x,-2.5,.105),(.09,1.8,.02),white,0)

# Art Deco hotel anchors the street, with contrasting low-rise retail wings.
box('Hotel coral mass',(-6,8,6.6),(15,10,12.5),coral,.18)
box('Hotel central tower',(-6,6,9),(4.4,7,17),coral,.2)
for z in [.8,4.1,7.6,11.8,13]:
    box('Hotel horizontal ivory band',(-6,2.94,z),(15.4,.26,.22),cream)
for x in [-12,-9,-3,0]:
    for z in [2.2,5.6,9.1]:
        box('Hotel window surround',(x,2.83,z),(1.95,.25,2.25),cream)
        box('Hotel window',(x,2.65,z),(1.63,.08,1.94),glass)
        box('Window mullion',(x,2.58,z),(.06,.06,1.94),cream,.01)
for x in [-7.3,-6,-4.7]:
    box('Tower vertical decoration',(x,2.39,12),(.17,.2,9),cream)
box('Hotel entry glass',(-6,2.42,1.85),(3,.12,2.8),glass)
box('Hotel entrance canopy',(-6,1.15,3.2),(5,3,.3),cream)
for x in [-8.15,-3.85]:
    rod('Canopy column',(x,.1,.45),(x,.1,3.2),.10,metal)
text('Hotel name','PALM\nROYAL',(-6,2.18,14.5),.85,pink)
text('Hotel subtitle','S O U T H   B E A C H',(-6,-.39,3.19),.26,metal)
for x in [-12,0]:
    box('Roof air conditioning',(x,8,13.3),(2.2,2,1.0),metal)
    for shift in [-.6,-.3,0,.3,.6]:
        box('AC ventilation grille',(x+shift,6.98,13.3),(.09,.04,.7),cream,.01)

box('Ocean Drive diner',(-20,7,2.8),(11,8,5),teal,.22)
for z in [.8,4.4,5.35]:
    box('Diner streamlined trim',(-20,2.94,z),(11.3,.25,.16),cream)
for x in [-23.6,-20,-16.4]:
    box('Diner storefront window',(x,2.85,2.4),(2.7,.1,2.4),glass)
    box('Window warm glow',(x,2.78,3.42),(2.4,.05,.07),yellow,.01)
box('Diner sign panel',(-20,2.6,5.55),(10.8,.4,1.4),metal,.16)
text('Diner neon','OCEAN DRIVE',(-20,2.35,5.5),.70,cyan)
text('Diner description','DINER  /  COFFEE  /  24 HOURS',(-20,2.33,4.98),.22,cream)
for x in [-24,-22,-20,-18,-16]:
    box('Diner striped awning',(x,1.96,3.8),(1.0,1.7,.15),coral)
    box('Diner cream awning',(x+1,1.96,3.8),(1.0,1.7,.15),cream)

box('Sunset club',(11,7,3.8),(14,8,7),cream,.16)
for x in [6.5,10.5,14.5]:
    box('Club tall teal frame',(x,2.86,3.1),(2.7,.2,4.5),teal)
    box('Club recessed glass',(x,2.70,3.1),(2.3,.1,4.1),glass)
box('Club upper neon fascia',(11,2.72,6.15),(13.8,.14,.10),pink)
text('Club sign','S U N S E T', (11,2.6,7.0),.84,pink)
text('Club small sign','SOCIAL CLUB', (11,2.55,5.8),.32,metal)
for x in [5,17]:
    rod('Roof terrace post',(x,3.5,7.35),(x,3.5,8.3),.06,metal)
rod('Terrace top rail',(5,3.5,8.3),(17,3.5,8.3),.06,metal)
for x in range(5,18):
    rod('Terrace baluster',(x,3.5,7.35),(x,3.5,8.3),.025,metal)

# Polygonal leaf ribbons produce a recognizable palm silhouette without external assets.
def palm(x,y,height):
    """Build a curved palm trunk and twelve arched fronds."""
    base = Vector((x,y,.45))
    for index in range(11):
        start = base + Vector((.38*(index/11)**2,0,height*index/11))
        end = base + Vector((.38*((index+1)/11)**2,0,height*(index+1)/11))
        rod('Segmented palm trunk',start,end,.19-.055*index/11,wood)
    top = base + Vector((.38,0,height))
    for index in range(12):
        angle = index*math.tau/12 + random.uniform(-.12,.12)
        length = random.uniform(2.5,3.8)
        vertices=[]
        for step in range(9):
            t=step/8
            center = top+Vector((math.cos(angle)*length*t,math.sin(angle)*length*t,1.35*math.sin(t*math.pi)-1.0*t))
            width=.39*math.sin(math.pi*t)**.7
            side=Vector((-math.sin(angle)*width,math.cos(angle)*width,0))
            vertices.extend([center-side,center+Vector((0,0,.09)),center+side])
        faces=[]
        for step in range(8):
            a=step*3
            faces.extend([(a,a+3,a+4,a+1),(a+1,a+4,a+5,a+2)])
        mesh=bpy.data.meshes.new('Folded frond mesh')
        mesh.from_pydata(vertices,[],faces)
        mesh.materials.append(leaf)
        obj=bpy.data.objects.new('Palm frond',mesh)
        bpy.context.collection.objects.link(obj)
    box('Palm planter',(x,y,.55),(1.4,1.4,.35),cream,.15)
for x,y,h in [(-27,1,8),(-14,1,9),(2,1,8.5),(20,1,9),(-25,-13,8),(-10,-13,8.8),(6,-13,8),(20,-13,9),(25,10,8),(25,17,7)]:
    palm(x,y,h)

def car(x,y,surface):
    """Create a stylized coupe facing along the boulevard."""
    box('Coupe lower body',(x,y,.65),(4.5,1.95,.65),surface,.22)
    box('Coupe upper cabin',(x-.2,y,1.22),(2.35,1.65,.68),glass,.25)
    box('Coupe roof',(x-.3,y,1.59),(1.8,1.65,.10),surface,.09)
    box('Coupe hood',(x+1.55,y,.98),(1.1,1.85,.18),surface,.10)
    for wheel_x in [x-1.4,x+1.4]:
        for wheel_y in [y-.98,y+.98]:
            rod('Tire',(wheel_x,wheel_y-.13,.5),(wheel_x,wheel_y+.13,.5),.43,rubber,24)
            rod('Alloy wheel',(wheel_x,wheel_y-.145,.5),(wheel_x,wheel_y+.145,.5),.23,metal,16)
    for offset in [-.64,.64]:
        box('Headlight',(x+2.26,y+offset,.82),(.04,.39,.18),yellow,.03)
        box('Rear light',(x-2.26,y+offset,.82),(.04,.39,.15),pink,.02)
    box('Front bumper',(x+2.28,y,.49),(.12,1.75,.12),metal)
car(-7,-8.5,red)
car(9,-3,teal)
car(-20,-3,cream)

for x in [-19,-1,15]:
    rod('Street lamp pole',(x,-11.5,.4),(x,-11.5,6.8),.075,metal)
    rod('Street lamp arm',(x,-11.5,6.8),(x,-10.4,6.8),.075,metal)
    box('Street lamp luminaire',(x,-10.35,6.74),(.6,1,.12),yellow)
    area_light('Warm street pool',(x,-10.35,6.5),(x,-9,0),(1,.52,.22),180,3)
for x in [-18,0,13]:
    box('Promenade bench seat',(x,-13,.95),(2.5,.7,.12),wood)
    box('Promenade bench back',(x,-13.3,1.4),(2.5,.10,.7),wood)
    for offset in [-.9,.9]:
        box('Bench leg',(x+offset,-13,.64),(.1,.6,.5),metal)
for x in [-26,-2,18]:
    box('Street litter bin',(x,.7,.9),(.55,.55,1),metal,.09)
for x in [7,11,15]:
    rod('Cafe table stem',(x,.6,.4),(x,.6,1.25),.06,metal)
    bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=.58,depth=.08,location=(x,.6,1.25))
    bpy.context.object.name='Cafe round table'
    bpy.context.object.data.materials.append(cream)
    for offset in [-.9,.9]:
        box('Cafe stool',(x+offset,.6,.82),(.45,.45,.1),teal,.09)
        rod('Stool leg',(x+offset,.6,.4),(x+offset,.6,.78),.045,metal)
# Low-detail distant skyline frames the neighborhood without competing with it.
for x,height in [(-24,10),(-17,14),(-9,11),(0,17),(9,12),(17,15)]:
    box('Distant pastel tower',(x,16,height/2),(5,3,height),teal if x%2 else coral,.12)
    for z in range(2,height,2):
        for offset in [-1.5,0,1.5]:
            box('Distant tower window',(x+offset,14.47,z),(.65,.04,.8),glass,.01)

scene=bpy.context.scene
scene.render.engine='CYCLES'
scene.cycles.samples=32
scene.cycles.use_denoising=True
scene.render.resolution_x=1500
scene.render.resolution_y=1100
scene.render.resolution_percentage=100
scene.world.color=(.16,.16,.16)
scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.12,.17,.30,1)
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.45
area_light('Large peach sunset',(-25,-15,35),(0,3,0),(1,.56,.34),6500,25)
area_light('Cool twilight fill',(15,12,28),(0,0,3),(.28,.5,1),5000,20)
area_light('Neon hotel wash',(-6,.6,14),(-6,3,8),(1,.035,.2),250,5)
area_light('Neon diner wash',(-20,1,5),(-20,-1,1),(.02,.7,1),200,6)
area_light('Neon club wash',(11,1,7),(11,0,2),(1,.04,.3),220,7)
bpy.ops.object.light_add(type='SUN',location=(-20,-20,30))
bpy.context.object.name='Late afternoon sun'
bpy.context.object.rotation_euler=(math.radians(35),math.radians(-25),math.radians(-35))
bpy.context.object.data.energy=2.0
bpy.context.object.data.color=(1,.67,.46)
bpy.context.object.data.angle=.15
bpy.ops.object.camera_add(location=(46,-64,43))
camera=bpy.context.object
camera.name='Hero camera - whole neighborhood'
camera.rotation_euler=(Vector((0,2,4))-camera.location).to_track_quat('-Z','Y').to_euler()
camera.data.type='ORTHO'
camera.data.ortho_scale=72
scene.camera=camera
# Save a second street camera for closer exploration.
bpy.ops.object.camera_add(location=(19,-20,5.0))
street=bpy.context.object
street.name='Street camera - Ocean Drive'
street.rotation_euler=(Vector((-9,3,5))-street.location).to_track_quat('-Z','Y').to_euler()
street.data.lens=28
scene.view_settings.view_transform='AgX'
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            area.spaces.active.region_3d.view_perspective='CAMERA'
            area.spaces.active.clip_end=1000
# Organize the scene by editable asset families.
for obj in list(scene.objects):
    name=obj.name.lower()
    group='Architecture'
    if any(word in name for word in ['palm','frond']): group='Palms'
    elif any(word in name for word in ['coupe','tire','wheel','headlight','rear light','bumper']): group='Vehicles'
    elif obj.type=='LIGHT': group='Lighting'
    elif obj.type=='CAMERA': group='Cameras'
    elif any(word in name for word in ['road','boulevard','sidewalk','promenade','beach','ocean strip','foundation','line','crosswalk','lane','parking']): group='Streets and landscape'
    collection=bpy.data.collections.get(group)
    if collection is None:
        collection=bpy.data.collections.new(group)
        scene.collection.children.link(collection)
    for old in list(obj.users_collection): old.objects.unlink(obj)
    collection.objects.link(obj)
bpy.ops.object.select_all(action='DESELECT')
scene.render.image_settings.file_format='PNG'
scene.render.filepath=str(RENDERS / 'palm-royal-preview.png')
bpy.ops.wm.save_as_mainfile(filepath=str(SCENES / 'palm-royal.blend'))
bpy.ops.render.render(write_still=True)
print('WORLD_BUILD_COMPLETE',len(scene.objects))
