"""Asset consistency and 1:1 scale checks; no ROS required."""
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
class FullScaleTests(unittest.TestCase):
    def test_geographic_horizontal_scale_is_restored(self):
        d=json.loads((ROOT/'layout.json').read_text())
        self.assertEqual(d['scale'],1.)
        self.assertEqual(d['previous_horizontal_scale'],.06)
        first=next(v for v in d['buildings'] if v['name']=='IST')['points'][0]
        for value,original in zip(first,[-7.0624,11.0594]):
            self.assertAlmostEqual(value,original/.06,places=5)
        self.assertGreater(d['bounds'][2]-d['bounds'][0],1200)
        self.assertTrue(all(v['width']>=3 for v in d['paths']))
        self.assertTrue(all('not surveyed' in v['width_source'] for v in d['paths']))

    def test_width_measurements_are_local_and_corridor_is_not_pavement(self):
        d=json.loads((ROOT/'layout.json').read_text())
        by_id={v['id']:v for v in d['paths']}
        for measurement in d['width_measurements']:
            if measurement['applied_as_pavement_width']:
                for name in measurement['feature_ids']+measurement.get('continuation_feature_ids',[]):
                    self.assertEqual(by_id[name]['width'],measurement['width_m'])
                    self.assertEqual(by_id[name]['width_measurement_id'],measurement['id'])
                    for world in ['campus.sdf','campus_blocked.sdf']:
                        tree=ET.parse(ROOT/world)
                        model=tree.find(f".//model[@name='{name}_0']")
                        width=float(model.findtext('link/visual/geometry/box/size').split()[1])
                        self.assertEqual(width,measurement['width_m'])
            else:
                self.assertEqual(measurement['width_m'],21.87)
                self.assertTrue(measurement['includes_median_sidewalk_or_verge'])
                self.assertEqual(measurement['feature_ids'],[])
        self.assertEqual(by_id['path_467811278_0']['width'],11.31)
        self.assertEqual(by_id['path_467810969_0']['width'],3.12)
        self.assertEqual(by_id['path_507676803_0']['width'],7.22)
        self.assertFalse(any(v['width']==21.87 for v in d['paths']))
        self.assertTrue(all(v['robot_access']=='motor_road' for v in d['paths'] if v['name']=='Polytechnic Circle'))
        self.assertEqual(by_id['path_467811278_0']['robot_access'],'pedestrian')
        self.assertEqual(by_id['path_507676803_0']['robot_access'],'pedestrian')
        self.assertTrue(all(v['surface']=='non_asphalt_paved' for v in d['paths'] if v['robot_access']=='pedestrian'))
        self.assertTrue(any(v['kind']=='road' and v['surface']=='non_asphalt_paved' for v in d['paths']))

    def test_all_manifest_assets_match(self):
        manifest=json.loads((ROOT/'assets_manifest.json').read_text())
        self.assertEqual(manifest['horizontal_scale'],1.)
        for name,digest in manifest['sha256'].items():
            self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),digest,name)

    def test_both_worlds_keep_geometry_and_camera_near_known_home(self):
        d=json.loads((ROOT/'layout.json').read_text());home=d['stops'][0]['xy']
        for file in ['campus.sdf','campus_blocked.sdf']:
            world=ET.parse(ROOT/file).getroot().find('world')
            group=world.find("model[@name='campus']")
            self.assertEqual(group.findtext('pose'),'0 0 0 0 0 0')
            camera=list(map(float,world.find(".//plugin[@filename='MinimalScene']/camera_pose").text.split()))
            self.assertLess(math.dist(camera[:2],home),10)
            for i,stop in enumerate(d['stops']):
                pose=list(map(float,group.find(f"model[@name='delivery_pad_{i}']/pose").text.split()))
                self.assertLess(math.dist(pose[:2],stop['xy']),1e-6)

    def test_scanline_raster_matches_point_membership(self):
        spec=importlib.util.spec_from_file_location('fullscale_generator',ROOT/'generate_campus.py')
        g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
        # Use a small isolated domain to check exact center sampling at edges.
        old=g.DATA;g.DATA=dict(bounds=[0,0,4,4],buildings=[dict(points=[[1,.7],[3,1.4],[2,3.2]])],water=[],barrier={})
        try:
            w,h,pixels=g.raster(.25)
            obstacles=g.obstacles()
            for j in range(h):
                for i in range(w):
                    occupied=any(g.inside((i+.5)*.25,4-(j+.5)*.25,p) for p in obstacles)
                    self.assertEqual(pixels[j*w+i]==0,occupied)
        finally:g.DATA=old

if __name__=='__main__':unittest.main()
