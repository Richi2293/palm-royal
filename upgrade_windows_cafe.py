"""Create actual window openings and a furnished, walkable cafe interior."""
import ast
import math
import random
from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parent
SCENES=ROOT/'scenes'
RENDERS=ROOT/'renders'
ASSETS=ROOT/'assets'
for filename in ['build_world.py','build_city.py','refine_showcase.py','build_showcase.py']:
    for node in ast.parse((ROOT/filename).read_text()).body:
        if isinstance(node,ast.FunctionDef) and node.name in ['material','text','area_light','collection','place','box','rod','lathe','load_template','instance','camera']:
            exec(compile(ast.Module(body=[node],type_ignores=[]),filename,'exec'))
bpy.ops.wm.open_mainfile(filepath=str(SCENES/'coastal-city-detailed.blend'))
scene=bpy.context.scene
random.seed(106)
MESH_CACHE={}
TEMPLATES={}
CURRENT_GROUP='Renovation - Real window openings'
plaster=bpy.data.materials['PBR - Coral weathered plaster']
white=bpy.data.materials['PBR - Warm mineral render']
blue=bpy.data.materials['PBR - Weathered teal plaster']
brick=bpy.data.materials['PBR - Brown masonry']
brass=bpy.data.materials['Brushed champagne brass']
black=bpy.data.materials['Black powder-coated framing']
wood=bpy.data.materials['Palm bark and timber']
ceramic=bpy.data.materials['Glazed ivory porcelain']
clear=material('Optical window glass - clear double glazing',(.92,.97,1),roughness=.025)
shader=clear.node_tree.nodes.get('Principled BSDF')
shader.inputs['Transmission Weight'].default_value=1
shader.inputs['IOR'].default_value=1.46
linen=material('Warm linen curtains',(.76,.69,.54),roughness=.95)
room_wall=material('Warm apartment paint',(.52,.47,.38),roughness=.85)
room_dark=material('Quiet apartment paint',(.25,.28,.27),roughness=.85)
lightmat=material('Warm lamp diffuser',(1,.64,.31),emission=2.5)
leather=material('Olive leather upholstery',(.13,.20,.10),roughness=.42)
marble=material('Ivory veined marble',(.78,.74,.63),roughness=.22)
# Subtle stone veins are evaluated in physical object coordinates.
nodes=marble.node_tree.nodes
links=marble.node_tree.links
noise=nodes.new('ShaderNodeTexNoise')
noise.inputs['Scale'].default_value=3
noise.inputs['Roughness'].default_value=.7
ramp=nodes.new('ShaderNodeValToRGB')
ramp.color_ramp.elements[0].position=.44
ramp.color_ramp.elements[0].color=(.22,.25,.23,1)
ramp.color_ramp.elements[1].position=.52
ramp.color_ramp.elements[1].color=(.79,.75,.63,1)
links.new(noise.outputs['Fac'],ramp.inputs[0])
links.new(ramp.outputs[0],nodes.get('Principled BSDF').inputs['Base Color'])

remove_prefixes=('Hotel upper plaster volume','Cafe upper volume','Window stone reveal','Recessed dark window','Window inner curtain','Side window reveal','Side reflective window','Cafe upper window reveal','Cafe upper glass','Lobby glazing','Cafe interior bar','Cafe bar marble top','Bar display bottle','Bottle neck','Bar display shelf','Cafe pendant','Pendant cord','Pendant brass shade')
for obj in list(scene.objects):
    if obj.name.startswith(remove_prefixes): bpy.data.objects.remove(obj,do_unlink=True)
    elif obj.name.startswith('outdoor_table_chair_set_01 instance') and obj.location.y>-12:
        bpy.data.objects.remove(obj,do_unlink=True)

HOTEL_X=[31,34.6,38.2,41.8,45.4,49]
HOTEL_Z=[6.65,10.5,14.35,17.9]
def perforated_wall(name,centers,rows,left,right,bottom,top,fixed,width,height,surface,axis='X'):
    """Assemble a structural wall around true rectangular apertures."""
    def panel(a,b,c,d):
        if b-a<.01 or d-c<.01: return
        if axis=='X': box(name,((a+b)/2,fixed,(c+d)/2),(b-a,.27,d-c),surface,.015)
        else: box(name,(fixed,(a+b)/2,(c+d)/2),(.27,b-a,d-c),surface,.015)
    z=bottom
    for row in rows:
        panel(left,right,z,row-height/2)
        start=left
        for center in centers:
            panel(start,center-width/2,row-height/2,row+height/2)
            start=center+width/2
        panel(start,right,row-height/2,row+height/2)
        z=row+height/2
    panel(left,right,z,top)

perforated_wall('Hotel facade around openings',HOTEL_X,HOTEL_Z,29.7,50.3,3.9,19.4,-14,2.22,2.48,plaster)
perforated_wall('Hotel side around openings',[-11,-7,-3,1],HOTEL_Z,-14,4,3.9,19.4,50,2.15,2.48,plaster,'Y')
box('Hotel rear structural wall',(40,4,11.7),(20,.3,15.5),plaster)
box('Hotel west structural wall',(30,-5,11.7),(.3,18,15.5),plaster)
box('Hotel roof',(40,-5,19.45),(20,18,.3),white)
perforated_wall('Cafe facade around openings',[12.5,18,23.5],[7.1],9.5,26.5,3.9,10.9,-14,1.95,2.8,blue)
for x in [9.5,26.5]: box('Cafe upper side',(x,-5,7.4),(.25,18,7),blue)
box('Cafe upper rear',(18,3.9,7.4),(17,.25,7),blue)
box('Cafe roof slab',(18,-5,10.9),(17,18,.25),white)

def curtain(name,x,y,z,width,height):
    """Make folded fabric with a smooth, scalloped cross section."""
    segments=32
    vertices=[]
    for level in range(9):
        t=level/8
        for i in range(segments+1):
            s=i/segments
            vertices.append((x+width*(s-.5),y+.06*math.sin(s*math.tau*7)*(1+.12*t),z+height*(t-.5)))
    faces=[]
    for level in range(8):
        for i in range(segments):
            a=level*(segments+1)+i
            faces.append((a,a+1,a+segments+2,a+segments+1))
    mesh=bpy.data.meshes.new(name)
    mesh.from_pydata(vertices,[],faces)
    mesh.materials.append(linen)
    obj=bpy.data.objects.new(name,mesh)
    collection(CURRENT_GROUP).objects.link(obj)
    for p in mesh.polygons: p.use_smooth=True

def framed_window(x,z,width=2.22,height=2.48):
    """Add a real glazing unit, shaped surround, sill, and opening hardware."""
    box('Clear window glazing',(x,-14.12,z),(width-.08,.012,height-.08),clear)
    for dx in [-width/2-.1,width/2+.1]:
        box('Window stone jamb',(x+dx,-14.10,z),(.19,.44,height+.37),white,.025)
        box('Window bronze jamb',(x+dx*.89,-14.23,z),(.055,.09,height),brass,.008)
    for dz in [-height/2-.1,height/2+.1]:
        box('Window stone head and sill',(x,-14.10,z+dz),(width+.37,.44,.19),white,.025)
    box('Window projecting sill',(x,-14.28,z-height/2-.14),(width+.47,.62,.10),white,.025)
    box('Window central vertical bar',(x,-14.23,z),(.05,.09,height),brass,.008)
    box('Window transom',(x,-14.23,z+.53),(width,.09,.045),brass,.008)
    rod('Window casement handle',(x+.15,-14.30,z-.20),(x+.15,-14.30,z+.03),.016,black)

for floor,z in enumerate(HOTEL_Z):
    floor_z=z-1.3
    box('Hotel occupied floor',(40,-5,floor_z-.12),(19.7,17.7,.2),room_wall)
    for index,x in enumerate(HOTEL_X):
        framed_window(x,z)
        wall=room_wall if (index+floor)%3 else room_dark
        box('Apartment back wall',(x,-10.1,z),(3.3,.12,2.6),wall)
        for dx in [-1.65,1.65]: box('Apartment partition',(x+dx,-12,z),(.10,3.8,2.6),wall)
        box('Apartment bed base',(x+.35,-11.6,floor_z+.35),(1.4,1.9,.35),wood,.06)
        box('Apartment linen duvet',(x+.35,-11.6,floor_z+.6),(1.42,1.91,.18),linen,.07)
        box('Apartment pillow',(x+.35,-10.96,floor_z+.75),(1,.42,.16),linen,.08)
        box('Apartment nightstand',(x-.85,-11.1,floor_z+.4),(.5,.5,.7),wood,.04)
        rod('Bedside lamp stem',(x-.85,-11.1,floor_z+.77),(x-.85,-11.1,floor_z+1.04),.025,brass)
        rod('Bedside lampshade',(x-.85,-11.1,floor_z+1.0),(x-.85,-11.1,floor_z+1.28),.16,lightmat)
        curtain('Pleated room curtain',x-.72,-13.7,z,.55,2.34)
        if (index+floor)%3:
            curtain('Second open room curtain',x+.82,-13.7,z,.35,2.34)
            area_light('Warm occupied apartment',(x,-11.5,z+.85),(x,-14,z),(1,.64,.34),35,1.0)
        else: curtain('Partially drawn curtain',x+.35,-13.7,z,1.2,2.34)
for z in HOTEL_Z:
    for y in [-11,-7,-3,1]:
        box('Side clear double glazing',(50.10,y,z),(.012,2.08,2.40),clear)
        for offset in [-1.2,1.2]: box('Side stone window jamb',(50.10,y+offset,z),(.4,.18,2.8),white,.025)
        for offset in [-1.34,1.34]: box('Side stone window sill',(50.10,y,z+offset),(.4,2.58,.18),white,.025)
for x in [12.5,18,23.5]:
    framed_window(x,7.1,1.95,2.8)
    box('Cafe upstairs floor',(x,-10,5.55),(5,7,.15),wood)
    box('Cafe upstairs back wall',(x,-8,7),(5,.15,3),room_wall)
    curtain('Cafe linen curtain',x-.65,-13.7,7.1,.5,2.65)
    box('Upstairs occasional table',(x,-11,6.15),(1.2,.7,.08),wood,.04)
    area_light('Cafe upstairs warm light',(x,-10,8.2),(x,-14,6.9),(1,.65,.35),65,1.4)
# Replace the lobby panels with clear glass as well.
for x in [36,38.6,41.2,43.8]: box('Clear lobby entrance glazing',(x,-14.12,2.1),(2.48,.012,2.95),clear)

CURRENT_GROUP='Miramar - Interior finishes'
# Distinct timber grain is shared by all boards with physical variation per board.
oak=material('Oiled walnut and oak grain',(.23,.11,.045),roughness=.4)
nodes=oak.node_tree.nodes
links=oak.node_tree.links
coords=nodes.new('ShaderNodeTexCoord')
scale=nodes.new('ShaderNodeVectorMath')
scale.operation='MULTIPLY'
scale.inputs[1].default_value=(3,160,4)
links.new(coords.outputs['Generated'],scale.inputs[0])
grain=nodes.new('ShaderNodeTexNoise')
grain.inputs['Scale'].default_value=1
links.new(scale.outputs[0],grain.inputs['Vector'])
ramp=nodes.new('ShaderNodeValToRGB')
ramp.color_ramp.elements[0].color=(.055,.018,.006,1)
ramp.color_ramp.elements[1].color=(.34,.16,.05,1)
links.new(grain.outputs['Fac'],ramp.inputs[0])
links.new(ramp.outputs[0],nodes.get('Principled BSDF').inputs['Base Color'])
for row in range(44):
    y=-13.7+row*.40
    for column in range(9):
        x=9.8+column*1.86
        box('Individual timber floorboard',(x+.85,y,.68),(1.84,.392,.05),oak,.006)
box('Cafe warm ceiling',(18,-5,3.87),(16.8,17.6,.16),room_wall)
for y in [-12,-8,-4,0]:
    box('Ceiling timber beam',(18,y,3.72),(16.8,.16,.22),oak,.015)
for x in [9.77,26.23]:
    box('Oak wall wainscot',(x,-5,1.2),(.11,17.5,1.1),oak,.01)
    box('Brass wainscot cap',(x,-5,1.78),(.13,17.5,.04),brass,.008)
# Slatted front bar, marble top, and service space behind it.
box('Service bar carcass',(19,-.25,1.22),(10.8,1.55,1.08),black,.04)
for index in range(108): box('Bar vertical walnut slat',(13.65+index*.1,-1.05,1.22),(.065,.055,1.02),oak,.01)
box('Bar veined marble counter',(19,-.25,1.82),(11.1,1.8,.13),marble,.035)
rod('Bar brass foot rail',(13.4,-1.38,.91),(24.5,-1.38,.91),.035,brass,20)
for x in [14,17,20,23]: rod('Foot rail mounting',(x,-1.05,.91),(x,-1.38,.91),.025,brass)
box('Back service counter',(19,2.85,1.19),(11,1.1,1.0),oak,.03)
box('Back service stone top',(19,2.85,1.73),(11.1,1.2,.1),marble,.025)
for x in [14,16,18,20,22,24]:
    box('Service cabinet door',(x,2.26,1.22),(1.8,.06,.8),oak,.01)
    rod('Cabinet brass handle',(x-.25,2.2,1.35),(x+.25,2.2,1.35),.018,brass)
# Illuminated bottle display behind the counter.
for z in [2.1,2.65,3.2]:
    box('Backbar shelf',(21,3.25,z),(7,.75,.07),oak,.015)
    box('Backbar concealed LED',(21,2.9,z-.05),(6.9,.025,.02),lightmat)
    for i in range(15):
        x=17.8+i*.44
        if random.random()<.85:
            bottle_material=material('Bottle glass %s %s'%(z,i),random.choice([(.05,.15,.04),(.22,.07,.025),(.13,.19,.18)]),roughness=.15)
            bottle_material.node_tree.nodes.get('Principled BSDF').inputs['Transmission Weight'].default_value=.4
            lathe('Backbar glass bottle',x,3.2,z+.035,[(0,0),(.07,0),(.073,.25),(.03,.32),(.025,.44),(.03,.45)],bottle_material)
            box('Bottle paper label',(x,3.125,z+.2),(.105,.005,.13),linen,.003)
# Menu board has actual legible lettering and prices.
box('Cafe chalkboard',(13.2,3.42,2.65),(4,.12,1.8),black,.04)
place(text('Cafe menu title','MIRAMAR',(13.2,3.33,3.27),.23,linen))
for i,line in enumerate(['ESPRESSO                 3.00','FLAT WHITE              4.50','ICED LATTE               5.00','FRESH CROISSANT      3.50','APERITIVO                9.00']):
    place(text('Cafe menu line',line,(13.2,3.32,2.97-i*.22),.125,linen))
# Espresso machine with group heads, a drip tray, pressure gauges, and steam wands.
box('Espresso machine polished body',(22.1,.08,2.16),(1.45,.69,.60),brass,.09)
box('Espresso machine dark front',(22.1,-.30,2.12),(1.28,.04,.39),black,.035)
box('Espresso drip tray',(22.1,-.51,1.96),(1.40,.38,.065),brass,.015)
for dx in [-.36,.36]:
    rod('Espresso group head',(22.1+dx,-.38,2.21),(22.1+dx,-.38,2.04),.085,brass,24)
    rod('Portafilter handle',(22.1+dx,-.38,2.07),(22.1+dx,-.64,2.07),.035,black,16)
    rod('Pressure gauge rim',(22.1+dx,-.325,2.30),(22.1+dx,-.36,2.30),.055,brass,32)
    rod('Pressure gauge face',(22.1+dx,-.363,2.30),(22.1+dx,-.365,2.30),.047,ceramic,32)
for dx in [-.62,.62]: rod('Steam wand',(22.1+dx,-.3,2.18),(22.1+dx,-.58,1.98),.016,brass)
for i in range(14): box('Drip tray perforation',(21.5+i*.09,-.52,2.0),(.015,.24,.008),black)
box('Coffee grinder base',(23.4,.08,1.99),(.38,.45,.24),black,.04)
rod('Coffee grinder hopper',(23.4,.08,2.18),(23.4,.08,2.55),.15,clear,32)
rod('Coffee beans in hopper',(23.4,.08,2.18),(23.4,.08,2.4),.135,oak,32)
# Pastry vitrine uses true glass, thin metal frames, and scanned pastries.
box('Pastry display base',(16,-.3,1.91),(2.3,1.05,.13),marble,.025)
box('Pastry glass front',(16,-.83,2.28),(2.3,.012,.64),clear)
box('Pastry glass roof',(16,-.3,2.60),(2.3,1.05,.012),clear)
for x in [14.85,17.15]: box('Pastry glass side',(x,-.3,2.28),(.012,1.05,.64),clear)
for x in [14.85,17.15]: rod('Vitrine brass upright',(x,-.83,1.97),(x,-.83,2.6),.015,brass)

CURRENT_GROUP='Miramar - Seating and furniture'
for x in [14,16,18,20,22,24]: instance('bar_chair_round_01',(x,-2.0,.72),1.02,math.pi)
for y in [-9.2,-5.2]:
    box('Olive leather booth base',(10.6,y,.95),(1.3,2.7,.45),oak,.06)
    box('Olive leather booth seat',(10.7,y,1.24),(1.32,2.65,.18),leather,.10)
    box('Olive leather booth back',(10.1,y,1.78),(.27,2.8,1.25),leather,.10)
    for shift in [-1,-.6,-.2,.2,.6,1]:
        box('Booth vertical padded channel',(10.29,y+shift,1.77),(.08,.34,1.05),leather,.04)
    box('Booth marble table',(12.55,y,1.46),(1.55,2.10,.075),marble,.045)
    rod('Booth table brass pedestal',(12.55,y,.75),(12.55,y,1.4),.065,brass)
    rod('Booth table foot',(12.55,y,.74),(12.55,y,.79),.42,black,32)
for x,y in [(18,-8),(22,-8),(18,-4.8),(23,-11.3)]:
    instance('outdoor_table_chair_set_01',(x,y,.72),.85,math.pi/2)
for x,y in [(25.1,-12.3),(10.8,-1.8),(25,1.5)]: instance('potted_plant_02',(x,y,.72),1.25)
for x in [15.3,15.8,16.3]: instance('croissant',(x,-.4,1.99),.075,random.uniform(0,6))
instance('carrot_cake',(16.7,-.2,1.99),.24)
for x,y,z in [(12.55,-9.2,1.50),(12.55,-5.2,1.50),(18,-8,1.46),(22,-8,1.46),(18,-4.8,1.46),(23,-11.3,1.46)]:
    for dx in [-.23,.23]:
        lathe('Cafe saucer',x+dx,y,z,[(0,0),(.10,.003),(.115,.02),(.10,.026),(0,.01)],ceramic)
        lathe('Cafe cup',x+dx,y,z+.015,[(.03,0),(.045,.02),(.06,.095),(.055,.10),(.036,.02)],ceramic)
    rod('Small tabletop vase',(x,y+.27,z),(x,y+.27,z+.19),.045,brass,20)
# Pendants, ceiling spots, and concealed LEDs establish warm indoor contrast.
CURRENT_GROUP='Miramar - Interior lighting'
for x,y in [(12.5,-9.2),(12.5,-5.2),(18,-8),(22,-8),(18,-4.8),(23,-11.3),(15,-.3),(19,-.3),(23,-.3)]:
    rod('Pendant braided cable',(x,y,3.72),(x,y,2.9),.012,black)
    lathe('Brass pendant shade',x,y,2.68,[(.31,0),(.32,.03),(.21,.16),(.06,.26),(.03,.28)],brass)
    rod('Pendant glowing diffuser',(x,y,2.685),(x,y,2.695),.275,lightmat,32)
    area_light('Pendant warm pool',(x,y,2.66),(x,y,.7),(1,.65,.36),75,1.1)
area_light('Cafe soft interior ambience',(18,-6,3.65),(18,-5,.7),(1,.77,.54),380,7)
area_light('Open doorway daylight',(18,-14.8,3),(18,-4,1.8),(.55,.70,1),450,7)
area_light('Backbar shelf wash',(20,2.3,3.65),(20,3.4,2.4),(1,.54,.24),100,4)
# Imported images are resolved and packed for a portable deliverable.
paths={p.name:p for p in ASSETS.rglob('*') if p.suffix.lower() in ['.jpg','.png','.exr','.hdr']}
for image in bpy.data.images:
    if image.source=='FILE' and not image.packed_file:
        name=Path(bpy.path.abspath(image.filepath)).name
        if name in paths: image.filepath=str(paths[name]); image.reload()
CURRENT_GROUP='Miramar - Inspection cameras'
inside=camera('08 - Inside Cafe Miramar',(24.7,-12.3,2.05),(16,-.1,1.95),23)
window_camera=camera('09 - Real glazing and room depth',(47,-22,8),(39,-12.5,9.5),43)
scene.camera=bpy.data.objects['07 - Cafe materials and street props']
scene.cycles.samples=40
scene.render.resolution_x=1600
scene.render.resolution_y=1100
scene.render.filepath=str(RENDERS/'miramar-exterior.png')
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            area.spaces.active.region_3d.view_perspective='CAMERA'
scene['Window upgrade']='True wall openings, clear transmission glass, frames, curtains and furnished room depth.'
scene['Cafe interior']='Open customer circulation, booths, furniture, walnut floor, marble bar, espresso machine, pastry case, menu and warm pendant lighting.'
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(SCENES/'coastal-city-interiors.blend'))
print('INTERIOR_SAVED',len(scene.objects),flush=True)
bpy.ops.render.render(write_still=True)
scene.camera=inside
scene.render.filepath=str(RENDERS/'miramar-interior.png')
bpy.ops.render.render(write_still=True)
scene.camera=window_camera
scene.render.filepath=str(RENDERS/'miramar-windows.png')
bpy.ops.render.render(write_still=True)
print('INTERIOR_COMPLETE',flush=True)
