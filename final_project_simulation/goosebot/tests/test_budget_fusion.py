"""Offline synthetic tests: measurement provenance, map likelihood, fair replay."""
import ast
import functools
import json
import math
from pathlib import Path
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import numpy as np
from PIL import Image
import yaml

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
from budget_fusion_core import WHEELS, wheel_geometry, wheel_speed, LikelihoodField, scan_points, estimate
from gps_fusion_core import read_settings


def description():
    return '<robot>'+''.join(
        f'<joint name="{name}"><child link="{name}_link"/><axis xyz="0 1 0"/></joint>'
        f'<link name="{name}_link"><collision><geometry><cylinder radius="0.03"/></geometry></collision></link>'
        for name in WHEELS)+'</robot>'


@functools.lru_cache(maxsize=1)
def fixture():
    temp = tempfile.TemporaryDirectory()
    root = Path(temp.name)
    pixels = np.full((100, 100), 254, dtype=np.uint8)
    pixels[:2, :] = pixels[-2:, :] = 0
    pixels[:, :2] = pixels[:, -2:] = 0
    pixels[15:35, 72:76] = 0
    pixels[76:80, 15:45] = 0
    Image.fromarray(pixels).save(root/'map.pgm')
    (root/'map.yaml').write_text(yaml.safe_dump({'image':'map.pgm','origin':[-5,-5,0],
        'resolution':.1,'negate':0,'occupied_thresh':.65,'free_thresh':.196}))
    field = LikelihoodField(root/'map.yaml')
    rng = np.random.default_rng(10)
    rows, truth = [], []
    datum = [28.1485,-81.8495,0.]
    for i in range(1321):
        t = i*.05
        elapsed = min(max(t-3,0),60)
        yaw = .1*elapsed
        xy = np.array([1.5*math.sin(yaw), 1.5*(1-math.cos(yaw))])
        moving = 3 <= t < 63
        rows.append(dict(kind='wheel',t=t,speed=.165 if moving else 0.)) # declared synthetic +10% encoder error
        rows.append(dict(kind='imu',t=t,yaw_rate=(.1 if moving else 0)+.002))
        truth.append([t,*xy])
        if i%4==0:
            fix = xy+rng.normal(0,1.5,2)
            rows.append(dict(kind='gps',t=t,latitude=datum[0]+fix[1]/110800,
                longitude=datum[1]+fix[0]/(111320*math.cos(math.radians(datum[0]))),
                altitude=0,status=0,covariance_type=2,r00=2.25,r01=0.,r11=2.25))
        if i%20==0:
            angles=np.linspace(-math.pi,math.pi,120,endpoint=False)
            steps=np.arange(.12,12,.04)
            xx=xy[0]+np.cos(angles[:,None]+yaw)*steps
            yy=xy[1]+np.sin(angles[:,None]+yaw)*steps
            ci=np.floor((xx+5)/.1).astype(int);cj=99-np.floor((yy+5)/.1).astype(int)
            outside=(ci<0)|(ci>=100)|(cj<0)|(cj>=100)
            hits=outside|(pixels[np.clip(cj,0,99),np.clip(ci,0,99)]==0)
            ranges=steps[np.argmax(hits,axis=1)]+rng.normal(0,.005,len(angles))
            rows.append(dict(kind='scan',t=t,angle_min=-math.pi,angle_increment=2*math.pi/120,
                             range_min=.12,range_max=12,ranges=ranges.tolist()))
    meta=dict(ready_t=3,world=dict(datum=datum,home_xy=[0.,0.],home_yaw=0.),
              settings=read_settings(HERE/'gps_fusion_settings.json'),lidar_mount_xyyaw=[0.,0.,0.])
    estimates,diagnostics=estimate(rows,meta,field)
    return temp,field,rows,meta,np.array(truth),estimates,diagnostics


class BudgetFusionTests(unittest.TestCase):
    def test_uses_measured_joint_rates_and_urdf_radii(self):
        radii=wheel_geometry(description())
        self.assertEqual(radii,[.03]*4)
        self.assertAlmostEqual(wheel_speed(list(WHEELS),[10]*4,radii),.3)
        shuffled=list(reversed(WHEELS))
        self.assertAlmostEqual(wheel_speed(shuffled,[10]*4,radii),.3)
        with self.assertRaisesRegex(ValueError,'missing'):
            wheel_speed(list(WHEELS)[:3],[1]*3,radii)
        with self.assertRaisesRegex(ValueError,'velocities'):
            wheel_speed(list(WHEELS),[],radii)
        with self.assertRaisesRegex(ValueError,'axes'):
            wheel_geometry(description().replace('0 1 0','0 -1 0'))

    def test_scan_conversion_uses_mount_and_rejects_no_return(self):
        row=dict(ranges=[1,None,12,.05,2],angle_min=0,angle_increment=0,
                 range_min=.12,range_max=12)
        points=scan_points(row,[1,2,math.pi/2])
        np.testing.assert_allclose(points,[[1,3],[1,4]],atol=1e-12)

    def test_lidar_fusion_corrects_declared_synthetic_encoder_error(self):
        _,_,_,meta,truth,out,diag=fixture()
        reference=np.column_stack([np.interp(out[:,0],truth[:,0],truth[:,k]) for k in (1,2)])
        errors=[np.sqrt(np.mean(np.sum((out[:,1+2*i:3+2*i]-reference)**2,axis=1))) for i in range(4)]
        self.assertLess(errors[2],errors[0])
        self.assertLess(errors[3],errors[0])
        self.assertGreater(diag['lidar_updates_C'],30)
        self.assertAlmostEqual(diag['gyro_bias_rad_s'],.002,delta=.002)
        self.assertGreater(diag['wheel_travel_m'],5)

    def test_dropout_keeps_lidar_estimate_finite_and_no_gps_control_unchanged(self):
        _,field,rows,meta,_,normal,_=fixture()
        dropped,diag=estimate(rows,meta,field,dropout=(10,30))
        self.assertTrue(np.isfinite(dropped).all())
        np.testing.assert_array_equal(dropped[:,7:9],normal[:,7:9])
        self.assertLess(diag['gps_accepted'],fixture()[-1]['gps_accepted'])

    def test_missing_sensors_and_short_routes_are_rejected(self):
        _,field,rows,meta,*_=fixture()
        with self.assertRaisesRegex(ValueError,'missing or stale'):
            estimate([r for r in rows if not(r['kind']=='wheel' and 10<r['t']<11)],meta,field)
        with self.assertRaisesRegex(ValueError,'below 5'):
            estimate([r for r in rows if r['t']<10],meta,field)

    def test_seed_reproduces_estimates_and_estimator_has_no_truth_argument(self):
        import inspect
        _,field,rows,meta,_,normal,_=fixture()
        again,_=estimate(rows,meta,field)
        np.testing.assert_array_equal(again,normal)
        self.assertNotIn('truth',inspect.signature(estimate).parameters)
        names={n.id for n in ast.walk(ast.parse(inspect.getsource(estimate))) if isinstance(n,ast.Name)}
        self.assertNotIn('truth',names)

    def test_recorder_has_no_rtk_command_odometry_or_truth_feedback(self):
        source=(HERE/'budget_compare.py').read_text()
        tree=ast.parse(source)
        calls=[n for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute)
               and n.func.attr=='create_subscription']
        topics={n.args[1].value for n in calls if isinstance(n.args[1],ast.Constant)}
        self.assertEqual(topics,{'/robot_description','/joint_states','/imu/data','/gps/fix','/scan','/ground_truth/pose'})
        self.assertNotIn('create_publisher',source)
        self.assertNotIn('TransformBroadcaster',source)
        self.assertLess(source.index('estimates, diagnostics = estimate('),source.index("truth = np.genfromtxt"))

    def test_report_writes_plot_metrics_and_estimates_without_truth_input(self):
        import budget_compare
        _,field,rows,meta,truth,_,_=fixture()
        # Isolate report serialization from the separate supplied-map validator.
        # Actual raster matching and geometry validation have their own tests.
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            (root/'metadata.json').write_text(json.dumps(dict(meta,complete=True)))
            (root/'sensors.jsonl').write_text('\n'.join(json.dumps(r) for r in rows)+'\n')
            np.savetxt(root/'truth.csv',truth,delimiter=',',header='t,x,y',comments='')
            map_path=Path(fixture()[0].name)/'map.yaml'
            (map_path.parent/'reference.png').write_bytes((map_path.parent/'map.pgm').read_bytes())
            args=SimpleNamespace(input=root,map=map_path,world='fixture',seed=7,gps_dropout=None)
            with patch('gps_reference_map.validate_reference_map'),patch('budget_compare.read_world',return_value=meta['world']):
                budget_compare.report(args)
            metrics=json.loads((root/'budget_comparison_metrics.json').read_text())
            self.assertEqual(set(metrics['metrics']),{'A','B','C','D'})
            self.assertGreater((root/'budget_comparison.png').stat().st_size,1000)
            self.assertTrue((root/'budget_comparison_estimates.csv').exists())


if __name__=='__main__':
    unittest.main()
