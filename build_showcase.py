"""Upgrade a central city block using scanned PBR assets and detailed architecture."""
import ast
import math
import random
from pathlib import Path
import bpy
from mathutils import Vector, Matrix
ROOT=Path(__file__).resolve().parent
ASSETS=ROOT/'assets'
# Reuse only constructors, never the scene-generation statements.
for filename in ['build_world.py','build_city.py']:
    for node in ast.parse((ROOT/filename).read_text(encoding='utf-8')).body:
        if isinstance(node,ast.FunctionDef) and node.name in ['material','text','area_light','collection','place','box','rod']:
            exec(compile(ast.Module(body=[node],type_ignores=[]),filename,'exec'))
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'coastal-city.blend'))
scene=bpy.context.scene
random.seed(73)
CURRENT_GROUP='Showcase - Detailed architecture'
MESH_CACHE={}
cream=bpy.data.materials['Warm ivory architectural trim']
metal=bpy.data.materials['Dark bronze metal']
glass=bpy.data.materials['Smoked blue glass']
wood=bpy.data.materials['Palm bark and timber']
pink=bpy.data.materials['Neon flamingo pink']
cyan=bpy.data.materials['Neon lagoon cyan']
yellow=bpy.data.materials['Warm interior lighting']
# Remove the two southern buildings and their immediate props from the showcase block.
for obj in list(scene.objects):
    x,y,z=obj.location
    if obj.type in {'MESH','FONT','CURVE'} and 8<x<53 and -19<y<3 and z>.25:
        bpy.data.objects.remove(obj,do_unlink=True)
# Clear nearby low-detail cars and scale figures so the close view is coherent.
for obj in list(scene.objects):
    x,y,z=obj.location
    if 3<x<78 and -35<y<-18 and any(word in obj.name.lower() for word in ['coupe','tire','wheel','headlight','rear light','bumper','pedestrian','signal']):
        bpy.data.objects.remove(obj,do_unlink=True)

def pbr(name,asset,tile_size=3,tint=None,wet=False):
    """Build a meter-scaled PBR material from downloaded scan maps."""
    result=material(name,(.5,.5,.5))
    nodes=result.node_tree.nodes
    links=result.node_tree.links
    shader=nodes.get('Principled BSDF')
    coords=nodes.new('ShaderNodeTexCoord')
    coords.object=bpy.data.objects.get('Texture space origin')
    mapping=nodes.new('ShaderNodeVectorMath')
    mapping.operation='SCALE'
    mapping.inputs[3].default_value=1/tile_size
    links.new(coords.outputs['Object'],mapping.inputs[0])
    paths=list((ASSETS/asset).glob('*'))
    textures={}
    for channel,tag in [('color','_diff_'),('rough','_rough_'),('height','_disp_')]:
        path=next((p for p in paths if tag in p.name),None)
        if path is None: continue
        node=nodes.new('ShaderNodeTexImage')
        node.image=bpy.data.images.load(str(path),check_existing=True)
        node.image.colorspace_settings.name='sRGB' if channel=='color' else 'Non-Color'
        node.projection='BOX'
        node.projection_blend=.2
        links.new(mapping.outputs[0],node.inputs['Vector'])
        textures[channel]=node
    if tint:
        mix=nodes.new('ShaderNodeMixRGB')
        mix.blend_type='MULTIPLY'
        mix.inputs[0].default_value=.68
        mix.inputs[2].default_value=(*tint,1)
        links.new(textures['color'].outputs['Color'],mix.inputs[1])
        links.new(mix.outputs[0],shader.inputs['Base Color'])
    else:
        links.new(textures['color'].outputs['Color'],shader.inputs['Base Color'])
    if 'rough' in textures: links.new(textures['rough'].outputs['Color'],shader.inputs['Roughness'])
    if 'height' in textures:
        bump=nodes.new('ShaderNodeBump')
        bump.inputs['Strength'].default_value=.45
        bump.inputs['Distance'].default_value=.06
        links.new(textures['height'].outputs[0],bump.inputs['Height'])
        links.new(bump.outputs[0],shader.inputs['Normal'])
    if wet:
        noise=nodes.new('ShaderNodeTexNoise')
        noise.inputs['Scale'].default_value=.38
        noise.inputs['Detail'].default_value=3
        links.new(coords.outputs['Object'],noise.inputs['Vector'])
        ramp=nodes.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].position=.42
        ramp.color_ramp.elements[0].color=(.12,.12,.12,1)
        ramp.color_ramp.elements[1].position=.61
        ramp.color_ramp.elements[1].color=(.78,.78,.78,1)
        links.new(noise.outputs['Fac'],ramp.inputs[0])
        links.new(ramp.outputs[0],shader.inputs['Roughness'])
        shader.inputs['Coat Weight'].default_value=.22
        shader.inputs['Coat Roughness'].default_value=.14
    return result

origin=bpy.data.objects.new('Texture space origin',None)
collection(CURRENT_GROUP).objects.link(origin)
plaster=pbr('PBR - Coral weathered plaster','red_plaster_weathered',4)
white=pbr('PBR - Warm mineral render','white_plaster_rough_02',3,tint=(.94,.83,.67))
blue=pbr('PBR - Weathered teal plaster','blue_plaster_weathered',4,tint=(.38,.87,.76))
brick=pbr('PBR - Brown masonry','brown_brick_02',3)
pavement=pbr('PBR - Concrete sidewalk slabs','concrete_pavement',3)
asphalt=pbr('PBR - Rain-darkened asphalt','asphalt_02',5,wet=True)
bark=pbr('PBR - Palm trunk bark','palm_bark',1.4)
brass=material('Brushed champagne brass',(.48,.30,.11),metallic=.8,roughness=.28)
black=material('Black powder-coated framing',(.014,.025,.029),metallic=.65,roughness=.3)
clear=material('Architectural reflective glazing',(.19,.29,.31),metallic=.15,roughness=.08)
clear.node_tree.nodes.get('Principled BSDF').inputs['Transmission Weight'].default_value=.65
clear.node_tree.nodes.get('Principled BSDF').inputs['IOR'].default_value=1.45
fabric=material('Ivory woven awning',(.68,.62,.46),roughness=.9)
leaves=material('Detailed palm leaf',(.105,.27,.045),roughness=.48)
leaves.node_tree.nodes.get('Principled BSDF').inputs['Subsurface Weight'].default_value=.12
for obj in scene.objects:
    if obj.type!='MESH': continue
    for slot in obj.material_slots:
        if slot.material and slot.material.name=='Asphalt': slot.material=asphalt

# A genuinely open ground floor exposes a lit lobby and cafe interior.
box('Hotel upper plaster volume',(40,-5,11.4),(20,18,15),plaster,.09)
box('Hotel lobby rear',(40,3.4,2.4),(20,.35,4),white,.04)
box('Hotel lobby floor',(40,-5,.5),(20,18,.3),pavement)
for x in [30.2,49.8]: box('Hotel lobby sidewall',(x,-5,2.4),(.35,18,4),white,.04)
for x in [30.7,34,46,49.3]:
    box('Ground-floor fluted pier',(x,-14,2.5),(.7,.65,4.2),white,.06)
    for shift in [-.18,0,.18]: box('Pier brass flute',(x+shift,-14.35,2.5),(.045,.045,3.8),brass,.01)
box('Hotel entry stone lintel',(40,-14,4.35),(20.4,.8,.6),white,.08)
for z in [4.75,8.6,12.45,16.3,19.1]:
    box('Facade projecting cornice',(40,-14.15,z),(20.4,.55,.18),white,.04)
for x in [31,34.6,38.2,41.8,45.4,49]:
    for z in [6.65,10.5,14.35,17.9]:
        box('Window stone reveal',(x,-14.06,z),(2.55,.35,2.85),white,.04)
        box('Recessed dark window',(x,-14.27,z),(2.22,.07,2.48),glass,.015)
        for offset in [-1.12,0,1.12]: box('Window bronze mullion',(x+offset,-14.35,z),(.05,.07,2.55),brass,.01)
        for offset in [-1.22,1.22]: box('Window cross frame',(x,-14.35,z+offset),(2.26,.07,.05),brass,.01)
        # Curtains and warm transoms give each opening a distinct interior impression.
        if random.random()<.55:
            box('Window inner curtain',(x+.65,-14.38,z),(.30,.025,2.38),fabric,.02)
        if z<17:
            box('Balcony stone slab',(x,-14.8,z-1.5),(2.95,1.7,.18),white,.05)
            rod('Balcony top rail',(x-1.4,-15.6,z-.45),(x+1.4,-15.6,z-.45),.035,brass)
            for offset in [-1.4,-1,-.6,-.2,.2,.6,1,1.4]:
                rod('Balcony baluster',(x+offset,-15.6,z-1.4),(x+offset,-15.6,z-.45),.022,black)
            for side in [-1,1]: rod('Balcony return rail',(x+side*1.4,-15.6,z-.45),(x+side*1.4,-14.1,z-.45),.03,brass)
# Side facade continues around the corner seen in the hero camera.
for z in [6.65,10.5,14.35,17.9]:
    for y in [-11,-7,-3,1]:
        box('Side window reveal',(50.05,y,z),(.20,2.5,2.8),white,.025)
        box('Side reflective window',(50.18,y,z),(.06,2.15,2.5),glass)
        box('Side mullion',(50.23,y,z),(.05,.05,2.5),brass)
box('Art Deco sign tower',(40,-13.8,20.1),(6,1.6,4),white,.14)
for x in [37.8,38.2,41.8,42.2]: box('Crown stepped fin',(x,-14.8,20.1),(.12,.3,4.7),brass,.025)
place(text('Hotel crown lettering','PALM\nROYAL',(40,-14.65,20.3),.85,pink))
box('Entrance canopy',(40,-16,3.7),(10,4.5,.27),black,.1)
box('Canopy illuminated edge',(40,-18.3,3.67),(9.7,.04,.07),yellow,.01)
place(text('Entrance sign','P A L M   R O Y A L',(40,-18.3,3.95),.39,brass))
for x in [35.5,44.5]: rod('Entrance canopy column',(x,-17.8,.55),(x,-17.8,3.65),.075,brass)
for x in [36,38.6,41.2,43.8]:
    box('Lobby glazing',(x,-14.12,2.1),(2.5,.045,2.95),clear,.005)
    rod('Lobby vertical frame',(x-1.25,-14.2,.6),(x-1.25,-14.2,3.6),.035,brass)
for x in [39.6,40.4]: rod('Entrance door pull',(x,-14.35,1.3),(x,-14.35,2.1),.025,brass)
box('Reception desk',(40,-9,1.15),(5,1,1.2),white,.1)
box('Reception brass top',(40,-9,1.79),(5.15,1.15,.1),brass,.04)
place(text('Lobby wall lettering','PALM ROYAL',(40,3.15,2.4),.6,brass))
for x in [34,40,46]:
    area_light('Warm lobby downlight',(x,-8,3.9),(x,-10,.5),(1,.64,.35),180,2)

# Adjacent cafe: textured masonry, fabric awnings, shuttered upper windows.
box('Cafe upper volume',(18,-5,7.4),(17,18,7),blue,.08)
box('Cafe back wall',(18,3.7,2.25),(17,.35,3.8),brick,.04)
box('Cafe floor',(18,-5,.5),(17,18,.3),pavement)
for x in [9.6,26.4]: box('Cafe side return',(x,-5,2.3),(.4,18,3.9),brick)
for x in [10,15.3,20.6,26]: box('Cafe masonry shop pier',(x,-14,2.4),(.7,.6,4),brick,.035)
box('Cafe shop lintel',(18,-14,4.1),(17.6,.7,.45),white,.05)
for x in [12.5,18,23.5]:
    box('Cafe upper window reveal',(x,-14.05,7.1),(2.3,.2,3.2),white,.03)
    box('Cafe upper glass',(x,-14.2,7.1),(1.95,.05,2.8),glass)
    for side in [-1,1]:
        box('Window louver shutter',(x+side*1.5,-14.25,7.1),(.7,.13,2.8),black,.025)
        for z in [5.85+i*.16 for i in range(17)]: box('Shutter blade',(x+side*1.5,-14.34,z),(.61,.09,.06),blue,.008)
    box('Cafe awning',(x,-15.2,3.45),(4.6,2.7,.1),fabric,.02).rotation_euler.x=.15
    for dx in [-1.8,-.9,0,.9,1.8]:
        box('Awning teal stripe',(x+dx,-15.2,3.53),(.40,2.7,.014),blue).rotation_euler.x=.15
    rod('Awning front frame',(x-2.3,-16.5,3.2),(x+2.3,-16.5,3.2),.025,black)
box('Cafe marquee panel',(18,-14.22,4.8),(16,.2,.85),black,.05)
place(text('Cafe marquee','CAFÉ  MIRAMAR',(18,-14.36,4.57),.67,cyan))
place(text('Cafe tagline','ESPRESSO    •    COCKTAILS    •    VINYL',(18,-14.37,4.26),.19,white))
box('Cafe interior bar',(17,-10.5,1.15),(10,1,1.2),wood,.04)
box('Cafe bar marble top',(17,-10.5,1.8),(10.2,1.2,.12),white,.04)
for x in [12,16,20,24]:
    rod('Pendant cord',(x,-10.5,3.9),(x,-10.5,2.7),.012,black)
    rod('Pendant brass shade',(x,-10.5,2.55),(x,-10.5,2.8),.26,brass,32)
    area_light('Cafe pendant',(x,-10.5,2.5),(x,-10.5,.5),(1,.5,.22),65,1)
for x in [11+i*.45 for i in range(31)]:
    for z in [1.3,2,2.7]:
        if random.random()<.55:
            rod('Bar display bottle',(x,2.9,z),(x,2.9,z+.3),.07,glass)
            rod('Bottle neck',(x,2.9,z+.3),(x,2.9,z+.43),.025,glass)
for z in [1.25,1.95,2.65]: box('Bar display shelf',(18,3,z),(15,.7,.08),wood)

CURRENT_GROUP='Showcase - Pavement details'
box('Detailed sidewalk',(30,-17,.39),(47,5,.18),pavement)
for x in range(7,54):
    box('Individual granite curb',(x,-19.45,.28),(.97,.3,.36),white,.04)
for x in [14,30,46]:
    box('Storm drain frame',(x,-19.9,.125),(1.4,.45,.07),black,.025)
    for offset in [i*.11 for i in range(-5,6)]: box('Storm drain grate',(x+offset,-19.9,.17),(.035,.40,.028),metal,.008)
# Palms with individually modeled leaflets replace the broad ribbon silhouettes.
CURRENT_GROUP='Showcase - Detailed tropical vegetation'
def detailed_palm(x,y,height):
    """Model a tapered ringed trunk and hundreds of pinnate leaflets."""
    vertices=[]
    faces=[]
    segments=48
    sides=16
    for ring in range(segments+1):
        t=ring/segments
        radius=.26*(1-.38*t)*(1+.04*math.sin(ring*2.4))
        for side in range(sides):
            a=side*math.tau/sides
            vertices.append((x+.55*t*t+radius*math.cos(a),y+radius*math.sin(a),.5+height*t))
    for ring in range(segments):
        for side in range(sides):
            a=ring*sides+side
            b=ring*sides+(side+1)%sides
            faces.append((a,b,b+sides,a+sides))
    mesh=bpy.data.meshes.new('Detailed palm trunk')
    mesh.from_pydata(vertices,[],faces)
    mesh.materials.append(bark)
    obj=bpy.data.objects.new('Textured curved palm trunk',mesh)
    collection(CURRENT_GROUP).objects.link(obj)
    for poly in mesh.polygons: poly.use_smooth=True
    top=Vector((x+.55,y,height+.5))
    points=[]
    leaf_faces=[]
    for frond in range(19):
        angle=frond*2.39996
        length=random.uniform(3.4,4.6)
        forward=Vector((math.cos(angle),math.sin(angle),0))
        side=Vector((-math.sin(angle),math.cos(angle),0))
        rise=random.uniform(.9,2.1)
        previous=top
        for step in range(1,32):
            t=step/32
            center=top+forward*length*t+Vector((0,0,rise*math.sin(t*math.pi)-1.5*t*t))
            if step%3==0: rod('Palm central rachis',previous,center,.015,leaves,6); previous=center
            for sign in [-1,1]:
                leaflet_length=(.88*math.sin(t*math.pi)**.6+.04)*random.uniform(.85,1.15)
                tip=center+side*leaflet_length*sign+forward*.30+Vector((0,0,-.23-leaflet_length*.28))
                mid=(center+tip)/2+Vector((0,0,.11))
                width=.035*math.sin(t*math.pi)
                start=len(points)
                points.extend([center,mid+forward*width,tip,mid-forward*width])
                leaf_faces.append((start,start+1,start+2,start+3))
    mesh=bpy.data.meshes.new('Individual pinnate leaflets')
    mesh.from_pydata(points,[],leaf_faces)
    mesh.materials.append(leaves)
    obj=bpy.data.objects.new('Detailed palm crown',mesh)
    collection(CURRENT_GROUP).objects.link(obj)
    box('Palm stone tree pit',(x,y,.49),(1.3,1.3,.14),black,.07)
for x,y,h in [(7,-17,9),(28,-17,11),(53,-17,10),(56,-4,11)]: detailed_palm(x,y,h)

CURRENT_GROUP='Showcase - Scanned assets'
TEMPLATES={}
def load_template(name):
    """Append native asset geometry, preserving its original UVs and materials."""
    if name in TEMPLATES: return TEMPLATES[name]
    path=ASSETS/name/(name+'.blend')
    with bpy.data.libraries.load(str(path),link=False) as (source,destination):
        chosen=name+'_LOD1' if name=='island_tree_01' else name
        destination.collections=[chosen]
    template=destination.collections[0]
    scene.collection.children.link(template)
    for obj in list(template.all_objects):
        if any(term in obj.name.lower() for term in ['aged','rusted']):
            bpy.data.objects.remove(obj,do_unlink=True)
    bpy.context.view_layer.update()
    geometry=[obj for obj in template.all_objects if obj.type=='MESH']
    points=[obj.matrix_world@Vector(corner) for obj in geometry for corner in obj.bound_box]
    low=Vector(tuple(min(p[i] for p in points) for i in range(3)))
    high=Vector(tuple(max(p[i] for p in points) for i in range(3)))
    template.instance_offset=((low.x+high.x)/2,(low.y+high.y)/2,low.z)
    scene.collection.children.unlink(template)
    TEMPLATES[name]=(template,high-low)
    print('ASSET_LOADED',name,tuple(high-low),flush=True)
    return TEMPLATES[name]

def instance(name,location,height=None,angle=0):
    """Instance a detailed asset at true street scale."""
    template,bounds=load_template(name)
    obj=bpy.data.objects.new(name+' instance',None)
    obj.instance_type='COLLECTION'
    obj.instance_collection=template
    collection(CURRENT_GROUP).objects.link(obj)
    obj.location=location
    obj.rotation_euler.z=angle
    if height: obj.scale=(height/max(bounds.z,.01),)*3
    return obj

for x in [11.5,17,22.5]:
    instance('outdoor_table_chair_set_01',(x,-16.5,.5),.85,math.pi/2)
    instance('outdoor_table_chair_set_01',(x,-7,.52),.85,math.pi/2)
for x in [31.5,48.3]: instance('potted_plant_02',(x,-15.1,.5),1.25)
for x,y in [(33,-17.2),(47,-17.2)]: instance('painted_wooden_bench',(x,y,.51),.95)
instance('fire_hydrant',(51,-18.6,.5),1.0)
instance('water_manhole_cover',(44,-22.2,.125),None)
for x in [10,25,51]: instance('street_lamp_01',(x,-18.9,.49),4.3)
for x in [12,24,35,46]: instance('exterior_aircon_unit',(x,-8,19.1 if x>30 else 11),.9)
instance('island_tree_01',(4,-13,.5),7.5)
instance('island_tree_01',(56,6,.5),8)
# Import the uncompressed, fully modeled car with its original PBR interior and tires.
before=set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath=str(ASSETS/'CarConcept/CarConcept-uncompressed.glb'))
imported=set(bpy.data.objects)-before
car_collection=bpy.data.collections.new('Car Concept - Eric Chadwick CC BY 4.0')
for obj in imported:
    for previous in list(obj.users_collection): previous.objects.unlink(obj)
    car_collection.objects.link(obj)
scene.collection.children.link(car_collection)
bpy.context.view_layer.update()
points=[obj.matrix_world@Vector(corner) for obj in imported if obj.type=='MESH' for corner in obj.bound_box]
low=Vector(tuple(min(p[i] for p in points) for i in range(3)))
high=Vector(tuple(max(p[i] for p in points) for i in range(3)))
car_collection.instance_offset=((low.x+high.x)/2,(low.y+high.y)/2,low.z)
scene.collection.children.unlink(car_collection)
car=bpy.data.objects.new('Detailed metallic concept car',None)
car.instance_type='COLLECTION'
car.instance_collection=car_collection
collection(CURRENT_GROUP).objects.link(car)
car.location=(39,-22.1,.15)
car.scale=(4.9/max(high.x-low.x,high.y-low.y),)*3
car.rotation_euler.z=math.pi/2
print('CAR_BOUNDS',tuple(high-low),flush=True)
# Resolve texture paths from every imported library before packing the deliverable.
texture_paths={p.name:p for p in ASSETS.rglob('*') if p.suffix.lower() in ['.png','.jpg','.exr','.hdr']}
for image in bpy.data.images:
    if image.source=='FILE' and not image.packed_file:
        filename=Path(bpy.path.abspath(image.filepath)).name
        if filename in texture_paths:
            image.filepath=str(texture_paths[filename])
            image.reload()

CURRENT_GROUP='Showcase - Lighting and cameras'
world_nodes=scene.world.node_tree.nodes
world_links=scene.world.node_tree.links
environment=world_nodes.new('ShaderNodeTexEnvironment')
environment.image=bpy.data.images.load(str(ASSETS/'venice_sunset.hdr'),check_existing=True)
world_links.new(environment.outputs['Color'],world_nodes.get('Background').inputs['Color'])
world_nodes.get('Background').inputs['Strength'].default_value=.38
for obj in scene.objects:
    if obj.type=='LIGHT' and obj.data.type=='SUN':
        obj.data.energy=1.4
        obj.rotation_euler=(math.radians(62),math.radians(-25),math.radians(-30))
area_light('Warm facade softbox',(22,-40,26),(33,-10,8),(1,.72,.46),2400,20)
area_light('Cool street reflection',(58,-26,15),(35,-12,5),(.24,.53,1),1100,12)
area_light('Hotel neon glow',(40,-15,20),(40,-18,14),(1,.035,.20),130,4)
area_light('Cafe sign glow',(18,-15,5),(18,-17,1),(.02,.65,1),110,5)

def camera(name,location,target,lens):
    """Create a cinematic perspective camera for close visual assessment."""
    data=bpy.data.cameras.new(name)
    data.lens=lens
    data.clip_end=2000
    obj=bpy.data.objects.new(name,data)
    collection(CURRENT_GROUP).objects.link(obj)
    obj.location=location
    obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
    return obj
hero=camera('06 - Detailed Palm Royal block',(65,-48,7.2),(31,-12,8),34)
close=camera('07 - Cafe materials and street props',(29,-26,2.1),(17,-14,3.1),35)
scene.camera=hero
scene.cycles.samples=48
scene.cycles.use_denoising=True
scene.render.resolution_x=1800
scene.render.resolution_y=1250
scene.render.resolution_percentage=100
scene.render.filepath=str(ROOT/'showcase-hero.png')
scene.view_settings.exposure=.3
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            space=area.spaces.active
            space.region_3d.view_perspective='CAMERA'
            space.region_3d.view_camera_zoom=10
            space.shading.type='MATERIAL'
            space.overlay.show_overlays=False
scene['Quality upgrade']='Detailed central block with real PBR textures, imported scan assets, detailed palms and a CC BY concept car. The rest of the city remains a stylized context.'
scene['Asset credits']='Powered by Poly Haven (CC0 assets); Car Concept by Eric Chadwick, Darmstadt Graphics Group GmbH, CC BY 4.0. See ASSET-CREDITS.md.'
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'coastal-city-detailed.blend'))
print('SHOWCASE_SAVED',len(scene.objects),flush=True)
bpy.ops.render.render(write_still=True)
scene.camera=close
scene.render.filepath=str(ROOT/'showcase-closeup.png')
scene.render.resolution_x=1600
scene.render.resolution_y=1100
bpy.ops.render.render(write_still=True)
print('SHOWCASE_COMPLETE',flush=True)
