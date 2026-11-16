#!/usr/bin/env python3
"""Create a small low-wall Goosebot practice world and matching geometric map.
Standard library only. This reference map is for perfect-localization warm-up,
not a student SLAM result. No robot is embedded; use Goosebot's spawn launch.
"""
import math,struct,zlib,json
from pathlib import Path
from collections import deque
R=Path(__file__).resolve().parent
BOXES=[('north_wall',0,4,10,.16,.45,'.45 .55 .65 1'),('south_wall',0,-4,10,.16,.45,'.45 .55 .65 1'),('west_wall',-5,0,.16,8,.45,'.45 .55 .65 1'),('east_wall',5,0,.16,8,.45,'.45 .55 .65 1'),('center_block',0,0,1.6,1.0,.35,'.30 .65 .85 1'),('upper_block',-2,1.8,.8,.8,.35,'.85 .55 .25 1'),('lower_block',2,-1,.8,.8,.35,'.45 .75 .40 1')]
START=(-3.5,-2.5);GOAL=(3.,-2.5)
def box(o):
 n,x,y,w,d,h,col=o;geo=f'<geometry><box><size>{w} {d} {h}</size></box></geometry>'
 return f'<model name="{n}"><static>true</static><pose>{x} {y} {h/2} 0 0 0</pose><link name="link"><collision name="collision">{geo}</collision><visual name="visual">{geo}<material><ambient>{col}</ambient><diffuse>{col}</diffuse></material></visual></link></model>'
plugins='''<plugin filename="gz-sim-physics-system" name="gz::sim::systems::Physics"/>
<plugin filename="gz-sim-user-commands-system" name="gz::sim::systems::UserCommands"/>
<plugin filename="gz-sim-scene-broadcaster-system" name="gz::sim::systems::SceneBroadcaster"/>
<plugin filename="gz-sim-sensors-system" name="gz::sim::systems::Sensors"><render_engine>ogre2</render_engine></plugin>
<plugin filename="gz-sim-imu-system" name="gz::sim::systems::Imu"/>
<plugin filename="gz-sim-navsat-system" name="gz::sim::systems::NavSat"/>'''
floor='<model name="ground_plane"><static>true</static><link name="link"><collision name="floor"><geometry><plane><normal>0 0 1</normal><size>12 10</size></plane></geometry></collision><visual name="floor"><geometry><plane><normal>0 0 1</normal><size>12 10</size></plane></geometry><material><ambient>.87 .87 .85 1</ambient><diffuse>.87 .87 .85 1</diffuse></material></visual></link></model>'
light='<light name="sun" type="directional"><pose>0 0 10 0 0 0</pose><diffuse>1 1 1 1</diffuse><specular>.2 .2 .2 1</specular><direction>-.2 -.3 -1</direction><cast_shadows>false</cast_shadows></light>'
(R/'warmup.sdf').write_text('<?xml version="1.0"?><sdf version="1.9"><world name="goosebot_warmup"><gravity>0 0 -9.8</gravity>'+plugins+floor+light+''.join(box(o) for o in BOXES)+'</world></sdf>\n')
def occupied(x,y,margin=0):
 if abs(x)>5 or abs(y)>4:return True
 return any(abs(x-b[1])<=b[3]/2+margin and abs(y-b[2])<=b[4]/2+margin for b in BOXES)
res=.05;xmin,ymin=-5.5,-4.5;nx,ny=220,180
# Cell centres match map origin/resolution; PNG rows run top-to-bottom.
raw=b''.join(b'\0'+bytes(0 if occupied(xmin+(i+.5)*res,ymin+(j+.5)*res) else 254 for i in range(nx)) for j in reversed(range(ny)))
def chunk(name,data):return struct.pack('!I',len(data))+name+data+struct.pack('!I',zlib.crc32(name+data)&0xffffffff)
(R/'reference.png').write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('!2I5B',nx,ny,8,0,0,0,0))+chunk(b'IDAT',zlib.compress(raw,9))+chunk(b'IEND',b''))
(R/'reference.yaml').write_text('image: reference.png\nmode: trinary\nresolution: 0.05\norigin: [-5.5, -4.5, 0.0]\nnegate: 0\noccupied_thresh: 0.65\nfree_thresh: 0.25\n')
# Independent inflated-grid reachability sanity check (not a Nav2 test).
step=.1;w,h=100,80
def cell(p):return (int((p[0]+5)/step),int((p[1]+4)/step))
a,b=cell(START),cell(GOAL);q=deque([a]);seen={a}
while q:
 x,y=q.popleft()
 for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]:
  c,d=x+dx,y+dy
  if 0<=c<w and 0<=d<h and (c,d) not in seen and not occupied(-5+(c+.5)*step,-4+(d+.5)*step,.3):seen.add((c,d));q.append((c,d))
assert b in seen and not occupied(*START,.3) and not occupied(*GOAL,.3)
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="850" height="730" viewBox="0 0 850 730"><rect width="850" height="730" fill="#faf8f2"/><style>text{font-family:Arial,sans-serif}</style><text x="45" y="36" font-size="23">Goosebot warm-up — open practice arena</text><text x="45" y="64" font-size="15">10 × 8 m • low walls • wide routes • no maze textures</text><g transform="translate(425 355) scale(65 -65)"><rect x="-5" y="-4" width="10" height="8" fill="#ecebe5"/>']
for n,x,y,w,d,h,col in BOXES:svg.append(f'<rect x="{x-w/2}" y="{y-d/2}" width="{w}" height="{d}" fill="#6d899b"/>')
svg.append('</g>')
for label,p,color in [('Start, facing +x',START,'#7954ac'),('Example goal',GOAL,'#25855c')]:
 x,y=425+65*p[0],355-65*p[1];svg.append(f'<circle cx="{x}" cy="{y}" r="9" fill="{color}"/><text x="{x}" y="{y+28}" text-anchor="middle" font-size="15">{label}</text>')
svg.append('<text x="45" y="666" font-size="16">Use the supplied geometric map and perfect localization for this warm-up only.</text><text x="45" y="695" font-size="14">Offline geometry preview; Gazebo/robot/Nav2 still require a local pilot run.</text></svg>')
(R/'warmup_plan.svg').write_text(''.join(svg)+'\n')
print('Generated low-wall warm-up and matching map; start/goal connected with 0.30 m grid clearance.')
