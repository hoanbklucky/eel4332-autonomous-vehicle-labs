"""Build Gazebo/reference assets from geographic layout.json; Python stdlib only.

OSM data attribution and the PDF-inferred additions are recorded in layout.json.
The footprints are not replaced by arbitrary boxes. STATIC collision and visual
meshes share triangulated geometry; map pixels use the same footprint polygons.
"""
from pathlib import Path
from collections import deque
import json, math, struct, zlib, hashlib, xml.etree.ElementTree as ET
from html import escape

ROOT = Path(__file__).resolve().parent
DATA = json.loads((ROOT / 'layout.json').read_text())
RES = float(DATA.get('reference_resolution_m', .25))


def area(p):
    return sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(p,p[1:]+p[:1]))/2


def cross(a,b,c):
    return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])


def clean(poly):
    p = [tuple(v) for v in poly]
    if p[0] == p[-1]: p.pop()
    change = True
    while change and len(p)>3:
        change=False
        for i in range(len(p)):
            if abs(cross(p[i-1],p[i],p[(i+1)%len(p)]))<1e-8:
                p.pop(i);change=True;break
    if area(p)<0:p.reverse()
    return p


def triangles(poly):
    p=clean(poly); ids=list(range(len(p))); faces=[]
    while len(ids)>3:
        for j,i in enumerate(ids):
            a,b,c=ids[j-1],i,ids[(j+1)%len(ids)]
            if cross(p[a],p[b],p[c])<=1e-9:continue
            if any(k not in (a,b,c) and min(cross(p[a],p[b],p[k]),cross(p[b],p[c],p[k]),cross(p[c],p[a],p[k]))>=-1e-9 for k in ids):continue
            faces.append((a,b,c));ids.pop(j);break
        else:raise ValueError('Polygon cannot be triangulated')
    faces.append(tuple(ids))
    assert abs(sum(abs(cross(p[a],p[b],p[c]))/2 for a,b,c in faces)-abs(area(p)))<1e-4
    return p,faces


def mesh(poly,h,path):
    p,faces=triangles(poly);n=len(p)
    vertices=[(round(x,5),round(y,5),round(z,5)) for z in (0,h) for x,y in p]
    indexed=[]
    for a,b,c in faces:indexed += [(a+n,b+n,c+n),(c,b,a)]
    for i in range(n):
        j=(i+1)%n
        indexed += [(i,j,j+n),(i,j+n,i+n)]
    # Flat-shaded triangles: explicit position/normal pairs for every corner.
    # DART rejects imported collision submeshes with missing vertex normals.
    points=[];normals=[]
    for face in indexed:
        a,b,c=[vertices[i] for i in face]
        u=[b[k]-a[k] for k in range(3)];v=[c[k]-a[k] for k in range(3)]
        normal=(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0])
        length=math.sqrt(sum(x*x for x in normal))
        if length<1e-12:raise ValueError(f'Degenerate triangle in {path}')
        normal=tuple(x/length for x in normal)
        points.extend((a,b,c));normals.extend((normal,normal,normal))
    text=['# Extruded static campus footprint; explicit flat vertex normals','s off']
    text += [f'v {x:.5f} {y:.5f} {z:.5f}' for x,y,z in points]
    text += [f'vn {x:.9f} {y:.9f} {z:.9f}' for x,y,z in normals]
    text += [f'f {i+1}//{i+1} {i+2}//{i+2} {i+3}//{i+3}' for i in range(0,len(points),3)]
    path.write_text('\n'.join(text)+'\n')
    return p


def color(h):return ' '.join(str(int(h[i:i+2],16)/255) for i in (1,3,5))+' 1'


def material(node,c):
    m=ET.SubElement(node,'material')
    ET.SubElement(m,'ambient').text=color(c)
    ET.SubElement(m,'diffuse').text=color(c)


def solid(world,v,h,c,collision=True):
    m=ET.SubElement(world,'model',name=v['id']);ET.SubElement(m,'static').text='true'
    link=ET.SubElement(m,'link',name='body')
    for typ in (['collision','visual'] if collision else ['visual']):
        node=ET.SubElement(link,typ,name=typ);g=ET.SubElement(node,'geometry')
        me=ET.SubElement(g,'mesh');ET.SubElement(me,'uri').text='meshes/'+v['id']+'.obj'
        if typ=='visual':material(node,c)


def box(world,name,x,y,w,d,h,c,yaw=0,z=None,collision=False):
    m=ET.SubElement(world,'model',name=name);ET.SubElement(m,'static').text='true'
    ET.SubElement(m,'pose').text=f'{x} {y} {h/2 if z is None else z} 0 0 {yaw}'
    l=ET.SubElement(m,'link',name='body')
    for typ in (['collision','visual'] if collision else ['visual']):
        v=ET.SubElement(l,typ,name=typ);g=ET.SubElement(v,'geometry')
        ET.SubElement(ET.SubElement(g,'box'),'size').text=f'{w} {d} {h}'
        if typ=='visual':material(v,c)


def barrier_poly():
    b=DATA['barrier'];ca,sa=math.cos(b['yaw']),math.sin(b['yaw'])
    return [(b['x']+ca*x-sa*y,b['y']+sa*x+ca*y) for x,y in [(-b['width']/2,-b['depth']/2),(b['width']/2,-b['depth']/2),(b['width']/2,b['depth']/2),(-b['width']/2,b['depth']/2)]]


def obstacles(blocked=False):
    p=[v['points'] for v in DATA['buildings']+DATA['water']]
    x0,y0,x1,y1=DATA['bounds'];t=.18
    p += [[(x0,y0),(x0+t,y0),(x0+t,y1),(x0,y1)],[(x1-t,y0),(x1,y0),(x1,y1),(x1-t,y1)],[(x0,y0),(x1,y0),(x1,y0+t),(x0,y0+t)],[(x0,y1-t),(x1,y1-t),(x1,y1),(x0,y1)]]
    return p+([barrier_poly()] if blocked else [])


def inside(x,y,p):
    hit=False
    for (ax,ay),(bx,by) in zip(p,p[1:]+p[:1]):
        if (ay>y)!=(by>y) and x<(bx-ax)*(y-ay)/(by-ay)+ax:hit=not hit
    return hit


def raster(res,blocked=False):
    x0,y0,x1,y1=DATA['bounds'];w=round((x1-x0)/res);h=round((y1-y0)/res)
    pixels=bytearray([254])*(w*h)
    # Scanline polygon fill: cost scales with polygon rows, not campus area.
    # This keeps the full-size campus reproducible without a Python point loop
    # over tens of millions of cells. Sample at the same cell centers as before.
    for p in obstacles(blocked):
        jmin=max(0,int((y1-max(y for x,y in p))/res)-1)
        jmax=min(h-1,int((y1-min(y for x,y in p))/res)+1)
        for j in range(jmin,jmax+1):
            y=y1-(j+.5)*res
            cuts=sorted(ax+(y-ay)*(bx-ax)/(by-ay)
                        for (ax,ay),(bx,by) in zip(p,p[1:]+p[:1])
                        if (ay>y)!=(by>y))
            for left,right in zip(cuts[::2],cuts[1::2]):
                start=max(0,math.ceil((left-x0)/res-.5))
                stop=min(w,math.ceil((right-x0)/res-.5))
                if stop>start:pixels[j*w+start:j*w+stop]=b'\0'*(stop-start)
    return w,h,pixels


def validate():
    # Coarse whole-campus connectivity only; fine footprint/road checks are
    # separate tests. A byte grid avoids millions of Python set entries.
    res=1.0
    for blocked in (False,True):
        w,h,pix=raster(res,blocked)
        x0,y0,x1,y1=DATA['bounds']
        def cell(v):return (int((v[0]-x0)/res),int((y1-v[1])/res))
        i,j=cell(DATA['stops'][0]['xy']);start=j*w+i
        assert pix[start]!=0,'Home is occupied'
        seen=bytearray(w*h);seen[start]=1;q=deque([start])
        while q:
            index=q.popleft();i=index%w;j=index//w
            for di,dj in ((-1,0),(1,0),(0,-1),(0,1)):
                ii,jj=i+di,j+dj
                if 0<=ii<w and 0<=jj<h:
                    nxt=jj*w+ii
                    if pix[nxt] and not seen[nxt]:seen[nxt]=1;q.append(nxt)
        for v in DATA['stops']+DATA.get('navigation_goals',[]):
            i,j=cell(v['xy']);assert seen[j*w+i],(v['name'],blocked)
    print('Campus markers connected on the coarse obstacle grid; road/footprint checks are separate.')


def organize_campus(world):
    """Separate overlapping ground visuals; nest static scenery at identity."""
    surfaces=[]
    for model in world.findall('model'):
        name=model.get('name')
        if not (name=='ground' or name.startswith('delivery_pad_')
                or name in {v['id'] for key in ('parking','sports') for v in DATA[key]}
                or any(name.startswith(v['id']+'_') for v in DATA['paths'])):
            continue
        if model.find('.//collision') is not None or name.startswith('delivery_pad_'):
            continue
        pose=model.find('pose')
        xyzrpy=list(map(float,pose.text.split())) if pose is not None else [0.0]*6
        size=model.find('.//visual/geometry/box/size')
        if size is not None:
            w,d,h=map(float,size.text.split());x,y,z,_,_,yaw=xyzrpy
            ca,sa=math.cos(yaw),math.sin(yaw)
            pts=[(x+ca*u-sa*v,y+sa*u+ca*v) for u,v in
                 [(-w/2,-d/2),(w/2,-d/2),(w/2,d/2),(-w/2,d/2)]]
            top=z+h/2
        else:
            uri=model.findtext('.//visual/geometry/mesh/uri')
            vertices=[list(map(float,line.split()[1:])) for line in
                      (ROOT/uri).read_text().splitlines() if line.startswith('v ')]
            pts=[v[:2] for v in vertices];top=max(v[2] for v in vertices)
        bounds=(min(p[0] for p in pts),min(p[1] for p in pts),
                max(p[0] for p in pts),max(p[1] for p in pts))
        # Conservative AABB overlap includes crossings and adjacent segment joins.
        used={layer for other,layer in surfaces
              if bounds[0]<=other[2] and other[0]<=bounds[2]
              and bounds[1]<=other[3] and other[1]<=bounds[3]}
        layer=0
        while layer in used:layer+=1
        surfaces.append((bounds,layer))
        xyzrpy[2]+=.006+.003*layer-top
        if pose is None:pose=ET.SubElement(model,'pose')
        pose.text=' '.join(f'{v:.9f}' for v in xyzrpy)
    highest=.006+.003*max((layer for _,layer in surfaces),default=0)
    for model in world.findall('model'):
        if model.get('name').startswith('delivery_pad_'):
            pose=model.find('pose');v=list(map(float,pose.text.split()))
            v[2]=highest+.01+.025/2;pose.text=' '.join(map(str,v))
    campus=ET.SubElement(world,'model',name='campus')
    ET.SubElement(campus,'static').text='true'
    ET.SubElement(campus,'pose').text='0 0 0 0 0 0'
    for model in list(world.findall('model')):
        if model is not campus:
            world.remove(model);campus.append(model)
    print(f'Campus scenery grouped; {len(surfaces)} ground visuals in '
          f'{1+max((layer for _,layer in surfaces),default=0)} separated layers.')


def write_world(blocked):
    root=ET.Element('sdf',version='1.8');world=ET.SubElement(root,'world',name='default')
    p=ET.SubElement(world,'physics',name='physics',type='ignored')
    ET.SubElement(p,'max_step_size').text='.001';ET.SubElement(p,'real_time_factor').text='1'
    for file,name in [('physics','Physics'),('user-commands','UserCommands'),('scene-broadcaster','SceneBroadcaster'),('sensors','Sensors'),('imu','Imu'),('navsat','NavSat')]:
        p=ET.SubElement(world,'plugin',filename=f'gz-sim-{file}-system',name=f'gz::sim::systems::{name}')
        if name=='Sensors':ET.SubElement(p,'render_engine').text='ogre2'
    # ENU datum anchors synthetic GPS readings; horizontal geometry is full-scale meters.
    lon,lat=DATA['origin_lon_lat']
    spherical=ET.SubElement(world,'spherical_coordinates')
    for tag,value in [('surface_model','EARTH_WGS84'),('world_frame_orientation','ENU'),
                      ('latitude_deg',lat),('longitude_deg',lon),('elevation',0),('heading_deg',0)]:
        ET.SubElement(spherical,tag).text=str(value)
    l=ET.SubElement(world,'light',name='sun',type='directional');ET.SubElement(l,'pose').text='0 0 40 0 0 0'
    ET.SubElement(l,'diffuse').text='.9 .9 .9 1';ET.SubElement(l,'direction').text='-.5 .1 -1'
    x0,y0,x1,y1=DATA['bounds']
    box(world,'ground',(x0+x1)/2,(y0+y1)/2,x1-x0+2,y1-y0+2,.1,'#92ae70',z=-.05,collision=True)
    for v in DATA['parking']:solid(world,v,.008,'#a3a6a3',False)
    for v in DATA['sports']:solid(world,v,.012,'#74a365',False)
    for v in DATA['paths']:
        for k,(a,b) in enumerate(zip(v['points'],v['points'][1:])):
            dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy)
            if length<.03:continue
            box(world,v['id']+'_'+str(k),(a[0]+b[0])/2,(a[1]+b[1])/2,length+.03,v['width'],.015 if v['bridge'] else .01,'#ded6bf' if v['kind']=='walk' or v['bridge'] else '#737b7d',yaw=math.atan2(dy,dx))
    for v in DATA['water']:solid(world,v,.45,'#397f99')
    for v in DATA['buildings']:
        solid(world,v,v['height'],v['color'])
        # Minimal roof ribs identify IST without pretending to reproduce its architecture.
        if v['letter']=='G':
            pts=v['points'];cx=sum(x for x,y in pts)/len(pts);cy=sum(y for x,y in pts)/len(pts)
            xx=sum((x-cx)**2 for x,y in pts);yy=sum((y-cy)**2 for x,y in pts);xy=sum((x-cx)*(y-cy) for x,y in pts)
            angle=.5*math.atan2(2*xy,xx-yy);ca,sa=math.cos(angle),math.sin(angle)
            u=[ca*(x-cx)+sa*(y-cy) for x,y in pts];vmin=min(-sa*(x-cx)+ca*(y-cy) for x,y in pts);vmax=max(-sa*(x-cx)+ca*(y-cy) for x,y in pts)
            lo,hi=min(u)*.9,max(u)*.9;rad=(vmax-vmin)/2*.86
            for j in range(23):
                u0=lo+(hi-lo)*j/22;f=math.sqrt(max(0,1-(u0/max(abs(lo),abs(hi)))**2))
                box(world,'IST_roof_rib_'+str(j),cx+ca*u0,cy+sa*u0,.09,max(.12,2*rad*f),.12,'#ffffff',yaw=angle,z=v['height']+.25+.35*f)
    for i,(p,side) in enumerate([(obstacles()[-4],'west'),(obstacles()[-3],'east'),(obstacles()[-2],'south'),(obstacles()[-1],'north')]):
        xs=[x for x,y in p];ys=[y for x,y in p];box(world,'arena_'+side,(min(xs)+max(xs))/2,(min(ys)+max(ys))/2,max(xs)-min(xs),max(ys)-min(ys),.65,'#5c7455',collision=True)
    for i,v in enumerate(DATA['stops']):box(world,'delivery_pad_'+str(i),*v['xy'],.7,.7,.025,'#ffda39')
    if blocked:
        b=DATA['barrier'];box(world,'causeway_barrier',b['x'],b['y'],b['width'],b['depth'],b['height'],'#f3a42d',yaw=b['yaw'],collision=True)
    world.append(ET.fromstring("<gui fullscreen=\"0\">\n<plugin filename=\"MinimalScene\" name=\"3D View\">\n  <gz-gui>\n    <title>3D View</title>\n    <property type=\"bool\" key=\"showTitleBar\">false</property>\n    <property type=\"string\" key=\"state\">docked</property>\n  </gz-gui>\n\n  <engine>ogre2</engine>\n  <scene>scene</scene>\n  <ambient_light>0.4 0.4 0.4</ambient_light>\n  <background_color>0.8 0.8 0.8</background_color>\n  <camera_pose>-10 3 5 0 0.633 1.344</camera_pose>\n</plugin>\n<plugin filename=\"EntityContextMenuPlugin\" name=\"Entity context menu\">\n  <gz-gui>\n    <property key=\"state\" type=\"string\">floating</property>\n    <property key=\"width\" type=\"double\">5</property>\n    <property key=\"height\" type=\"double\">5</property>\n    <property key=\"showTitleBar\" type=\"bool\">false</property>\n  </gz-gui>\n</plugin>\n<plugin filename=\"GzSceneManager\" name=\"Scene Manager\">\n  <gz-gui>\n    <property key=\"resizable\" type=\"bool\">false</property>\n    <property key=\"width\" type=\"double\">5</property>\n    <property key=\"height\" type=\"double\">5</property>\n    <property key=\"state\" type=\"string\">floating</property>\n    <property key=\"showTitleBar\" type=\"bool\">false</property>\n  </gz-gui>\n</plugin>\n<plugin filename=\"InteractiveViewControl\" name=\"Interactive view control\">\n  <gz-gui>\n    <property key=\"resizable\" type=\"bool\">false</property>\n    <property key=\"width\" type=\"double\">5</property>\n    <property key=\"height\" type=\"double\">5</property>\n    <property key=\"state\" type=\"string\">floating</property>\n    <property key=\"showTitleBar\" type=\"bool\">false</property>\n  </gz-gui>\n</plugin>\n<plugin filename=\"CameraTracking\" name=\"Camera Tracking\">\n  <gz-gui>\n    <property key=\"resizable\" type=\"bool\">false</property>\n    <property key=\"width\" type=\"double\">5</property>\n    <property key=\"height\" type=\"double\">5</property>\n    <property key=\"state\" type=\"string\">floating</property>\n    <property key=\"showTitleBar\" type=\"bool\">false</property>\n  </gz-gui>\n</plugin>\n<plugin filename=\"MarkerManager\" name=\"Marker manager\">\n  <gz-gui>\n    <property key=\"resizable\" type=\"bool\">false</property>\n    <property key=\"width\" type=\"double\">5</property>\n    <property key=\"height\" type=\"double\">5</property>\n    <property key=\"state\" type=\"string\">floating</property>\n    <property key=\"showTitleBar\" type=\"bool\">false</property>\n  </gz-gui>\n</plugin>\n<plugin filename=\"SelectEntities\" name=\"Select Entities\">\n  <gz-gui>\n    <property key=\"resizable\" type=\"bool\">false</property>\n    <property key=\"width\" type=\"double\">5</property>\n    <property key=\"height\" type=\"double\">5</property>\n    <property key=\"state\" type=\"string\">floating</property>\n    <property key=\"showTitleBar\" type=\"bool\">false</property>\n  </gz-gui>\n</plugin>\n<plugin filename=\"Spawn\" name=\"Spawn Entities\">\n  <gz-gui>\n    <property key=\"resizable\" type=\"bool\">false</property>\n    <property key=\"width\" type=\"double\">5</property>\n    <property key=\"height\" type=\"double\">5</property>\n    <property key=\"state\" type=\"string\">floating</property>\n    <property key=\"showTitleBar\" type=\"bool\">false</property>\n  </gz-gui>\n</plugin>\n<plugin filename=\"VisualizationCapabilities\" name=\"Visualization Capabilities\">\n  <gz-gui>\n    <property key=\"resizable\" type=\"bool\">false</property>\n    <property key=\"width\" type=\"double\">5</property>\n    <property key=\"height\" type=\"double\">5</property>\n    <property key=\"state\" type=\"string\">floating</property>\n    <property key=\"showTitleBar\" type=\"bool\">false</property>\n  </gz-gui>\n</plugin>\n<plugin filename=\"WorldControl\" name=\"World control\">\n  <gz-gui>\n    <title>World control</title>\n    <property type=\"bool\" key=\"showTitleBar\">false</property>\n    <property type=\"bool\" key=\"resizable\">false</property>\n    <property type=\"double\" key=\"height\">72</property>\n    <property type=\"double\" key=\"z\">1</property>\n\n    <property type=\"string\" key=\"state\">floating</property>\n    <anchors target=\"3D View\">\n      <line own=\"left\" target=\"left\"/>\n      <line own=\"bottom\" target=\"bottom\"/>\n    </anchors>\n  </gz-gui>\n\n  <play_pause>true</play_pause>\n  <step>true</step>\n  <start_paused>true</start_paused>\n  <use_event>true</use_event>\n\n</plugin>\n<plugin filename=\"WorldStats\" name=\"World stats\">\n  <gz-gui>\n    <title>World stats</title>\n    <property type=\"bool\" key=\"showTitleBar\">false</property>\n    <property type=\"bool\" key=\"resizable\">false</property>\n    <property type=\"double\" key=\"height\">110</property>\n    <property type=\"double\" key=\"width\">290</property>\n    <property type=\"double\" key=\"z\">1</property>\n\n    <property type=\"string\" key=\"state\">floating</property>\n    <anchors target=\"3D View\">\n      <line own=\"right\" target=\"right\"/>\n      <line own=\"bottom\" target=\"bottom\"/>\n    </anchors>\n  </gz-gui>\n\n  <sim_time>true</sim_time>\n  <real_time>true</real_time>\n  <real_time_factor>true</real_time_factor>\n  <iterations>true</iterations>\n</plugin>\n<plugin filename=\"Shapes\" name=\"Shapes\">\n  <gz-gui>\n    <property key=\"resizable\" type=\"bool\">false</property>\n    <property key=\"x\" type=\"double\">0</property>\n    <property key=\"y\" type=\"double\">0</property>\n    <property key=\"width\" type=\"double\">300</property>\n    <property key=\"height\" type=\"double\">50</property>\n    <property key=\"state\" type=\"string\">floating</property>\n    <property key=\"showTitleBar\" type=\"bool\">false</property>\n    <property key=\"cardBackground\" type=\"string\">#666666</property>\n  </gz-gui>\n</plugin>\n<plugin filename=\"Lights\" name=\"Lights\">\n  <gz-gui>\n    <property key=\"resizable\" type=\"bool\">false</property>\n    <property key=\"x\" type=\"double\">300</property>\n    <property key=\"y\" type=\"double\">0</property>\n    <property key=\"width\" type=\"double\">150</property>\n    <property key=\"height\" type=\"double\">50</property>\n    <property key=\"state\" type=\"string\">floating</property>\n    <property key=\"showTitleBar\" type=\"bool\">false</property>\n    <property key=\"cardBackground\" type=\"string\">#666666</property>\n  </gz-gui>\n</plugin>\n<plugin filename=\"TransformControl\" name=\"Transform control\">\n  <gz-gui>\n    <property key=\"resizable\" type=\"bool\">false</property>\n    <property key=\"x\" type=\"double\">0</property>\n    <property key=\"y\" type=\"double\">50</property>\n    <property key=\"width\" type=\"double\">250</property>\n    <property key=\"height\" type=\"double\">50</property>\n    <property key=\"state\" type=\"string\">floating</property>\n    <property key=\"showTitleBar\" type=\"bool\">false</property>\n    <property key=\"cardBackground\" type=\"string\">#777777</property>\n  </gz-gui>\n</plugin>\n<plugin filename=\"Screenshot\" name=\"Screenshot\">\n  <gz-gui>\n    <property key=\"resizable\" type=\"bool\">false</property>\n    <property key=\"x\" type=\"double\">250</property>\n    <property key=\"y\" type=\"double\">50</property>\n    <property key=\"width\" type=\"double\">50</property>\n    <property key=\"height\" type=\"double\">50</property>\n    <property key=\"state\" type=\"string\">floating</property>\n    <property key=\"showTitleBar\" type=\"bool\">false</property>\n    <property key=\"cardBackground\" type=\"string\">#777777</property>\n  </gz-gui>\n</plugin>\n<plugin filename=\"CopyPaste\" name=\"CopyPaste\">\n  <gz-gui>\n    <property key=\"resizable\" type=\"bool\">false</property>\n    <property key=\"x\" type=\"double\">300</property>\n    <property key=\"y\" type=\"double\">50</property>\n    <property key=\"width\" type=\"double\">100</property>\n    <property key=\"height\" type=\"double\">50</property>\n    <property key=\"state\" type=\"string\">floating</property>\n    <property key=\"showTitleBar\" type=\"bool\">false</property>\n    <property key=\"cardBackground\" type=\"string\">#777777</property>\n  </gz-gui>\n</plugin>\n<plugin filename=\"ComponentInspector\" name=\"Component inspector\">\n  <gz-gui>\n    <property type=\"bool\" key=\"showTitleBar\">false</property>\n    <property type=\"string\" key=\"state\">docked</property>\n  </gz-gui>\n</plugin>\n<plugin filename=\"EntityTree\" name=\"Entity tree\">\n  <gz-gui>\n    <property type=\"bool\" key=\"showTitleBar\">false</property>\n    <property type=\"string\" key=\"state\">docked</property>\n  </gz-gui>\n</plugin>\n</gui>"))
    camera=world.find("gui/plugin[@filename='MinimalScene']/camera_pose")
    home=DATA['stops'][0];yaw=home['yaw']
    camera.text=f"{home['xy'][0]-6*math.cos(yaw):.6f} {home['xy'][1]-6*math.sin(yaw):.6f} 5 0 0.633 {yaw}"
    organize_campus(world)
    ET.indent(root)
    (ROOT/('campus_blocked.sdf' if blocked else 'campus.sdf')).write_text(ET.tostring(root,encoding='unicode')+'\n')


def png(path,w,h,pix):
    def chunk(t,d):return struct.pack('>I',len(d))+t+d+struct.pack('>I',zlib.crc32(t+d)&0xffffffff)
    raw=b''.join(b'\0'+pix[j*w:(j+1)*w] for j in range(h))
    path.write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,8,0,0,0,0))+chunk(b'IDAT',zlib.compress(raw,9))+chunk(b'IEND',b''))


def plan():
    x0,y0,x1,y1=DATA['bounds'];k=730/(x1-x0);left,top=45,80
    def xy(p):return (left+(p[0]-x0)*k,top+(y1-p[1])*k)
    width=(x1-x0)*k+360;height=(y1-y0)*k+135
    s=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
       '<rect width="100%" height="100%" fill="#faf8f2"/>','<g font-family="sans-serif">',
       '<text x="45" y="30" font-size="23" font-weight="bold">Florida Polytechnic University — campus footprint model</text>',
       '<text x="45" y="54" font-size="13">Geographic outlines · north up · 1:1 horizontal meters · illustrative heights</text>']
    def poly(v,c):
        ps=' '.join(f'{a:.2f},{b:.2f}' for a,b in map(xy,v['points']))
        s.append(f'<polygon points="{ps}" fill="{c}" stroke="#46534b" stroke-width=".4"/>')
    s.append(f'<rect x="{left}" y="{top}" width="{(x1-x0)*k}" height="{(y1-y0)*k}" fill="#c0d4a6"/>')
    for v in DATA['parking']:poly(v,'#b4b7b3')
    for v in DATA['sports']:poly(v,'#94be7e')
    for v in DATA['paths']:
        pts=' '.join(f'{a:.2f},{b:.2f}' for a,b in map(xy,v['points']))
        s.append(f'<polyline points="{pts}" fill="none" stroke="'+('#f1ead8' if v['kind']=='walk' or v['bridge'] else '#858e8d')+f'" stroke-width="{v["width"]*k}" stroke-linejoin="round"/>')
    for v in DATA['water']:poly(v,'#78b9cc')
    for v in DATA['buildings']:poly(v,'#9c83bc' if v['source'].startswith('Approximate') else '#e9e1d5')
    labels=[]
    for v in DATA['buildings']:
        if not v['letter'] or v['letter'] in ['N2','N3','N4','N5']:continue
        letter='N' if v['letter']=='N1' else v['letter']
        p=v['points'];a,b=xy((sum(x for x,y in p)/len(p),sum(y for x,y in p)/len(p)))
        s.append(f'<circle cx="{a}" cy="{b}" r="10" fill="#59358b"/><text x="{a}" y="{b+4}" text-anchor="middle" fill="white" font-size="11">{letter}</text>')
        labels.append((letter,'Administration (N1-N5)' if letter=='N' else v['name']))
    for i,v in enumerate(DATA['stops']):
        a,b=xy(v['xy']);s.append(f'<circle cx="{a}" cy="{b}" r="7" fill="#ffdb37" stroke="#333"/><text x="{a}" y="{b+3}" font-size="9" text-anchor="middle">{i}</text>')
    a,b=xy((x1+2,y1-2));s.append(f'<text x="{a}" y="{b}" font-size="17">N ↑</text>')
    for j,(letter,name) in enumerate(sorted(labels)):
        s.append(f'<text x="{left+(x1-x0)*k+25}" y="{top+65+j*24}" font-size="12">{letter}  {escape(name)}</text>')
    by=top+65+len(labels)*24+35
    for i,v in enumerate(DATA['stops']):s.append(f'<text x="{left+(x1-x0)*k+25}" y="{by+i*24}" font-size="12">Yellow {i}: {escape(v["name"])}</text>')
    s += [f'<text x="45" y="{height-35}" font-size="11">Map data © OpenStreetMap contributors (ODbL); 2026 PDF used for labels and approximate purple additions.</text>',
          f'<text x="45" y="{height-17}" font-size="11">Blue = non-traversable water. Widths: map measurements where matched; other paths estimated. Not surveyed.</text>','</g></svg>']
    (ROOT/'campus_plan.svg').write_text('\n'.join(s)+'\n')


def generate():
    (ROOT/'meshes').mkdir(exist_ok=True)
    for v in DATA['buildings']+DATA['water']+DATA['parking']+DATA['sports']:
        h=v.get('height',.45 if v in DATA['water'] else .008 if v in DATA['parking'] else .012)
        mesh(v['points'],h,ROOT/'meshes'/(v['id']+'.obj'))
    validate()
    write_world(False);write_world(True)
    w,h,pix=raster(RES);png(ROOT/'reference.png',w,h,pix)
    x0,y0,_,_=DATA['bounds']
    (ROOT/'reference.yaml').write_text(f'image: reference.png\nmode: trinary\nresolution: {RES}\norigin: [{x0}, {y0}, 0.0]\nnegate: 0\noccupied_thresh: 0.65\nfree_thresh: 0.25\n')
    (ROOT/'mission.json').write_text(json.dumps(dict(scale=DATA['scale'], stops=DATA['stops'], navigation_goals=DATA.get('navigation_goals',[]), barrier=DATA['barrier']),indent=2)+'\n')
    (ROOT/'reference_goals.csv').write_text('x_m,y_m,yaw_rad\n'+''.join(f'{v["xy"][0]},{v["xy"][1]},{v["yaw"]}\n' for v in DATA['stops'][1:]))
    plan()
    assets = ['layout.json', 'generate_campus.py', 'campus.sdf', 'campus_blocked.sdf',
              'reference.yaml', 'reference.png', 'mission.json', 'reference_goals.csv', 'campus_plan.svg']
    assets += [str(p.relative_to(ROOT)) for p in sorted((ROOT/'meshes').glob('*.obj'))]
    manifest = {'schema': 1, 'horizontal_scale': DATA['scale'],
                'sha256': {name: hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in assets}}
    (ROOT/'assets_manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    print(f'Generated geographic campus: {len(DATA["buildings"])} buildings; {len(DATA["water"])} water polygons; {len(DATA["paths"])} path/road features; {w}x{h} map.')


if __name__=='__main__':generate()
