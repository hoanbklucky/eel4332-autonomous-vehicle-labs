#!/usr/bin/env python3
"""Approximate IST teaching interior traced by layout, not surveyed dimensions.
Stdlib only. Regenerates two SDF worlds, reference PGM/YAML, SVG and mission.
"""
import math,json
from pathlib import Path
from collections import deque
R=Path(__file__).resolve().parent
WALLS=[]
def wall(a,b,name,height=2.4):
 x,y=(a[0]+b[0])/2,(a[1]+b[1])/2
 WALLS.append(dict(name=name,x=x,y=y,w=math.dist(a,b)+.02,d=.16,h=height,yaw=math.atan2(b[1]-a[1],b[0]-a[0])))
def pt(a,b,t):return (a*math.cos(t),b*math.sin(t))
def arc(a,b,start,end,name,door=False):
 # Leave a 1.2 m door at the middle of each outer classroom's hall wall.
 mid=(start+end)/2
 gap=.6/math.hypot(a*math.sin(mid),b*math.cos(mid)) if door else 0
 spans=[(start,mid-gap),(mid+gap,end)] if door else [(start,end)]
 for q,(s,e) in enumerate(spans):
  n=max(1,math.ceil((e-s)/.035))
  for i in range(n):wall(pt(a,b,s+(e-s)*i/n),pt(a,b,s+(e-s)*(i+1)/n),f'{name}_{q}_{i}')
# Photo orientation retained: north/1045 at left; south/1002 at right.
top=['1002','1003','1012','1014','1015','1017','1026','1028','1030','1032','1044','1045']
bottom=['1048','1049','1051','1053','1056','1058','1060','1062','1064','1066','1067','1068']
ROOMS=[]
for half,labels in enumerate([top,bottom]):
 for i,label in enumerate(labels):
  s=half*math.pi+i*math.pi/len(labels);e=s+math.pi/len(labels);m=(s+e)/2
  arc(28,14,s,e,'exterior_'+label)
  arc(24,10.5,s,e,'hall_'+label,True)
  wall(pt(24,10.5,s),pt(28,14,s),'partition_'+label)
  ROOMS.append(dict(label=label,xy=pt(26,12.2,m)))
# Inner oval encloses atria and core; broad openings join the central passage.
for i in range(180):
 s=2*math.pi*i/180;e=2*math.pi*(i+1)/180;m=(s+e)/2
 if abs(22*math.cos(m))>1.4:wall(pt(22,8,s),pt(22,8,e),'inner_'+str(i))
# Four teaching blocks and north/south cross passage, plus east/west access.
for x,y,label in [(-3.8,2.9,'1023'),(3.8,2.9,'1020'),(-3.8,-2.9,'1022'),(3.8,-2.9,'1021')]:
 a,b=x-2.5,x+2.5;c,d=y-1.8,y+1.8
 wall((a,c),(b,c),'core_'+label+'_south');wall((a,d),(b,d),'core_'+label+'_north')
 wall((a,c),(a,d),'core_'+label+'_west')
 wall((b,c),(b,y-.6),'core_'+label+'_east1');wall((b,y+.6),(b,d),'core_'+label+'_east2')
 ROOMS.append(dict(label=label,xy=(x,y)))
# Inner classroom bands beside the end atria (simplified photo layout).
for x,y,label in [(-10,3.5,'1031'),(10,3.5,'1013'),(-10,-3.5,'1052'),(10,-3.5,'1063')]:
 a,b=x-2.1,x+2.1;c,d=y-1.1,y+1.1
 wall((a,c),(b,c),'band_'+label+'_south');wall((a,d),(b,d),'band_'+label+'_north')
 wall((a,c),(a,d),'band_'+label+'_west')
 wall((b,c),(b,y-.5),'band_'+label+'_east1');wall((b,y+.5),(b,d),'band_'+label+'_east2')
 ROOMS.append(dict(label=label,xy=(x,y)))
STOPS=[dict(name='Home / north end',xy=[-23,0],yaw=math.pi/2),dict(name='Near 1044',xy=list(pt(23,9.25,2.65)),yaw=0),dict(name='Near 1003',xy=list(pt(23,9.25,.40)),yaw=0),dict(name='Near 1066',xy=list(pt(23,9.25,-.55)),yaw=0)]
BARRIER=dict(name='hall_barrier',x=0,y=9.25,w=2.8,d=.35,h=1,yaw=math.pi/2)
def box(o,visual_only=False,color='.72 .76 .80 1'):
 geom=f'<geometry><box><size>{o["w"]} {o["d"]} {o["h"]}</size></box></geometry>'
 return f'<model name="{o["name"]}"><static>true</static><pose>{o["x"]} {o["y"]} {o["h"]/2} 0 0 {o.get("yaw",0)}</pose><link name="link">'+('' if visual_only else '<collision name="collision">'+geom+'</collision>')+'<visual name="visual">'+geom+f'<material><ambient>{color}</ambient><diffuse>{color}</diffuse></material></visual></link></model>'
plugins='''<plugin filename="gz-sim-physics-system" name="gz::sim::systems::Physics"/>
<plugin filename="gz-sim-user-commands-system" name="gz::sim::systems::UserCommands"/>
<plugin filename="gz-sim-scene-broadcaster-system" name="gz::sim::systems::SceneBroadcaster"/>
<plugin filename="gz-sim-sensors-system" name="gz::sim::systems::Sensors"><render_engine>ogre2</render_engine></plugin>
<plugin filename="gz-sim-imu-system" name="gz::sim::systems::Imu"/>
<plugin filename="gz-sim-navsat-system" name="gz::sim::systems::NavSat"/>'''
floor='<model name="floor"><static>true</static><link name="link"><collision name="floor"><geometry><plane><normal>0 0 1</normal><size>70 38</size></plane></geometry></collision><visual name="floor"><geometry><plane><normal>0 0 1</normal><size>70 38</size></plane></geometry><material><ambient>.85 .85 .82 1</ambient><diffuse>.85 .85 .82 1</diffuse></material></visual></link></model>'
light='<light name="sun" type="directional"><pose>0 0 12 0 0 0</pose><diffuse>1 1 1 1</diffuse><specular>.2 .2 .2 1</specular><direction>-.2 -.3 -1</direction><cast_shadows>true</cast_shadows></light>'
# Yellow visual-only floor strips follow the hallway. No roof for inspection.
strips=[]
for i in range(120):
 a=pt(23,9.25,i*2*math.pi/120);b=pt(23,9.25,(i+1)*2*math.pi/120)
 strips.append(box(dict(name='hall_floor_'+str(i),x=(a[0]+b[0])/2,y=(a[1]+b[1])/2,w=math.dist(a,b)+.03,d=1.65,h=.008,yaw=math.atan2(b[1]-a[1],b[0]-a[0])),True,'.88 .77 .30 1'))
strips.append(box(dict(name='cross_passage_floor',x=0,y=0,w=2.4,d=18.5,h=.01),True,'.88 .77 .30 1'))
for blocked in [False,True]:
 models=''.join(box(w) for w in WALLS)+''.join(strips)
 if blocked:models+=box(BARRIER,color='.95 .35 .08 1')
 (R/('ist_blocked.sdf' if blocked else 'ist.sdf')).write_text('<?xml version="1.0"?><sdf version="1.9"><world name="ist">'+plugins+floor+light+models+'</world></sdf>\n')
def occupied(x,y,blocked=False,clearance=0):
 if (x/28)**2+(y/14)**2>=1:return True
 for o in WALLS+([BARRIER] if blocked else []):
  c,s=math.cos(o.get('yaw',0)),math.sin(o.get('yaw',0));dx,dy=x-o['x'],y-o['y']
  if abs(c*dx+s*dy)<=o['w']/2+clearance and abs(-s*dx+c*dy)<=o['d']/2+clearance:return True
 return False
# Rasterize each box only within its bounding box, not all walls at every pixel.
def grid(res,blocked=False,clearance=0):
 nx,ny=round(60/res),round(32/res);g=bytearray(nx*ny)
 for j in range(ny):
  for i in range(nx):
   x,y=-30+(i+.5)*res,-16+(j+.5)*res
   if (x/28)**2+(y/14)**2>=1:g[j*nx+i]=1
 for o in WALLS+([BARRIER] if blocked else []):
  rad=math.hypot(o['w']/2+clearance,o['d']/2+clearance);c,s=math.cos(o.get('yaw',0)),math.sin(o.get('yaw',0))
  for j in range(max(0,int((o['y']-rad+16)/res)),min(ny,int((o['y']+rad+16)/res)+1)):
   for i in range(max(0,int((o['x']-rad+30)/res)),min(nx,int((o['x']+rad+30)/res)+1)):
    dx,dy=-30+(i+.5)*res-o['x'],-16+(j+.5)*res-o['y']
    if abs(c*dx+s*dy)<=o['w']/2+clearance and abs(-s*dx+c*dy)<=o['d']/2+clearance:g[j*nx+i]=1
 return nx,ny,g
for blocked in [False,True]:
 res=.15;nx,ny,g=grid(res,blocked,.25)
 cells=[(int((o['xy'][0]+30)/res),int((o['xy'][1]+16)/res)) for o in STOPS]
 assert all(not g[y*nx+x] for x,y in cells),'Stop too close to wall'
 q=deque([cells[0]]);seen=set(q)
 while q:
  x,y=q.popleft()
  for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]:
   a,b=x+dx,y+dy
   if 0<=a<nx and 0<=b<ny and not g[b*nx+a] and (a,b) not in seen:seen.add((a,b));q.append((a,b))
 assert all(c in seen for c in cells),'Disconnected mission'
nx,ny,g=grid(.05)
(R/'reference.pgm').write_bytes(f'P5\n{nx} {ny}\n255\n'.encode()+bytes(0 if g[j*nx+i] else 254 for j in reversed(range(ny)) for i in range(nx)))
(R/'reference.yaml').write_text('image: reference.pgm\nmode: trinary\nresolution: 0.05\norigin: [-30.0, -16.0, 0.0]\nnegate: 0\noccupied_thresh: 0.65\nfree_thresh: 0.25\n')
(R/'mission.json').write_text(json.dumps(dict(stops=STOPS,barrier=BARRIER,dimensions='approximate 56 x 28 m',orientation='north at left in supplied photo; not geographic north-up'),indent=2)+'\n')
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="620" viewBox="0 0 1200 620"><rect width="1200" height="620" fill="#faf8f2"/><text x="40" y="38" font-size="25" font-family="sans-serif">IST teaching interior — oval hallway and classrooms</text><text x="40" y="65" font-size="15" font-family="sans-serif">Approximate geometry; room labels follow the photo, dimensions/doors are illustrative. North is at left.</text><g transform="translate(600 310) scale(16 -16)"><ellipse rx="28" ry="14" fill="#e2edf0"/><ellipse rx="24" ry="10.5" fill="#f4d96c"/><ellipse rx="22" ry="8" fill="#f3f0e5"/><rect x="-1.2" y="-9.25" width="2.4" height="18.5" fill="#f4d96c"/>']
for o in WALLS:svg.append(f'<rect x="{-o["w"]/2}" y="{-o["d"]/2}" width="{o["w"]}" height="{o["d"]}" fill="#4b5663" transform="translate({o["x"]} {o["y"]}) rotate({math.degrees(o["yaw"])})"/>')
svg.append('</g>')
for o in ROOMS:
 x,y=o['xy'];svg.append(f'<text x="{600+16*x}" y="{310-16*y+4}" text-anchor="middle" font-size="13" font-family="sans-serif">{o["label"]}</text>')
for i,o in enumerate(STOPS):
 x,y=o['xy'];svg.append(f'<circle cx="{600+16*x}" cy="{310-16*y}" r="10" fill="#a35cbe"/><text x="{600+16*x}" y="{314-16*y}" text-anchor="middle" fill="white" font-size="12">{i}</text>')
svg.append('<text x="40" y="555" font-size="17" font-family="sans-serif">Yellow: oval hallway and cross passage. Purple 0: home; 1–3: delivery stops in the hallway.</text><text x="40" y="582" font-size="15" font-family="sans-serif">Blocked variant: orange barrier across upper hallway at (0, 9.25); use the lower loop or central passage.</text></svg>')
(R/'ist_plan.svg').write_text(''.join(svg)+'\n')
print(f'Generated IST: {len(WALLS)} wall segments, {len(ROOMS)} labelled teaching rooms. Both missions connected at 0.25 m clearance.')
