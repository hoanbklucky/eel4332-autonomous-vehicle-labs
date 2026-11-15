"""Generate a schematic teaching world, reference occupancy map, and SVG plan.

All geometry is approximate and intentionally reduced to a 24 x 30 m arena.
No image tracing, geographic scale, or surveyed campus accuracy is claimed.
Run with Python 3; no third-party dependencies.
"""
from pathlib import Path
from collections import deque
from html import escape
import math
import json
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
RES = 0.1
WIDTH, HEIGHT = 240, 300
# name, x, y, width, depth, height, color. All boxes have matching collisions.
BOXES = [
    ('boundary_w', -11.9, 0, .2, 30, 1.2, '#786a58'),
    ('boundary_e', 11.9, 0, .2, 30, 1.2, '#786a58'),
    ('boundary_s', 0, -14.9, 24, .2, 1.2, '#786a58'),
    ('boundary_n', 0, 14.9, 24, .2, 1.2, '#786a58'),
    ('IST', -7.5, 8, 4, 5, 2, '#dddded'),
    ('BARC', -8, 0.5, 3, 3, 1.5, '#806aa7'),
    ('Residence_I', 7, 9, 4, 2, 1.6, '#c6b99a'),
    ('Residence_II', 8, 5, 2, 4, 1.6, '#c6b99a'),
    ('Engineering', 7, -6, 4, 3, 1.5, '#806aa7'),
    ('Recreation', 7, -11, 4, 2, 1, '#8daf6e'),
    ('lake_north', 0, 8, 4, 5, .5, '#369aa8'),
    ('lake_middle', 0, 1, 4, 5, .5, '#369aa8'),
    ('lake_south', 0, -6, 4, 5, .5, '#369aa8'),
]
BARRIER = ('route_barrier', -8, -3, 8, .5, 1, '#ed9c25')
STOPS = [('Home', -8, -11), ('IST delivery', -4, 8),
         ('Residence delivery', 6, 6), ('Engineering delivery', 6, -9)]


def rgba(color):
    return ' '.join(str(int(color[i:i+2], 16) / 255) for i in (1, 3, 5)) + ' 1'


def model(parent, name, x, y, w, d, h, color, collision=True):
    m = ET.SubElement(parent, 'model', name=name)
    ET.SubElement(m, 'static').text = 'true'
    ET.SubElement(m, 'pose').text = f'{x} {y} {h/2} 0 0 0'
    link = ET.SubElement(m, 'link', name='body')
    for tag in (['collision', 'visual'] if collision else ['visual']):
        node = ET.SubElement(link, tag, name=tag)
        geometry = ET.SubElement(node, 'geometry')
        ET.SubElement(ET.SubElement(geometry, 'box'), 'size').text = f'{w} {d} {h}'
        if tag == 'visual':
            mat = ET.SubElement(node, 'material')
            ET.SubElement(mat, 'ambient').text = rgba(color)
            ET.SubElement(mat, 'diffuse').text = rgba(color)


def world(blocked):
    sdf = ET.Element('sdf', version='1.8')
    w = ET.SubElement(sdf, 'world', name='default')
    physics = ET.SubElement(w, 'physics', name='physics', type='ignored')
    ET.SubElement(physics, 'max_step_size').text = '0.001'
    ET.SubElement(physics, 'real_time_factor').text = '1'
    for filename, name in [('physics', 'Physics'), ('user-commands', 'UserCommands'),
                           ('scene-broadcaster', 'SceneBroadcaster'),
                           ('sensors', 'Sensors'), ('imu', 'Imu')]:
        p = ET.SubElement(w, 'plugin', filename=f'gz-sim-{filename}-system',
                          name=f'gz::sim::systems::{name}')
        if name == 'Sensors':
            ET.SubElement(p, 'render_engine').text = 'ogre2'
    light = ET.SubElement(w, 'light', name='sun', type='directional')
    ET.SubElement(light, 'pose').text = '0 0 15 0 0 0'
    ET.SubElement(light, 'diffuse').text = '.9 .9 .9 1'
    ET.SubElement(light, 'specular').text = '.2 .2 .2 1'
    ET.SubElement(light, 'direction').text = '-.5 .1 -1'
    model(w, 'ground', 0, 0, 26, 32, .1, '#c7d3b3')
    # Put the top of the ground at z=0; flat crossing strips are visual only.
    w.find("model[@name='ground']/pose").text = '0 0 -0.05 0 0 0'
    for y in (4.5, -2.5):
        model(w, f'crossing_{y}', 0, y, 10, 1.8, .006, '#dfdbd0', False)
    for box in BOXES + ([BARRIER] if blocked else []):
        model(w, *box)
    for label, x, y in STOPS:
        model(w, label.replace(' ', '_') + '_pad', x, y, .7, .7, .008,
              '#f8dc49', False)
    ET.indent(sdf)
    return ET.tostring(sdf, encoding='unicode') + '\n'


def occupied(x, y, boxes, margin=0):
    return any(abs(x-b[1]) <= b[3]/2+margin and abs(y-b[2]) <= b[4]/2+margin
               for b in boxes)


def validate():
    # Conservative 0.4 m center clearance; 0.1 m grid connectivity in both worlds.
    for blocked in (False, True):
        boxes = BOXES + ([BARRIER] if blocked else [])
        def cell(x, y): return (round((x+12)*10), round((y+15)*10))
        start = cell(STOPS[0][1], STOPS[0][2])
        seen, queue = {start}, deque([start])
        while queue:
            i, j = queue.popleft()
            for ni, nj in ((i-1,j), (i+1,j), (i,j-1), (i,j+1)):
                if (ni,nj) in seen or not (0 <= ni <= 240 and 0 <= nj <= 300):
                    continue
                if occupied(ni/10-12, nj/10-15, boxes, .4): continue
                seen.add((ni,nj)); queue.append((ni,nj))
        for name, x, y in STOPS:
            assert not occupied(x,y,boxes,.4), f'{name}: insufficient clearance'
            assert cell(x,y) in seen, f'{name}: disconnected in blocked={blocked}'
    print('Geometry check passed: all four stops connected with 0.4 m clearance in both worlds.')


def generate():
    validate()
    (ROOT/'mission.json').write_text(json.dumps({'stops': [{'name': label, 'xy': [x, y], 'yaw': 0} for label, x, y in STOPS]}, indent=2)+'\n')
    for blocked in (False, True):
        (ROOT / ('campus_blocked.sdf' if blocked else 'campus.sdf')).write_text(world(blocked))
    # ASCII PGM is accepted by image/map loaders and can be committed as text.
    rows = []
    for j in range(HEIGHT):
        y = 15 - (j+.5)*RES
        rows.append(' '.join('0' if occupied(-12+(i+.5)*RES,y,BOXES) else '254'
                             for i in range(WIDTH)))
    (ROOT/'reference.pgm').write_text(f'P2\n# Geometric reference, not SLAM output\n{WIDTH} {HEIGHT}\n255\n'+'\n'.join(rows)+'\n')
    (ROOT/'reference.yaml').write_text('image: reference.pgm\nmode: trinary\nresolution: 0.1\norigin: [-12.0, -15.0, 0.0]\nnegate: 0\noccupied_thresh: 0.65\nfree_thresh: 0.25\n')
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="720" height="980" viewBox="0 0 720 980">',
           '<rect width="720" height="980" fill="#faf8f3"/>',
           '<text x="36" y="35" font-size="22" font-family="sans-serif">Florida Poly-inspired delivery arena</text>',
           '<text x="36" y="60" font-size="14">Schematic 24 x 30 m; not a surveyed campus map</text>']
    def pt(x,y): return (60+(x+12)*25, 95+(15-y)*25)
    for name,x,y,w,d,h,color in BOXES:
        px,py=pt(x-w/2,y+d/2)
        svg.append(f'<rect x="{px}" y="{py}" width="{w*25}" height="{d*25}" fill="{color}"/>')
        if not name.startswith('boundary'):
            cx,cy=pt(x,y)
            svg.append(f'<text x="{cx}" y="{cy}" font-size="11" text-anchor="middle">{escape(name.replace("_", " "))}</text>')
    for label,x,y in STOPS:
        px,py=pt(x,y)
        svg.append(f'<circle cx="{px}" cy="{py}" r="8" fill="#ffce22" stroke="#222"/><text x="{px+12}" y="{py+5}" font-size="12">{label}</text>')
    px,py=pt(-12,-2.75)
    svg.append(f'<rect x="{px}" y="{py}" width="200" height="12.5" fill="none" stroke="#b56d00" stroke-dasharray="5 3"/>')
    svg += ['<text x="60" y="885" font-size="14">Dashed orange: obstacle variant only. Blue: solid lake barriers.</text>',
            '<text x="60" y="910" font-size="14">World axes: +x right, +y up. Yellow: delivery/home pads.</text>',
            '<text x="60" y="935" font-size="14">Reference map and SDF use the same obstacle geometry.</text>', '</svg>']
    (ROOT/'campus_plan.svg').write_text('\n'.join(svg)+'\n')


if __name__ == '__main__':
    generate()

