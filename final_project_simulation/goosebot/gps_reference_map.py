"""Validate the supplied geometric campus map for GPS-ENU planning.

Only a known prior obstacle map is loaded. No localization, TF or truth topic.
Student SLAM maps need independent alignment and are deliberately rejected.
"""
import importlib.util
import json
import hashlib
import math
from pathlib import Path

import numpy as np
import yaml

from gps_fusion_core import read_world


def crossing_candidates(layout):
    """Short transverse intersections of existing pedestrian and motor paths.

    This is a supplied simulation access rule, not detection of real crosswalks.
    Parallel/oblique shared road segments do not become pedestrian routes.
    """
    pedestrians=[]; motors=[]
    for feature in layout['paths']:
        access=feature.get('robot_access', 'pedestrian' if feature['kind']=='walk' else 'motor_road')
        target=pedestrians if access=='pedestrian' else motors
        for start,end in zip(feature['points'],feature['points'][1:]):
            a,b=np.asarray(start,dtype=float),np.asarray(end,dtype=float)
            length=float(np.linalg.norm(b-a))
            if length>=.03:target.append((feature,a,b-a,length))
    def cross(a,b):return float(a[0]*b[1]-a[1]*b[0])
    for pedestrian,a,v,length in pedestrians:
        for motor,c,w,motor_length in motors:
            det=cross(v,w)
            sine=abs(det)/(length*motor_length)
            if sine<math.sin(math.pi/4)-1e-9:continue
            t=cross(c-a,w)/det;u=cross(c-a,v)/det
            if not (-1e-9<=t<=1+1e-9 and -1e-9<=u<=1+1e-9):continue
            cosine=abs(float(np.dot(v,w)))/(length*motor_length)
            half_length=(motor['width']/2+pedestrian['width']/2*cosine)/sine+.5
            if half_length>10:continue  # do not open a long asphalt corridor
            yield dict(center=a+t*v, direction=v/length, half_length=half_length,
                       width=pedestrian['width'], pedestrian=pedestrian.get('id'),
                       motor=motor.get('id'))


def road_mask(layout, obstacle_pixels, resolution, origin):
    """Permit pedestrian pavement and short mapped crossings across asphalt lanes.

    No added connectors, widened corridors, parking lots or grass shortcuts.
    Flat round joins match the world pavement at bends.
    One-cell erosion leaves a conservative raster boundary margin.
    """
    from PIL import Image, ImageFilter
    height, width = obstacle_pixels.shape
    allowed = np.zeros((height, width), dtype=bool)
    motor_roads = np.zeros((height, width), dtype=bool)
    for feature in layout['paths']:
        if feature['kind'] not in ('road', 'walk'):
            continue
        access = feature.get('robot_access', 'pedestrian' if feature['kind']=='walk' else 'motor_road')
        if access not in ('pedestrian','motor_road'):
            raise ValueError('Unknown campus access classification')
        target = allowed if access=='pedestrian' else motor_roads
        half_width = float(feature['width']) / 2
        for start, end in zip(feature['points'], feature['points'][1:]):
            a, b = np.asarray(start, dtype=float), np.asarray(end, dtype=float)
            delta = b - a
            length = float(np.linalg.norm(delta))
            if length < .03:
                continue
            unit = delta / length
            # The world generator draws a rectangle length+0.03, not a capsule.
            lo = np.minimum(a, b) - half_width - .015
            hi = np.maximum(a, b) + half_width + .015
            i0 = max(0, int(math.floor((lo[0] - origin[0]) / resolution)))
            i1 = min(width, int(math.ceil((hi[0] - origin[0]) / resolution)))
            j0 = max(0, int(math.floor(height - (hi[1] - origin[1]) / resolution)))
            j1 = min(height, int(math.ceil(height - (lo[1] - origin[1]) / resolution)))
            if i1 <= i0 or j1 <= j0:
                continue
            x = origin[0] + (np.arange(i0, i1) + .5) * resolution - a[0]
            y = origin[1] + (height - np.arange(j0, j1) - .5) * resolution - a[1]
            along = x[None, :] * unit[0] + y[:, None] * unit[1]
            across = -x[None, :] * unit[1] + y[:, None] * unit[0]
            target[j0:j1, i0:i1] |= ((along >= -.015) & (along <= length + .015)
                                      & (np.abs(across) <= half_width))
        # Match the flat circular pavement joins in the Gazebo world. Segment
        # rectangles alone create post-like forbidden wedges at polyline bends.
        for point in feature['points'][1:-1]:
            cx, cy = point
            i0=max(0,int(math.floor((cx-half_width-origin[0])/resolution)))
            i1=min(width,int(math.ceil((cx+half_width-origin[0])/resolution)))
            j0=max(0,int(math.floor(height-(cy+half_width-origin[1])/resolution)))
            j1=min(height,int(math.ceil(height-(cy-half_width-origin[1])/resolution)))
            if i1<=i0 or j1<=j0:continue
            x=origin[0]+(np.arange(i0,i1)+.5)*resolution-cx
            y=origin[1]+(height-np.arange(j0,j1)-.5)*resolution-cy
            target[j0:j1,i0:i1] |= x[None,:]**2+y[:,None]**2<=half_width**2
    # Restore only short transverse crossings supported by mapped pedestrian
    # pavement on BOTH sides. Intersect with allowed pavement below; this
    # cannot invent grass links, remove buildings, or open asphalt lengthwise.
    crossings=np.zeros_like(allowed)
    def on_pavement(xy):
        i=int(math.floor((xy[0]-origin[0])/resolution))
        j=height-1-int(math.floor((xy[1]-origin[1])/resolution))
        return (0<=i<width and 0<=j<height and allowed[j,i]
                and obstacle_pixels[j,i]==254)
    for crossing in crossing_candidates(layout):
        center=crossing['center'];unit=crossing['direction']
        span=crossing['half_length'];half_width=crossing['width']/2
        if not all(on_pavement(center+sign*span*unit) for sign in (-1,1)):continue
        a,b=center-span*unit,center+span*unit
        lo=np.minimum(a,b)-half_width;hi=np.maximum(a,b)+half_width
        i0=max(0,int(math.floor((lo[0]-origin[0])/resolution)))
        i1=min(width,int(math.ceil((hi[0]-origin[0])/resolution)))
        j0=max(0,int(math.floor(height-(hi[1]-origin[1])/resolution)))
        j1=min(height,int(math.ceil(height-(lo[1]-origin[1])/resolution)))
        if i1<=i0 or j1<=j0:continue
        x=origin[0]+(np.arange(i0,i1)+.5)*resolution-center[0]
        y=origin[1]+(height-np.arange(j0,j1)-.5)*resolution-center[1]
        along=x[None,:]*unit[0]+y[:,None]*unit[1]
        across=-x[None,:]*unit[1]+y[:,None]*unit[0]
        crossings[j0:j1,i0:i1] |= (np.abs(along)<=span)&(np.abs(across)<=half_width)
    allowed &= (obstacle_pixels == 254) & (~motor_roads | crossings)
    safe = np.asarray(Image.fromarray(allowed.astype('uint8') * 255).filter(ImageFilter.MinFilter(3))) == 255
    return np.where(safe, 254, 0).astype('uint8')


def prepare_reference_map(map_path, world_path, destination):
    """Write a temporary pedestrian-only navigation map; never modify supplied assets."""
    from PIL import Image
    data = validate_reference_map(map_path, world_path)
    source = Path(map_path).expanduser().resolve()
    layout = json.loads(source.with_name('layout.json').read_text())
    with Image.open(source.parent / data['image']) as image:
        pixels = np.asarray(image.convert('L'))
    # Full campus: retain the supplied 25 cm global grid. Upsampling the
    # entire 1.2 km campus to 5 cm would allocate hundreds of millions of cells.
    # Nav2's rolling local grid remains fine-resolution for footprint checking.
    resolution = float(data['resolution'])
    mask = road_mask(layout, pixels, resolution, data['origin'])
    world = read_world(world_path)
    home = np.asarray(world['home_xy'])
    cell = np.floor((home - np.asarray(data['origin'][:2])) / resolution).astype(int)
    row = mask.shape[0] - 1 - cell[1]
    if not (0 <= row < mask.shape[0] and 0 <= cell[0] < mask.shape[1]
            and mask[row, cell[0]] == 254):
        raise ValueError('Known Home is outside the permitted pedestrian mask')
    output = Path(destination).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    raster_path = output.with_suffix('.pgm')
    Image.fromarray(mask).save(raster_path)
    result = dict(data, image=str(raster_path), resolution=resolution, mode='trinary', negate=0)
    output.write_text(yaml.safe_dump(result, sort_keys=False))
    return output


def validate_reference_map(map_path, world_path):
    """Check map/datum/extent and pixels against the campus layout generator."""
    world_path = Path(world_path).expanduser().resolve()
    path = Path(map_path).expanduser().resolve()
    if (world_path.name not in ('campus.sdf', 'campus_blocked.sdf')
            or path != world_path.with_name('reference.yaml')):
        raise ValueError('GPS prior-map mode accepts only campus/reference.yaml beside the selected campus world; not an unaligned SLAM map')
    world = read_world(world_path)
    layout = json.loads(path.with_name('layout.json').read_text())
    if layout.get('scale') != 1.0:
        raise ValueError('Use the full-scale campus layout, world and reference map together')
    for feature in layout['paths']:
        surface=feature.get('surface')
        wanted={'non_asphalt_paved':'pedestrian','asphalt':'motor_road'}.get(surface)
        if wanted is None or feature.get('robot_access')!=wanted:
            raise ValueError('Restore the explicit matching campus surface/access classifications')
    lon, lat = layout['origin_lon_lat']
    if world['datum'] != [lat, lon, 0.0]:
        raise ValueError('Campus map layout and GPS world datum differ')
    data = yaml.safe_load(path.read_text())
    if not isinstance(data, dict):
        raise ValueError('Invalid reference map YAML')
    if (data.get('mode', 'trinary') != 'trinary' or data.get('negate') != 0
            or data.get('occupied_thresh') != .65 or data.get('free_thresh') != .25):
        raise ValueError('Use the supplied trinary reference-map settings')
    bounds = np.asarray(layout['bounds'], dtype=float)
    origin = np.asarray(data.get('origin', []), dtype=float)
    resolution = float(data.get('resolution', 0))
    if (bounds.shape != (4,) or not np.isfinite(bounds).all()
            or origin.shape != (3,) or not np.isfinite(origin).all()
            or not np.array_equal(origin, [bounds[0], bounds[1], 0.])
            or resolution != float(layout.get('reference_resolution_m', .25))):
        raise ValueError('Reference-map origin/resolution no longer matches the generated campus grid')
    image = (path.parent / data['image']).resolve()
    if image != path.with_name('reference.png'):
        raise ValueError('Reference map must use its matching campus/reference.png')
    from PIL import Image
    with Image.open(image) as raster:
        pixels = np.asarray(raster.convert('L'))
    # Load only the supplied generator (its main() is not run), then compare
    # regenerated pixels in memory. No world, mesh or map files are rewritten.
    generator_path = path.with_name('generate_campus.py')
    spec = importlib.util.spec_from_file_location('course_campus_reference', generator_path)
    generator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(generator)
    width, height, expected = generator.raster(resolution)
    if pixels.shape != (height, width) or pixels.tobytes() != bytes(expected):
        raise ValueError('Reference image differs from layout-generated obstacles; restore matching supplied assets')
    manifest = json.loads(path.with_name('assets_manifest.json').read_text())
    required = [world_path.name, 'layout.json', 'generate_campus.py', 'reference.yaml',
                'reference.png', 'mission.json']
    required += [name for name in manifest.get('sha256', {}) if name.startswith('meshes/')]
    if manifest.get('horizontal_scale') != 1.0:
        raise ValueError('Use the matching full-scale campus asset manifest')
    for name in required:
        asset = path.parent/name
        if (not asset.is_file() or hashlib.sha256(asset.read_bytes()).hexdigest()
                != manifest.get('sha256', {}).get(name)):
            raise ValueError(f'Campus asset bundle mismatch: {name}; update world/map/meshes together')
    return data
