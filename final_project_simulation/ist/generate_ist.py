#!/usr/bin/env python3
"""Rebuild IST from image-digitized rooms/corridors; Python standard library only.
Scale and doorway widths are illustrative, not architectural measurements.
"""
import math,json
from pathlib import Path
from collections import deque
R=Path(__file__).resolve().parent
D=json.loads((R/'layout.json').read_text())
S=D['pixel_to_metres'];OX,OY=D['pixel_origin']
def xy(p):return ((p[0]-OX)*S,(OY-p[1])*S)
FLOOR=[xy(p) for p in D['floor_polygon']]
WALLS=[]
def wall(a,b,name,h=2.4):
 a,b=xy(a),xy(b)
 WALLS.append(dict(name=name,x=(a[0]+b[0])/2,y=(a[1]+b[1])/2,w=math.dist(a,b)+.01,d=.10,h=h,yaw=math.atan2(b[1]-a[1],b[0]-a[0])))
def edges(poly):return zip(poly,poly[1:]+poly[:1])
for i,(a,b) in enumerate(edges(D['floor_polygon'])):wall(a,b,'exterior_'+str(i))
for room in D['rooms']:
 for i,(a,b) in enumerate(edges(room['polygon'])):
  if i==room['door_edge']:
   length=math.dist(a,b);half=min(6,length*.3)/length
   p=lambda t:[a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t]
   wall(a,p(.5-half),'room_'+room['label']+'_door_a')
   wall(p(.5+half),b,'room_'+room['label']+'_door_b')
  else:wall(a,b,'room_'+room['label']+'_wall_'+str(i))
for n,poly in enumerate(D['stairs']):
 for i,(a,b) in enumerate(edges(poly)):wall(a,b,f'stairwell_{n}_{i}',1.)
for n,poly in enumerate(D['atria']):
 for i,(a,b) in enumerate(edges(poly)):wall(a,b,f'atrium_railing_{n}_{i}',.8)
STOPS=[dict(name=p['name'],xy=list(xy(p['pixel'])),yaw=p['yaw']) for p in D['stops']]
b=D['barrier'];bx,by=xy(b['pixel']);BARRIER=dict(name=b['name'],x=bx,y=by,w=b['width'],d=b['depth'],h=b['height'],yaw=b['yaw'])
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
strips=[]
for route in D['corridors']:
 for i,(a,b) in enumerate(zip(route['points'],route['points'][1:])):
  a,b=xy(a),xy(b)
  strips.append(box(dict(name=route['name']+'_floor_'+str(i),x=(a[0]+b[0])/2,y=(a[1]+b[1])/2,w=math.dist(a,b)+.01,d=route['width']*S,h=.008,yaw=math.atan2(b[1]-a[1],b[0]-a[0])),True,'.90 .80 .35 1'))
for blocked in [False,True]:
 models=''.join(box(w) for w in WALLS)+''.join(strips)
 if blocked:models+=box(BARRIER,color='.95 .35 .08 1')
 (R/('ist_blocked.sdf' if blocked else 'ist.sdf')).write_text('<?xml version="1.0"?><sdf version="1.9"><world name="ist">'+plugins+floor+light+models+'</world></sdf>\n')
def inside(x,y,poly):
 hit=False
 for (a,b),(c,d) in edges(poly):
  if (b>y)!=(d>y) and x<(c-a)*(y-b)/(d-b)+a:hit=not hit
 return hit
XMIN,YMIN,WIDTH,HEIGHT=-29.,-17.,58.,34.
def grid(res,blocked=False,clearance=0):
 nx,ny=round(WIDTH/res),round(HEIGHT/res);g=bytearray(nx*ny)
 for j in range(ny):
  for i in range(nx):
   x,y=XMIN+(i+.5)*res,YMIN+(j+.5)*res
   if not inside(x,y,FLOOR) or any(inside(x,y,[xy(p) for p in a]) for a in D['atria']):g[j*nx+i]=1
 for o in WALLS+([BARRIER] if blocked else []):
  rad=math.hypot(o['w']/2+clearance,o['d']/2+clearance);c,s=math.cos(o.get('yaw',0)),math.sin(o.get('yaw',0))
  for j in range(max(0,int((o['y']-rad-YMIN)/res)),min(ny,int((o['y']+rad-YMIN)/res)+1)):
   for i in range(max(0,int((o['x']-rad-XMIN)/res)),min(nx,int((o['x']+rad-XMIN)/res)+1)):
    dx,dy=XMIN+(i+.5)*res-o['x'],YMIN+(j+.5)*res-o['y']
    if abs(c*dx+s*dy)<=o['w']/2+clearance and abs(-s*dx+c*dy)<=o['d']/2+clearance:g[j*nx+i]=1
 return nx,ny,g
# Check mission, entrance landings, and each of the added cross passages.
CHECKS=STOPS+[dict(name=e['name'],xy=list(xy(e['xy']))) for e in D['entrances']]
CHECKS += [dict(name=r['name'],xy=list(xy(r['points'][len(r['points'])//2]))) for r in D['corridors'] if 'cross_passage' in r['name']]
for blocked in [False,True]:
 res=.10;nx,ny,g=grid(res,blocked,.20)
 cells=[(int((p['xy'][0]-XMIN)/res),int((p['xy'][1]-YMIN)/res)) for p in CHECKS]
 assert all(not g[y*nx+x] for x,y in cells),[(p['name'],p['xy']) for p,(x,y) in zip(CHECKS,cells) if g[y*nx+x]]
 q=deque([cells[0]]);seen=set(q)
 while q:
  x,y=q.popleft()
  for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]:
   a,b=x+dx,y+dy
   if 0<=a<nx and 0<=b<ny and not g[b*nx+a] and (a,b) not in seen:seen.add((a,b));q.append((a,b))
 assert all(c in seen for c in cells),[(p['name'],p['xy']) for p,c in zip(CHECKS,cells) if c not in seen]
nx,ny,g=grid(.05)
(R/'reference.pgm').write_bytes(f'P5\n{nx} {ny}\n255\n'.encode()+bytes(0 if g[j*nx+i] else 254 for j in reversed(range(ny)) for i in range(nx)))
(R/'reference.yaml').write_text('image: reference.pgm\nmode: trinary\nresolution: 0.05\norigin: [-29.0, -17.0, 0.0]\nnegate: 0\noccupied_thresh: 0.65\nfree_thresh: 0.25\n')
(R/'mission.json').write_text(json.dumps(dict(version=3,stops=STOPS,barrier=BARRIER,orientation=D['orientation'],scale_note=D['dimensions_note']),indent=2)+'\n')
# Preview uses the same digitized polygons and generated wall geometry.
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="900" viewBox="0 0 1400 900"><rect width="1400" height="900" fill="#faf8f2"/><style>text{font-family:Arial,sans-serif}</style><text x="45" y="38" font-size="25">IST interior — photograph-traced classrooms and passages</text><text x="45" y="68" font-size="16">North at left; south at right. Room positions follow the photo. Scale and doors are illustrative.</text><g transform="translate(-300 -370) scale(2.5)">']
def points(poly):return ' '.join(f'{x},{y}' for x,y in poly)
svg.append(f'<polygon points="{points(D["floor_polygon"])}" fill="#f7e9a7" stroke="#485866" stroke-width=".7"/>')
for poly in D['atria']:svg.append(f'<polygon points="{points(poly)}" fill="#ffffff"/>')
for room in D['rooms']:svg.append(f'<polygon points="{points(room["polygon"])}" fill="#dcebf0"/>')
for poly in D['stairs']:svg.append(f'<polygon points="{points(poly)}" fill="#b6bec7"/>')
for o in WALLS:
 # Convert world boxes back to pixel-coordinate preview.
 x,y=OX+o['x']/S,OY-o['y']/S
 svg.append(f'<rect x="{-o["w"]/2/S}" y="{-o["d"]/2/S}" width="{o["w"]/S}" height="{o["d"]/S}" fill="#485866" transform="translate({x} {y}) rotate({-math.degrees(o["yaw"])})"/>')
for room in D['rooms']:
 x,y=room['label_position'];svg.append(f'<text x="{x}" y="{y+2}" text-anchor="middle" font-size="6.5">{room["label"]}</text>')
for label,x,y in [('NORTH',175,313),('ENTRANCE',175,337),('SOUTH',637,321),('ENTRANCE',637,330)]:svg.append(f'<text x="{x}" y="{y}" font-size="5" text-anchor="middle" fill="#155d6d">{label}</text>')
for i,p in enumerate(D['stops']):
 x,y=p['pixel'];svg.append(f'<circle cx="{x}" cy="{y}" r="4.5" fill="#8d4caf"/><text x="{x}" y="{y+2}" font-size="5.5" text-anchor="middle" fill="white">{i}</text>')
svg.append('</g><text x="45" y="845" font-size="17">Yellow: connected hallway network, end cross-passages, and four entrance/exit landings. Purple: home/deliveries.</text><text x="45" y="875" font-size="15">Image-traced teaching layout — not measured architecture. All maps from the previous IST version must be rebuilt.</text></svg>')
(R/'ist_plan.svg').write_text(''.join(svg)+'\n')
print(f'IST v3: {len(D["rooms"])} photo-traced rooms; {len(WALLS)} wall segments. Mission, 4 entrances and 2 end cross-passages connected in both variants (0.20 m clearance).')
