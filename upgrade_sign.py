"""Build an original neon Art Deco sign for the tropical urban cafe."""
import ast
import math
from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parent
for filename in ['build_world.py','build_city.py']:
    for node in ast.parse((ROOT/filename).read_text(encoding='utf-8')).body:
        if isinstance(node,ast.FunctionDef) and node.name in ['material','text','area_light','collection','place','box','rod']:
            exec(compile(ast.Module(body=[node],type_ignores=[]),filename,'exec'))
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'coastal-city-interiors.blend'))
scene=bpy.context.scene
CURRENT_GROUP='Miramar - Art Deco neon signage'
MESH_CACHE={}
for obj in list(scene.objects):
    if obj.name.startswith(('Cafe marquee','Cafe tagline','Cafe sign glow')):
        bpy.data.objects.remove(obj,do_unlink=True)
navy=material('Sign enamel midnight petrol',(.009,.025,.035),metallic=.4,roughness=.27)
brass=material('Sign aged champagne brass',(.53,.32,.12),metallic=.85,roughness=.29)
pink=material('Sign hot coral neon',(1,.014,.12),emission=5)
aqua=material('Sign electric aqua',(.025,1,.74),emission=4)
cream=material('Sign warm white neon',(1,.78,.42),emission=2.8)
black=material('Sign black mounting hardware',(.012,.016,.022),metallic=.65,roughness=.4)
# Keep the upper windows clear and anchor the sign between the shop lintel and sill.
box('Stepped enamel marquee',(18,-14.46,4.82),(16.8,.40,1.28),navy,.14)
box('Marquee upper stepped cap',(18,-14.40,5.50),(13.8,.32,.10),brass,.03)
box('Marquee lower stepped cap',(18,-14.40,4.14),(13.8,.32,.10),brass,.03)
for x in [9.4,26.6]:
    box('Marquee Art Deco end block',(x,-14.47,4.82),(.55,.48,1.0),navy,.1)
    for z in [4.53,4.82,5.11]:
        box('Marquee wing accent',(x,-14.75,z),(1.08,.045,.035),pink,.014)

def tube(name,points,surface,radius=.018):
    """Create a continuous rounded neon tube along a designed polyline."""
    data=bpy.data.curves.new(name,'CURVE')
    data.dimensions='3D'
    data.resolution_u=16
    data.bevel_depth=radius
    data.bevel_resolution=4
    spline=data.splines.new('POLY')
    spline.points.add(len(points)-1)
    for point,co in zip(spline.points,points): point.co=(*co,1)
    obj=bpy.data.objects.new(name,data)
    collection(CURRENT_GROUP).objects.link(obj)
    obj.data.materials.append(surface)
    return obj

def rounded_border(name,cx,cy,cz,width,height,surface):
    """Trace a radiused rectangular neon border in the facade plane."""
    radius=.17
    points=[]
    for corner_x,corner_z,start in [(cx+width/2-radius,cz+height/2-radius,0),(cx-width/2+radius,cz+height/2-radius,90),(cx-width/2+radius,cz-height/2+radius,180),(cx+width/2-radius,cz-height/2+radius,270)]:
        for step in range(9):
            angle=math.radians(start+step*90/8)
            points.append((corner_x+radius*math.cos(angle),cy,corner_z+radius*math.sin(angle)))
    points.append(points[0])
    tube(name,points,surface,.014)
rounded_border('Coral neon outline',18,-14.70,4.82,16.35,1.08,pink)
# Dimensional backing and offset luminous faces keep the lettering readable in daylight.
back=place(text('Miramar metal letter bodies','M I R A M A R',(18,-14.73,4.73),.65,brass))
back.data.extrude=.052
front=place(text('Miramar luminous letter faces','M I R A M A R',(18,-14.81,4.73),.65,aqua))
front.data.extrude=.012
front.data.bevel_depth=.009
place(text('Marquee cafe label','C A F É',(11.75,-14.79,4.75),.28,cream))
place(text('Marquee late night label','LATE\nNIGHTS',(24.1,-14.79,4.89),.19,cream))
place(text('Miramar supporting line','ESPRESSO   •   COCKTAILS   •   GOOD TIMES',(18,-14.80,4.39),.145,cream))
# A small neon sunrise over waves gives the venue its own original symbol.
points=[(11.75+.38*math.cos(a),-14.8,5.06+.19*math.sin(a)) for a in [i*math.pi/24 for i in range(25)]]
tube('Cafe neon sunrise',points,pink,.012)
for offset in [0,.075]:
    tube('Neon ocean wave',[(11.28+i*.047,-14.8,4.46+offset+.018*math.sin(i*.7)) for i in range(21)],aqua,.009)
# A double-sided blade sign perpendicular to the facade reads along the boulevard.
box('Blade sign metal cabinet',(26.8,-15.3,5.12),(.22,1.40,2.35),navy,.1)
for y in [-14.75,-15.86]:
    rod('Blade sign bracket',(26.8,-14.1,5.9),(26.8,y,5.9),.035,black)
# Text local plane is rotated to face east/west, with readable lettering on each face.
for side in [-1,1]:
    x=26.8+side*.14
    label=place(text('Blade sign cafe lettering','C\nA\nF\nÉ',(x,-15.3,5.77),.33,aqua))
    label.rotation_euler=(math.pi/2,0,side*math.pi/2)
    label.data.space_line=1.08
    for y in [-15.87,-14.73]:
        tube('Blade coral vertical edge',[(x,y,4.09),(x,y,6.15)],pink,.016)
    tube('Blade coral lower edge',[(x,-15.87,4.09),(x,-14.73,4.09)],pink,.016)
    tube('Blade coral upper edge',[(x,-15.87,6.15),(x,-14.73,6.15)],pink,.016)
# Local pools of colored light support the neon without tinting the entire city.
area_light('Miramar aqua sign spill',(17,-15.05,4.65),(17,-17.1,2),(.05,1,.68),95,5)
area_light('Miramar coral wing spill',(25,-14.95,4.7),(25,-15.9,3.1),(1,.015,.12),45,2)
scene.camera=bpy.data.objects['07 - Cafe materials and street props']
scene.cycles.samples=40
scene.render.resolution_x=1600
scene.render.resolution_y=1100
scene.render.filepath=str(ROOT/'miramar-neon-sign.png')
scene['Sign direction']='Original tropical Art Deco signage inspired by 1980s Miami nightlife; aqua and coral neon, dimensional letters, sunrise waves, and a double-sided blade sign.'
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'coastal-city-neon.blend'))
bpy.ops.render.render(write_still=True)
print('NEON_COMPLETE',flush=True)
