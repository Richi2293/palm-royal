"""Generate an explorable coastal city with linked geometry and cinematic cameras."""
import ast
import math
import random
from pathlib import Path
import bpy
from mathutils import Vector

OUTPUT = Path(__file__).resolve().parent
SOURCE = (OUTPUT / 'build_world.py').read_text()
# Reuse the original palette and prop constructors while replacing the layout.
# MARKER delimits the shared preamble inside build_world.py. Both files depend
# on that comment staying exactly as it is: keep them in sync when editing.
MARKER = '# Fine procedural'
if MARKER not in SOURCE:
    raise SystemExit(
        f'build_city.py could not find the marker {MARKER!r} in build_world.py. '
        'That comment delimits the shared setup reused here. Restore it, or '
        'update MARKER in this file to match the new delimiter.'
    )
exec(SOURCE[:SOURCE.index(MARKER)])
for definition in ast.parse(SOURCE).body:
    if isinstance(definition, ast.FunctionDef):
        exec(compile(ast.Module(body=[definition], type_ignores=[]), '<asset-library>', 'exec'))
random.seed(41)
CURRENT_GROUP = 'Ground and water'
MESH_CACHE = {}

def collection(name):
    """Return a scene collection, creating it when necessary."""
    result = bpy.data.collections.get(name)
    if result is None:
        result = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(result)
    return result

def place(obj):
    """Move an object into the active district collection."""
    for previous in list(obj.users_collection):
        previous.objects.unlink(obj)
    collection(CURRENT_GROUP).objects.link(obj)
    return obj

def box(name, location, size, surface, bevel=.0):
    """Create lightweight boxes sharing geometry for repeated dimensions."""
    key = (tuple(size), surface.name)
    mesh = MESH_CACHE.get(key)
    if mesh is None:
        sx,sy,sz = (value/2 for value in size)
        vertices=[(-sx,-sy,-sz),(-sx,-sy,sz),(-sx,sy,-sz),(-sx,sy,sz),(sx,-sy,-sz),(sx,-sy,sz),(sx,sy,-sz),(sx,sy,sz)]
        faces=[(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)]
        mesh=bpy.data.meshes.new(name+' geometry')
        mesh.from_pydata(vertices,[],faces)
        mesh.materials.append(surface)
        MESH_CACHE[key]=mesh
    obj=bpy.data.objects.new(name,mesh)
    collection(CURRENT_GROUP).objects.link(obj)
    obj.location=location
    if bevel:
        modifier=obj.modifiers.new('Architectural edge highlights','BEVEL')
        modifier.width=bevel
        modifier.segments=2
        obj.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return obj


def rod(name, start, end, radius, surface, vertices=12):
    """Build cylinders directly to avoid expensive scene-wide operator updates."""
    key = ('cylinder', vertices, surface.name)
    mesh = MESH_CACHE.get(key)
    if mesh is None:
        points = [(math.cos(i*math.tau/vertices), math.sin(i*math.tau/vertices), z) for z in [-.5,.5] for i in range(vertices)]
        faces = [tuple(reversed(range(vertices))), tuple(range(vertices,2*vertices))]
        faces += [(i,(i+1)%vertices,(i+1)%vertices+vertices,i+vertices) for i in range(vertices)]
        mesh = bpy.data.meshes.new(name+' shared cylinder')
        mesh.from_pydata(points,[],faces)
        mesh.materials.append(surface)
        MESH_CACHE[key] = mesh
    obj = bpy.data.objects.new(name,mesh)
    collection(CURRENT_GROUP).objects.link(obj)
    delta = Vector(end)-Vector(start)
    obj.location = (Vector(start)+Vector(end))/2
    obj.rotation_euler = delta.to_track_quat('Z','Y').to_euler()
    obj.scale = (radius,radius,delta.length)
    return obj

def umbrella(x,y,surface):
    """Construct a low-poly beach umbrella canopy without operators."""
    vertices=[(0,0,.4)]+[(2.3*math.cos(i*math.tau/12),2.3*math.sin(i*math.tau/12),-.35) for i in range(12)]
    mesh=bpy.data.meshes.new('Umbrella canopy')
    mesh.from_pydata(vertices,[],[(0,i+1,(i+1)%12+1) for i in range(12)])
    mesh.materials.append(surface)
    obj=bpy.data.objects.new('Beach parasol',mesh)
    collection(CURRENT_GROUP).objects.link(obj)
    obj.location=(x,y,3)

navy=material('Deep navy tower cladding',(.045,.10,.16),metallic=.5,roughness=.25)
lavender=material('Lavender stucco',(.42,.32,.53))
blue=material('Ocean blue facade',(.13,.32,.47))
grass=material('Tropical park grass',(.12,.26,.10))
orange=material('Amber neon', (1,.25,.025),emission=4)
warm_window=material('Occupied apartment windows',(.95,.53,.23),emission=.8)
water.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.22
nodes=water.node_tree.nodes
noise=nodes.new('ShaderNodeTexNoise')
noise.inputs['Scale'].default_value=1.3
noise.inputs['Detail'].default_value=3
bump=nodes.new('ShaderNodeBump')
bump.inputs['Strength'].default_value=.23
bump.inputs['Distance'].default_value=.15
water.node_tree.links.new(noise.outputs['Fac'],bump.inputs['Height'])
water.node_tree.links.new(bump.outputs['Normal'],nodes.get('Principled BSDF').inputs['Normal'])

box('Coastal terrain',(0,5,-1),(280,250,2),sand)
box('Atlantic ocean',(40,-5,-1.1),(500,460,.35),water)
box('Urban ground',(-20,10,-.05),(235,230,.12),concrete)
box('Long sandy beach',(113,15,.05),(35,225,.18),sand)
box('Oceanfront promenade',(91,15,.16),(8,225,.4),cream)
# Connected streets form nine complete blocks plus the downtown edge.
for x in [-120,-60,0,60]:
    box('North south avenue',(x,5,.02),(12,235,.12),road)
    for offset in [-.16,.16]: box('Avenue double line',(x+offset,5,.087),(.10,232,.012),line)
    for y in range(-105,115,8):
        box('Avenue lane dash',(x-3,y,.09),(.10,3,.012),white)
for y in [-85,-25,35,95]:
    box('East west boulevard',(-20,y,.03),(230,12,.14),road)
    for offset in [-.16,.16]: box('Boulevard double line',(-20,y+offset,.106),(230,.10,.012),line)
    for x in range(-130,88,8): box('Boulevard lane dash',(x,y-3,.108),(3,.1,.013),white)
    for x in [-120,-60,0,60]:
        # Restore asphalt over intersecting center lines before adding crossings.
        box('Clear intersection',(x,y,.115),(12,12,.015),road)
        for t in range(-4,5,2):
            for side in [-1,1]:
                box('Pedestrian crossing',(x+t,y+side*8,.13),(.8,2.5,.02),white)
                box('Pedestrian crossing',(x+side*8,y+t,.13),(2.5,.8,.02),white)

PALETTE=[coral,teal,cream,lavender,blue]
def building(x,y,width,depth,height,index):
    """Build a four-sided facade with shopfronts, roof details and balconies."""
    surface=PALETTE[index%len(PALETTE)]
    box('Building %03d stucco'%index,(x,y,height/2+.35),(width,depth,height),surface,.10)
    box('Roof parapet front',(x,y-depth/2,height+.6),(width+.3,.3,.8),cream)
    box('Roof parapet back',(x,y+depth/2,height+.6),(width+.3,.3,.8),cream)
    box('Roof parapet side',(x-width/2,y,height+.6),(.3,depth,.8),cream)
    box('Roof parapet side',(x+width/2,y,height+.6),(.3,depth,.8),cream)
    for z in range(5,int(height),3):
        box('Continuous floor trim',(x,y,z-.95),(width+.12,depth+.12,.12),cream)
        for shift in range(-int(width/2)+2,int(width/2),3):
            for sign in [-1,1]:
                surface_window=warm_window if random.random()<.2 else glass
                box('Apartment window',(x+shift,y+sign*(depth/2+.035),z),(1.45,.09,1.75),surface_window)
                box('Window sill',(x+shift,y+sign*(depth/2+.12),z-.9),(1.65,.25,.1),cream)
                if index%3==0 and sign==-1:
                    box('Balcony platform',(x+shift,y-depth/2-.55,z-1),(2.4,1.2,.15),cream)
                    box('Balcony glass railing',(x+shift,y-depth/2-1.1,z-.5),(2.4,.07,.85),glass)
        for shift in range(-int(depth/2)+2,int(depth/2),3):
            for sign in [-1,1]:
                box('Side window',(x+sign*(width/2+.035),y+shift,z),(.09,1.45,1.75),glass)
    for shift in range(-int(width/2)+2,int(width/2),4):
        box('Retail glazing',(x+shift,y-depth/2-.06,1.8),(2.9,.1,2.5),glass)
        box('Retail canopy',(x+shift,y-depth/2-.8,3.3),(3.5,1.6,.15),surface)
    box('Roof mechanical unit',(x+2,y+1,height+.8),(2.4,2,1),metal)
    for offset in [-.7,-.35,0,.35,.7]:
        box('Mechanical ventilation',(x+2+offset,y-.02,height+.8),(.12,.05,.7),cream)
    if index%4==0:
        box('Rooftop pool coping',(x-2,y,height+.42),(5.7,7.7,.2),cream)
        box('Rooftop swimming pool',(x-2,y,height+.55),(5,7,.12),water)
    if index%2==0:
        names=['PALM MARKET','AZURE HOTEL','VINYL & CO.','SUNSET BAR','OCEAN COFFEE','PARADISE MOTEL']
        box('Shop sign panel',(x,y-depth/2-.17,3.95),(width-.5,.18,.7),metal)
        place(text('Street business sign',names[index%6],(x,y-depth/2-.3,3.72),.45,cyan if index%4 else pink))

index=0
for row,cy in enumerate([-55,5,65]):
    for column,cx in enumerate([-90,-30,30]):
        CURRENT_GROUP=f'District {row+1}-{column+1}'
        box('Raised city block',(cx,cy,.18),(47,47,.4),concrete)
        for dx,dy in [(-12,-12),(12,-12),(-12,12),(12,12)]:
            index+=1
            height=random.choice([10,13,16,19,22])
            if row==2: height+=9
            building(cx+dx,cy+dy,random.choice([16,18]),random.choice([15,18]),height,index)
        for dx in [-21,21]:
            for dy in [-19,0,19]: palm(cx+dx,cy+dy,random.uniform(8,11))
        # The interior lanes remain open for walking between buildings.
        for dy in [-7,7]:
            box('Courtyard bench',(cx,cy+dy,.8),(2.6,.65,.2),wood)

CURRENT_GROUP='Downtown skyline'
for index,(x,y,h) in enumerate([(-107,112,48),(-78,112,62),(-43,112,42),(-13,112,75),(21,112,53),(53,112,40)],100):
    box('Glass tower',(x,y,h/2),(21,20,h),navy,.15)
    for z in range(3,h,3):
        box('Tower floor band',(x,y,z),(21.25,20.25,.14),cream)
        for offset in range(-9,11,3):
            box('Tower front glass',(x+offset,y-10.06,z-1.4),(2.3,.08,2.3),warm_window if random.random()<.15 else glass)
    for offset in range(-9,11,3):
        box('Tower vertical fin',(x+offset,y-10.2,h/2),(.10,.28,h),metal)
    box('Tower luminous crown',(x,y,h+.2),(21.4,20.4,.25),cyan)
    box('Tower rooftop core',(x,y,h+2),(9,10,4),navy)
    if h>60: rod('Tower antenna',(x,y,h+4),(x,y,h+13),.15,metal)

CURRENT_GROUP='Oceanfront leisure district'
for y in range(-91,116,15):
    palm(89,y,10)
for y in [-64,-4,56]:
    box('Oceanfront park',(75,y,.25),(15,38,.25),grass)
    for dy in [-13,0,13]:
        palm(75,y+dy,9)
        box('Park bench',(80,y+dy,.8),(2,.7,.2),wood)
for y in range(-90,101,14):
    for x in [105,120]:
        rod('Beach parasol pole',(x,y,0),(x,y,2.9),.055,cream)
        umbrella(x,y,coral if y%3 else teal)
        for dy in [-2,2]:
            box('Beach lounger',(x,y+dy,.4),(1,2,.18),cream)
            back=box('Lounger back',(x,y+dy+.65,.7),(1,.8,.15),teal)
            back.rotation_euler.x=.5
# Landmark wheel faces the city and oceanfront boulevard.
center=Vector((78,91,16))
for x in [73,83]:
    rod('Observation wheel support',(x,88,.4),center,.35,cream)
for index in range(48):
    a=index*math.tau/48
    b=(index+1)*math.tau/48
    p=center+Vector((math.cos(a)*14,0,math.sin(a)*14))
    q=center+Vector((math.cos(b)*14,0,math.sin(b)*14))
    rod('Illuminated wheel rim',p,q,.095,pink)
    if index%4==0:
        rod('Wheel spoke',center,p,.055,cream)
        box('Wheel passenger cabin',p+Vector((0,0,-1)),(1.6,1.7,1.8),teal,.12)
        box('Wheel cabin glazing',p+Vector((0,-.86,-.8)),(1.3,.04,.75),glass)
place(text('Wheel plaza sign','PARADISE PIER',(78,87,2.4),.75,cyan))

CURRENT_GROUP='Marina and waterfront'
box('Marina seawall',(-15,-114,.5),(220,4,1.2),cream)
for x in [-105,-65,-25,15,55]:
    box('Timber marina pier',(x,-136,.35),(3,42,.5),wood)
    for y in [-120,-133,-146]:
        for dx in [-2,2]: rod('Mooring bollard',(x+dx,y,0),(x+dx,y,1),.13,metal)
        bx=x+8
        box('Yacht hull',(bx,y,.45),(5,10,1.3),cream,.6)
        box('Yacht dark waterline',(bx,y,.04),(5.02,9.5,.25),navy,.1)
        box('Yacht cabin',(bx,y+1,1.5),(3.7,4.7,1.6),glass,.25)
        box('Yacht roof',(bx,y+1,2.36),(4.1,5,.18),cream,.1)
        box('Yacht sun deck',(bx,y-3,1.17),(3.8,2,.15),wood)
        rod('Yacht antenna',(bx,y+1,2.4),(bx,y+1,4),.035,metal)
box('Waterfront club',(-30,-101,3),(25,12,5.5),teal,.1)
place(text('Marina sign','THE MARINA  /  YACHT CLUB',(-30,-107.1,4.2),.65,cyan))

CURRENT_GROUP='Street details and traffic'
for y in [-85,-25,35,95]:
    for x in [-106,-77,-46,-17,14,43,73]:
        car(x,y+random.choice([-3,3]),random.choice([red,teal,cream,navy]))
        rod('Boulevard lamp',(x,y-7,.3),(x,y-7,7),.085,metal)
        rod('Lamp arm',(x,y-7,7),(x,y-5.7,7),.075,metal)
        box('Lamp glowing panel',(x,y-5.6,6.9),(.65,1.2,.13),yellow)
        box('Street bin',(x+2,y-8,.8),(.6,.6,1.2),metal,.06)
for x in [-120,-60,0,60]:
    for y in [-85,-25,35,95]:
        rod('Traffic signal post',(x+7,y-7,.3),(x+7,y-7,4.8),.09,metal)
        box('Signal housing',(x+7,y-7,4.3),(.45,.4,1.2),metal,.08)
        box('Signal red',(x+7,y-7.22,4.65),(.22,.05,.22),pink)
        box('Signal green',(x+7,y-7.22,3.98),(.22,.05,.22),cyan)
# Silhouettes lend scale to pedestrian-level views.
for index in range(65):
    x=random.uniform(-112,80)
    y=random.choice([-77,-33,43,87])+random.uniform(-.7,.7)
    surface=random.choice([coral,teal,cream,navy])
    rod('Pedestrian torso',(x,y,.85),(x,y,1.4),.18,surface)
    for dx in [-.11,.11]: rod('Pedestrian leg',(x+dx,y,.3),(x+dx,y,.9),.065,metal)
    box('Pedestrian head',(x,y,1.62),(.24,.24,.28),sand,.10)

CURRENT_GROUP='Cinematic lighting'
scene=bpy.context.scene
scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.085,.14,.24,1)
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.5
bpy.ops.object.light_add(type='SUN',location=(-80,-100,120))
sun=place(bpy.context.object)
sun.name='Golden hour coastal sunlight'
sun.rotation_euler=(math.radians(55),math.radians(-20),math.radians(-35))
sun.data.energy=2.4
sun.data.color=(1,.69,.43)
sun.data.angle=.12
area_light('Blue sky fill',(30,0,170),(0,0,0),(.35,.55,1),60000,180)
for y in [-85,-25,35,95]:
    for x in [-95,-35,25,75]:
        area_light('Warm boulevard light',(x,y,8),(x,y,0),(1,.48,.18),140,5)

CURRENT_GROUP='Exploration cameras'
def camera(name,position,target,lens=35):
    """Create a perspective camera with generous city-scale clipping."""
    data=bpy.data.cameras.new(name)
    data.lens=lens
    data.clip_end=2000
    obj=bpy.data.objects.new(name,data)
    collection(CURRENT_GROUP).objects.link(obj)
    obj.location=position
    obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
    return obj
hero=camera('01 - Entire coastal city',(305,-365,285),(-5,0,16),42)
street=camera('02 - Walk Ocean Boulevard',(78,-28,2.1),(-95,-24,9),25)
camera('03 - Marina and skyline',(70,-176,9),(-20,30,18),30)
camera('04 - Beach promenade',(93,-65,2.1),(90,82,10),28)
camera('05 - Downtown roof terraces',(-65,35,46),(-15,112,33),32)
scene.camera=hero
scene.render.engine='CYCLES'
scene.cycles.samples=24
scene.cycles.use_denoising=True
scene.render.resolution_x=1700
scene.render.resolution_y=1200
scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.view_settings.view_transform='AgX'
# A compositor glow makes bright signage and reflective highlights visible at dusk.
scene.use_nodes=True
node_tree=scene.compositing_node_group
if node_tree is None:
    node_tree=bpy.data.node_groups.new('Coastal city glow','CompositorNodeTree')
    scene.compositing_node_group=node_tree
    node_tree.interface.new_socket(name='Image',in_out='OUTPUT',socket_type='NodeSocketColor')
    output=node_tree.nodes.new('NodeGroupOutput')
else:
    output=next((node for node in node_tree.nodes if node.type=='GROUP_OUTPUT'),None)
    if output is None:
        output=node_tree.nodes.new('NodeGroupOutput')
render_layers=node_tree.nodes.new('CompositorNodeRLayers')
glow=node_tree.nodes.new('CompositorNodeGlare')
glow.inputs['Type'].default_value='Fog Glow'
glow.inputs['Quality'].default_value='Medium'
glow.inputs['Strength'].default_value=.3
node_tree.links.new(render_layers.outputs['Image'],glow.inputs['Image'])
node_tree.links.new(glow.outputs['Image'],output.inputs[0])
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            space=area.spaces.active
            space.clip_end=2500
            space.overlay.show_overlays=False
            space.shading.type='MATERIAL'
            space.region_3d.view_perspective='CAMERA'
            space.region_3d.view_camera_zoom=8
scene['City dimensions']='280 x 250 meters of land, plus a 220 x 42 meter marina and ocean'
scene['Scale comparison']='30.4 times the original 59 x 39 meter land area'
scene['Explore']='Use camera 02 or 04; Shift+accent grave enters Walk Navigation. WASD moves, mouse looks, wheel adjusts speed.'
bpy.ops.object.select_all(action='DESELECT')
scene.render.filepath=str(OUTPUT/'coastal-city-aerial.png')
bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT/'coastal-city.blend'))
print('CITY_SAVED',len(scene.objects),flush=True)
bpy.ops.render.render(write_still=True)
scene.camera=street
scene.render.filepath=str(OUTPUT/'coastal-city-street.png')
scene.render.resolution_x=1500
scene.render.resolution_y=1000
bpy.ops.render.render(write_still=True)
print('CITY_COMPLETE',flush=True)
